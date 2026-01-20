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

                # Log activity
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

        # Update deal
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
            contact=contact,
            subject=f"Reply: {subject}",
            direction='inbound',
            replied=True,
            replied_at=timezone.now()
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

    # Build columns with deals
    columns = []
    for stage in stages:
        deals = Deal.objects.filter(
            pipeline=pipeline,
            current_stage=stage,
            status='active'
        ).select_related('contact').order_by('-updated_at')[:50]

        columns.append({
            'stage': stage,
            'deals': deals,
            'count': deals.count(),
        })

    # Stats
    total_active = Deal.objects.filter(pipeline=pipeline, status='active').count()
    total_won = Deal.objects.filter(pipeline=pipeline, status='won').count()
    total_lost = Deal.objects.filter(pipeline=pipeline, status='lost').count()

    # Get admin context for Unfold sidebar
    context = {
        **admin.site.each_context(request),
        'title': f'{pipeline.name}',
        'pipeline': pipeline,
        'columns': columns,
        'total_active': total_active,
        'total_won': total_won,
        'total_lost': total_lost,
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


def get_unsubscribe_url(email: str, brand_slug: str = 'desifirms') -> str:
    """Generate full unsubscribe URL for an email."""
    token = generate_unsubscribe_token(email)
    # Use production URL
    base_url = 'https://codeteki.au'
    return f"{base_url}/crm/unsubscribe/?email={email}&token={token}&brand={brand_slug}"


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
            })

        # Find and unsubscribe contact(s)
        contacts = Contact.objects.filter(email__iexact=email)

        for contact in contacts:
            contact.is_unsubscribed = True
            contact.unsubscribed_at = timezone.now()
            contact.unsubscribe_reason = reason or 'Clicked unsubscribe link'
            contact.status = 'unsubscribed'
            contact.save()

            # Move all active deals to "Not Interested" stage
            for deal in contact.deals.filter(status='active'):
                not_interested_stage = deal.pipeline.stages.filter(
                    name__icontains='not interested'
                ).first()
                if not_interested_stage:
                    deal.current_stage = not_interested_stage
                deal.status = 'lost'
                deal.ai_notes = (deal.ai_notes or '') + f'\n[AUTO] Unsubscribed via link on {timezone.now().strftime("%Y-%m-%d")}'
                deal.save()

        # Also create/update contact if doesn't exist (track opt-out for future)
        if not contacts.exists():
            from crm.models import Brand
            brand = Brand.objects.filter(slug=brand_slug).first()
            Contact.objects.create(
                email=email,
                name=email.split('@')[0],
                brand=brand,
                is_unsubscribed=True,
                unsubscribed_at=timezone.now(),
                unsubscribe_reason=reason or 'Clicked unsubscribe link (no prior contact)',
                status='unsubscribed',
                source='unsubscribe_link',
            )

        return render(request, 'crm/unsubscribe.html', {
            'email': email,
            'confirmed': True,
        })


def check_can_email(email: str) -> dict:
    """
    Check if an email address can be contacted.
    Returns {'can_email': bool, 'reason': str}
    """
    # Check if unsubscribed
    contact = Contact.objects.filter(email__iexact=email, is_unsubscribed=True).first()
    if contact:
        return {
            'can_email': False,
            'reason': f'Unsubscribed on {contact.unsubscribed_at.strftime("%Y-%m-%d") if contact.unsubscribed_at else "unknown date"}',
        }

    return {'can_email': True, 'reason': ''}
