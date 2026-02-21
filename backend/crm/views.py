"""
CRM API Views

API endpoints for CRM management:
- Pipelines
- Deals
- Contacts
- Email Sequences
- AI Activity
- Email tracking
"""

import json
from datetime import timedelta
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Count, Q

from .models import (
    Pipeline, PipelineStage, Deal, Contact,
    EmailSequence, SequenceStep, EmailLog,
    AIDecisionLog, BacklinkOpportunity, DealActivity
)


def _serialize_contact(contact):
    """Serialize a Contact object to dict."""
    return {
        'id': str(contact.id),
        'email': contact.email,
        'name': contact.name,
        'company': contact.company,
        'website': contact.website,
        'domain_authority': contact.domain_authority,
        'contact_type': contact.contact_type,
        'source': contact.source,
        'tags': contact.tags,
        'ai_score': contact.ai_score,
        'notes': contact.notes,
        'created_at': contact.created_at.isoformat() if contact.created_at else None,
    }


def _serialize_pipeline(pipeline, include_stages=True):
    """Serialize a Pipeline object to dict."""
    data = {
        'id': pipeline.id,
        'name': pipeline.name,
        'pipeline_type': pipeline.pipeline_type,
        'description': pipeline.description,
        'is_active': pipeline.is_active,
        'deals_count': pipeline.deals.count(),
    }
    if include_stages:
        data['stages'] = [
            {
                'id': stage.id,
                'name': stage.name,
                'order': stage.order,
                'days_until_followup': stage.days_until_followup,
                'is_terminal': stage.is_terminal,
                'deals_count': stage.deals.filter(status='active').count(),
            }
            for stage in pipeline.stages.order_by('order')
        ]
    return data


def _serialize_deal(deal, include_activities=False):
    """Serialize a Deal object to dict."""
    data = {
        'id': str(deal.id),
        'contact': _serialize_contact(deal.contact) if deal.contact else None,
        'pipeline': {
            'id': deal.pipeline.id,
            'name': deal.pipeline.name,
            'pipeline_type': deal.pipeline.pipeline_type,
        } if deal.pipeline else None,
        'current_stage': {
            'id': deal.current_stage.id,
            'name': deal.current_stage.name,
            'order': deal.current_stage.order,
        } if deal.current_stage else None,
        'status': deal.status,
        'ai_notes': deal.ai_notes,
        'next_action_date': deal.next_action_date.isoformat() if deal.next_action_date else None,
        'value': str(deal.value) if deal.value else None,
        'emails_sent': deal.emails_sent,
        'last_contact_date': deal.last_contact_date.isoformat() if deal.last_contact_date else None,
        'stage_entered_at': deal.stage_entered_at.isoformat() if deal.stage_entered_at else None,
        'created_at': deal.created_at.isoformat() if deal.created_at else None,
    }
    if include_activities:
        data['activities'] = [
            {
                'id': str(a.id),
                'activity_type': a.activity_type,
                'description': a.description,
                'created_at': a.created_at.isoformat(),
            }
            for a in deal.activities.order_by('-created_at')[:20]
        ]
    return data


def _serialize_email_sequence(sequence, include_steps=True):
    """Serialize an EmailSequence object to dict."""
    data = {
        'id': sequence.id,
        'name': sequence.name,
        'pipeline': {
            'id': sequence.pipeline.id,
            'name': sequence.pipeline.name,
        } if sequence.pipeline else None,
        'description': sequence.description,
        'is_active': sequence.is_active,
    }
    if include_steps:
        data['steps'] = [
            {
                'id': step.id,
                'order': step.order,
                'delay_days': step.delay_days,
                'subject_template': step.subject_template,
                'body_template': step.body_template,
                'ai_personalize': step.ai_personalize,
            }
            for step in sequence.steps.order_by('order')
        ]
    return data


@method_decorator(csrf_exempt, name='dispatch')
class PipelineListView(View):
    """List and create pipelines."""

    def get(self, request):
        pipelines = Pipeline.objects.filter(is_active=True).prefetch_related('stages')
        return JsonResponse({
            'pipelines': [_serialize_pipeline(p) for p in pipelines]
        })

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        pipeline = Pipeline.objects.create(
            name=data.get('name', 'New Pipeline'),
            pipeline_type=data.get('pipeline_type', 'sales'),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )

        return JsonResponse({'pipeline': _serialize_pipeline(pipeline)}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class PipelineDetailView(View):
    """Get pipeline detail with stages."""

    def get(self, request, pipeline_id):
        try:
            pipeline = Pipeline.objects.prefetch_related('stages').get(id=pipeline_id)
        except Pipeline.DoesNotExist:
            return JsonResponse({'error': 'Pipeline not found'}, status=404)

        return JsonResponse({'pipeline': _serialize_pipeline(pipeline)})


@method_decorator(csrf_exempt, name='dispatch')
class DealListView(View):
    """List and create deals."""

    def get(self, request):
        deals = Deal.objects.select_related(
            'contact', 'pipeline', 'current_stage'
        ).order_by('-created_at')

        # Filter by query params
        pipeline_id = request.GET.get('pipeline')
        if pipeline_id:
            deals = deals.filter(pipeline_id=pipeline_id)

        stage_id = request.GET.get('stage')
        if stage_id:
            deals = deals.filter(current_stage_id=stage_id)

        status = request.GET.get('status')
        if status:
            deals = deals.filter(status=status)

        # Pagination
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        deals = deals[offset:offset + limit]

        return JsonResponse({
            'deals': [_serialize_deal(d) for d in deals]
        })

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Get or create contact
        contact_id = data.get('contact_id')
        if contact_id:
            try:
                contact = Contact.objects.get(id=contact_id)
            except Contact.DoesNotExist:
                return JsonResponse({'error': 'Contact not found'}, status=404)
        else:
            # Create new contact
            contact_data = data.get('contact', {})
            if not contact_data.get('email'):
                return JsonResponse({'error': 'Contact email required'}, status=400)

            contact, _ = Contact.objects.get_or_create(
                email=contact_data['email'],
                defaults={
                    'name': contact_data.get('name', ''),
                    'company': contact_data.get('company', ''),
                    'website': contact_data.get('website', ''),
                    'contact_type': contact_data.get('contact_type', 'lead'),
                    'source': contact_data.get('source', 'api'),
                }
            )

        # Get pipeline
        pipeline_id = data.get('pipeline_id')
        if not pipeline_id:
            # Default to first active sales pipeline
            pipeline = Pipeline.objects.filter(is_active=True, pipeline_type='sales').first()
            if not pipeline:
                return JsonResponse({'error': 'No active pipeline found'}, status=400)
        else:
            try:
                pipeline = Pipeline.objects.get(id=pipeline_id)
            except Pipeline.DoesNotExist:
                return JsonResponse({'error': 'Pipeline not found'}, status=404)

        # Get first stage
        first_stage = pipeline.stages.order_by('order').first()

        deal = Deal.objects.create(
            contact=contact,
            pipeline=pipeline,
            current_stage=first_stage,
            status='active',
            next_action_date=timezone.now(),
            value=data.get('value'),
        )

        return JsonResponse({'deal': _serialize_deal(deal)}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class DealDetailView(View):
    """Get, update, or delete a deal."""

    def get(self, request, deal_id):
        try:
            deal = Deal.objects.select_related(
                'contact', 'pipeline', 'current_stage'
            ).prefetch_related('activities').get(id=deal_id)
        except Deal.DoesNotExist:
            return JsonResponse({'error': 'Deal not found'}, status=404)

        return JsonResponse({'deal': _serialize_deal(deal, include_activities=True)})

    def patch(self, request, deal_id):
        try:
            deal = Deal.objects.get(id=deal_id)
        except Deal.DoesNotExist:
            return JsonResponse({'error': 'Deal not found'}, status=404)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Update allowed fields
        if 'status' in data:
            deal.status = data['status']
        if 'ai_notes' in data:
            deal.ai_notes = data['ai_notes']
        if 'value' in data:
            deal.value = data['value']
        if 'next_action_date' in data:
            deal.next_action_date = data['next_action_date']

        deal.save()

        return JsonResponse({'deal': _serialize_deal(deal)})


@method_decorator(csrf_exempt, name='dispatch')
class DealMoveStageView(View):
    """Move a deal to a specific stage."""

    def post(self, request, deal_id):
        try:
            deal = Deal.objects.select_related('pipeline').get(id=deal_id)
        except Deal.DoesNotExist:
            return JsonResponse({'error': 'Deal not found'}, status=404)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        stage_id = data.get('stage_id')
        if not stage_id:
            return JsonResponse({'error': 'stage_id required'}, status=400)

        try:
            stage = PipelineStage.objects.get(id=stage_id, pipeline=deal.pipeline)
        except PipelineStage.DoesNotExist:
            return JsonResponse({'error': 'Stage not found in pipeline'}, status=404)

        old_stage = deal.current_stage
        deal.move_to_stage(stage)

        # Log activity
        DealActivity.objects.create(
            deal=deal,
            activity_type='stage_change',
            description=f"Moved from {old_stage.name if old_stage else 'None'} to {stage.name}",
        )

        return JsonResponse({'deal': _serialize_deal(deal)})


@method_decorator(csrf_exempt, name='dispatch')
class ContactListView(View):
    """List and create contacts."""

    def get(self, request):
        contacts = Contact.objects.order_by('-created_at')

        # Filter by query params
        contact_type = request.GET.get('type')
        if contact_type:
            contacts = contacts.filter(contact_type=contact_type)

        search = request.GET.get('search')
        if search:
            contacts = contacts.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(company__icontains=search)
            )

        # Pagination
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        contacts = contacts[offset:offset + limit]

        return JsonResponse({
            'contacts': [_serialize_contact(c) for c in contacts]
        })

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not data.get('email'):
            return JsonResponse({'error': 'Email required'}, status=400)

        contact, created = Contact.objects.get_or_create(
            email=data['email'],
            defaults={
                'name': data.get('name', ''),
                'company': data.get('company', ''),
                'website': data.get('website', ''),
                'domain_authority': data.get('domain_authority'),
                'contact_type': data.get('contact_type', 'lead'),
                'source': data.get('source', 'api'),
                'tags': data.get('tags', []),
                'notes': data.get('notes', ''),
            }
        )

        status_code = 201 if created else 200
        return JsonResponse({'contact': _serialize_contact(contact)}, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class ContactDetailView(View):
    """Get or update a contact."""

    def get(self, request, contact_id):
        try:
            contact = Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return JsonResponse({'error': 'Contact not found'}, status=404)

        return JsonResponse({'contact': _serialize_contact(contact)})

    def patch(self, request, contact_id):
        try:
            contact = Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return JsonResponse({'error': 'Contact not found'}, status=404)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Update allowed fields
        for field in ['name', 'company', 'website', 'domain_authority', 'contact_type', 'source', 'tags', 'notes']:
            if field in data:
                setattr(contact, field, data[field])

        contact.save()

        return JsonResponse({'contact': _serialize_contact(contact)})


@method_decorator(csrf_exempt, name='dispatch')
class EmailSequenceListView(View):
    """List email sequences."""

    def get(self, request):
        sequences = EmailSequence.objects.filter(
            is_active=True
        ).select_related('pipeline').prefetch_related('steps')

        pipeline_id = request.GET.get('pipeline')
        if pipeline_id:
            sequences = sequences.filter(pipeline_id=pipeline_id)

        return JsonResponse({
            'sequences': [_serialize_email_sequence(s) for s in sequences]
        })


@method_decorator(csrf_exempt, name='dispatch')
class AIActivityView(View):
    """List AI decisions/activity."""

    def get(self, request):
        decisions = AIDecisionLog.objects.select_related(
            'deal', 'contact'
        ).order_by('-created_at')

        deal_id = request.GET.get('deal_id')
        if deal_id:
            decisions = decisions.filter(deal_id=deal_id)

        decision_type = request.GET.get('type')
        if decision_type:
            decisions = decisions.filter(decision_type=decision_type)

        # Pagination
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        decisions = decisions[offset:offset + limit]

        return JsonResponse({
            'decisions': [
                {
                    'id': str(d.id),
                    'deal_id': str(d.deal_id) if d.deal_id else None,
                    'contact_id': str(d.contact_id) if d.contact_id else None,
                    'decision_type': d.decision_type,
                    'reasoning': d.reasoning,
                    'action_taken': d.action_taken,
                    'tokens_used': d.tokens_used,
                    'model_used': d.model_used,
                    'created_at': d.created_at.isoformat(),
                }
                for d in decisions
            ]
        })


@method_decorator(csrf_exempt, name='dispatch')
class CRMStatsView(View):
    """Get CRM statistics."""

    def get(self, request):
        # Pipeline stats
        pipelines = Pipeline.objects.filter(is_active=True).annotate(
            total_deals=Count('deals'),
            active_deals=Count('deals', filter=Q(deals__status='active')),
            won_deals=Count('deals', filter=Q(deals__status='won')),
            lost_deals=Count('deals', filter=Q(deals__status='lost')),
        )

        pipeline_stats = []
        for p in pipelines:
            stage_stats = []
            for stage in p.stages.order_by('order'):
                stage_stats.append({
                    'id': stage.id,
                    'name': stage.name,
                    'deals_count': Deal.objects.filter(
                        pipeline=p,
                        current_stage=stage,
                        status='active'
                    ).count()
                })

            pipeline_stats.append({
                'id': p.id,
                'name': p.name,
                'pipeline_type': p.pipeline_type,
                'total_deals': p.total_deals,
                'active_deals': p.active_deals,
                'won_deals': p.won_deals,
                'lost_deals': p.lost_deals,
                'stages': stage_stats,
            })

        # Contact stats
        contact_stats = {
            'total': Contact.objects.count(),
            'leads': Contact.objects.filter(contact_type='lead').count(),
            'backlink_targets': Contact.objects.filter(contact_type='backlink_target').count(),
            'partners': Contact.objects.filter(contact_type='partner').count(),
        }

        # Email stats
        email_stats = {
            'total_sent': EmailLog.objects.filter(sent_at__isnull=False).count(),
            'opened': EmailLog.objects.filter(opened=True).count(),
            'replied': EmailLog.objects.filter(replied=True).count(),
        }

        # AI stats
        ai_stats = {
            'total_decisions': AIDecisionLog.objects.count(),
            'today': AIDecisionLog.objects.filter(
                created_at__date=timezone.now().date()
            ).count(),
        }

        return JsonResponse({
            'pipelines': pipeline_stats,
            'contacts': contact_stats,
            'emails': email_stats,
            'ai': ai_stats,
        })


class EmailTrackingPixelView(View):
    """Track email opens via tracking pixel."""

    def get(self, request, tracking_id):
        try:
            email_log = EmailLog.objects.get(tracking_id=tracking_id)
            if not email_log.opened:
                email_log.opened = True
                email_log.opened_at = timezone.now()
                email_log.save()

                # Log activity for pipeline emails
                if email_log.deal:
                    DealActivity.objects.create(
                        deal=email_log.deal,
                        activity_type='email_opened',
                        description=f"Email opened: {email_log.subject}",
                    )

        except EmailLog.DoesNotExist:
            pass

        # Return 1x1 transparent GIF
        gif_data = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        return HttpResponse(gif_data, content_type='image/gif')


@method_decorator(csrf_exempt, name='dispatch')
class EmailReplyWebhookView(View):
    """
    Webhook endpoint for email reply notifications.
    Called by Zoho Mail (or other email service) when someone replies.

    Updates pipeline stage to "Responded" and logs activity.

    Expected payload:
    {
        "from_email": "customer@example.com",
        "to_email": "sales@codeteki.com",
        "subject": "Re: Your proposal",
        "body": "Thanks for reaching out...",
        "received_at": "2024-01-15T10:30:00Z"
    }
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        from_email = data.get('from_email', '').lower().strip()
        subject = data.get('subject', '')
        body = data.get('body', '')

        if not from_email:
            return JsonResponse({'error': 'from_email required'}, status=400)

        # Find contact by email
        contact = Contact.objects.filter(email__iexact=from_email).first()
        if not contact:
            return JsonResponse({
                'status': 'ignored',
                'message': f'No contact found for {from_email}'
            })

        # Find active deal for this contact
        deal = Deal.objects.filter(
            contact=contact,
            status='active'
        ).select_related('pipeline', 'current_stage').first()

        if not deal:
            # Update contact status anyway
            contact.status = 'replied'
            contact.save(update_fields=['status'])
            return JsonResponse({
                'status': 'contact_updated',
                'message': f'No active deal, but updated contact status for {from_email}'
            })

        # Find "Responded" or "Replied" stage in pipeline
        responded_stage = PipelineStage.objects.filter(
            pipeline=deal.pipeline,
            name__icontains='respond'
        ).first()

        if not responded_stage:
            responded_stage = PipelineStage.objects.filter(
                pipeline=deal.pipeline,
                name__icontains='repl'
            ).first()

        # Move deal to responded stage
        old_stage_name = deal.current_stage.name if deal.current_stage else 'Unknown'

        if responded_stage and deal.current_stage != responded_stage:
            deal.current_stage = responded_stage
            deal.stage_entered_at = timezone.now()

        # Update deal - pause autopilot so human can respond
        deal.autopilot_paused = True
        deal.last_contact_date = timezone.now()
        deal.ai_notes = f"{deal.ai_notes or ''}\n\n[REPLY RECEIVED {timezone.now().strftime('%Y-%m-%d %H:%M')}]\nSubject: {subject}\n{body[:500]}..."
        deal.save()

        # Log activity
        DealActivity.objects.create(
            deal=deal,
            activity_type='email_reply',
            description=f"Reply received from {from_email}. Subject: {subject[:100]}"
        )

        # Update contact status
        contact.status = 'replied'
        contact.save(update_fields=['status'])

        # Log email
        EmailLog.objects.create(
            deal=deal,
            subject=f"Reply: {subject}",
            body=body[:2000] if body else '',
            to_email=deal.contact.email,
            from_email=from_email,
            replied=True,
            replied_at=timezone.now(),
        )

        return JsonResponse({
            'status': 'success',
            'contact': from_email,
            'deal_id': str(deal.id),
            'stage_moved': responded_stage.name if responded_stage else None,
            'message': f'Deal updated for {from_email}'
        })


@method_decorator(csrf_exempt, name='dispatch')
class UnsubscribeWebhookView(View):
    """
    Webhook endpoint for unsubscribe requests.
    Called when someone clicks unsubscribe link or reports spam.

    Expected payload:
    {
        "email": "customer@example.com",
        "reason": "unsubscribe" | "spam_report" | "bounce",
        "source": "zoho" | "manual"
    }
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        email = data.get('email', '').lower().strip()
        reason = data.get('reason', 'unsubscribe')

        if not email:
            return JsonResponse({'error': 'email required'}, status=400)

        # Find contact
        contact = Contact.objects.filter(email__iexact=email).first()
        if not contact:
            return JsonResponse({
                'status': 'ignored',
                'message': f'No contact found for {email}'
            })

        # Mark as unsubscribed
        contact.is_unsubscribed = True
        contact.unsubscribed_at = timezone.now()
        contact.unsubscribe_reason = reason
        contact.status = 'unsubscribed'
        contact.save()

        # Pause all active deals for this contact
        deals_paused = Deal.objects.filter(
            contact=contact,
            status='active'
        ).update(status='paused')

        return JsonResponse({
            'status': 'success',
            'email': email,
            'deals_paused': deals_paused,
            'message': f'Unsubscribed {email}'
        })


@method_decorator(csrf_exempt, name='dispatch')
class ZeptoMailBounceWebhookView(View):
    """
    Webhook endpoint for ZeptoMail bounce and spam notifications.
    Handles hard bounces, soft bounces, and feedback loop (spam reports).

    Events:
    - hardbounce: Invalid email → mark bounced, close all deals
    - softbounce: Temporary failure → track count, auto-escalate to hard bounce after 3
    - feedback_loop: Spam report → treat as unsubscribe, close all deals

    Configure in ZeptoMail: Settings > Webhooks > Add webhook URL:
    https://yourdomain.com/api/crm/webhooks/bounce/
    Enable: Hard bounced, Soft bounced, Feedback loop

    Security: Set ZEPTOMAIL_WEBHOOK_KEY in .env and add the same key
    in ZeptoMail's "Authorization headers" field.
    """

    SOFT_BOUNCE_THRESHOLD = 3  # Convert to hard bounce after this many

    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)

        # Verify webhook auth key if configured
        webhook_key = getattr(settings, 'ZEPTOMAIL_WEBHOOK_KEY', '')
        if webhook_key:
            auth_header = request.headers.get('Authorization', '')
            if auth_header != webhook_key:
                logger.warning(f"Bounce webhook: invalid auth key")
                return JsonResponse({'error': 'Unauthorized'}, status=401)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        event_names = data.get('event_name', [])
        event_messages = data.get('event_message', [])

        if not event_messages:
            return JsonResponse({'error': 'No event_message'}, status=400)

        # Determine event type
        event_type = 'unknown'
        if 'hardbounce' in event_names:
            event_type = 'hardbounce'
        elif 'softbounce' in event_names:
            event_type = 'softbounce'
        elif 'feedback_loop' in event_names or 'spam' in event_names:
            event_type = 'spam'

        results = []
        for message in event_messages:
            # Extract affected recipient emails
            affected_emails = set()

            # From event_data details (bounce events)
            for event_data in message.get('event_data', []):
                for detail in event_data.get('details', []):
                    recipient = detail.get('bounced_recipient', '').lower().strip()
                    if recipient:
                        affected_emails.add(recipient)
                    # Feedback loop may use different field
                    recipient = detail.get('recipient', '').lower().strip()
                    if recipient:
                        affected_emails.add(recipient)

            # Fallback: from email_info.to
            if not affected_emails:
                email_info = message.get('email_info', {})
                for to_entry in email_info.get('to', []):
                    addr = to_entry.get('email_address', {}).get('address', '').lower().strip()
                    if addr:
                        affected_emails.add(addr)

            for email in affected_emails:
                if event_type == 'hardbounce':
                    result = self._handle_hard_bounce(email, logger)
                elif event_type == 'softbounce':
                    result = self._handle_soft_bounce(email, logger)
                elif event_type == 'spam':
                    result = self._handle_spam_report(email, logger)
                else:
                    result = {'email': email, 'action': 'ignored', 'reason': f'unknown event: {event_names}'}
                results.append(result)

        return JsonResponse({
            'status': 'processed',
            'event': event_names,
            'results': results,
        })

    def _mark_bounced_and_close_deals(self, contact, reason_desc, logger):
        """Shared logic: mark contact bounced + close all active deals."""
        contact.email_bounced = True
        contact.bounced_at = timezone.now()
        contact.save(update_fields=['email_bounced', 'bounced_at'])

        active_deals = Deal.objects.filter(contact=contact, status='active')
        deals_closed = 0
        for deal in active_deals:
            deal.status = 'lost'
            deal.lost_reason = 'invalid_email'
            deal.save(update_fields=['status', 'lost_reason'])
            DealActivity.objects.create(
                deal=deal,
                activity_type='status_change',
                description=f"[Webhook] {reason_desc} - deal auto-closed"
            )
            deals_closed += 1

        return deals_closed

    def _handle_hard_bounce(self, email, logger):
        """Mark contact as bounced and close all active deals."""
        contact = Contact.objects.filter(email__iexact=email).first()
        if not contact:
            logger.info(f"Bounce webhook: no contact for {email}")
            return {'email': email, 'action': 'ignored', 'reason': 'no_contact'}

        if contact.email_bounced:
            return {'email': email, 'action': 'already_bounced'}

        deals_closed = self._mark_bounced_and_close_deals(
            contact, "Hard bounce from ZeptoMail", logger
        )

        logger.warning(f"Hard bounce webhook: {email} - marked bounced, {deals_closed} deals closed")
        return {'email': email, 'action': 'bounced', 'deals_closed': deals_closed}

    def _handle_soft_bounce(self, email, logger):
        """Track soft bounce count. Auto-escalate to hard bounce after threshold."""
        contact = Contact.objects.filter(email__iexact=email).first()
        if not contact:
            logger.info(f"Soft bounce webhook: no contact for {email}")
            return {'email': email, 'action': 'ignored', 'reason': 'no_contact'}

        if contact.email_bounced:
            return {'email': email, 'action': 'already_bounced'}

        contact.soft_bounce_count = (contact.soft_bounce_count or 0) + 1
        contact.save(update_fields=['soft_bounce_count'])

        # Auto-escalate to hard bounce after threshold
        if contact.soft_bounce_count >= self.SOFT_BOUNCE_THRESHOLD:
            deals_closed = self._mark_bounced_and_close_deals(
                contact, f"Soft bounce escalated to hard bounce ({contact.soft_bounce_count} soft bounces)", logger
            )
            logger.warning(f"Soft bounce escalated: {email} - {contact.soft_bounce_count} soft bounces → marked bounced, {deals_closed} deals closed")
            return {'email': email, 'action': 'escalated_to_hard_bounce', 'soft_bounce_count': contact.soft_bounce_count, 'deals_closed': deals_closed}

        logger.info(f"Soft bounce webhook: {email} - count now {contact.soft_bounce_count}/{self.SOFT_BOUNCE_THRESHOLD}")
        return {'email': email, 'action': 'soft_bounce_tracked', 'soft_bounce_count': contact.soft_bounce_count}

    def _handle_spam_report(self, email, logger):
        """Recipient reported spam. Treat as unsubscribe and close all deals."""
        contact = Contact.objects.filter(email__iexact=email).first()
        if not contact:
            logger.info(f"Spam report webhook: no contact for {email}")
            return {'email': email, 'action': 'ignored', 'reason': 'no_contact'}

        if contact.spam_reported:
            return {'email': email, 'action': 'already_reported'}

        # Mark as spam reported + unsubscribed
        contact.spam_reported = True
        contact.spam_reported_at = timezone.now()
        contact.is_unsubscribed = True
        contact.unsubscribed_at = timezone.now()
        contact.unsubscribe_reason = 'Spam report (ZeptoMail feedback loop)'
        contact.status = 'unsubscribed'
        contact.save(update_fields=[
            'spam_reported', 'spam_reported_at',
            'is_unsubscribed', 'unsubscribed_at', 'unsubscribe_reason', 'status'
        ])

        # Close all active deals
        active_deals = Deal.objects.filter(contact=contact, status='active')
        deals_closed = 0
        for deal in active_deals:
            deal.status = 'lost'
            deal.lost_reason = 'unsubscribed'
            deal.save(update_fields=['status', 'lost_reason'])
            DealActivity.objects.create(
                deal=deal,
                activity_type='status_change',
                description=f"[Webhook] Spam report - contact unsubscribed, deal auto-closed"
            )
            deals_closed += 1

        logger.warning(f"Spam report webhook: {email} - unsubscribed, {deals_closed} deals closed")
        return {'email': email, 'action': 'spam_unsubscribed', 'deals_closed': deals_closed}


@method_decorator(csrf_exempt, name='dispatch')
class DesiFirmsWebhookView(View):
    """
    Webhook receiver for Desi Firms application events.
    Tracks the full user journey from registration through listing completion.

    Registration events (create contact + deal):
      user_registered — New user signed up

    Progress events (advance deal stage):
      business_created — User submitted a business listing (pending approval)
      business_approved — Admin approved the business listing (won)
      event_created — User submitted an event listing (pending approval)
      event_approved — Admin approved the event listing (won)
      agency_created — User created a real estate agency profile
      agent_created — Agent profile created (independent or via invitation)
      agent_invitation_sent — Agency invited a team member
      agent_invitation_accepted — Agent accepted the invitation
      agent_verified — Admin verified agent credentials
      property_submitted — Agent submitted a property listing
      property_approved — Admin approved the property listing (won)

    Pipeline mapping (matched by pipeline_type):
      pipeline_hint in payload → pipeline_type in CRM
      'business' → 'business'
      'events'   → 'events'
      'realestate' → 'realestate'
      fallback   → 'registered_users'

    Auth: Authorization header must match DESIFIRMS_WEBHOOK_KEY setting.
    """

    # Events that mark the deal as won
    WON_EVENTS = {'business_approved', 'event_approved', 'property_approved'}

    # Map: event_type → (target_pipeline_name, stage_name_to_advance_to)
    # Pipeline name uses icontains match. Stage name is exact.
    # For outreach pipelines (cold leads we emailed who then converted):
    #   user_registered → "Signed Up" / "Registered"
    #   business_created → "Listed"  (they listed = won)
    # For registered_users pipelines (users who came organically):
    #   business_created → "Listed"
    #   event_created → "Event Posted"
    EVENT_STAGE_MAP = {
        # Business journey
        'business_created': {
            'outreach_pipeline': 'Business Listings',
            'nudge_pipeline': 'Registered Users - Business',
            'outreach_stage': 'Signed Up',
            'nudge_stage': 'Listed',
        },
        'business_approved': {
            'outreach_pipeline': 'Business Listings',
            'nudge_pipeline': 'Registered Users - Business',
            'outreach_stage': 'Listed',
            'nudge_stage': 'Listed',
        },
        # Events journey
        'event_created': {
            'outreach_pipeline': 'Desi Firms Events',
            'nudge_pipeline': 'Registered Users - Events',
            'outreach_stage': 'Signed Up',
            'nudge_stage': 'Event Posted',
        },
        'event_approved': {
            'outreach_pipeline': 'Desi Firms Events',
            'nudge_pipeline': 'Registered Users - Events',
            'outreach_stage': 'Event Listed',
            'nudge_stage': 'Event Posted',
        },
        # Real estate journey — Agents & Agencies pipeline
        'agency_created': {'stage': 'Agency Created'},
        'agent_created': {'stage': 'Profile Complete'},
        'agent_invitation_sent': {'stage': 'Team Invited'},
        'agent_invitation_accepted': {'stage': 'Profile Complete'},
        'agent_verified': {'stage': 'Verified'},
        'property_submitted': {'stage': 'First Listing'},
        'property_approved': {'stage': 'Active Lister'},
    }

    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)

        # Verify webhook auth key
        webhook_key = getattr(settings, 'DESIFIRMS_WEBHOOK_KEY', '')
        if webhook_key:
            auth_header = request.headers.get('Authorization', '')
            if auth_header != webhook_key:
                logger.warning("Desi Firms webhook: invalid auth key")
                return JsonResponse({'error': 'Unauthorized'}, status=401)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        event_type = data.get('event_type', '')
        email = data.get('email', '').lower().strip()

        if not email or not event_type:
            return JsonResponse({'error': 'email and event_type required'}, status=400)

        from crm.models import Brand

        brand = Brand.objects.filter(slug='desifirms').first()
        if not brand:
            logger.error("Desi Firms webhook: no brand with slug 'desifirms'")
            return JsonResponse({'error': 'Desi Firms brand not configured'}, status=500)

        if event_type == 'user_registered':
            return self._handle_registration(data, email, brand, logger)
        elif event_type in self.EVENT_STAGE_MAP:
            mark_won = event_type in self.WON_EVENTS
            return self._handle_progress(data, email, event_type, brand, logger, mark_won)
        else:
            return JsonResponse({'status': 'ignored', 'message': f'Unknown event: {event_type}'})

    def _get_or_create_contact(self, email, brand, data):
        """Get or create a contact, updating name if provided."""
        name = data.get('name', '')
        contact, created = Contact.objects.get_or_create(
            email=email,
            brand=brand,
            defaults={
                'name': name,
                'source': 'desifirms_webhook',
                'status': 'new',
                'contact_type': 'lead',
            }
        )
        if not created and name and not contact.name:
            contact.name = name
            contact.save(update_fields=['name'])
        return contact, created

    def _find_nudge_pipeline(self, brand, pipeline_hint):
        """Find the right Registered Users pipeline by name hint."""
        from crm.models import Pipeline

        name_map = {
            'business': 'Registered Users - Business',
            'events': 'Registered Users - Events',
            'realestate': 'Registered Users - Real Estate',
        }
        name = name_map.get(pipeline_hint, '')
        if name:
            p = Pipeline.objects.filter(brand=brand, name=name, is_active=True).first()
            if p:
                return p

        # Fallback: Agents & Agencies for realestate, or first registered_users
        if pipeline_hint == 'realestate':
            return Pipeline.objects.filter(
                brand=brand, name__icontains='Agents', is_active=True,
            ).first()

        return Pipeline.objects.filter(
            brand=brand, pipeline_type='registered_users', is_active=True,
        ).first()

    def _handle_registration(self, data, email, brand, logger):
        """User registered on Desi Firms. Create contact + deal in nudge pipeline."""
        from crm.models import Pipeline, PipelineStage

        contact, _ = self._get_or_create_contact(email, brand, data)
        phone = data.get('phone', '')
        pipeline_hint = data.get('pipeline_hint', '')

        # Check for existing active deal in ANY Desi Firms pipeline
        existing_deal = Deal.objects.filter(
            contact=contact, pipeline__brand=brand, status='active',
        ).select_related('pipeline', 'current_stage').first()

        if existing_deal:
            # Already tracked (likely from outreach). Advance to "Signed Up" or "Registered"
            registered_stage = PipelineStage.objects.filter(
                pipeline=existing_deal.pipeline,
                name__in=['Signed Up', 'Registered'],
            ).order_by('-order').first()  # prefer Signed Up over Registered

            if registered_stage and existing_deal.current_stage != registered_stage:
                old_stage = existing_deal.current_stage.name if existing_deal.current_stage else 'None'
                existing_deal.move_to_stage(registered_stage)
                existing_deal.autopilot_paused = True
                existing_deal.save(update_fields=['autopilot_paused'])
                DealActivity.objects.create(
                    deal=existing_deal,
                    activity_type='stage_change',
                    description=f"[Webhook] User registered on Desi Firms: {old_stage} → {registered_stage.name}",
                )

            return JsonResponse({
                'status': 'advanced',
                'deal_id': str(existing_deal.id),
                'pipeline': existing_deal.pipeline.name,
            })

        # No existing deal — create in appropriate Registered Users pipeline
        pipeline = self._find_nudge_pipeline(brand, pipeline_hint)
        if not pipeline:
            logger.warning(f"Desi Firms webhook: no nudge pipeline for hint={pipeline_hint}")
            return JsonResponse({
                'status': 'contact_created',
                'contact_id': str(contact.id),
            })

        first_stage = PipelineStage.objects.filter(
            pipeline=pipeline
        ).order_by('order').first()

        notes = f"Registered on Desi Firms via webhook."
        if phone:
            notes += f"\nPhone: {phone}"

        deal = Deal.objects.create(
            contact=contact,
            pipeline=pipeline,
            current_stage=first_stage,
            status='active',
            next_action_date=timezone.now(),
            ai_notes=notes,
        )

        DealActivity.objects.create(
            deal=deal,
            activity_type='status_change',
            description=f"[Webhook] User registered on Desi Firms: {email} → {pipeline.name}",
        )

        logger.info(f"Desi Firms webhook: created deal {deal.id} for {email} in {pipeline.name}")
        return JsonResponse({
            'status': 'success',
            'contact_id': str(contact.id),
            'deal_id': str(deal.id),
        }, status=201)

    def _handle_progress(self, data, email, event_type, brand, logger, mark_won=False):
        """User took an action on Desi Firms. Advance their deal to the right stage."""
        from crm.models import Pipeline, PipelineStage

        contact, _ = self._get_or_create_contact(email, brand, data)
        detail = (
            data.get('detail', '') or data.get('business_name', '') or
            data.get('event_name', '') or data.get('property_address', '') or
            data.get('agent_name', '') or ''
        )

        mapping = self.EVENT_STAGE_MAP[event_type]

        # Find the contact's active deal in any Desi Firms pipeline
        deal = Deal.objects.filter(
            contact=contact, pipeline__brand=brand, status='active',
        ).select_related('pipeline', 'current_stage').first()

        if not deal:
            # No deal yet — auto-create in the right pipeline
            if 'nudge_pipeline' in mapping:
                # Business/Events: use nudge pipeline
                pipeline = Pipeline.objects.filter(
                    brand=brand, name=mapping['nudge_pipeline'], is_active=True,
                ).first()
            else:
                # Real estate events: use Agents & Agencies pipeline
                pipeline = Pipeline.objects.filter(
                    brand=brand, name__icontains='Agents', is_active=True,
                ).first()

            if not pipeline:
                logger.info(f"Desi Firms webhook: no pipeline for {event_type}")
                return JsonResponse({'status': 'ignored', 'message': 'No matching pipeline'})

            first_stage = PipelineStage.objects.filter(
                pipeline=pipeline
            ).order_by('order').first()

            deal = Deal.objects.create(
                contact=contact,
                pipeline=pipeline,
                current_stage=first_stage,
                status='active',
                next_action_date=timezone.now(),
                ai_notes=f"Auto-created from webhook: {event_type}\n{detail}",
            )
            DealActivity.objects.create(
                deal=deal,
                activity_type='status_change',
                description=f"[Webhook] Auto-created deal for {email} ({event_type})",
            )
            logger.info(f"Desi Firms webhook: auto-created deal {deal.id} for {email}")

        # Determine target stage name based on which pipeline the deal is in
        if 'outreach_pipeline' in mapping and mapping['outreach_pipeline'] in deal.pipeline.name:
            target_stage_name = mapping['outreach_stage']
        elif 'nudge_pipeline' in mapping and mapping['nudge_pipeline'] in deal.pipeline.name:
            target_stage_name = mapping['nudge_stage']
        elif 'stage' in mapping:
            target_stage_name = mapping['stage']
        else:
            target_stage_name = None

        # For real estate events: if deal is in a non-RE pipeline, move to Agents & Agencies
        if 'stage' in mapping and 'Agents' not in deal.pipeline.name and 'Real Estate' not in deal.pipeline.name:
            re_pipeline = Pipeline.objects.filter(
                brand=brand, name__icontains='Agents', is_active=True,
            ).first()
            if re_pipeline:
                old_name = deal.pipeline.name
                first_stage = PipelineStage.objects.filter(
                    pipeline=re_pipeline
                ).order_by('order').first()
                deal.pipeline = re_pipeline
                deal.current_stage = first_stage
                deal.save(update_fields=['pipeline', 'current_stage'])
                DealActivity.objects.create(
                    deal=deal,
                    activity_type='stage_change',
                    description=f"[Webhook] Moved {old_name} → {re_pipeline.name} ({event_type})",
                )

        # Advance to target stage
        if target_stage_name:
            target_stage = PipelineStage.objects.filter(
                pipeline=deal.pipeline, name=target_stage_name,
            ).first()
            if target_stage and deal.current_stage != target_stage:
                # Only advance forward, never backward
                current_order = deal.current_stage.order if deal.current_stage else -1
                if target_stage.order > current_order:
                    old_stage = deal.current_stage.name if deal.current_stage else 'None'
                    deal.move_to_stage(target_stage)
                    DealActivity.objects.create(
                        deal=deal,
                        activity_type='stage_change',
                        description=f"[Webhook] {event_type}: {old_stage} → {target_stage.name}. {detail}",
                    )

        if mark_won:
            deal.status = 'won'
            deal.save(update_fields=['status'])
            DealActivity.objects.create(
                deal=deal,
                activity_type='status_change',
                description=f"[Webhook] {event_type}: {detail}. Deal won!",
            )
        else:
            # Pause autopilot — user is actively progressing on their own
            if not deal.autopilot_paused:
                deal.autopilot_paused = True
                deal.save(update_fields=['autopilot_paused'])

        logger.info(f"Desi Firms webhook: {event_type} for {email}, deal {deal.id}")
        return JsonResponse({
            'status': 'success',
            'deal_id': str(deal.id),
            'action': 'won' if mark_won else 'stage_advanced',
        })


@method_decorator(csrf_exempt, name='dispatch')
class ContactSearchView(View):
    """
    Fast contact search for email composer autocomplete.
    Returns contacts not in active pipelines and not unsubscribed.
    """

    def get(self, request):
        query = request.GET.get('q', '').strip()
        brand_id = request.GET.get('brand')
        limit = min(int(request.GET.get('limit', 10)), 50)

        if len(query) < 2:
            return JsonResponse({'contacts': []})

        contacts = Contact.objects.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(company__icontains=query),
            is_unsubscribed=False
        ).exclude(
            # Exclude contacts with active deals (already in pipeline)
            deals__status='active'
        ).order_by('name')

        if brand_id:
            contacts = contacts.filter(brand_id=brand_id)

        contacts = contacts.distinct()[:limit]

        return JsonResponse({
            'contacts': [
                {
                    'id': str(c.id),
                    'email': c.email,
                    'name': c.name or '',
                    'company': c.company or '',
                    'status': c.status,
                }
                for c in contacts
            ]
        })


@method_decorator(csrf_exempt, name='dispatch')
class GenerateAIEmailView(View):
    """
    Generate AI email content for the email composer.
    Called via AJAX from the unified composer interface.
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        brand_id = data.get('brand_id')
        pipeline_id = data.get('pipeline_id')  # Get pipeline for context
        email_type = data.get('email_type', 'sales_intro')
        tone = data.get('tone', 'professional')
        suggestions = data.get('suggestions', '')
        # Optional recipient info for smart salutation
        recipient_emails = data.get('recipient_emails', [])  # List of emails
        recipient_name = data.get('recipient_name', '')
        recipient_company = data.get('recipient_company', '')

        # Get brand info
        brand_name = 'Our Company'
        brand_website = ''
        brand_description = ''
        value_proposition = ''

        if brand_id:
            from crm.models import Brand
            try:
                brand = Brand.objects.get(id=brand_id)
                brand_name = brand.name
                brand_website = brand.website or ''
                brand_description = brand.ai_company_description or ''
                value_proposition = brand.ai_value_proposition or ''
            except Brand.DoesNotExist:
                pass

        # Get pipeline type for contextual email generation
        pipeline_type = ''
        pipeline_name = ''
        if pipeline_id:
            from crm.models import Pipeline
            try:
                pipeline = Pipeline.objects.get(id=pipeline_id)
                pipeline_type = pipeline.pipeline_type
                pipeline_name = pipeline.name
            except Pipeline.DoesNotExist:
                pass

        # Use first recipient email for smart salutation
        first_recipient_email = recipient_emails[0] if recipient_emails else ''

        # Build context for AI
        context = {
            'email_type': email_type,
            'tone': tone,
            'suggestions': suggestions,
            'pipeline_type': pipeline_type,  # For contextual email generation
            'pipeline_name': pipeline_name,
            'recipient_email': first_recipient_email,  # For smart salutation detection
            'recipient_name': recipient_name,
            'recipient_company': recipient_company,
            'recipient_website': '',
            'brand_name': brand_name,
            'brand_website': brand_website,
            'brand_description': brand_description,
            'value_proposition': value_proposition,
        }

        # Generate email with AI
        from crm.services.ai_agent import CRMAIAgent
        import traceback
        import logging
        logger = logging.getLogger(__name__)

        try:
            ai_agent = CRMAIAgent()
            result = ai_agent.compose_email_from_context(context)

            if result.get('success'):
                return JsonResponse({
                    'success': True,
                    'subject': result.get('subject', ''),
                    'body': result.get('body', ''),
                })
            else:
                error_msg = result.get('error', 'AI generation failed')
                logger.error(f"AI email generation failed: {error_msg}")
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=500)

        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"AI email generation exception: {e}\n{error_trace}")
            print(f"AI Email Generation Error: {e}")
            print(error_trace)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# =============================================================================
# PIPELINE DASHBOARD - KANBAN VIEW
# =============================================================================

from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST


@staff_member_required
def pipeline_dashboard(request):
    """
    Simple overview of all pipelines with deal counts per stage.
    """
    from django.contrib import admin

    pipelines = Pipeline.objects.filter(is_active=True).prefetch_related(
        'stages', 'deals'
    ).order_by('name')

    pipeline_data = []
    for pipeline in pipelines:
        stages_with_counts = []
        for stage in pipeline.stages.order_by('order'):
            count = Deal.objects.filter(
                pipeline=pipeline,
                current_stage=stage,
                status='active'
            ).count()
            stages_with_counts.append({
                'stage': stage,
                'count': count,
            })

        total_active = Deal.objects.filter(pipeline=pipeline, status='active').count()

        pipeline_data.append({
            'pipeline': pipeline,
            'stages': stages_with_counts,
            'total_active': total_active,
        })

    # Get admin context for Unfold sidebar
    context = {
        **admin.site.each_context(request),
        'title': 'Pipeline Dashboard',
        'pipeline_data': pipeline_data,
    }
    return render(request, 'admin/crm/pipeline_dashboard.html', context)


@staff_member_required
def pipeline_board(request, pipeline_id):
    """
    Kanban board view for a single pipeline.
    Shows stages as columns with deal cards.
    """
    from django.contrib import admin

    pipeline = get_object_or_404(Pipeline, id=pipeline_id)
    stages = pipeline.stages.order_by('order')

    # Build columns with deals (include active, won, and paused deals)
    columns = []
    for stage in stages:
        deals = Deal.objects.filter(
            pipeline=pipeline,
            current_stage=stage,
            status__in=['active', 'won', 'paused']  # Show active, won, and paused deals
        ).select_related('contact').order_by('-updated_at')[:50]

        columns.append({
            'stage': stage,
            'deals': deals,
            'count': deals.count(),
        })

    # Stats
    total_active = Deal.objects.filter(pipeline=pipeline, status='active').count()
    total_won = Deal.objects.filter(pipeline=pipeline, status='won').count()
    total_paused = Deal.objects.filter(pipeline=pipeline, status='paused').count()

    # Split lost deals into categories — query each separately to avoid cutoff
    lost_qs = Deal.objects.filter(pipeline=pipeline, status='lost').select_related('contact').order_by('-updated_at')

    reactivatable_reasons = {'no_response', 'not_interested', 'competitor', 'budget', 'timing', 'other', ''}
    inactive_deals = list(lost_qs.filter(lost_reason__in=reactivatable_reasons)[:200])
    unsubscribed_deals = list(lost_qs.filter(lost_reason='unsubscribed')[:200])
    bounced_deals = list(lost_qs.filter(lost_reason='invalid_email')[:200])

    total_lost = lost_qs.count()

    # Get admin context for Unfold sidebar
    context = {
        **admin.site.each_context(request),
        'title': f'{pipeline.name}',
        'pipeline': pipeline,
        'columns': columns,
        'total_active': total_active,
        'total_won': total_won,
        'total_lost': total_lost,
        'total_paused': total_paused,
        'unsubscribed_deals': unsubscribed_deals,
        'bounced_deals': bounced_deals,
        'inactive_deals': inactive_deals,
        'today': timezone.now().date(),
    }
    return render(request, 'admin/crm/pipeline_board.html', context)


@staff_member_required
@require_POST
def move_deal_stage(request):
    """
    AJAX endpoint to move a deal to a different stage (drag & drop).
    """
    deal_id = request.POST.get('deal_id')
    stage_id = request.POST.get('stage_id')

    try:
        deal = Deal.objects.get(id=deal_id)
        stage = PipelineStage.objects.get(id=stage_id)
        deal.move_to_stage(stage)
        return JsonResponse({'success': True, 'message': f'Moved to {stage.name}'})
    except (Deal.DoesNotExist, PipelineStage.DoesNotExist) as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@staff_member_required
@require_POST
def reactivate_deal(request):
    """
    Reactivate a lost deal (no_response, not_interested, etc.).
    Moves it back to the first stage of its pipeline and sets next action date.
    Does NOT allow reactivating unsubscribed/bounced deals.
    """
    deal_id = request.POST.get('deal_id')

    try:
        deal = Deal.objects.select_related('contact', 'pipeline').get(id=deal_id)
    except Deal.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Deal not found'}, status=400)

    # Block reactivation of permanently blocked contacts
    contact = deal.contact
    if contact.email_bounced:
        return JsonResponse({'success': False, 'error': 'Cannot reactivate - email has bounced'}, status=400)
    if contact.is_unsubscribed or contact.spam_reported:
        return JsonResponse({'success': False, 'error': 'Cannot reactivate - contact is unsubscribed'}, status=400)

    # Find the first stage of the pipeline
    first_stage = PipelineStage.objects.filter(
        pipeline=deal.pipeline
    ).order_by('order').first()

    deal.status = 'active'
    deal.lost_reason = ''
    deal.current_stage = first_stage
    deal.next_action_date = timezone.now() + timedelta(days=1)
    deal.autopilot_paused = False
    deal.save(update_fields=['status', 'lost_reason', 'current_stage', 'next_action_date', 'autopilot_paused'])

    DealActivity.objects.create(
        deal=deal,
        activity_type='status_change',
        description=f"Deal reactivated - moved back to {first_stage.name if first_stage else 'first stage'}"
    )

    return JsonResponse({
        'success': True,
        'message': f'Deal reactivated - moved to {first_stage.name if first_stage else "first stage"}'
    })


# =============================================================================
# UNSUBSCRIBE / OPT-OUT HANDLING
# =============================================================================

import hashlib
import hmac
from django.conf import settings
from django.shortcuts import render


def generate_unsubscribe_token(email: str) -> str:
    """Generate a secure token for unsubscribe link."""
    secret = getattr(settings, 'SECRET_KEY', 'fallback-secret')
    return hmac.new(
        secret.encode(),
        email.lower().encode(),
        hashlib.sha256
    ).hexdigest()[:32]


def verify_unsubscribe_token(email: str, token: str) -> bool:
    """Verify an unsubscribe token is valid."""
    expected = generate_unsubscribe_token(email)
    return hmac.compare_digest(expected, token)


def get_unsubscribe_url(email: str, brand_slug: str = 'desifirms', brand=None) -> str:
    """
    Generate full unsubscribe URL for an email.

    The CRM backend lives on codeteki.au, so all unsubscribe links point there.
    The brand parameter ensures the unsubscribe page shows correct branding.

    To use brand-specific domains (e.g., desifirms.com.au), set up a nginx
    redirect from /crm/* on that domain to codeteki.au/crm/*
    """
    token = generate_unsubscribe_token(email)

    # CRM lives on codeteki.au - all unsubscribe links go there
    # Using /api/crm/ path which is the established CRM URL namespace
    base_url = 'https://codeteki.au'

    return f"{base_url}/api/crm/unsubscribe/?email={email}&token={token}&brand={brand_slug}"


@method_decorator(csrf_exempt, name='dispatch')
class UnsubscribeView(View):
    """
    Handle email unsubscribe/opt-out requests.

    GET: Show confirmation page
    POST: Process unsubscribe
    """

    def get(self, request):
        """Show unsubscribe confirmation page."""
        email = request.GET.get('email', '')
        token = request.GET.get('token', '')
        brand_slug = request.GET.get('brand', 'desifirms')

        # Verify token
        if not email or not token or not verify_unsubscribe_token(email, token):
            return render(request, 'crm/unsubscribe.html', {
                'error': 'Invalid or expired unsubscribe link.',
                'email': email,
                'brand': brand_slug,
            })

        return render(request, 'crm/unsubscribe.html', {
            'email': email,
            'token': token,
            'brand': brand_slug,
            'confirmed': False,
        })

    def post(self, request):
        """Process unsubscribe request."""
        email = request.POST.get('email', '')
        token = request.POST.get('token', '')
        brand_slug = request.POST.get('brand', 'desifirms')
        reason = request.POST.get('reason', '')

        # Verify token
        if not email or not token or not verify_unsubscribe_token(email, token):
            return render(request, 'crm/unsubscribe.html', {
                'error': 'Invalid or expired unsubscribe link.',
                'email': email,
                'brand': brand_slug,
            })

        # Find and unsubscribe contact from this specific brand
        from crm.models import Brand
        brand = Brand.objects.filter(slug__iexact=brand_slug).first()
        contact = Contact.objects.filter(email__iexact=email, brand=brand).first() if brand else None

        if contact:
            # Use brand-specific unsubscribe (doesn't affect other brands)
            contact.unsubscribe_from_brand(brand_slug, reason or 'Clicked unsubscribe link')

            # Move active deals to "Lost" with reason - only for this brand's pipelines
            for deal in contact.deals.filter(status='active'):
                # Only affect deals from the same brand
                if deal.pipeline.brand and deal.pipeline.brand.slug.lower() == brand_slug.lower():
                    not_interested_stage = deal.pipeline.stages.filter(
                        name__icontains='not interested'
                    ).first()
                    if not_interested_stage:
                        deal.current_stage = not_interested_stage
                    deal.status = 'lost'
                    deal.lost_reason = 'unsubscribed'
                    deal.ai_notes = (deal.ai_notes or '') + f'\n[AUTO] Unsubscribed from {brand_slug} via link on {timezone.now().strftime("%Y-%m-%d")}'
                    deal.save()

        else:
            # Create contact record to track opt-out for future (brand already fetched above)
            Contact.objects.create(
                email=email,
                name=email.split('@')[0],
                brand=brand,
                unsubscribed_brands=[brand_slug.lower()],
                unsubscribed_at=timezone.now(),
                unsubscribe_reason=reason or 'Clicked unsubscribe link (no prior contact)',
                status='unsubscribed',
                source='unsubscribe_link',
            )

        return render(request, 'crm/unsubscribe.html', {
            'email': email,
            'confirmed': True,
            'brand': brand_slug,
        })


def check_can_email(email: str, brand_slug: str = None) -> dict:
    """
    Check if an email address can be contacted for a specific brand.

    Args:
        email: The email address to check
        brand_slug: Optional brand to check against. If provided, checks brand-specific
                   unsubscribe. If None, checks global unsubscribe only.

    Returns:
        {'can_email': bool, 'reason': str}
    """
    # Find contact for specific brand if provided, otherwise check any contact with that email
    if brand_slug:
        from crm.models import Brand
        brand = Brand.objects.filter(slug__iexact=brand_slug).first()
        contact = Contact.objects.filter(email__iexact=email, brand=brand).first() if brand else None
    else:
        contact = Contact.objects.filter(email__iexact=email).first()
    if not contact:
        return {'can_email': True, 'reason': ''}

    # Check global unsubscribe first
    if contact.is_unsubscribed:
        return {
            'can_email': False,
            'reason': f'Globally unsubscribed on {contact.unsubscribed_at.strftime("%Y-%m-%d") if contact.unsubscribed_at else "unknown date"}',
        }

    # Check brand-specific unsubscribe
    if brand_slug and contact.is_unsubscribed_from_brand(brand_slug):
        return {
            'can_email': False,
            'reason': f'Unsubscribed from {brand_slug} on {contact.unsubscribed_at.strftime("%Y-%m-%d") if contact.unsubscribed_at else "unknown date"}',
        }

    return {'can_email': True, 'reason': ''}
