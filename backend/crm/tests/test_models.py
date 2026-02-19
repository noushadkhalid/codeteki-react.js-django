from django.utils import timezone

from .helpers import CRMTestCase
from crm.models import Contact, Deal


class TestContactNormalizeEmail(CRMTestCase):
    """Test Contact.normalize_email static method."""

    def test_normalize_standard_email(self):
        self.assertEqual(Contact.normalize_email('User@Example.COM'), 'user@example.com')

    def test_normalize_angle_brackets(self):
        self.assertEqual(
            Contact.normalize_email('John Doe <john@example.com>'),
            'john@example.com',
        )

    def test_normalize_empty(self):
        self.assertEqual(Contact.normalize_email(''), '')
        self.assertEqual(Contact.normalize_email('  '), '')

    def test_normalize_with_whitespace(self):
        self.assertEqual(Contact.normalize_email('  user@test.com  '), 'user@test.com')


class TestContactUnsubscribe(CRMTestCase):
    """Test Contact unsubscribe methods."""

    def setUp(self):
        self.brand = self._create_brand()

    def test_is_unsubscribed_global(self):
        contact = self._create_contact(self.brand, is_unsubscribed=True)
        self.assertTrue(contact.is_unsubscribed_from_brand('testbrand'))
        self.assertTrue(contact.is_unsubscribed_from_brand('otherbrand'))

    def test_is_unsubscribed_brand_specific(self):
        contact = self._create_contact(
            self.brand, unsubscribed_brands=['testbrand'],
        )
        self.assertTrue(contact.is_unsubscribed_from_brand('testbrand'))
        self.assertFalse(contact.is_unsubscribed_from_brand('otherbrand'))

    def test_is_unsubscribed_case_insensitive(self):
        contact = self._create_contact(
            self.brand, unsubscribed_brands=['TestBrand'],
        )
        self.assertTrue(contact.is_unsubscribed_from_brand('testbrand'))
        self.assertTrue(contact.is_unsubscribed_from_brand('TESTBRAND'))

    def test_not_unsubscribed(self):
        contact = self._create_contact(self.brand)
        self.assertFalse(contact.is_unsubscribed_from_brand('testbrand'))

    def test_unsubscribe_from_brand_adds_slug(self):
        contact = self._create_contact(self.brand)
        contact.unsubscribe_from_brand('testbrand', reason='Test')
        contact.refresh_from_db()
        self.assertIn('testbrand', contact.unsubscribed_brands)
        self.assertEqual(contact.unsubscribe_reason, 'Test')
        self.assertIsNotNone(contact.unsubscribed_at)

    def test_unsubscribe_from_brand_idempotent(self):
        contact = self._create_contact(self.brand)
        contact.unsubscribe_from_brand('testbrand')
        contact.unsubscribe_from_brand('testbrand')
        contact.refresh_from_db()
        self.assertEqual(contact.unsubscribed_brands.count('testbrand'), 1)


class TestContactSaveAutoPopulation(CRMTestCase):
    """Test Contact.save() auto-population logic."""

    def setUp(self):
        self.brand = self._create_brand()

    def test_email_normalized_on_save(self):
        contact = Contact.objects.create(
            brand=self.brand, email='USER@Example.COM',
            name='User', company='Co', website='https://example.com',
        )
        self.assertEqual(contact.email, 'user@example.com')

    def test_name_extraction_personal_email(self):
        """Personal prefix like 'rajesh' should extract first name."""
        contact = Contact.objects.create(
            brand=self.brand, email='rajesh.kumar@testco.com.au', name='',
        )
        self.assertIn('Rajesh', contact.name)

    def test_name_extraction_generic_email(self):
        """Generic prefix like 'info' should use company or domain."""
        contact = Contact.objects.create(
            brand=self.brand, email='info@bombayre.com.au', name='',
        )
        # Should NOT be "Info" — should use domain name
        self.assertNotEqual(contact.name.lower(), 'info')
        self.assertTrue(len(contact.name) > 0)

    def test_company_extraction_from_domain(self):
        contact = Contact.objects.create(
            brand=self.brand, email='hello@acmecorp.com',
            name='Hello', company='',
        )
        self.assertTrue(len(contact.company) > 0)
        self.assertIn('Acmecorp', contact.company)

    def test_website_extraction_from_domain(self):
        contact = Contact.objects.create(
            brand=self.brand, email='hello@acmecorp.com',
            name='Hello', company='', website='',
        )
        self.assertEqual(contact.website, 'https://acmecorp.com')

    def test_skips_personal_email_domains(self):
        """Gmail, Yahoo, etc. should NOT populate company/website."""
        contact = Contact.objects.create(
            brand=self.brand, email='john@gmail.com',
            name='John', company='', website='',
        )
        # Company and website should remain empty for personal domains
        self.assertEqual(contact.company, '')
        self.assertEqual(contact.website, '')


class TestDealMoveToStage(CRMTestCase):
    """Test Deal.move_to_stage method."""

    def setUp(self):
        self.brand = self._create_brand()
        self.pipeline = self._create_pipeline(self.brand)
        self.stage1 = self._create_stage(self.pipeline, 'Stage 1', 0)
        self.stage2 = self._create_stage(
            self.pipeline, 'Stage 2', 1, days_until_followup=5,
        )
        self.contact = self._create_contact(self.brand)
        self.deal = self._create_deal(self.contact, self.pipeline, self.stage1)

    def test_updates_stage_and_timestamps(self):
        before = timezone.now()
        self.deal.move_to_stage(self.stage2)
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.current_stage, self.stage2)
        self.assertGreaterEqual(self.deal.stage_entered_at, before)

    def test_sets_next_action_date_from_stage(self):
        self.deal.move_to_stage(self.stage2)
        self.deal.refresh_from_db()
        # stage2 has days_until_followup=5
        expected_min = timezone.now() + timezone.timedelta(days=4)
        self.assertGreater(self.deal.next_action_date, expected_min)


class TestDefaultFieldValues(CRMTestCase):
    """Test that new model fields have correct defaults."""

    def setUp(self):
        self.brand = self._create_brand()
        self.pipeline = self._create_pipeline(self.brand)
        self.stage = self._create_stage(self.pipeline)
        self.contact = self._create_contact(self.brand)

    def test_preferred_send_hour_defaults_none(self):
        self.assertIsNone(self.contact.preferred_send_hour)

    def test_re_engagement_attempted_defaults_false(self):
        deal = self._create_deal(self.contact, self.pipeline, self.stage)
        self.assertFalse(deal.re_engagement_attempted)

    def test_engagement_tier_defaults_empty(self):
        deal = self._create_deal(self.contact, self.pipeline, self.stage)
        self.assertEqual(deal.engagement_tier, '')

    def test_autopilot_paused_defaults_false(self):
        deal = self._create_deal(self.contact, self.pipeline, self.stage)
        self.assertFalse(deal.autopilot_paused)
