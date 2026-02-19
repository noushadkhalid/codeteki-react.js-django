from django.test import TestCase
from django.utils import timezone

from crm.models import (
    Brand, Contact, Pipeline, PipelineStage, Deal, EmailLog, DealActivity,
)


class CRMTestCase(TestCase):
    """Base test case with helper methods for creating CRM test data."""

    def _create_brand(self, slug='testbrand', name='Test Brand', **kwargs):
        defaults = {
            'website': f'https://{slug}.com',
            'from_email': f'hello@{slug}.com',
            'from_name': name,
        }
        defaults.update(kwargs)
        return Brand.objects.create(slug=slug, name=name, **defaults)

    def _create_contact(self, brand, email='test@example.com', **kwargs):
        defaults = {
            'name': 'Test Contact',
            'company': 'Test Company',
            'website': 'https://example.com',
            'contact_type': 'lead',
            'source': 'test',
        }
        defaults.update(kwargs)
        return Contact.objects.create(brand=brand, email=email, **defaults)

    def _create_pipeline(self, brand, name='Test Pipeline', pipeline_type='sales', **kwargs):
        defaults = {'is_active': True}
        defaults.update(kwargs)
        return Pipeline.objects.create(
            brand=brand, name=name, pipeline_type=pipeline_type, **defaults,
        )

    def _create_stage(self, pipeline, name='Stage 1', order=0, **kwargs):
        defaults = {'days_until_followup': 3}
        defaults.update(kwargs)
        return PipelineStage.objects.create(
            pipeline=pipeline, name=name, order=order, **defaults,
        )

    def _create_deal(self, contact, pipeline, stage, **kwargs):
        defaults = {
            'status': 'active',
            'next_action_date': timezone.now(),
        }
        defaults.update(kwargs)
        return Deal.objects.create(
            contact=contact, pipeline=pipeline, current_stage=stage, **defaults,
        )

    def _create_email_log(self, deal, **kwargs):
        defaults = {
            'subject': 'Test Email',
            'body': 'Test body',
            'to_email': deal.contact.email if deal else 'test@example.com',
            'sent_at': timezone.now(),
        }
        defaults.update(kwargs)
        return EmailLog.objects.create(deal=deal, **defaults)
