from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from core.models import ChatLead, ContactInquiry
from .models import Contact, Deal, Pipeline, DealActivity


@receiver(post_save, sender=ChatLead)
def create_contact_from_chat_lead(sender, instance, created, **kwargs):
    """
    When a ChatLead is created with an email, create a CRM Contact.
    """
    if created and instance.email:
        contact, was_created = Contact.objects.get_or_create(
            email=instance.email,
            defaults={
                'name': instance.name or 'Unknown',
                'company': instance.company or '',
                'contact_type': 'lead',
                'source': 'chatbot',
                'chat_lead': instance,
            }
        )

        # If contact exists, link the chat lead
        if not was_created and not contact.chat_lead:
            contact.chat_lead = instance
            contact.save()

        # Auto-create deal in sales pipeline if active
        try:
            sales_pipeline = Pipeline.objects.filter(
                pipeline_type='sales',
                is_active=True
            ).first()

            if sales_pipeline and was_created:
                first_stage = sales_pipeline.stages.order_by('order').first()
                if first_stage:
                    Deal.objects.create(
                        contact=contact,
                        pipeline=sales_pipeline,
                        current_stage=first_stage,
                        next_action_date=timezone.now(),
                    )
        except Exception:
            pass  # Don't break lead creation if deal creation fails


@receiver(post_save, sender=ContactInquiry)
def create_contact_from_inquiry(sender, instance, created, **kwargs):
    """
    When a ContactInquiry is created, create a CRM Contact and Deal.
    """
    if created and instance.email:
        contact, was_created = Contact.objects.get_or_create(
            email=instance.email,
            defaults={
                'name': instance.name or 'Unknown',
                'contact_type': 'lead',
                'source': 'contact_form',
                'contact_inquiry': instance,
                'notes': instance.message or '',
            }
        )

        # If contact exists, link the inquiry
        if not was_created and not contact.contact_inquiry:
            contact.contact_inquiry = instance
            contact.save()

        # Auto-create deal in sales pipeline
        try:
            sales_pipeline = Pipeline.objects.filter(
                pipeline_type='sales',
                is_active=True
            ).first()

            if sales_pipeline:
                first_stage = sales_pipeline.stages.order_by('order').first()
                if first_stage:
                    # Check if deal already exists
                    existing_deal = Deal.objects.filter(
                        contact=contact,
                        pipeline=sales_pipeline,
                        status='active'
                    ).first()

                    if not existing_deal:
                        Deal.objects.create(
                            contact=contact,
                            pipeline=sales_pipeline,
                            current_stage=first_stage,
                            next_action_date=timezone.now(),
                            ai_notes=f"Created from contact form. Service interest: {instance.service or 'Not specified'}",
                        )
        except Exception:
            pass


@receiver(post_save, sender=Deal)
def log_deal_stage_change(sender, instance, created, **kwargs):
    """
    Log stage changes and status changes on deals.
    """
    if created:
        DealActivity.objects.create(
            deal=instance,
            activity_type='stage_change',
            description=f"Deal created in stage: {instance.current_stage.name if instance.current_stage else 'Unknown'}",
        )


@receiver(post_save, sender=Deal)
def move_won_deal_to_registered_pipeline(sender, instance, created, **kwargs):
    """
    When a deal is marked as 'won', create a new deal in the appropriate
    Registered Users pipeline for nurturing/follow-up.

    Maps:
    - Desi Firms Real Estate → Registered Users - Real Estate
    - Desi Firms Business Directory → Registered Users - Business
    - etc.
    """
    # Skip if just created or not won
    if created or instance.status != 'won':
        return

    # Skip if already in a registered users pipeline (avoid infinite loop)
    pipeline_name = instance.pipeline.name.lower() if instance.pipeline else ''
    if 'registered users' in pipeline_name or 'nudge' in pipeline_name:
        return

    # Determine the target registered users pipeline based on source pipeline type
    source_type = instance.pipeline.pipeline_type if instance.pipeline else None
    if not source_type:
        return

    # Map source pipeline type to registered users pipeline
    pipeline_mapping = {
        'realestate': 'Registered Users - Real Estate',
        'business': 'Registered Users - Business',
        'events': 'Registered Users - Events',
    }

    target_pipeline_name = pipeline_mapping.get(source_type)
    if not target_pipeline_name:
        return

    try:
        # Find the target pipeline
        target_pipeline = Pipeline.objects.filter(
            name__iexact=target_pipeline_name,
            is_active=True
        ).first()

        if not target_pipeline:
            # Try partial match
            target_pipeline = Pipeline.objects.filter(
                name__icontains=target_pipeline_name.split(' - ')[1] if ' - ' in target_pipeline_name else target_pipeline_name,
                pipeline_type='registered_users',
                is_active=True
            ).first()

        if not target_pipeline:
            return

        # Check if contact already has an active deal in target pipeline
        existing_deal = Deal.objects.filter(
            contact=instance.contact,
            pipeline=target_pipeline,
            status='active'
        ).exists()

        if existing_deal:
            return

        # Get first stage (usually "Registered")
        first_stage = target_pipeline.stages.order_by('order').first()
        if not first_stage:
            return

        # Create new deal in registered users pipeline
        new_deal = Deal.objects.create(
            contact=instance.contact,
            pipeline=target_pipeline,
            current_stage=first_stage,
            status='active',
            next_action_date=timezone.now(),
            ai_notes=f"Auto-created from won deal in {instance.pipeline.name}",
        )

        # Log the activity
        DealActivity.objects.create(
            deal=new_deal,
            activity_type='stage_change',
            description=f"Deal created from won deal in {instance.pipeline.name}",
        )

    except Exception as e:
        # Don't break the save if this fails
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create registered users deal: {e}")
