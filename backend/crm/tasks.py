"""
CRM Celery Tasks

Background tasks for AI-powered CRM automation:
- process_pending_deals: Hourly check for deals needing action (weekdays 9-5)
- send_scheduled_emails: Every 15 min, send pending emails (weekdays 9-5)
- check_email_replies: Every 30 min, poll inbox for replies (24/7)
- daily_ai_review: Daily review and scoring (weekday mornings)
"""

import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)

# Office hours: Mon-Fri 9AM-5PM (server timezone)
OFFICE_HOUR_START = 9
OFFICE_HOUR_END = 17  # 5 PM
OFFICE_DAYS = range(0, 5)  # Monday=0 through Friday=4


def is_office_hours() -> bool:
    """Check if current time is within office hours (Mon-Fri 9AM-5PM)."""
    now = timezone.localtime()
    return now.weekday() in OFFICE_DAYS and OFFICE_HOUR_START <= now.hour < OFFICE_HOUR_END


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_pending_deals(self):
    """
    Process deals that need action based on next_action_date.
    Runs hourly during office hours (Mon-Fri 9AM-5PM).
    Engagement-aware with burnout detection and ghost handling.
    """
    if not is_office_hours():
        logger.info("process_pending_deals skipped: outside office hours")
        return {'processed': 0, 'errors': 0, 'skipped': 'outside_office_hours'}

    from crm.models import Deal, DealActivity, PipelineStage
    from crm.services.ai_agent import CRMAIAgent
    from crm.services.engagement_engine import get_engagement_profile

    logger.info("Starting process_pending_deals task")

    ai_agent = CRMAIAgent()
    processed = 0
    errors = 0

    # Find deals with next_action_date <= now and status active
    pending_deals = Deal.objects.filter(
        status='active',
        next_action_date__lte=timezone.now(),
        autopilot_paused=False,
    ).select_related('contact', 'pipeline', 'current_stage')[:50]

    for deal in pending_deals:
        try:
            with transaction.atomic():
                # SAFETY: Skip bounced contacts
                contact = deal.contact
                if contact.email_bounced:
                    deal.status = 'lost'
                    deal.lost_reason = 'invalid_email'
                    deal.save(update_fields=['status', 'lost_reason'])
                    DealActivity.objects.create(
                        deal=deal,
                        activity_type='status_change',
                        description=f"[Autopilot] Contact email bounced - deal auto-closed"
                    )
                    processed += 1
                    logger.info(f"Deal {deal.id}: Contact email bounced, auto-closed")
                    continue

                # SAFETY: Skip unsubscribed contacts (belt-and-suspenders)
                brand_slug = deal.pipeline.brand.slug if deal.pipeline and deal.pipeline.brand else None
                if contact.is_unsubscribed or (brand_slug and contact.is_unsubscribed_from_brand(brand_slug)):
                    deal.status = 'lost'
                    deal.lost_reason = 'unsubscribed'
                    deal.save(update_fields=['status', 'lost_reason'])
                    DealActivity.objects.create(
                        deal=deal,
                        activity_type='status_change',
                        description=f"[Autopilot] Contact is unsubscribed - deal auto-closed"
                    )
                    processed += 1
                    logger.info(f"Deal {deal.id}: Contact unsubscribed, auto-closed")
                    continue

                # Check if this is a "Follow Up 3 (Final)" stage that has expired
                # If so, automatically move to "Not Interested" without AI analysis
                stage_name = deal.current_stage.name.lower() if deal.current_stage else ''
                if 'follow up 3' in stage_name or 'final' in stage_name:
                    not_interested_stage = PipelineStage.objects.filter(
                        pipeline=deal.pipeline,
                        name__icontains='not interested'
                    ).first()
                    if not_interested_stage:
                        deal.move_to_stage(not_interested_stage)
                        deal.status = 'lost'
                        deal.lost_reason = 'no_response'
                        deal.save(update_fields=['status', 'lost_reason'])
                        DealActivity.objects.create(
                            deal=deal,
                            activity_type='stage_change',
                            description=f"Auto-closed: No response after final follow-up"
                        )
                        processed += 1
                        logger.info(f"Deal {deal.id}: Auto-moved to Not Interested after final follow-up")
                        continue

                # === ENGAGEMENT-AWARE ROUTING ===
                profile = get_engagement_profile(deal)

                # Update engagement tier on deal
                if deal.engagement_tier != profile.tier:
                    deal.engagement_tier = profile.tier
                    deal.save(update_fields=['engagement_tier'])

                # GUARD: Ghost detection - stop wasting emails
                if profile.tier == 'ghost' and profile.total_sent >= 3:
                    not_interested_stage = PipelineStage.objects.filter(
                        pipeline=deal.pipeline,
                        name__icontains='not interested'
                    ).first()
                    if not_interested_stage:
                        deal.move_to_stage(not_interested_stage)
                        deal.status = 'lost'
                        deal.lost_reason = 'no_response'
                        deal.save(update_fields=['status', 'lost_reason'])
                        DealActivity.objects.create(
                            deal=deal,
                            activity_type='stage_change',
                            description=f"[Autopilot] Ghost detected: {profile.total_sent} emails sent, 0 opens. Auto-closed."
                        )
                        processed += 1
                        logger.info(f"Deal {deal.id}: Ghost detected, moved to Not Interested")
                        continue

                # GUARD: Burnout risk - extend wait time
                if profile.is_burnout_risk and profile.tier not in ('engaged', 'hot'):
                    deal.next_action_date = timezone.now() + timedelta(days=7)
                    deal.ai_notes = (deal.ai_notes or '') + f"\n[{timezone.now().strftime('%Y-%m-%d')}] [Autopilot] Burnout risk: {profile.consecutive_unopened} consecutive unopened. Extended wait 7 days."
                    deal.save(update_fields=['next_action_date', 'ai_notes'])
                    processed += 1
                    logger.info(f"Deal {deal.id}: Burnout risk detected, extending wait")
                    continue

                # Pass engagement profile to AI for smarter analysis
                result = ai_agent.analyze_deal(deal, engagement_profile=profile)
                action = result.get('action', 'flag_for_review')
                metadata = result.get('metadata', {})

                logger.info(f"Deal {deal.id}: AI recommends '{action}' (tier: {profile.tier})")

                if action == 'send_email':
                    email_type = metadata.get('email_type', 'followup')
                    # A/B testing: check if stage has variant B subject
                    ab_variant = ''
                    if deal.current_stage and deal.current_stage.subject_variant_b:
                        import random
                        ab_variant = 'A' if random.random() > 0.5 else 'B'
                    queue_deal_email.delay(str(deal.id), email_type, ab_variant=ab_variant)

                elif action == 'move_stage':
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
                    wait_days = int(metadata.get('wait_days', 3))
                    deal.next_action_date = timezone.now() + timedelta(days=wait_days)
                    deal.save(update_fields=['next_action_date'])

                elif action == 'change_approach':
                    # AI says try something different - extend wait and note it
                    wait_days = int(metadata.get('wait_days', 5))
                    deal.next_action_date = timezone.now() + timedelta(days=wait_days)
                    deal.ai_notes = (deal.ai_notes or '') + f"\n[{timezone.now().strftime('%Y-%m-%d')}] [Autopilot] Changing approach: {result.get('reasoning', '')}"
                    deal.save(update_fields=['next_action_date', 'ai_notes'])

                elif action == 'pause':
                    deal.status = 'paused'
                    deal.save(update_fields=['status'])
                    DealActivity.objects.create(
                        deal=deal,
                        activity_type='status_change',
                        description=f"AI paused deal: {result.get('reasoning', '')}",
                    )

                elif action == 'flag_for_review':
                    deal.ai_notes = (deal.ai_notes or '') + f"\n[{timezone.now().strftime('%Y-%m-%d')}] Flagged for review: {result.get('reasoning', '')}"
                    deal.save(update_fields=['ai_notes'])

                processed += 1

        except Exception as e:
            logger.error(f"Error processing deal {deal.id}: {e}")
            errors += 1

    logger.info(f"process_pending_deals completed: {processed} processed, {errors} errors")
    return {'processed': processed, 'errors': errors}


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def queue_deal_email(self, deal_id: str, email_type: str = 'followup', ab_variant: str = ''):
    """
    Queue an email to be sent for a deal.
    Called by process_pending_deals or manually.
    Only sends during office hours (Mon-Fri 9AM-5PM).

    For Desi Firms emails with pre-designed templates, uses the template directly.
    For other emails, uses AI to generate content.
    """
    if not is_office_hours():
        logger.info(f"queue_deal_email skipped for deal {deal_id}: outside office hours")
        return {'success': False, 'error': 'Outside office hours'}

    from crm.models import Deal, EmailLog, DealActivity
    from crm.services.email_service import get_email_service
    from crm.services.email_templates import (
        get_styled_email, get_pipeline_type_from_name,
        get_template_for_email, get_email_type_for_stage
    )
    from crm.views import get_unsubscribe_url
    from django.template.loader import render_to_string

    logger.info(f"Queuing email for deal {deal_id}, type: {email_type}")

    try:
        deal = Deal.objects.select_related('contact', 'pipeline', 'pipeline__brand', 'current_stage').get(id=deal_id)
    except Deal.DoesNotExist:
        logger.error(f"Deal {deal_id} not found")
        return {'success': False, 'error': 'Deal not found'}

    brand = deal.pipeline.brand if deal.pipeline else None
    email_service = get_email_service(brand)
    contact = deal.contact

    # SAFETY: Never email unsubscribed contacts
    brand_slug = brand.slug if brand else 'desifirms'
    if contact.is_unsubscribed or contact.is_unsubscribed_from_brand(brand_slug):
        logger.warning(f"Blocked email to unsubscribed contact {contact.email} (brand: {brand_slug})")
        return {'success': False, 'error': 'Contact is unsubscribed'}

    # SAFETY: Never email bounced or spam-reported contacts
    if contact.email_bounced:
        logger.warning(f"Blocked email to bounced contact {contact.email}")
        return {'success': False, 'error': 'Contact email has bounced'}
    if contact.spam_reported:
        logger.warning(f"Blocked email to spam-reported contact {contact.email}")
        return {'success': False, 'error': 'Contact reported spam'}

    # Determine brand and pipeline info
    pipeline_type = deal.pipeline.pipeline_type if deal.pipeline else 'sales'
    pipeline_name = deal.pipeline.name if deal.pipeline else ''

    # Get the appropriate email type based on current stage and pipeline type
    stage_name = deal.current_stage.name if deal.current_stage else 'follow_up'
    template_email_type = get_email_type_for_stage(stage_name, pipeline_type, pipeline_name) or 'agent_followup_1'

    # Get recipient info
    recipient_name = contact.name.split()[0] if contact.name else 'there'
    recipient_company = contact.company or 'your business'

    # Check if we have a pre-designed template
    template_path = get_template_for_email(brand_slug, pipeline_type, template_email_type)

    if template_path and 'generic' not in template_path:
        # USE PRE-DESIGNED TEMPLATE - no AI needed!
        logger.info(f"Using pre-designed template: {template_path}")

        context = {
            'recipient_name': recipient_name,
            'recipient_email': contact.email,
            'recipient_company': recipient_company,
            'unsubscribe_url': get_unsubscribe_url(contact.email, brand_slug),
            'current_year': timezone.now().year,
            'brand_slug': brand_slug,
        }

        html_body = render_to_string(template_path, context)

        # Get subject based on email type
        subject_map = {
            # Desi Firms Real Estate
            'agent_invitation': f"Join Desi Firms Real Estate as a Founding Member",
            'agent_followup_1': f"Just checking in - free listing opportunity",
            'agent_followup_2': f"Quick reminder - free real estate listing",
            'agent_followup_3': f"Closing the loop - Desi Firms",
            'realestate_followup_3': f"Closing the loop - Desi Firms",
            # Desi Firms Business
            'directory_invitation': f"List {recipient_company} on Desi Firms - FREE",
            'directory_followup_1': f"Quick follow-up - free business listing",
            'directory_followup_2': f"Quick reminder - free listing opportunity",
            'directory_followup_3': f"Closing the loop - Desi Firms",
            # Desi Firms Events
            'events_invitation': f"List your events on Desi Firms - FREE",
            'events_followup_1': f"Quick follow-up - free event listing",
            'events_followup_2': f"Quick reminder - free event listing",
            'events_followup_3': f"Closing the loop - Desi Firms",
            # Codeteki Sales
            'services_intro': f"AI-powered solutions for {recipient_company}",
            'sales_followup': f"Quick follow-up - {recipient_company}",
            'sales_followup_2': f"One more thought for {recipient_company}",
            # Codeteki Backlink
            'backlink_pitch': f"Content collaboration opportunity - {recipient_company}",
            'backlink_followup': f"Following up on content collaboration",
        }
        subject = subject_map.get(template_email_type, 'Following up')
        # A/B testing: use variant B subject if specified
        if ab_variant == 'B' and deal.current_stage and deal.current_stage.subject_variant_b:
            subject = deal.current_stage.subject_variant_b
        plain_body = f"(Pre-designed template: {template_email_type})"
        ai_generated = False

    else:
        # No pre-designed template - use AI generation
        logger.info(f"No pre-designed template, using AI generation")
        from crm.services.ai_agent import CRMAIAgent
        ai_agent = CRMAIAgent()

        email_result = ai_agent.compose_email(deal, context={'email_type': email_type})

        if not email_result.get('success'):
            logger.error(f"Failed to compose email for deal {deal_id}")
            return {'success': False, 'error': 'Email composition failed'}

        styled_email = get_styled_email(
            brand_slug=brand_slug,
            pipeline_type=pipeline_type,
            email_type=email_type,
            recipient_name=recipient_name,
            recipient_email=contact.email,
            recipient_company=contact.company,
            subject=email_result['subject'],
            body=email_result['body'],
        )

        html_body = styled_email['html']
        subject = email_result['subject']
        # A/B testing: use variant B subject if specified
        if ab_variant == 'B' and deal.current_stage and deal.current_stage.subject_variant_b:
            subject = deal.current_stage.subject_variant_b
        plain_body = email_result['body']
        ai_generated = True

    # Create email log entry
    email_log = EmailLog.objects.create(
        deal=deal,
        subject=subject,
        body=plain_body,
        to_email=deal.contact.email,
        ai_generated=ai_generated,
        ab_variant=ab_variant,
    )

    # Send styled HTML email
    send_result = email_service.send(
        to=deal.contact.email,
        subject=subject,  # Use the subject variable (works for both AI and template)
        body=html_body,  # Send HTML version
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
            description=f"Email sent: {subject}" + (f" [Variant {ab_variant}]" if ab_variant else ""),
            metadata={'email_log_id': str(email_log.id)}
        )

        # Auto-advance to next stage so the next email uses the next template
        # Only advance into follow-up or nudge stages, never into response/conversion stages
        from crm.models import PipelineStage
        if deal.current_stage and not deal.current_stage.is_terminal:
            next_stage = PipelineStage.objects.filter(
                pipeline=deal.pipeline,
                order__gt=deal.current_stage.order
            ).order_by('order').first()

            if next_stage and not next_stage.is_terminal:
                next_name = next_stage.name.lower()
                # Only auto-advance into follow-up or nudge stages
                if 'follow up' in next_name or 'nudge' in next_name:
                    deal.move_to_stage(next_stage)
                    DealActivity.objects.create(
                        deal=deal,
                        activity_type='stage_change',
                        description=f"Auto-advanced to {next_stage.name} after email sent"
                    )
                    logger.info(f"Deal {deal.id}: Auto-advanced to {next_stage.name}")

        logger.info(f"Email sent successfully to {deal.contact.email}")
        return {'success': True, 'email_log_id': str(email_log.id)}
    else:
        error_msg = send_result.get('error', '')
        logger.error(f"Failed to send email: {error_msg}")

        # HARD BOUNCE DETECTION: mark contact as bounced, close the deal
        if send_result.get('is_hard_bounce'):
            logger.warning(f"HARD BOUNCE detected for {contact.email}: {error_msg}")

            # Mark contact as bounced
            contact.email_bounced = True
            contact.bounced_at = timezone.now()
            contact.save(update_fields=['email_bounced', 'bounced_at'])

            # Close the deal
            deal.status = 'lost'
            deal.lost_reason = 'invalid_email'
            deal.save(update_fields=['status', 'lost_reason'])

            DealActivity.objects.create(
                deal=deal,
                activity_type='status_change',
                description=f"[Autopilot] Hard bounce: {error_msg[:200]}. Deal closed, no more emails will be sent."
            )

            # Also close any OTHER active deals for the same contact
            other_deals = Deal.objects.filter(
                contact=contact,
                status='active'
            ).exclude(id=deal.id)
            closed_count = 0
            for other_deal in other_deals:
                other_deal.status = 'lost'
                other_deal.lost_reason = 'invalid_email'
                other_deal.save(update_fields=['status', 'lost_reason'])
                DealActivity.objects.create(
                    deal=other_deal,
                    activity_type='status_change',
                    description=f"[Autopilot] Hard bounce on contact email - deal auto-closed"
                )
                closed_count += 1

            if closed_count:
                logger.info(f"Also closed {closed_count} other active deals for bounced contact {contact.email}")

            return {'success': False, 'error': error_msg, 'hard_bounce': True}

        return {'success': False, 'error': error_msg}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def send_scheduled_emails(self):
    """
    Send emails that are queued but not yet sent.
    Runs every 15 minutes.
    """
    from crm.models import EmailLog, DealActivity
    from crm.services.email_service import get_email_service
    from crm.services.email_templates import get_styled_email

    logger.info("Starting send_scheduled_emails task")

    sent = 0
    errors = 0

    # Find unsent pipeline emails (created in last 24 hours, with deals only)
    unsent_emails = EmailLog.objects.filter(
        sent_at__isnull=True,
        deal__isnull=False,
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).select_related('deal', 'deal__contact', 'deal__pipeline', 'deal__pipeline__brand')[:20]

    for email_log in unsent_emails:
        try:
            deal = email_log.deal
            if not deal:
                continue  # Guard: skip emails without deals
            contact = deal.contact if deal else None
            brand = deal.pipeline.brand if deal and deal.pipeline else None
            email_service = get_email_service(brand)

            # Wrap plain text body in styled HTML template
            brand_slug = brand.slug if brand else 'desifirms'
            pipeline_type = deal.pipeline.pipeline_type if deal and deal.pipeline else 'sales'

            styled_email = get_styled_email(
                brand_slug=brand_slug,
                pipeline_type=pipeline_type,
                email_type='followup',  # Default type for scheduled emails
                recipient_name=contact.name.split()[0] if contact and contact.name else 'there',
                recipient_email=email_log.to_email,
                recipient_company=contact.company if contact else '',
                subject=email_log.subject,
                body=email_log.body,
            )

            html_body = styled_email['html']

            result = email_service.send(
                to=email_log.to_email,
                subject=email_log.subject,
                body=html_body,  # Send styled HTML
                tracking_id=str(email_log.tracking_id)
            )

            if result['success']:
                email_log.sent_at = timezone.now()
                email_log.zoho_message_id = result.get('message_id', '')
                email_log.save()

                # Update deal
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


# =============================================================================
# SCHEDULED EMAIL DRAFT TASKS
# =============================================================================

@shared_task
def check_scheduled_drafts():
    """
    Check for scheduled EmailDrafts that are due to be sent.
    Runs every 5 minutes via Celery Beat.
    """
    from crm.models import EmailDraft

    logger.info("Checking for scheduled email drafts to send")

    # Find drafts scheduled for now or in the past
    due_drafts = EmailDraft.objects.filter(
        schedule_status='scheduled',
        scheduled_for__lte=timezone.now()
    )

    queued = 0
    for draft in due_drafts:
        # Queue the send task
        send_scheduled_draft.delay(str(draft.id))
        queued += 1
        logger.info(f"Queued scheduled draft {draft.id} for sending")

    if queued:
        logger.info(f"Queued {queued} scheduled draft(s) for sending")

    return {'queued': queued}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_scheduled_draft(self, draft_id: str):
    """
    Send a scheduled EmailDraft at its scheduled time.

    Args:
        draft_id: UUID of the EmailDraft to send
    """
    from crm.models import EmailDraft, Contact, Deal, PipelineStage
    from crm.services.email_templates import get_styled_email
    from crm.services.ai_agent import CRMAIAgent

    logger.info(f"Starting scheduled send for draft {draft_id}")

    try:
        draft = EmailDraft.objects.select_related('brand', 'pipeline').get(id=draft_id)
    except EmailDraft.DoesNotExist:
        logger.error(f"EmailDraft {draft_id} not found")
        return {'success': False, 'error': 'Draft not found'}

    # Check if still scheduled (not cancelled)
    if draft.schedule_status != 'scheduled':
        logger.info(f"Draft {draft_id} no longer scheduled (status: {draft.schedule_status})")
        return {'success': False, 'error': 'Draft no longer scheduled'}

    # Update status to sending
    draft.schedule_status = 'sending'
    draft.save(update_fields=['schedule_status'])

    try:
        # Validate basics
        if not draft.pipeline:
            raise ValueError("No pipeline selected")

        subject = draft.final_subject or draft.generated_subject
        body_text = draft.final_body or draft.generated_body

        if not subject or not body_text:
            raise ValueError("No email content")

        # Get all valid recipients
        all_recipients = draft.get_all_recipients()
        valid_recipients = []

        for recipient in all_recipients:
            recipient_email = Contact.normalize_email(recipient['email'])
            if not recipient_email:
                continue

            contact = recipient.get('contact')
            if not contact:
                contact = Contact.objects.filter(
                    email__iexact=recipient_email,
                    brand=draft.brand
                ).first()

            # Check unsubscribed
            brand_slug = draft.brand.slug if draft.brand else None
            if contact and (contact.is_unsubscribed or contact.is_unsubscribed_from_brand(brand_slug)):
                continue

            # Check in pipeline (unless override is set)
            if contact and not draft.send_to_pipeline_contacts:
                if Deal.objects.filter(contact=contact, status='active').exists():
                    continue

            valid_recipients.append({
                'email': recipient_email,
                'name': recipient.get('name', ''),
                'company': recipient.get('company', ''),
                'website': recipient.get('website', ''),
                'contact': contact,
            })

        if not valid_recipients:
            raise ValueError("No valid recipients")

        # Get pipeline stage
        invited_stage = PipelineStage.objects.filter(
            pipeline=draft.pipeline,
            name__icontains='invited'
        ).first() or PipelineStage.objects.filter(
            pipeline=draft.pipeline
        ).order_by('order').first()

        if not invited_stage:
            raise ValueError("Pipeline has no stages")

        # Initialize services (uses ZeptoMail if configured, else Zoho)
        from crm.services.email_service import get_email_service
        email_service = get_email_service(brand=draft.brand)
        if not email_service.enabled:
            raise ValueError(f"Email service not configured for {draft.brand.name}")

        ai_agent = CRMAIAgent()

        # Send to each recipient
        sent_count = 0
        failed_count = 0
        total_deals = 0

        for recipient in valid_recipients:
            try:
                result = _send_scheduled_to_recipient(
                    draft, recipient, subject, body_text,
                    invited_stage, email_service, ai_agent
                )
                if result['success']:
                    sent_count += 1
                    if result.get('deal_created'):
                        total_deals += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error sending to {recipient['email']}: {e}")
                failed_count += 1

        # Update draft tracking
        draft.sent_count = (draft.sent_count or 0) + sent_count
        draft.deals_created = (draft.deals_created or 0) + total_deals
        draft.is_sent = True
        draft.sent_at = timezone.now()
        draft.schedule_status = 'completed'
        draft.save(update_fields=[
            'sent_count', 'deals_created', 'is_sent', 'sent_at', 'schedule_status'
        ])

        logger.info(f"Scheduled send completed for draft {draft_id}: "
                   f"{sent_count} sent, {failed_count} failed, {total_deals} deals")

        return {
            'success': True,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'deals_created': total_deals
        }

    except Exception as e:
        logger.error(f"Scheduled send failed for draft {draft_id}: {e}")
        draft.schedule_status = 'failed'
        draft.schedule_error = str(e)
        draft.save(update_fields=['schedule_status', 'schedule_error'])
        return {'success': False, 'error': str(e)}


def _send_scheduled_to_recipient(draft, recipient, subject, body_text, invited_stage,
                                  email_service, ai_agent):
    """Helper function to send to a single recipient."""
    from crm.models import Contact, Deal
    from crm.services.email_templates import get_styled_email

    recipient_email = recipient['email']
    recipient_name = recipient.get('name', '')
    recipient_company = recipient.get('company', '')
    contact = recipient.get('contact')

    # Generate smart salutation
    salutation = ai_agent.get_smart_salutation(
        email=recipient_email,
        name=recipient_name,
        company=recipient_company
    )

    # Personalize body
    personalized_body = body_text.replace('{{SALUTATION}}', salutation)

    # Extract name for template
    extracted_name = salutation.replace('Hi ', '').replace(',', '').strip() \
        if salutation.startswith('Hi ') else 'there'
    if ' Team' in extracted_name:
        extracted_name = 'there'

    # Generate styled HTML
    styled_email = get_styled_email(
        brand_slug=draft.brand.slug if draft.brand else 'desifirms',
        pipeline_type=draft.pipeline.pipeline_type if draft.pipeline else 'business',
        email_type=draft.email_type or 'directory_invitation',
        recipient_name=extracted_name,
        recipient_email=recipient_email,
        recipient_company=recipient_company,
        subject=subject,
        body=personalized_body,
    )

    # Send email
    result = email_service.send(
        to=recipient_email,
        subject=subject,
        body=styled_email['html'],
        from_name=draft.brand.from_name
    )

    if not result.get('success'):
        return {'success': False, 'error': result.get('error')}

    # Create/update contact and deal
    deal_created = False
    if not contact:
        contact = Contact.objects.filter(
            email__iexact=recipient_email,
            brand=draft.brand
        ).first()

    if not contact:
        try:
            with transaction.atomic():
                contact = Contact.objects.create(
                    email=recipient_email,
                    brand=draft.brand,
                    name=recipient_name or extracted_name,
                    company=recipient_company,
                    website=recipient.get('website', ''),
                    status='contacted',
                    last_emailed_at=timezone.now(),
                    email_count=1,
                    source='email_composer_scheduled'
                )
        except Exception:
            contact = Contact.objects.filter(
                email__iexact=recipient_email,
                brand=draft.brand
            ).first()

    if contact:
        contact.last_emailed_at = timezone.now()
        contact.email_count = (contact.email_count or 0) + 1
        contact.status = 'contacted'
        contact.save(update_fields=['last_emailed_at', 'email_count', 'status'])

        # Create deal if doesn't exist
        existing_deal = Deal.objects.filter(
            contact=contact,
            pipeline=draft.pipeline,
            status='active'
        ).first()

        if existing_deal:
            existing_deal.emails_sent = (existing_deal.emails_sent or 0) + 1
            existing_deal.last_contact_date = timezone.now()
            existing_deal.next_action_date = timezone.now() + timedelta(
                days=existing_deal.current_stage.days_until_followup
                if existing_deal.current_stage else 3
            )
            existing_deal.save()
        else:
            Deal.objects.create(
                contact=contact,
                pipeline=draft.pipeline,
                current_stage=invited_stage,
                status='active',
                emails_sent=1,
                last_contact_date=timezone.now(),
                next_action_date=timezone.now() + timedelta(
                    days=invited_stage.days_until_followup or 3
                ),
                ai_notes=f"First contact via scheduled Email Composer\nSubject: {subject}"
            )
            deal_created = True

    return {'success': True, 'deal_created': deal_created}


@shared_task
def autopilot_engagement_scan():
    """
    Daily scan of all active deals to update engagement tiers and detect issues.
    Runs at 8 AM daily, before the main email processing.
    """
    from crm.models import Deal, DealActivity, PipelineStage
    from crm.services.engagement_engine import get_engagement_profile

    logger.info("Starting autopilot_engagement_scan")

    active_deals = Deal.objects.filter(
        status='active',
    ).select_related('contact', 'pipeline', 'current_stage')

    stats = {'total': 0, 'updated': 0, 'ghosts': 0, 'burnout': 0, 'hot': 0}

    for deal in active_deals:
        try:
            profile = get_engagement_profile(deal)
            stats['total'] += 1

            # Update tier if changed
            if deal.engagement_tier != profile.tier:
                deal.engagement_tier = profile.tier
                deal.save(update_fields=['engagement_tier'])
                stats['updated'] += 1

            # Count stats
            if profile.tier == 'ghost':
                stats['ghosts'] += 1
            if profile.tier == 'hot':
                stats['hot'] += 1
            if profile.is_burnout_risk:
                stats['burnout'] += 1

        except Exception as e:
            logger.error(f"Error scanning deal {deal.id}: {e}")

    logger.info(f"autopilot_engagement_scan completed: {stats}")
    return stats
