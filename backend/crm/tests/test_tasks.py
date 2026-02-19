from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.test import override_settings
from django.utils import timezone

from .helpers import CRMTestCase
from crm.models import Contact, Deal, DealActivity, EmailLog, PipelineStage


# =============================================================================
# process_pending_deals
# =============================================================================


class TestProcessPendingDeals(CRMTestCase):
    """Test the process_pending_deals Celery task."""

    def setUp(self):
        self.brand = self._create_brand()
        self.pipeline = self._create_pipeline(self.brand)
        self.stage1 = self._create_stage(self.pipeline, 'Follow Up 1', 0)
        self.stage2 = self._create_stage(self.pipeline, 'Follow Up 2', 1)
        self.stage_final = self._create_stage(
            self.pipeline, 'Follow Up 3 (Final)', 2,
        )
        self.stage_ni = self._create_stage(
            self.pipeline, 'Not Interested', 3, is_terminal=True,
        )
        self.contact = self._create_contact(self.brand, email='deal@test.com')

    def _run_task(self):
        from crm.tasks import process_pending_deals
        return process_pending_deals()

    @patch('crm.tasks.is_office_hours', return_value=False)
    def test_outside_office_hours_skipped(self, mock_hours):
        result = self._run_task()
        self.assertEqual(result['skipped'], 'outside_office_hours')

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_bounced_contact_closes_deal(self, MockAgent, mock_hours):
        self.contact.email_bounced = True
        self.contact.save(update_fields=['email_bounced'])
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)

        self._run_task()
        deal.refresh_from_db()
        self.assertEqual(deal.status, 'lost')
        self.assertEqual(deal.lost_reason, 'invalid_email')

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_unsubscribed_contact_closes_deal(self, MockAgent, mock_hours):
        self.contact.is_unsubscribed = True
        self.contact.save(update_fields=['is_unsubscribed'])
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)

        self._run_task()
        deal.refresh_from_db()
        self.assertEqual(deal.status, 'lost')
        self.assertEqual(deal.lost_reason, 'unsubscribed')

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_domain_reputation_pauses_deal(self, MockAgent, mock_hours):
        """3+ bad contacts at same domain pauses the deal."""
        domain = 'baddomain.com'
        # Create 3 bounced contacts at same domain
        for i in range(3):
            self._create_contact(
                self.brand, email=f'bad{i}@{domain}',
                email_bounced=True,
            )
        good_contact = self._create_contact(
            self.brand, email=f'target@{domain}',
        )
        deal = self._create_deal(good_contact, self.pipeline, self.stage1)

        self._run_task()
        deal.refresh_from_db()
        self.assertTrue(deal.autopilot_paused)

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_domain_reputation_2_does_not_pause(self, MockAgent, mock_hours):
        """Only 2 bad contacts should NOT pause."""
        domain = 'okdomain.com'
        for i in range(2):
            self._create_contact(
                self.brand, email=f'bad{i}@{domain}', email_bounced=True,
            )
        good_contact = self._create_contact(
            self.brand, email=f'target@{domain}',
        )
        deal = self._create_deal(good_contact, self.pipeline, self.stage1)
        mock_agent = MockAgent.return_value
        mock_agent.analyze_deal.return_value = {
            'action': 'wait', 'metadata': {'wait_days': '3'},
        }

        self._run_task()
        deal.refresh_from_db()
        self.assertFalse(deal.autopilot_paused)

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_domain_reputation_only_counts_same_brand(self, MockAgent, mock_hours):
        """Bad contacts on other brands shouldn't count."""
        domain = 'cross.com'
        other_brand = self._create_brand(slug='other', name='Other')
        for i in range(3):
            self._create_contact(
                other_brand, email=f'bad{i}@{domain}', email_bounced=True,
            )
        good_contact = self._create_contact(
            self.brand, email=f'target@{domain}',
        )
        deal = self._create_deal(good_contact, self.pipeline, self.stage1)
        mock_agent = MockAgent.return_value
        mock_agent.analyze_deal.return_value = {
            'action': 'wait', 'metadata': {'wait_days': '3'},
        }

        self._run_task()
        deal.refresh_from_db()
        self.assertFalse(deal.autopilot_paused)

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_final_followup_auto_closes(self, MockAgent, mock_hours):
        deal = self._create_deal(self.contact, self.pipeline, self.stage_final)
        self._run_task()
        deal.refresh_from_db()
        self.assertEqual(deal.status, 'lost')
        self.assertEqual(deal.lost_reason, 'no_response')

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_ghost_detection_closes_deal(self, MockAgent, mock_hours):
        """Ghost tier with 3+ sent emails should close deal."""
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        for i in range(3):
            self._create_email_log(deal, opened=False)

        self._run_task()
        deal.refresh_from_db()
        self.assertEqual(deal.status, 'lost')
        self.assertEqual(deal.lost_reason, 'no_response')

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_burnout_risk_extends_wait(self, MockAgent, mock_hours):
        """Burnout risk (3+ consecutive unopened) for non-engaged should extend wait."""
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        # 3 unopened but only 2 sent total won't be ghost (needs 3+ sent for ghost)
        # Actually 3 unopened and 3 sent would be ghost. Let's do 3 unopened + 1 opened = warm with burnout
        now = timezone.now()
        self._create_email_log(deal, opened=False, sent_at=now - timedelta(days=1))
        self._create_email_log(deal, opened=False, sent_at=now - timedelta(days=3))
        self._create_email_log(deal, opened=False, sent_at=now - timedelta(days=5))
        self._create_email_log(
            deal, opened=True, opened_at=now - timedelta(days=10),
            sent_at=now - timedelta(days=11),
        )

        self._run_task()
        deal.refresh_from_db()
        # Should have extended next_action_date by 7 days
        self.assertGreater(
            deal.next_action_date,
            timezone.now() + timedelta(days=5),
        )

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.tasks.queue_deal_email')
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_ai_send_email_triggers_queue(self, MockAgent, mock_queue, mock_hours):
        mock_agent = MockAgent.return_value
        mock_agent.analyze_deal.return_value = {
            'action': 'send_email',
            'metadata': {'email_type': 'followup'},
        }
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)

        self._run_task()
        mock_queue.delay.assert_called_once()
        args = mock_queue.delay.call_args[0]
        self.assertEqual(args[0], str(deal.id))

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_ai_wait_action(self, MockAgent, mock_hours):
        mock_agent = MockAgent.return_value
        mock_agent.analyze_deal.return_value = {
            'action': 'wait', 'metadata': {'wait_days': '5'},
        }
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)

        self._run_task()
        deal.refresh_from_db()
        self.assertGreater(
            deal.next_action_date,
            timezone.now() + timedelta(days=3),
        )

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_ai_pause_action(self, MockAgent, mock_hours):
        mock_agent = MockAgent.return_value
        mock_agent.analyze_deal.return_value = {
            'action': 'pause', 'metadata': {},
            'reasoning': 'Contact seems inactive',
        }
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)

        self._run_task()
        deal.refresh_from_db()
        self.assertEqual(deal.status, 'paused')

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_ai_flag_action(self, MockAgent, mock_hours):
        mock_agent = MockAgent.return_value
        mock_agent.analyze_deal.return_value = {
            'action': 'flag_for_review', 'metadata': {},
            'reasoning': 'Unusual pattern',
        }
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)

        self._run_task()
        deal.refresh_from_db()
        self.assertIn('Flagged for review', deal.ai_notes)

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.tasks.queue_deal_email')
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_send_time_optimization_defers(self, MockAgent, mock_queue, mock_hours):
        """When preferred_send_hour is far from current time, defer."""
        self.contact.preferred_send_hour = 3  # 3 AM — always far from business hours
        self.contact.save(update_fields=['preferred_send_hour'])
        mock_agent = MockAgent.return_value
        mock_agent.analyze_deal.return_value = {
            'action': 'send_email', 'metadata': {'email_type': 'followup'},
        }
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)

        self._run_task()
        # Should NOT call queue_deal_email because it deferred
        mock_queue.delay.assert_not_called()
        deal.refresh_from_db()
        self.assertIsNotNone(deal.next_action_date)

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_skips_paused_deals(self, MockAgent, mock_hours):
        deal = self._create_deal(
            self.contact, self.pipeline, self.stage1, autopilot_paused=True,
        )
        result = self._run_task()
        # Paused deals are filtered out by the query
        mock_agent = MockAgent.return_value
        mock_agent.analyze_deal.assert_not_called()

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_skips_future_deals(self, MockAgent, mock_hours):
        deal = self._create_deal(
            self.contact, self.pipeline, self.stage1,
            next_action_date=timezone.now() + timedelta(days=5),
        )
        self._run_task()
        mock_agent = MockAgent.return_value
        mock_agent.analyze_deal.assert_not_called()

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_updates_engagement_tier(self, MockAgent, mock_hours):
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        # 2 sent, 0 opens → cold
        self._create_email_log(deal, opened=False)
        self._create_email_log(deal, opened=False)
        mock_agent = MockAgent.return_value
        mock_agent.analyze_deal.return_value = {
            'action': 'wait', 'metadata': {'wait_days': '3'},
        }

        self._run_task()
        deal.refresh_from_db()
        self.assertEqual(deal.engagement_tier, 'cold')


# =============================================================================
# queue_deal_email
# =============================================================================


class TestQueueDealEmail(CRMTestCase):
    """Test the queue_deal_email Celery task."""

    def setUp(self):
        self.brand = self._create_brand(slug='testbrand', name='Test Brand')
        self.pipeline = self._create_pipeline(self.brand)
        self.stage1 = self._create_stage(self.pipeline, 'Invited', 0)
        self.stage2 = self._create_stage(self.pipeline, 'Follow Up 1', 1)
        self.stage3 = self._create_stage(self.pipeline, 'Follow Up 2', 2)
        self.stage_terminal = self._create_stage(
            self.pipeline, 'Won', 3, is_terminal=True,
        )
        self.contact = self._create_contact(self.brand, email='queue@test.com')

    def _mock_email_service(self, success=True, is_hard_bounce=False):
        mock_service = MagicMock()
        mock_service.enabled = True
        if success:
            mock_service.send.return_value = {
                'success': True, 'message_id': 'msg-123',
            }
        else:
            mock_service.send.return_value = {
                'success': False, 'error': 'Send failed',
                'is_hard_bounce': is_hard_bounce,
            }
        return mock_service

    @patch('crm.tasks.is_office_hours', return_value=True)
    def _run_task(self, deal_id, mock_hours, email_type='followup', ab_variant='', **mock_patches):
        from crm.tasks import queue_deal_email
        return queue_deal_email(deal_id, email_type, ab_variant=ab_variant)

    # --- Blocking checks ---

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    def test_blocks_unsubscribed_contact(self, mock_get_svc, mock_hours):
        self.contact.is_unsubscribed = True
        self.contact.save(update_fields=['is_unsubscribed'])
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        from crm.tasks import queue_deal_email
        result = queue_deal_email(str(deal.id))
        self.assertFalse(result['success'])
        self.assertIn('unsubscribed', result['error'])

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    def test_blocks_bounced_contact(self, mock_get_svc, mock_hours):
        self.contact.email_bounced = True
        self.contact.save(update_fields=['email_bounced'])
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        from crm.tasks import queue_deal_email
        result = queue_deal_email(str(deal.id))
        self.assertFalse(result['success'])
        self.assertIn('bounced', result['error'])

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    def test_blocks_spam_reported_contact(self, mock_get_svc, mock_hours):
        self.contact.spam_reported = True
        self.contact.save(update_fields=['spam_reported'])
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        from crm.tasks import queue_deal_email
        result = queue_deal_email(str(deal.id))
        self.assertFalse(result['success'])
        self.assertIn('spam', result['error'])

    @patch('crm.tasks.is_office_hours', return_value=True)
    def test_deal_not_found(self, mock_hours):
        from crm.tasks import queue_deal_email
        result = queue_deal_email('00000000-0000-0000-0000-000000000000')
        self.assertFalse(result['success'])
        self.assertIn('not found', result['error'])

    # --- Cross-brand cooldown ---

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    def test_cross_brand_cooldown_defers(self, mock_get_svc, mock_hours):
        """If contact was emailed by another brand today, defer to tomorrow."""
        other_brand = self._create_brand(slug='other', name='Other')
        other_pipeline = self._create_pipeline(other_brand, name='Other Pipeline')
        other_stage = self._create_stage(other_pipeline, 'Stage', 0)
        other_contact = self._create_contact(
            other_brand, email='queue@test.com',
        )
        other_deal = self._create_deal(other_contact, other_pipeline, other_stage)
        # Log sent from other brand today
        self._create_email_log(
            other_deal, to_email='queue@test.com', sent_at=timezone.now(),
        )

        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        from crm.tasks import queue_deal_email
        result = queue_deal_email(str(deal.id))
        self.assertFalse(result['success'])
        self.assertIn('cooldown', result['error'])

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    @patch('crm.services.email_templates.get_template_for_email', return_value=None)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_same_brand_today_ok(self, MockAgent, mock_template, mock_get_svc, mock_hours):
        """Same brand can email again same day (no cross-brand cooldown)."""
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        # Log sent from same brand today
        self._create_email_log(
            deal, to_email='queue@test.com', sent_at=timezone.now(),
        )

        mock_svc = self._mock_email_service()
        mock_get_svc.return_value = mock_svc
        mock_agent = MockAgent.return_value
        mock_agent.compose_email.return_value = {
            'success': True, 'subject': 'Test', 'body': 'Body',
        }

        from crm.tasks import queue_deal_email
        result = queue_deal_email(str(deal.id))
        self.assertTrue(result['success'])

    # --- Successful send ---

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    @patch('crm.services.email_templates.get_template_for_email', return_value=None)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_successful_send_updates_deal(self, MockAgent, mock_template, mock_get_svc, mock_hours):
        deal = self._create_deal(
            self.contact, self.pipeline, self.stage1, emails_sent=0,
        )
        mock_svc = self._mock_email_service()
        mock_get_svc.return_value = mock_svc
        mock_agent = MockAgent.return_value
        mock_agent.compose_email.return_value = {
            'success': True, 'subject': 'Hey', 'body': 'Content',
        }

        from crm.tasks import queue_deal_email
        result = queue_deal_email(str(deal.id))
        self.assertTrue(result['success'])

        deal.refresh_from_db()
        self.assertEqual(deal.emails_sent, 1)
        self.assertIsNotNone(deal.last_contact_date)
        self.assertIsNotNone(deal.next_action_date)

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    @patch('crm.services.email_templates.get_template_for_email', return_value=None)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_smart_interval_engaged(self, MockAgent, mock_template, mock_get_svc, mock_hours):
        """Engaged tier should get 2-day follow-up interval."""
        # Use stage3 so next stage is terminal (no auto-advance to overwrite interval)
        deal = self._create_deal(
            self.contact, self.pipeline, self.stage3,
            engagement_tier='engaged',
        )
        mock_svc = self._mock_email_service()
        mock_get_svc.return_value = mock_svc
        mock_agent = MockAgent.return_value
        mock_agent.compose_email.return_value = {
            'success': True, 'subject': 'Hey', 'body': 'Body',
        }

        from crm.tasks import queue_deal_email
        queue_deal_email(str(deal.id))
        deal.refresh_from_db()
        # 2-day interval for engaged
        expected_min = timezone.now() + timedelta(days=1, hours=12)
        expected_max = timezone.now() + timedelta(days=2, hours=1)
        self.assertGreater(deal.next_action_date, expected_min)
        self.assertLess(deal.next_action_date, expected_max)

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    @patch('crm.services.email_templates.get_template_for_email', return_value=None)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_smart_interval_cold(self, MockAgent, mock_template, mock_get_svc, mock_hours):
        """Cold tier should get 7-day follow-up interval."""
        # Use stage3 so next stage is terminal (no auto-advance to overwrite interval)
        deal = self._create_deal(
            self.contact, self.pipeline, self.stage3,
            engagement_tier='cold',
        )
        mock_svc = self._mock_email_service()
        mock_get_svc.return_value = mock_svc
        mock_agent = MockAgent.return_value
        mock_agent.compose_email.return_value = {
            'success': True, 'subject': 'Hey', 'body': 'Body',
        }

        from crm.tasks import queue_deal_email
        queue_deal_email(str(deal.id))
        deal.refresh_from_db()
        expected_min = timezone.now() + timedelta(days=6)
        self.assertGreater(deal.next_action_date, expected_min)

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    @patch('crm.services.email_templates.get_template_for_email', return_value=None)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_fallback_to_stage_default_interval(self, MockAgent, mock_template, mock_get_svc, mock_hours):
        """Unknown tier falls back to stage's days_until_followup."""
        # Use stage3 so next stage is terminal (no auto-advance to overwrite interval)
        deal = self._create_deal(
            self.contact, self.pipeline, self.stage3,
            engagement_tier='',  # Unknown
        )
        mock_svc = self._mock_email_service()
        mock_get_svc.return_value = mock_svc
        mock_agent = MockAgent.return_value
        mock_agent.compose_email.return_value = {
            'success': True, 'subject': 'Hi', 'body': 'Body',
        }

        from crm.tasks import queue_deal_email
        queue_deal_email(str(deal.id))
        deal.refresh_from_db()
        # stage3 has days_until_followup=3 (default from _create_stage)
        expected_min = timezone.now() + timedelta(days=2)
        expected_max = timezone.now() + timedelta(days=4)
        self.assertGreater(deal.next_action_date, expected_min)
        self.assertLess(deal.next_action_date, expected_max)

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    @patch('crm.services.email_templates.get_template_for_email', return_value=None)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_ab_variant_b_uses_subject_variant(self, MockAgent, mock_template, mock_get_svc, mock_hours):
        """Variant B should use stage's subject_variant_b."""
        self.stage1.subject_variant_b = 'Alt Subject Line'
        self.stage1.save(update_fields=['subject_variant_b'])
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)

        mock_svc = self._mock_email_service()
        mock_get_svc.return_value = mock_svc
        mock_agent = MockAgent.return_value
        mock_agent.compose_email.return_value = {
            'success': True, 'subject': 'Original Subject', 'body': 'Body',
        }

        from crm.tasks import queue_deal_email
        queue_deal_email(str(deal.id), ab_variant='B')
        # Check the email log was created with variant B subject
        email_log = EmailLog.objects.filter(deal=deal).first()
        self.assertEqual(email_log.subject, 'Alt Subject Line')
        self.assertEqual(email_log.ab_variant, 'B')

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    @patch('crm.services.email_templates.get_template_for_email', return_value=None)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_creates_email_log_and_activity(self, MockAgent, mock_template, mock_get_svc, mock_hours):
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        mock_svc = self._mock_email_service()
        mock_get_svc.return_value = mock_svc
        mock_agent = MockAgent.return_value
        mock_agent.compose_email.return_value = {
            'success': True, 'subject': 'Subject', 'body': 'Body',
        }

        from crm.tasks import queue_deal_email
        queue_deal_email(str(deal.id))
        self.assertTrue(EmailLog.objects.filter(deal=deal, sent_at__isnull=False).exists())
        self.assertTrue(
            DealActivity.objects.filter(deal=deal, activity_type='email_sent').exists()
        )

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    @patch('crm.services.email_templates.get_template_for_email', return_value=None)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_auto_advances_to_followup_stage(self, MockAgent, mock_template, mock_get_svc, mock_hours):
        """After sending email, should advance to next Follow Up stage."""
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        mock_svc = self._mock_email_service()
        mock_get_svc.return_value = mock_svc
        mock_agent = MockAgent.return_value
        mock_agent.compose_email.return_value = {
            'success': True, 'subject': 'Hey', 'body': 'Body',
        }

        from crm.tasks import queue_deal_email
        queue_deal_email(str(deal.id))
        deal.refresh_from_db()
        self.assertEqual(deal.current_stage, self.stage2)

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    @patch('crm.services.email_templates.get_template_for_email', return_value=None)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_does_not_advance_to_terminal(self, MockAgent, mock_template, mock_get_svc, mock_hours):
        """Should not auto-advance into terminal stages."""
        deal = self._create_deal(self.contact, self.pipeline, self.stage3)
        mock_svc = self._mock_email_service()
        mock_get_svc.return_value = mock_svc
        mock_agent = MockAgent.return_value
        mock_agent.compose_email.return_value = {
            'success': True, 'subject': 'Hey', 'body': 'Body',
        }

        from crm.tasks import queue_deal_email
        queue_deal_email(str(deal.id))
        deal.refresh_from_db()
        # Should stay at stage3 since next stage (Won) is terminal
        self.assertEqual(deal.current_stage, self.stage3)

    # --- Hard bounce on send ---

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    @patch('crm.services.email_templates.get_template_for_email', return_value=None)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_hard_bounce_marks_contact_and_closes_deal(self, MockAgent, mock_template, mock_get_svc, mock_hours):
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        mock_svc = self._mock_email_service(success=False, is_hard_bounce=True)
        mock_get_svc.return_value = mock_svc
        mock_agent = MockAgent.return_value
        mock_agent.compose_email.return_value = {
            'success': True, 'subject': 'Hey', 'body': 'Body',
        }

        from crm.tasks import queue_deal_email
        result = queue_deal_email(str(deal.id))
        self.assertFalse(result['success'])
        self.assertTrue(result.get('hard_bounce'))

        self.contact.refresh_from_db()
        self.assertTrue(self.contact.email_bounced)
        deal.refresh_from_db()
        self.assertEqual(deal.status, 'lost')
        self.assertEqual(deal.lost_reason, 'invalid_email')

    @patch('crm.tasks.is_office_hours', return_value=True)
    @patch('crm.services.email_service.get_email_service')
    @patch('crm.services.email_templates.get_template_for_email', return_value=None)
    @patch('crm.services.ai_agent.CRMAIAgent')
    def test_hard_bounce_closes_other_active_deals(self, MockAgent, mock_template, mock_get_svc, mock_hours):
        """Hard bounce should also close other active deals for same contact."""
        deal1 = self._create_deal(self.contact, self.pipeline, self.stage1)
        other_pipeline = self._create_pipeline(
            self.brand, name='Other Pipeline', pipeline_type='backlink',
        )
        other_stage = self._create_stage(other_pipeline, 'Stage', 0)
        deal2 = self._create_deal(self.contact, other_pipeline, other_stage)

        mock_svc = self._mock_email_service(success=False, is_hard_bounce=True)
        mock_get_svc.return_value = mock_svc
        mock_agent = MockAgent.return_value
        mock_agent.compose_email.return_value = {
            'success': True, 'subject': 'Hey', 'body': 'Body',
        }

        from crm.tasks import queue_deal_email
        queue_deal_email(str(deal1.id))
        deal2.refresh_from_db()
        self.assertEqual(deal2.status, 'lost')
        self.assertEqual(deal2.lost_reason, 'invalid_email')


# =============================================================================
# check_email_replies
# =============================================================================


class TestCheckEmailReplies(CRMTestCase):
    """Test the check_email_replies Celery task."""

    def setUp(self):
        self.brand = self._create_brand()
        self.pipeline = self._create_pipeline(self.brand)
        self.stage1 = self._create_stage(self.pipeline, 'Follow Up 1', 0)
        self.interested_stage = self._create_stage(
            self.pipeline, 'Interested', 1,
        )
        self.contact = self._create_contact(self.brand, email='reply@test.com')

    @patch('crm.services.ai_agent.CRMAIAgent')
    @patch('crm.services.email_service.get_email_service')
    def _run_task(self, mock_get_svc, MockAgent, messages=None, classification=None):
        mock_svc = MagicMock()
        mock_svc.get_inbox_messages.return_value = messages or []
        mock_svc.match_reply_to_deal.return_value = None
        mock_svc.get_message_content.return_value = 'Reply content'
        mock_get_svc.return_value = mock_svc

        mock_agent = MockAgent.return_value
        mock_agent.classify_reply.return_value = classification or {
            'intent': 'other', 'sentiment': 'neutral', 'summary': 'Reply',
        }
        from crm.tasks import check_email_replies
        return check_email_replies(), mock_svc, mock_agent

    def test_pauses_autopilot_on_reply(self):
        deal = self._create_deal(
            self.contact, self.pipeline, self.stage1, autopilot_paused=False,
        )
        original = self._create_email_log(deal)
        mock_svc = MagicMock()
        mock_svc.get_inbox_messages.return_value = [{
            'message_id': 'new-msg-id',
            'from_email': 'reply@test.com',
            'subject': 'Re: Test Email',
            'received_at': timezone.now(),
        }]
        mock_svc.match_reply_to_deal.return_value = deal
        mock_svc.get_message_content.return_value = 'Thanks!'

        with patch('crm.services.email_service.get_email_service', return_value=mock_svc), \
             patch('crm.services.ai_agent.CRMAIAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.classify_reply.return_value = {
                'intent': 'other', 'sentiment': 'positive', 'summary': 'Thanks',
            }
            from crm.tasks import check_email_replies
            check_email_replies()

        deal.refresh_from_db()
        self.assertTrue(deal.autopilot_paused)

    def test_interested_reply_moves_stage(self):
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        self._create_email_log(deal)
        mock_svc = MagicMock()
        mock_svc.get_inbox_messages.return_value = [{
            'message_id': 'interest-msg',
            'from_email': 'reply@test.com',
            'subject': 'Re: Test',
            'received_at': timezone.now(),
        }]
        mock_svc.match_reply_to_deal.return_value = deal
        mock_svc.get_message_content.return_value = 'Very interested!'

        with patch('crm.services.email_service.get_email_service', return_value=mock_svc), \
             patch('crm.services.ai_agent.CRMAIAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.classify_reply.return_value = {
                'intent': 'interested', 'summary': 'Interested',
            }
            from crm.tasks import check_email_replies
            check_email_replies()

        deal.refresh_from_db()
        self.assertEqual(deal.current_stage, self.interested_stage)

    def test_not_interested_marks_lost(self):
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        self._create_email_log(deal)
        mock_svc = MagicMock()
        mock_svc.get_inbox_messages.return_value = [{
            'message_id': 'notinterest-msg',
            'from_email': 'reply@test.com',
            'subject': 'Re: Test',
            'received_at': timezone.now(),
        }]
        mock_svc.match_reply_to_deal.return_value = deal
        mock_svc.get_message_content.return_value = 'Not interested.'

        with patch('crm.services.email_service.get_email_service', return_value=mock_svc), \
             patch('crm.services.ai_agent.CRMAIAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.classify_reply.return_value = {
                'intent': 'not_interested', 'summary': 'Not interested',
            }
            from crm.tasks import check_email_replies
            check_email_replies()

        deal.refresh_from_db()
        self.assertEqual(deal.status, 'lost')

    def test_ooo_extends_wait(self):
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        self._create_email_log(deal)
        mock_svc = MagicMock()
        mock_svc.get_inbox_messages.return_value = [{
            'message_id': 'ooo-msg',
            'from_email': 'reply@test.com',
            'subject': 'OOO',
            'received_at': timezone.now(),
        }]
        mock_svc.match_reply_to_deal.return_value = deal
        mock_svc.get_message_content.return_value = 'Out of office'

        with patch('crm.services.email_service.get_email_service', return_value=mock_svc), \
             patch('crm.services.ai_agent.CRMAIAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.classify_reply.return_value = {
                'intent': 'out_of_office', 'summary': 'OOO',
            }
            from crm.tasks import check_email_replies
            check_email_replies()

        deal.refresh_from_db()
        expected_min = timezone.now() + timedelta(days=5)
        self.assertGreater(deal.next_action_date, expected_min)

    def test_skips_already_processed(self):
        """Messages with existing zoho_message_id should be skipped."""
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        self._create_email_log(deal, zoho_message_id='already-seen')
        mock_svc = MagicMock()
        mock_svc.get_inbox_messages.return_value = [{
            'message_id': 'already-seen',
            'from_email': 'reply@test.com',
            'subject': 'Re: test',
            'received_at': timezone.now(),
        }]
        mock_svc.match_reply_to_deal.return_value = deal

        with patch('crm.services.email_service.get_email_service', return_value=mock_svc), \
             patch('crm.services.ai_agent.CRMAIAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            from crm.tasks import check_email_replies
            result = check_email_replies()

        # Should not have called classify_reply since message was already processed
        mock_agent.classify_reply.assert_not_called()

    def test_marks_original_email_replied(self):
        deal = self._create_deal(self.contact, self.pipeline, self.stage1)
        original = self._create_email_log(deal)
        mock_svc = MagicMock()
        mock_svc.get_inbox_messages.return_value = [{
            'message_id': 'mark-replied-msg',
            'from_email': 'reply@test.com',
            'subject': 'Re: Test Email',
            'received_at': timezone.now(),
        }]
        mock_svc.match_reply_to_deal.return_value = deal
        mock_svc.get_message_content.return_value = 'Reply!'

        with patch('crm.services.email_service.get_email_service', return_value=mock_svc), \
             patch('crm.services.ai_agent.CRMAIAgent') as MockAgent:
            mock_agent = MockAgent.return_value
            mock_agent.classify_reply.return_value = {
                'intent': 'other', 'summary': 'Reply',
            }
            from crm.tasks import check_email_replies
            check_email_replies()

        original.refresh_from_db()
        self.assertTrue(original.replied)


# =============================================================================
# attempt_re_engagement
# =============================================================================


class TestAttemptReEngagement(CRMTestCase):
    """Test the attempt_re_engagement Celery task."""

    def setUp(self):
        self.brand = self._create_brand()
        self.pipeline = self._create_pipeline(self.brand)
        self.stage1 = self._create_stage(self.pipeline, 'Stage 1', 0)
        self.stage_ni = self._create_stage(
            self.pipeline, 'Not Interested', 1, is_terminal=True,
        )
        self.contact = self._create_contact(self.brand, email='reengage@test.com')

    def _create_lost_deal(self, **kwargs):
        defaults = {
            'status': 'lost',
            'lost_reason': 'no_response',
            're_engagement_attempted': False,
        }
        defaults.update(kwargs)
        deal = self._create_deal(self.contact, self.pipeline, self.stage_ni, **defaults)
        # Set updated_at to 31 days ago
        Deal.objects.filter(id=deal.id).update(
            updated_at=timezone.now() - timedelta(days=31),
        )
        deal.refresh_from_db()
        return deal

    @patch('crm.tasks.queue_deal_email')
    def test_reactivates_eligible_deal(self, mock_queue):
        deal = self._create_lost_deal()
        from crm.tasks import attempt_re_engagement
        result = attempt_re_engagement()
        deal.refresh_from_db()
        self.assertEqual(deal.status, 'active')
        self.assertTrue(deal.re_engagement_attempted)
        self.assertEqual(deal.current_stage, self.stage1)
        self.assertEqual(result['reactivated'], 1)

    @patch('crm.tasks.queue_deal_email')
    def test_sets_re_engagement_attempted(self, mock_queue):
        deal = self._create_lost_deal()
        from crm.tasks import attempt_re_engagement
        attempt_re_engagement()
        deal.refresh_from_db()
        self.assertTrue(deal.re_engagement_attempted)

    @patch('crm.tasks.queue_deal_email')
    def test_skips_bounced_contact(self, mock_queue):
        self.contact.email_bounced = True
        self.contact.save(update_fields=['email_bounced'])
        deal = self._create_lost_deal()
        from crm.tasks import attempt_re_engagement
        result = attempt_re_engagement()
        self.assertEqual(result['reactivated'], 0)

    @patch('crm.tasks.queue_deal_email')
    def test_skips_unsubscribed_contact(self, mock_queue):
        self.contact.is_unsubscribed = True
        self.contact.save(update_fields=['is_unsubscribed'])
        deal = self._create_lost_deal()
        from crm.tasks import attempt_re_engagement
        result = attempt_re_engagement()
        self.assertEqual(result['reactivated'], 0)

    @patch('crm.tasks.queue_deal_email')
    def test_skips_spam_reported_contact(self, mock_queue):
        self.contact.spam_reported = True
        self.contact.save(update_fields=['spam_reported'])
        deal = self._create_lost_deal()
        from crm.tasks import attempt_re_engagement
        result = attempt_re_engagement()
        self.assertEqual(result['reactivated'], 0)

    @patch('crm.tasks.queue_deal_email')
    def test_skips_already_attempted(self, mock_queue):
        deal = self._create_lost_deal(re_engagement_attempted=True)
        from crm.tasks import attempt_re_engagement
        result = attempt_re_engagement()
        self.assertEqual(result['reactivated'], 0)

    @patch('crm.tasks.queue_deal_email')
    def test_skips_recent_lost_deal(self, mock_queue):
        """Deals lost < 30 days ago should not be re-engaged."""
        deal = self._create_deal(
            self.contact, self.pipeline, self.stage_ni,
            status='lost', lost_reason='no_response',
            re_engagement_attempted=False,
        )
        # updated_at is auto-set to now, which is < 30 days ago
        from crm.tasks import attempt_re_engagement
        result = attempt_re_engagement()
        self.assertEqual(result['reactivated'], 0)

    @patch('crm.tasks.queue_deal_email')
    def test_skips_brand_unsubscribed_contact(self, mock_queue):
        self.contact.unsubscribed_brands = ['testbrand']
        self.contact.save(update_fields=['unsubscribed_brands'])
        deal = self._create_lost_deal()
        from crm.tasks import attempt_re_engagement
        result = attempt_re_engagement()
        self.assertEqual(result['reactivated'], 0)

    @patch('crm.tasks.queue_deal_email')
    def test_moves_to_first_stage(self, mock_queue):
        deal = self._create_lost_deal()
        from crm.tasks import attempt_re_engagement
        attempt_re_engagement()
        deal.refresh_from_db()
        self.assertEqual(deal.current_stage, self.stage1)

    @patch('crm.tasks.queue_deal_email')
    def test_max_20_per_run(self, mock_queue):
        """Should only reactivate up to 20 deals per run."""
        contacts = []
        for i in range(25):
            c = self._create_contact(self.brand, email=f'reengage{i}@test.com')
            contacts.append(c)
        for c in contacts:
            deal = self._create_deal(
                c, self.pipeline, self.stage_ni,
                status='lost', lost_reason='no_response',
                re_engagement_attempted=False,
            )
            Deal.objects.filter(id=deal.id).update(
                updated_at=timezone.now() - timedelta(days=31),
            )
        from crm.tasks import attempt_re_engagement
        result = attempt_re_engagement()
        self.assertLessEqual(result['reactivated'], 20)

    @patch('crm.tasks.queue_deal_email')
    def test_queues_followup_email(self, mock_queue):
        deal = self._create_lost_deal()
        from crm.tasks import attempt_re_engagement
        attempt_re_engagement()
        mock_queue.delay.assert_called_once_with(str(deal.id), 'followup')

    @patch('crm.tasks.queue_deal_email')
    def test_creates_activity(self, mock_queue):
        deal = self._create_lost_deal()
        from crm.tasks import attempt_re_engagement
        attempt_re_engagement()
        self.assertTrue(
            DealActivity.objects.filter(
                deal=deal, description__icontains='Re-engagement',
            ).exists()
        )


# =============================================================================
# send_weekly_report
# =============================================================================


class TestSendWeeklyReport(CRMTestCase):
    """Test the send_weekly_report Celery task."""

    @patch('crm.services.email_service.get_email_service')
    def test_sends_email(self, mock_get_svc):
        brand = self._create_brand()
        mock_svc = MagicMock()
        mock_svc.send.return_value = {'success': True}
        mock_get_svc.return_value = mock_svc

        from crm.tasks import send_weekly_report
        result = send_weekly_report()
        self.assertTrue(result['success'])
        mock_svc.send.assert_called_once()

    @patch('crm.services.email_service.get_email_service')
    def test_includes_per_brand_stats(self, mock_get_svc):
        brand = self._create_brand()
        pipeline = self._create_pipeline(brand)
        stage = self._create_stage(pipeline)
        contact = self._create_contact(brand, email='report@test.com')
        deal = self._create_deal(contact, pipeline, stage)
        self._create_email_log(deal, to_email='report@test.com')

        mock_svc = MagicMock()
        mock_svc.send.return_value = {'success': True}
        mock_get_svc.return_value = mock_svc

        from crm.tasks import send_weekly_report
        send_weekly_report()
        call_kwargs = mock_svc.send.call_args
        body = call_kwargs[1].get('body', '') if call_kwargs[1] else call_kwargs[0][2]
        self.assertIn(brand.name, body)

    @patch('crm.services.email_service.get_email_service')
    def test_handles_zero_emails_no_div_by_zero(self, mock_get_svc):
        """When no emails sent, should not crash with division by zero."""
        brand = self._create_brand()
        mock_svc = MagicMock()
        mock_svc.send.return_value = {'success': True}
        mock_get_svc.return_value = mock_svc

        from crm.tasks import send_weekly_report
        # Should not raise any exceptions
        result = send_weekly_report()
        self.assertTrue(result['success'])


# =============================================================================
# autopilot_engagement_scan
# =============================================================================


class TestAutopilotEngagementScan(CRMTestCase):
    """Test the autopilot_engagement_scan Celery task."""

    def setUp(self):
        self.brand = self._create_brand()
        self.pipeline = self._create_pipeline(self.brand)
        self.stage = self._create_stage(self.pipeline)
        self.contact = self._create_contact(self.brand, email='scan@test.com')

    def test_updates_engagement_tier(self):
        deal = self._create_deal(self.contact, self.pipeline, self.stage)
        # Create email history that would make the tier "cold"
        self._create_email_log(deal, opened=False)
        self._create_email_log(deal, opened=False)

        from crm.tasks import autopilot_engagement_scan
        stats = autopilot_engagement_scan()
        deal.refresh_from_db()
        self.assertEqual(deal.engagement_tier, 'cold')
        self.assertGreater(stats['total'], 0)

    def test_updates_preferred_send_hour(self):
        deal = self._create_deal(self.contact, self.pipeline, self.stage)
        now = timezone.now()
        # Create 3+ opens at hour 14
        for i in range(3):
            self._create_email_log(
                deal,
                to_email=self.contact.email,
                opened=True,
                opened_at=now.replace(hour=14, minute=0) - timedelta(days=i),
            )

        from crm.tasks import autopilot_engagement_scan
        autopilot_engagement_scan()
        self.contact.refresh_from_db()
        self.assertIsNotNone(self.contact.preferred_send_hour)

    def test_returns_stats_dict(self):
        deal = self._create_deal(self.contact, self.pipeline, self.stage)
        from crm.tasks import autopilot_engagement_scan
        stats = autopilot_engagement_scan()
        self.assertIn('total', stats)
        self.assertIn('updated', stats)
        self.assertIn('ghosts', stats)
        self.assertIn('burnout', stats)
        self.assertIn('hot', stats)
