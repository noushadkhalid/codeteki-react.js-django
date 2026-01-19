"""
CRM Celery Tasks

Background tasks for AI-powered CRM automation:
- process_pending_deals: Hourly check for deals needing action
- send_scheduled_emails: Every 15 min, send pending emails
- check_email_replies: Every 30 min, poll inbox for replies
- daily_ai_review: Daily review and scoring
"""

import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_pending_deals(self):
    """
    Process deals that need action based on next_action_date.
    Runs hourly.
    """
    from crm.models import Deal, DealActivity, PipelineStage
    from crm.services.ai_agent import CRMAIAgent

    logger.info("Starting process_pending_deals task")

    ai_agent = CRMAIAgent()
    processed = 0
    errors = 0

    # Find deals with next_action_date <= now and status active
    pending_deals = Deal.objects.filter(
        status='active',
        next_action_date__lte=timezone.now()
    ).select_related('contact', 'pipeline', 'current_stage')[:50]  # Process in batches

    for deal in pending_deals:
        try:
            with transaction.atomic():
                # Get AI recommendation
                result = ai_agent.analyze_deal(deal)
                action = result.get('action', 'flag_for_review')
                metadata = result.get('metadata', {})

                logger.info(f"Deal {deal.id}: AI recommends '{action}'")

                if action == 'send_email':
                    # Queue email for sending
                    queue_deal_email.delay(str(deal.id), metadata.get('email_type', 'followup'))

                elif action == 'move_stage':
                    # Move to suggested stage
                    suggested_stage_name = metadata.get('suggested_stage', '')
                    if suggested_stage_name:
                        next_stage = PipelineStage.objects.filter(
                            pipeline=deal.pipeline,
                            name__icontains=suggested_stage_name
                        ).first()
                        if next_stage:
                            deal.move_to_stage(next_stage)
                            DealActivity.objects.create(
                                deal=deal,
                                activity_type='stage_change',
                                description=f"AI moved to stage: {next_stage.name}",
                                metadata={'reason': result.get('reasoning', '')}
                            )

                elif action == 'wait':
                    # Update next action date
                    wait_days = int(metadata.get('wait_days', 3))
                    deal.next_action_date = timezone.now() + timedelta(days=wait_days)
                    deal.save(update_fields=['next_action_date'])

                elif action == 'pause':
                    deal.status = 'paused'
                    deal.save(update_fields=['status'])
                    DealActivity.objects.create(
                        deal=deal,
                        activity_type='status_change',
                        description=f"AI paused deal: {result.get('reasoning', '')}",
                    )

                elif action == 'flag_for_review':
                    # Add to AI notes for human review
                    deal.ai_notes = (deal.ai_notes or '') + f"\n[{timezone.now().strftime('%Y-%m-%d')}] Flagged for review: {result.get('reasoning', '')}"
                    deal.save(update_fields=['ai_notes'])

                processed += 1

        except Exception as e:
            logger.error(f"Error processing deal {deal.id}: {e}")
            errors += 1

    logger.info(f"process_pending_deals completed: {processed} processed, {errors} errors")
    return {'processed': processed, 'errors': errors}


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def queue_deal_email(self, deal_id: str, email_type: str = 'followup'):
    """
    Queue an email to be sent for a deal.
    Called by process_pending_deals or manually.
    """
    from crm.models import Deal, EmailLog, DealActivity
    from crm.services.ai_agent import CRMAIAgent
    from crm.services.email_service import get_email_service

    logger.info(f"Queuing email for deal {deal_id}, type: {email_type}")

    try:
        deal = Deal.objects.select_related('contact', 'pipeline', 'current_stage').get(id=deal_id)
    except Deal.DoesNotExist:
        logger.error(f"Deal {deal_id} not found")
        return {'success': False, 'error': 'Deal not found'}

    ai_agent = CRMAIAgent()
    email_service = get_email_service()

    # Compose email using AI
    email_result = ai_agent.compose_email(deal, context={'email_type': email_type})

    if not email_result.get('success'):
        logger.error(f"Failed to compose email for deal {deal_id}")
        return {'success': False, 'error': 'Email composition failed'}

    # Create email log entry
    email_log = EmailLog.objects.create(
        deal=deal,
        subject=email_result['subject'],
        body=email_result['body'],
        to_email=deal.contact.email,
        ai_generated=True
    )

    # Send email
    send_result = email_service.send(
        to=deal.contact.email,
        subject=email_result['subject'],
        body=email_result['body'],
        tracking_id=str(email_log.tracking_id)
    )

    if send_result['success']:
        email_log.sent_at = timezone.now()
        email_log.zoho_message_id = send_result.get('message_id', '')
        email_log.save()

        # Update deal
        deal.emails_sent += 1
        deal.last_contact_date = timezone.now()
        deal.next_action_date = timezone.now() + timedelta(days=deal.current_stage.days_until_followup if deal.current_stage else 3)
        deal.save(update_fields=['emails_sent', 'last_contact_date', 'next_action_date'])

        # Log activity
        DealActivity.objects.create(
            deal=deal,
            activity_type='email_sent',
            description=f"Email sent: {email_result['subject']}",
            metadata={'email_log_id': str(email_log.id)}
        )

        logger.info(f"Email sent successfully to {deal.contact.email}")
        return {'success': True, 'email_log_id': str(email_log.id)}
    else:
        logger.error(f"Failed to send email: {send_result.get('error')}")
        return {'success': False, 'error': send_result.get('error')}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def send_scheduled_emails(self):
    """
    Send emails that are queued but not yet sent.
    Runs every 15 minutes.
    """
    from crm.models import EmailLog, DealActivity
    from crm.services.email_service import get_email_service

    logger.info("Starting send_scheduled_emails task")

    email_service = get_email_service()
    sent = 0
    errors = 0

    # Find unsent emails (created in last 24 hours)
    unsent_emails = EmailLog.objects.filter(
        sent_at__isnull=True,
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).select_related('deal', 'deal__contact')[:20]

    for email_log in unsent_emails:
        try:
            result = email_service.send(
                to=email_log.to_email,
                subject=email_log.subject,
                body=email_log.body,
                tracking_id=str(email_log.tracking_id)
            )

            if result['success']:
                email_log.sent_at = timezone.now()
                email_log.zoho_message_id = result.get('message_id', '')
                email_log.save()

                # Update deal
                deal = email_log.deal
                deal.emails_sent += 1
                deal.last_contact_date = timezone.now()
                deal.save(update_fields=['emails_sent', 'last_contact_date'])

                DealActivity.objects.create(
                    deal=deal,
                    activity_type='email_sent',
                    description=f"Email sent: {email_log.subject}",
                )

                sent += 1
            else:
                errors += 1

        except Exception as e:
            logger.error(f"Error sending email {email_log.id}: {e}")
            errors += 1

    logger.info(f"send_scheduled_emails completed: {sent} sent, {errors} errors")
    return {'sent': sent, 'errors': errors}


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def check_email_replies(self):
    """
    Check inbox for replies and process them.
    Runs every 30 minutes.
    """
    from crm.models import EmailLog, Deal, DealActivity, PipelineStage
    from crm.services.email_service import get_email_service
    from crm.services.ai_agent import CRMAIAgent

    logger.info("Starting check_email_replies task")

    email_service = get_email_service()
    ai_agent = CRMAIAgent()
    processed = 0

    # Get recent inbox messages
    since = timezone.now() - timedelta(hours=2)  # Last 2 hours
    messages = email_service.get_inbox_messages(since=since, limit=50)

    for msg in messages:
        try:
            # Skip if already processed (check by message_id)
            if EmailLog.objects.filter(zoho_message_id=msg['message_id']).exists():
                continue

            # Try to match to a deal
            deal = email_service.match_reply_to_deal(
                from_email=msg['from_email'],
                subject=msg['subject']
            )

            if not deal:
                logger.debug(f"No deal match for email from {msg['from_email']}")
                continue

            # Get full message content
            content = email_service.get_message_content(msg['message_id'])
            if not content:
                content = msg.get('summary', '')

            # Classify the reply using AI
            classification = ai_agent.classify_reply(content, deal=deal)

            # Find the original email log and mark as replied
            original_email = EmailLog.objects.filter(
                deal=deal,
                sent_at__isnull=False
            ).order_by('-sent_at').first()

            if original_email:
                original_email.replied = True
                original_email.replied_at = msg['received_at']
                original_email.reply_content = content[:2000]  # Truncate if too long
                original_email.save()

            # Log activity
            DealActivity.objects.create(
                deal=deal,
                activity_type='email_replied',
                description=f"Reply received: {classification.get('summary', 'No summary')}",
                metadata={
                    'sentiment': classification.get('sentiment'),
                    'intent': classification.get('intent'),
                    'from_email': msg['from_email']
                }
            )

            # Take action based on classification
            intent = classification.get('intent', 'other')
            suggested_action = classification.get('suggested_action', '')

            if intent == 'interested':
                # Move to interested stage if exists
                interested_stage = PipelineStage.objects.filter(
                    pipeline=deal.pipeline,
                    name__icontains='interested'
                ).first()
                if interested_stage and deal.current_stage != interested_stage:
                    deal.move_to_stage(interested_stage)
                    DealActivity.objects.create(
                        deal=deal,
                        activity_type='stage_change',
                        description=f"Moved to {interested_stage.name} based on reply"
                    )

            elif intent == 'not_interested':
                deal.status = 'lost'
                deal.ai_notes = (deal.ai_notes or '') + f"\n[{timezone.now().strftime('%Y-%m-%d')}] Marked as not interested based on reply"
                deal.save()
                DealActivity.objects.create(
                    deal=deal,
                    activity_type='status_change',
                    description="Deal marked as lost - not interested"
                )

            elif intent == 'unsubscribe':
                deal.status = 'lost'
                deal.save()

            elif intent == 'out_of_office':
                # Push next action date
                deal.next_action_date = timezone.now() + timedelta(days=7)
                deal.save(update_fields=['next_action_date'])

            processed += 1

        except Exception as e:
            logger.error(f"Error processing reply: {e}")

    logger.info(f"check_email_replies completed: {processed} processed")
    return {'processed': processed}


@shared_task(bind=True, max_retries=1)
def daily_ai_review(self):
    """
    Daily review of all active deals and contacts.
    Runs at 9 AM.
    """
    from crm.models import Deal, Contact, DealActivity
    from crm.services.ai_agent import CRMAIAgent

    logger.info("Starting daily_ai_review task")

    ai_agent = CRMAIAgent()
    reviewed_deals = 0
    scored_contacts = 0

    # Review active deals
    active_deals = Deal.objects.filter(status='active').select_related(
        'contact', 'pipeline', 'current_stage'
    )[:100]

    for deal in active_deals:
        try:
            # Check for stuck deals (no activity in 14+ days)
            if deal.last_contact_date:
                days_since_contact = (timezone.now() - deal.last_contact_date).days
                if days_since_contact > 14:
                    deal.ai_notes = (deal.ai_notes or '') + f"\n[{timezone.now().strftime('%Y-%m-%d')}] STALE: No contact in {days_since_contact} days"
                    deal.save(update_fields=['ai_notes'])

            # Ensure next_action_date is set for active deals
            if not deal.next_action_date:
                deal.next_action_date = timezone.now()
                deal.save(update_fields=['next_action_date'])

            reviewed_deals += 1

        except Exception as e:
            logger.error(f"Error reviewing deal {deal.id}: {e}")

    # Score new contacts without scores
    unscored_contacts = Contact.objects.filter(
        ai_score=0
    )[:50]

    for contact in unscored_contacts:
        try:
            ai_agent.score_lead(contact)
            scored_contacts += 1
        except Exception as e:
            logger.error(f"Error scoring contact {contact.id}: {e}")

    logger.info(f"daily_ai_review completed: {reviewed_deals} deals reviewed, {scored_contacts} contacts scored")
    return {
        'reviewed_deals': reviewed_deals,
        'scored_contacts': scored_contacts
    }


@shared_task
def score_contact(contact_id: str):
    """
    Score a single contact using AI.
    Can be called manually or triggered by signals.
    """
    from crm.models import Contact
    from crm.services.ai_agent import CRMAIAgent

    try:
        contact = Contact.objects.get(id=contact_id)
    except Contact.DoesNotExist:
        logger.error(f"Contact {contact_id} not found")
        return {'success': False, 'error': 'Contact not found'}

    ai_agent = CRMAIAgent()
    score = ai_agent.score_lead(contact)

    logger.info(f"Contact {contact_id} scored: {score}/100")
    return {'success': True, 'score': score}


@shared_task
def process_backlink_opportunity(opportunity_id: str):
    """
    Process a backlink opportunity - generate pitch and create contact.
    """
    from crm.models import BacklinkOpportunity, Contact, Deal, Pipeline
    from crm.services.ai_agent import CRMAIAgent

    logger.info(f"Processing backlink opportunity {opportunity_id}")

    try:
        opportunity = BacklinkOpportunity.objects.get(id=opportunity_id)
    except BacklinkOpportunity.DoesNotExist:
        return {'success': False, 'error': 'Opportunity not found'}

    ai_agent = CRMAIAgent()

    # Generate pitch
    pitch_result = ai_agent.generate_backlink_pitch(opportunity)

    if not pitch_result.get('success'):
        return {'success': False, 'error': 'Failed to generate pitch'}

    # Update opportunity status
    opportunity.status = 'researching'
    opportunity.save()

    logger.info(f"Backlink opportunity {opportunity_id} processed successfully")
    return {
        'success': True,
        'pitch_angle': pitch_result.get('angle', ''),
        'email_subject': pitch_result.get('email_subject', '')
    }


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def process_contact_import(self, import_id: str):
    """
    Process a CSV contact import asynchronously.

    Args:
        import_id: UUID of the ContactImport record
    """
    from crm.models import ContactImport
    from crm.services.csv_importer import CSVContactImporter

    logger.info(f"Processing contact import {import_id}")

    try:
        contact_import = ContactImport.objects.get(id=import_id)
    except ContactImport.DoesNotExist:
        logger.error(f"ContactImport {import_id} not found")
        return {'success': False, 'error': 'Import not found'}

    importer = CSVContactImporter(contact_import)
    result = importer.process()

    logger.info(f"Contact import {import_id} completed: {result}")
    return result


@shared_task
def generate_email_draft(deal_id: str):
    """
    Generate an email draft for a deal and save to AI notes.
    Used for bulk draft generation without sending.
    """
    from crm.models import Deal
    from crm.services.ai_agent import CRMAIAgent

    logger.info(f"Generating email draft for deal {deal_id}")

    try:
        deal = Deal.objects.select_related('contact', 'pipeline', 'current_stage').get(id=deal_id)
    except Deal.DoesNotExist:
        logger.error(f"Deal {deal_id} not found")
        return {'success': False, 'error': 'Deal not found'}

    ai_agent = CRMAIAgent()

    try:
        email_result = ai_agent.compose_email(deal, context={'email_type': 'outreach'})

        if email_result.get('success'):
            # Save draft to AI notes
            draft_text = f"[DRAFT - {timezone.now().strftime('%Y-%m-%d %H:%M')}]\n"
            draft_text += f"To: {deal.contact.email}\n"
            draft_text += f"Subject: {email_result['subject']}\n\n"
            draft_text += email_result['body']

            deal.ai_notes = draft_text
            deal.save(update_fields=['ai_notes'])

            logger.info(f"Draft saved for deal {deal_id}")
            return {'success': True, 'subject': email_result['subject']}
        else:
            logger.error(f"Failed to generate draft: {email_result.get('error')}")
            return {'success': False, 'error': email_result.get('error')}

    except Exception as e:
        logger.error(f"Error generating draft for deal {deal_id}: {e}")
        return {'success': False, 'error': str(e)}


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def process_backlink_import(self, import_id: str):
    """
    Process a backlink opportunity import asynchronously.

    Args:
        import_id: UUID of the BacklinkImport record
    """
    from crm.models import BacklinkImport
    from crm.services.backlink_importer import BacklinkImporter

    logger.info(f"Processing backlink import {import_id}")

    try:
        backlink_import = BacklinkImport.objects.get(id=import_id)
    except BacklinkImport.DoesNotExist:
        logger.error(f"BacklinkImport {import_id} not found")
        return {'success': False, 'error': 'Import not found'}

    importer = BacklinkImporter(backlink_import)
    result = importer.process()

    logger.info(f"Backlink import {import_id} completed: {result}")
    return result
