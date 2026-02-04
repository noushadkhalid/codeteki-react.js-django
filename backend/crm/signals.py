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


