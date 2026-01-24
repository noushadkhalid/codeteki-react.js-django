"""
Lead Integration Service

Integrates leads from website forms and chatbot into CRM pipeline.
Automatically creates Contact and Deal for follow-up.
"""

from django.db import transaction
from django.utils import timezone
from crm.models import Brand, Contact, Deal, Pipeline, PipelineStage


class LeadIntegrationService:
    """
    Integrates leads from various sources into CRM pipeline.

    Sources:
    - ContactInquiry (contact form submissions)
    - ChatConversation (chatbot leads)
    - API webhooks
    """

    CODETEKI_SLUG = 'codeteki'

    @classmethod
    def get_codeteki_brand(cls):
        """Get the Codeteki brand for pipeline assignment."""
        return Brand.objects.filter(slug=cls.CODETEKI_SLUG).first()

    @classmethod
    def get_sales_pipeline(cls, brand=None):
        """Get the default sales pipeline for a brand."""
        if brand is None:
            brand = cls.get_codeteki_brand()
        if not brand:
            return None
        return Pipeline.objects.filter(
            brand=brand,
            pipeline_type='sales',
            is_active=True
        ).first()

    @classmethod
    def get_first_stage(cls, pipeline):
        """Get the first stage of a pipeline."""
        return pipeline.stages.order_by('order').first()

    @classmethod
    @transaction.atomic
    def create_lead_from_inquiry(cls, inquiry, auto_create_deal=True):
        """
        Create a CRM Contact and Deal from a ContactInquiry.

        Args:
            inquiry: ContactInquiry instance
            auto_create_deal: Whether to create a deal in the pipeline

        Returns:
            tuple: (contact, deal, created)
        """
        brand = cls.get_codeteki_brand()
        if not brand:
            return None, None, False

        # Normalize email
        email = Contact.normalize_email(inquiry.email)

        # Create or get contact
        contact, created = Contact.objects.get_or_create(
            email=email,
            defaults={
                'name': inquiry.name,
                'company': inquiry.phone,  # Store phone in company temporarily
                'brand': brand,
                'source': f'contact_form:{inquiry.source or "website"}',
                'contact_type': 'lead',
                'notes': f"Service Interest: {inquiry.service}\n\nMessage:\n{inquiry.message}",
                'tags': ['website_inquiry', inquiry.service.lower().replace(' ', '_')] if inquiry.service else ['website_inquiry'],
            }
        )

        # Update existing contact with new inquiry info
        if not created:
            if inquiry.message:
                contact.notes = f"{contact.notes}\n\n---\nNew Inquiry ({timezone.now().strftime('%Y-%m-%d')}):\nService: {inquiry.service}\nMessage: {inquiry.message}"
            contact.save()

        deal = None
        if auto_create_deal:
            pipeline = cls.get_sales_pipeline(brand)
            if pipeline:
                first_stage = cls.get_first_stage(pipeline)
                if first_stage:
                    # Check for existing active deal
                    existing_deal = Deal.objects.filter(
                        contact=contact,
                        pipeline=pipeline,
                        status='active'
                    ).first()

                    if existing_deal:
                        # Update existing deal notes
                        existing_deal.notes = f"{existing_deal.notes}\n\nNew inquiry received: {inquiry.service}"
                        existing_deal.save()
                        deal = existing_deal
                    else:
                        # Create new deal
                        deal = Deal.objects.create(
                            contact=contact,
                            pipeline=pipeline,
                            stage=first_stage,
                            status='active',
                            notes=f"Lead from contact form\nService Interest: {inquiry.service}",
                        )

        # Mark inquiry as reviewed
        inquiry.status = 'reviewed'
        inquiry.metadata = inquiry.metadata or {}
        inquiry.metadata['crm_contact_id'] = str(contact.id)
        if deal:
            inquiry.metadata['crm_deal_id'] = str(deal.id)
        inquiry.save()

        return contact, deal, created

    @classmethod
    @transaction.atomic
    def create_lead_from_chat(cls, conversation, auto_create_deal=True):
        """
        Create a CRM Contact and Deal from a ChatConversation.

        Args:
            conversation: ChatConversation instance
            auto_create_deal: Whether to create a deal in the pipeline

        Returns:
            tuple: (contact, deal, created)
        """
        # Must have email to create lead
        if not conversation.visitor_email:
            return None, None, False

        brand = cls.get_codeteki_brand()
        if not brand:
            return None, None, False

        # Normalize email
        email = Contact.normalize_email(conversation.visitor_email)

        # Build notes from conversation
        notes = f"Chatbot Lead\n"
        if conversation.last_user_message:
            notes += f"Last Message: {conversation.last_user_message}\n"

        # Create or get contact
        contact, created = Contact.objects.get_or_create(
            email=email,
            defaults={
                'name': conversation.visitor_name or email.split('@')[0],
                'company': conversation.visitor_company or '',
                'brand': brand,
                'source': f'chatbot:{conversation.source or "website"}',
                'contact_type': 'lead',
                'notes': notes,
                'tags': ['chatbot_lead'],
            }
        )

        # Update existing contact
        if not created:
            if conversation.last_user_message:
                contact.notes = f"{contact.notes}\n\n---\nChatbot ({timezone.now().strftime('%Y-%m-%d')}):\n{conversation.last_user_message}"
            contact.save()

        deal = None
        if auto_create_deal:
            pipeline = cls.get_sales_pipeline(brand)
            if pipeline:
                first_stage = cls.get_first_stage(pipeline)
                if first_stage:
                    # Check for existing active deal
                    existing_deal = Deal.objects.filter(
                        contact=contact,
                        pipeline=pipeline,
                        status='active'
                    ).first()

                    if existing_deal:
                        deal = existing_deal
                    else:
                        deal = Deal.objects.create(
                            contact=contact,
                            pipeline=pipeline,
                            stage=first_stage,
                            status='active',
                            notes=f"Lead from chatbot conversation",
                        )

        # Update conversation metadata
        conversation.metadata = conversation.metadata or {}
        conversation.metadata['crm_contact_id'] = str(contact.id)
        if deal:
            conversation.metadata['crm_deal_id'] = str(deal.id)
        conversation.save()

        return contact, deal, created

    @classmethod
    def create_lead_from_api(cls, data, source='api'):
        """
        Create a CRM Contact and Deal from API data.

        Args:
            data: dict with keys: email, name, company, phone, message, service
            source: Source identifier

        Returns:
            tuple: (contact, deal, created)
        """
        email = data.get('email')
        if not email:
            return None, None, False

        brand = cls.get_codeteki_brand()
        if not brand:
            return None, None, False

        email = Contact.normalize_email(email)

        contact, created = Contact.objects.get_or_create(
            email=email,
            defaults={
                'name': data.get('name', email.split('@')[0]),
                'company': data.get('company', ''),
                'brand': brand,
                'source': f'api:{source}',
                'contact_type': 'lead',
                'notes': data.get('message', ''),
                'tags': ['api_lead'],
            }
        )

        deal = None
        pipeline = cls.get_sales_pipeline(brand)
        if pipeline:
            first_stage = cls.get_first_stage(pipeline)
            if first_stage:
                existing_deal = Deal.objects.filter(
                    contact=contact,
                    pipeline=pipeline,
                    status='active'
                ).first()

                if not existing_deal:
                    deal = Deal.objects.create(
                        contact=contact,
                        pipeline=pipeline,
                        stage=first_stage,
                        status='active',
                        notes=f"API Lead: {data.get('service', 'General Inquiry')}",
                    )
                else:
                    deal = existing_deal

        return contact, deal, created
