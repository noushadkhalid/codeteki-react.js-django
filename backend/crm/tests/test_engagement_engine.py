from datetime import timedelta

from django.utils import timezone

from .helpers import CRMTestCase
from crm.services.engagement_engine import (
    get_engagement_profile,
    compute_preferred_send_hour,
    get_engagement_summary_for_ai,
)


class TestGetEngagementProfile(CRMTestCase):
    """Test get_engagement_profile() with various email histories."""

    def setUp(self):
        self.brand = self._create_brand()
        self.pipeline = self._create_pipeline(self.brand)
        self.stage = self._create_stage(self.pipeline)
        self.contact = self._create_contact(self.brand)
        self.deal = self._create_deal(self.contact, self.pipeline, self.stage)

    # --- Tier classification ---

    def test_no_emails_returns_cold(self):
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.tier, 'cold')
        self.assertEqual(profile.total_sent, 0)

    def test_replied_returns_engaged(self):
        self._create_email_log(
            self.deal, replied=True, replied_at=timezone.now(),
            opened=True, opened_at=timezone.now(),
        )
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.tier, 'engaged')

    def test_ghost_detection(self):
        """3+ sent, 0 opens, 3+ consecutive unopened → ghost."""
        for i in range(3):
            self._create_email_log(self.deal, opened=False)
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.tier, 'ghost')

    def test_cold_detection(self):
        """2 sent, 0 opens → cold."""
        for i in range(2):
            self._create_email_log(self.deal, opened=False)
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.tier, 'cold')

    def test_hot_detection(self):
        """Recent open + high open rate → hot."""
        now = timezone.now()
        # 3 emails: 2 opened (one recently), 1 not → 66% open rate
        self._create_email_log(
            self.deal, opened=True, opened_at=now - timedelta(days=1),
            sent_at=now - timedelta(days=3),
        )
        self._create_email_log(
            self.deal, opened=True, opened_at=now - timedelta(days=5),
            sent_at=now - timedelta(days=6),
        )
        self._create_email_log(
            self.deal, opened=False,
            sent_at=now - timedelta(days=8),
        )
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.tier, 'hot')
        self.assertGreater(profile.open_rate, 0.5)

    def test_warm_detection(self):
        """Opened at least once within 14 days → warm."""
        now = timezone.now()
        self._create_email_log(
            self.deal, opened=True, opened_at=now - timedelta(days=10),
            sent_at=now - timedelta(days=12),
        )
        self._create_email_log(
            self.deal, opened=False,
            sent_at=now - timedelta(days=15),
        )
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.tier, 'warm')

    def test_lurker_detection(self):
        """Opened 1-2 emails but not recently (>14 days) → lurker."""
        now = timezone.now()
        self._create_email_log(
            self.deal, opened=True, opened_at=now - timedelta(days=20),
            sent_at=now - timedelta(days=22),
        )
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.tier, 'lurker')

    # --- Rate calculations ---

    def test_open_rate_calculation(self):
        now = timezone.now()
        self._create_email_log(
            self.deal, opened=True, opened_at=now,
        )
        self._create_email_log(self.deal, opened=False)
        profile = get_engagement_profile(self.deal)
        self.assertAlmostEqual(profile.open_rate, 0.5)

    def test_click_rate_calculation(self):
        now = timezone.now()
        self._create_email_log(
            self.deal,
            opened=True, opened_at=now,
            clicked=True, clicked_at=now,
        )
        self._create_email_log(self.deal, opened=False)
        profile = get_engagement_profile(self.deal)
        self.assertAlmostEqual(profile.click_rate, 0.5)

    # --- Behavioral signals ---

    def test_consecutive_unopened_count(self):
        """Count consecutive unopened from most recent backwards."""
        now = timezone.now()
        # Most recent 2 unopened, then an opened one
        self._create_email_log(
            self.deal, opened=False, sent_at=now - timedelta(days=1),
        )
        self._create_email_log(
            self.deal, opened=False, sent_at=now - timedelta(days=3),
        )
        self._create_email_log(
            self.deal, opened=True, opened_at=now - timedelta(days=5),
            sent_at=now - timedelta(days=6),
        )
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.consecutive_unopened, 2)

    def test_burnout_risk_at_threshold(self):
        """3+ consecutive unopened triggers burnout risk."""
        for i in range(3):
            self._create_email_log(self.deal, opened=False)
        profile = get_engagement_profile(self.deal)
        self.assertTrue(profile.is_burnout_risk)

    def test_no_burnout_risk_below_threshold(self):
        for i in range(2):
            self._create_email_log(self.deal, opened=False)
        profile = get_engagement_profile(self.deal)
        self.assertFalse(profile.is_burnout_risk)

    def test_last_open_days_ago(self):
        now = timezone.now()
        self._create_email_log(
            self.deal, opened=True, opened_at=now - timedelta(days=5),
        )
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.last_open_days_ago, 5)

    def test_opens_last_7_days(self):
        now = timezone.now()
        # One open 3 days ago (within window), one 10 days ago (outside)
        self._create_email_log(
            self.deal, opened=True, opened_at=now - timedelta(days=3),
            sent_at=now - timedelta(days=4),
        )
        self._create_email_log(
            self.deal, opened=True, opened_at=now - timedelta(days=10),
            sent_at=now - timedelta(days=12),
        )
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.opens_last_7_days, 1)

    def test_last_click_days_ago(self):
        now = timezone.now()
        self._create_email_log(
            self.deal,
            opened=True, opened_at=now - timedelta(days=2),
            clicked=True, clicked_at=now - timedelta(days=2),
        )
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.last_click_days_ago, 2)

    def test_last_reply_days_ago(self):
        now = timezone.now()
        self._create_email_log(
            self.deal,
            opened=True, opened_at=now,
            replied=True, replied_at=now - timedelta(days=1),
        )
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.last_reply_days_ago, 1)

    # --- Edge cases ---

    def test_only_unsent_emails_are_ignored(self):
        """Emails without sent_at should not count."""
        self._create_email_log(self.deal, sent_at=None, opened=False)
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.total_sent, 0)
        self.assertEqual(profile.tier, 'cold')

    def test_single_sent_no_open(self):
        """1 sent, 0 opens → cold (not ghost, need 2+ for cold and 3+ for ghost)."""
        self._create_email_log(self.deal, opened=False)
        profile = get_engagement_profile(self.deal)
        self.assertEqual(profile.tier, 'cold')

    def test_many_opens_old_returns_warm(self):
        """Opened many emails but all >14 days ago, >2 opens → warm (not lurker)."""
        now = timezone.now()
        for i in range(4):
            self._create_email_log(
                self.deal,
                opened=True, opened_at=now - timedelta(days=20 + i),
                sent_at=now - timedelta(days=21 + i),
            )
        profile = get_engagement_profile(self.deal)
        # >2 opens, all old → warm (lurker is only for 1-2 opens)
        self.assertEqual(profile.tier, 'warm')


class TestComputePreferredSendHour(CRMTestCase):
    """Test compute_preferred_send_hour()."""

    def setUp(self):
        self.brand = self._create_brand()
        self.pipeline = self._create_pipeline(self.brand)
        self.stage = self._create_stage(self.pipeline)
        self.contact = self._create_contact(self.brand)
        self.deal = self._create_deal(self.contact, self.pipeline, self.stage)

    def test_less_than_3_opens_returns_none(self):
        # Only 2 opens
        now = timezone.now()
        for i in range(2):
            self._create_email_log(
                self.deal,
                to_email=self.contact.email,
                opened=True, opened_at=now.replace(hour=10) - timedelta(days=i),
            )
        result = compute_preferred_send_hour(self.contact)
        self.assertIsNone(result)

    def test_returns_most_common_hour(self):
        """With 3+ opens, returns the most common local-time hour."""
        from django.utils.timezone import localtime
        now = timezone.now()
        # Create 3 opens: 2 at same hour, 1 at different hour
        open_time_a = now.replace(hour=14, minute=0, second=0)
        open_time_b = now.replace(hour=9, minute=0, second=0)
        expected_hour = localtime(open_time_a).hour  # convert to local tz

        for i in range(2):
            self._create_email_log(
                self.deal,
                to_email=self.contact.email,
                opened=True,
                opened_at=open_time_a - timedelta(days=i),
            )
        self._create_email_log(
            self.deal,
            to_email=self.contact.email,
            opened=True,
            opened_at=open_time_b - timedelta(days=3),
        )
        result = compute_preferred_send_hour(self.contact)
        self.assertIsNotNone(result)
        self.assertEqual(result, expected_hour)

    def test_no_opens_returns_none(self):
        result = compute_preferred_send_hour(self.contact)
        self.assertIsNone(result)


class TestGetEngagementSummaryForAI(CRMTestCase):
    """Test get_engagement_summary_for_ai()."""

    def setUp(self):
        self.brand = self._create_brand()
        self.pipeline = self._create_pipeline(self.brand)
        self.stage = self._create_stage(self.pipeline)
        self.contact = self._create_contact(self.brand)
        self.deal = self._create_deal(self.contact, self.pipeline, self.stage)

    def test_contains_tier(self):
        summary = get_engagement_summary_for_ai(self.deal)
        self.assertIn('COLD', summary)
        self.assertIn('Engagement Tier', summary)

    def test_contains_burnout_flag(self):
        for i in range(4):
            self._create_email_log(self.deal, opened=False)
        summary = get_engagement_summary_for_ai(self.deal)
        self.assertIn('Burnout Risk: YES', summary)

    def test_no_emails_shows_na(self):
        summary = get_engagement_summary_for_ai(self.deal)
        self.assertIn('N/A', summary)

    def test_with_activity_shows_rates(self):
        now = timezone.now()
        self._create_email_log(
            self.deal, opened=True, opened_at=now,
        )
        self._create_email_log(self.deal, opened=False)
        summary = get_engagement_summary_for_ai(self.deal)
        self.assertIn('Open Rate: 50%', summary)
        self.assertIn('Emails Sent: 2', summary)
