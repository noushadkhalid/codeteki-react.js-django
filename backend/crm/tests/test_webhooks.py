import json

from django.test import override_settings
from django.utils import timezone

from .helpers import CRMTestCase
from crm.models import Contact, Deal, DealActivity, EmailLog, Pipeline, PipelineStage


# =============================================================================
# DesiFirmsWebhookView
# =============================================================================


class TestDesiFirmsWebhookAuth(CRMTestCase):
    """Test DesiFirms webhook authentication."""

    URL = '/api/crm/webhooks/desifirms/'

    def _post(self, data, auth=None):
        headers = {}
        if auth is not None:
            headers['HTTP_AUTHORIZATION'] = auth
        return self.client.post(
            self.URL, json.dumps(data), content_type='application/json', **headers,
        )

    @override_settings(DESIFIRMS_WEBHOOK_KEY='secret-key')
    def test_missing_key_returns_401(self):
        resp = self._post({'event_type': 'user_registered', 'email': 't@t.com'})
        self.assertEqual(resp.status_code, 401)

    @override_settings(DESIFIRMS_WEBHOOK_KEY='secret-key')
    def test_wrong_key_returns_401(self):
        resp = self._post(
            {'event_type': 'user_registered', 'email': 't@t.com'},
            auth='wrong-key',
        )
        self.assertEqual(resp.status_code, 401)

    @override_settings(DESIFIRMS_WEBHOOK_KEY='secret-key')
    def test_valid_key_passes(self):
        # No brand configured, but auth should pass (500 from missing brand)
        self._create_brand(slug='desifirms', name='Desi Firms')
        resp = self._post(
            {'event_type': 'user_registered', 'email': 'test@test.com'},
            auth='secret-key',
        )
        self.assertNotEqual(resp.status_code, 401)

    @override_settings(DESIFIRMS_WEBHOOK_KEY='')
    def test_empty_setting_passes_without_auth(self):
        self._create_brand(slug='desifirms', name='Desi Firms')
        resp = self._post(
            {'event_type': 'user_registered', 'email': 'test@test.com'},
        )
        self.assertNotEqual(resp.status_code, 401)


class TestDesiFirmsWebhookValidation(CRMTestCase):
    """Test DesiFirms webhook input validation."""

    URL = '/api/crm/webhooks/desifirms/'

    def _post(self, data=None, raw=None):
        body = raw if raw is not None else json.dumps(data)
        return self.client.post(self.URL, body, content_type='application/json')

    def test_invalid_json(self):
        resp = self._post(raw='not json')
        self.assertEqual(resp.status_code, 400)

    def test_missing_email(self):
        resp = self._post({'event_type': 'user_registered'})
        self.assertEqual(resp.status_code, 400)

    def test_missing_event_type(self):
        resp = self._post({'email': 'test@test.com'})
        self.assertEqual(resp.status_code, 400)

    def test_no_brand_returns_500(self):
        # No desifirms brand exists
        resp = self._post({'event_type': 'user_registered', 'email': 't@t.com'})
        self.assertEqual(resp.status_code, 500)


class TestDesiFirmsWebhookRegistration(CRMTestCase):
    """Test DesiFirms user_registered event handling."""

    URL = '/api/crm/webhooks/desifirms/'

    def setUp(self):
        self.brand = self._create_brand(slug='desifirms', name='Desi Firms')
        self.pipeline = self._create_pipeline(
            self.brand, name='Registered Users - Business',
            pipeline_type='registered_users',
        )
        self.stage1 = self._create_stage(self.pipeline, 'New Registration', 0)
        self.stage2 = self._create_stage(self.pipeline, 'Nudge 1', 1)

    def _post(self, data):
        return self.client.post(
            self.URL, json.dumps(data), content_type='application/json',
        )

    def test_creates_contact_and_deal(self):
        resp = self._post({
            'event_type': 'user_registered',
            'email': 'newuser@test.com',
            'pipeline_hint': 'business',
        })
        self.assertIn(resp.status_code, [200, 201])
        self.assertTrue(
            Contact.objects.filter(email='newuser@test.com', brand=self.brand).exists()
        )
        self.assertTrue(
            Deal.objects.filter(
                contact__email='newuser@test.com', pipeline=self.pipeline,
            ).exists()
        )

    def test_with_name_and_phone(self):
        resp = self._post({
            'event_type': 'user_registered',
            'email': 'named@test.com',
            'name': 'Rajesh Kumar',
            'phone': '0412345678',
            'pipeline_hint': 'business',
        })
        self.assertIn(resp.status_code, [200, 201])
        contact = Contact.objects.get(email='named@test.com', brand=self.brand)
        self.assertEqual(contact.name, 'Rajesh Kumar')
        deal = Deal.objects.get(contact=contact)
        self.assertIn('0412345678', deal.ai_notes)

    def test_existing_outreach_deal_advances_stage(self):
        """If contact already has an active deal, advance to Signed Up."""
        outreach_pipeline = self._create_pipeline(
            self.brand, name='Business Listings', pipeline_type='business',
        )
        invite_stage = self._create_stage(outreach_pipeline, 'Invited', 0)
        signed_up_stage = self._create_stage(outreach_pipeline, 'Signed Up', 1)
        contact = self._create_contact(
            self.brand, email='existing@test.com',
        )
        deal = self._create_deal(contact, outreach_pipeline, invite_stage)

        resp = self._post({
            'event_type': 'user_registered',
            'email': 'existing@test.com',
        })
        self.assertEqual(resp.status_code, 200)
        deal.refresh_from_db()
        self.assertEqual(deal.current_stage, signed_up_stage)

    def test_existing_deal_pauses_autopilot(self):
        outreach_pipeline = self._create_pipeline(
            self.brand, name='Business Listings', pipeline_type='business',
        )
        invite_stage = self._create_stage(outreach_pipeline, 'Invited', 0)
        signed_up_stage = self._create_stage(outreach_pipeline, 'Signed Up', 1)
        contact = self._create_contact(self.brand, email='pause@test.com')
        deal = self._create_deal(
            contact, outreach_pipeline, invite_stage, autopilot_paused=False,
        )

        self._post({
            'event_type': 'user_registered', 'email': 'pause@test.com',
        })
        deal.refresh_from_db()
        self.assertTrue(deal.autopilot_paused)

    def test_idempotent_no_duplicate_deals(self):
        """Second registration for same email doesn't create duplicate deal."""
        self._post({
            'event_type': 'user_registered',
            'email': 'idem@test.com',
            'pipeline_hint': 'business',
        })
        self._post({
            'event_type': 'user_registered',
            'email': 'idem@test.com',
            'pipeline_hint': 'business',
        })
        self.assertEqual(
            Deal.objects.filter(contact__email='idem@test.com').count(), 1,
        )

    def test_creates_activity(self):
        self._post({
            'event_type': 'user_registered',
            'email': 'activity@test.com',
            'pipeline_hint': 'business',
        })
        deal = Deal.objects.get(contact__email='activity@test.com')
        self.assertTrue(deal.activities.exists())

    def test_no_pipeline_returns_contact_created(self):
        """If no matching pipeline, still creates contact but no deal."""
        # Delete the pipeline
        self.pipeline.delete()
        resp = self._post({
            'event_type': 'user_registered',
            'email': 'nopipe@test.com',
            'pipeline_hint': 'business',
        })
        data = resp.json()
        self.assertEqual(data['status'], 'contact_created')
        self.assertTrue(
            Contact.objects.filter(email='nopipe@test.com').exists()
        )

    def test_pipeline_hint_routing(self):
        """pipeline_hint='events' routes to events pipeline."""
        events_pipeline = self._create_pipeline(
            self.brand, name='Registered Users - Events',
            pipeline_type='registered_users',
        )
        events_stage = self._create_stage(events_pipeline, 'New', 0)

        self._post({
            'event_type': 'user_registered',
            'email': 'eventer@test.com',
            'pipeline_hint': 'events',
        })
        deal = Deal.objects.get(contact__email='eventer@test.com')
        self.assertEqual(deal.pipeline, events_pipeline)


class TestDesiFirmsWebhookProgress(CRMTestCase):
    """Test DesiFirms progress events (business_created, approved, etc.)."""

    URL = '/api/crm/webhooks/desifirms/'

    def setUp(self):
        self.brand = self._create_brand(slug='desifirms', name='Desi Firms')
        # Nudge pipeline with stages
        self.pipeline = self._create_pipeline(
            self.brand, name='Registered Users - Business',
            pipeline_type='registered_users',
        )
        self.stage_new = self._create_stage(self.pipeline, 'New Registration', 0)
        self.stage_listed = self._create_stage(self.pipeline, 'Listed', 1)

    def _post(self, data):
        return self.client.post(
            self.URL, json.dumps(data), content_type='application/json',
        )

    def _setup_contact_with_deal(self, email='progress@test.com'):
        contact = self._create_contact(self.brand, email=email)
        deal = self._create_deal(contact, self.pipeline, self.stage_new)
        return contact, deal

    def test_business_created_advances_stage(self):
        contact, deal = self._setup_contact_with_deal()
        self._post({
            'event_type': 'business_created',
            'email': contact.email,
            'detail': 'Test Business',
        })
        deal.refresh_from_db()
        self.assertEqual(deal.current_stage, self.stage_listed)

    def test_business_approved_marks_won(self):
        contact, deal = self._setup_contact_with_deal('approved@test.com')
        self._post({
            'event_type': 'business_approved',
            'email': 'approved@test.com',
            'detail': 'Approved Biz',
        })
        deal.refresh_from_db()
        self.assertEqual(deal.status, 'won')

    def test_event_created_with_events_pipeline(self):
        events_pipeline = self._create_pipeline(
            self.brand, name='Registered Users - Events',
            pipeline_type='registered_users',
        )
        stage_new = self._create_stage(events_pipeline, 'New', 0)
        stage_posted = self._create_stage(events_pipeline, 'Event Posted', 1)
        contact = self._create_contact(self.brand, email='eventer@test.com')
        deal = self._create_deal(contact, events_pipeline, stage_new)

        self._post({
            'event_type': 'event_created',
            'email': 'eventer@test.com',
        })
        deal.refresh_from_db()
        self.assertEqual(deal.current_stage, stage_posted)

    def test_event_approved_marks_won(self):
        events_pipeline = self._create_pipeline(
            self.brand, name='Registered Users - Events',
            pipeline_type='registered_users',
        )
        stage_new = self._create_stage(events_pipeline, 'New', 0)
        stage_posted = self._create_stage(events_pipeline, 'Event Posted', 1)
        contact = self._create_contact(self.brand, email='eventapproved@test.com')
        deal = self._create_deal(contact, events_pipeline, stage_new)

        self._post({
            'event_type': 'event_approved',
            'email': 'eventapproved@test.com',
        })
        deal.refresh_from_db()
        self.assertEqual(deal.status, 'won')

    def test_agent_created_in_realestate_pipeline(self):
        re_pipeline = self._create_pipeline(
            self.brand, name='Desi Firms Agents & Agencies',
            pipeline_type='realestate',
        )
        stage_new = self._create_stage(re_pipeline, 'New Lead', 0)
        stage_profile = self._create_stage(re_pipeline, 'Profile Complete', 1)
        contact = self._create_contact(self.brand, email='agent@test.com')
        deal = self._create_deal(contact, re_pipeline, stage_new)

        self._post({
            'event_type': 'agent_created',
            'email': 'agent@test.com',
        })
        deal.refresh_from_db()
        self.assertEqual(deal.current_stage, stage_profile)

    def test_property_approved_marks_won(self):
        re_pipeline = self._create_pipeline(
            self.brand, name='Desi Firms Agents & Agencies',
            pipeline_type='realestate',
        )
        stage_new = self._create_stage(re_pipeline, 'New Lead', 0)
        stage_lister = self._create_stage(re_pipeline, 'Active Lister', 1)
        contact = self._create_contact(self.brand, email='property@test.com')
        deal = self._create_deal(contact, re_pipeline, stage_new)

        self._post({
            'event_type': 'property_approved',
            'email': 'property@test.com',
        })
        deal.refresh_from_db()
        self.assertEqual(deal.status, 'won')

    def test_only_advances_forward(self):
        """Should not move backward to a lower-order stage."""
        contact, deal = self._setup_contact_with_deal('forward@test.com')
        # Move deal to Listed (order=1) first
        deal.current_stage = self.stage_listed
        deal.save(update_fields=['current_stage'])

        # business_created targets "Listed" (order=1) — same stage, no move
        self._post({
            'event_type': 'business_created',
            'email': 'forward@test.com',
        })
        deal.refresh_from_db()
        self.assertEqual(deal.current_stage, self.stage_listed)

    def test_auto_creates_deal_if_none_exists(self):
        """Progress events auto-create a deal if no active deal found."""
        contact = self._create_contact(self.brand, email='nodeal@test.com')
        # No deal exists — business_created should auto-create
        self._post({
            'event_type': 'business_created',
            'email': 'nodeal@test.com',
        })
        self.assertTrue(
            Deal.objects.filter(contact=contact).exists()
        )

    def test_pauses_autopilot_on_non_won_event(self):
        contact, deal = self._setup_contact_with_deal('autopause@test.com')
        deal.autopilot_paused = False
        deal.save(update_fields=['autopilot_paused'])

        self._post({
            'event_type': 'business_created',
            'email': 'autopause@test.com',
        })
        deal.refresh_from_db()
        self.assertTrue(deal.autopilot_paused)


class TestDesiFirmsWebhookContactUpdate(CRMTestCase):
    """Test that webhook updates contact name if empty."""

    URL = '/api/crm/webhooks/desifirms/'

    def test_updates_name_if_empty(self):
        brand = self._create_brand(slug='desifirms', name='Desi Firms')
        pipeline = self._create_pipeline(
            brand, name='Registered Users - Business',
            pipeline_type='registered_users',
        )
        self._create_stage(pipeline, 'New', 0)
        # Create contact then force name to empty (bypassing save auto-populate)
        contact = self._create_contact(brand, email='noname@test.com', name='Auto')
        Contact.objects.filter(id=contact.id).update(name='')
        contact.refresh_from_db()
        self.assertEqual(contact.name, '')

        self.client.post(
            self.URL,
            json.dumps({
                'event_type': 'user_registered',
                'email': 'noname@test.com',
                'name': 'New Name',
                'pipeline_hint': 'business',
            }),
            content_type='application/json',
        )
        contact.refresh_from_db()
        self.assertEqual(contact.name, 'New Name')


# =============================================================================
# EmailReplyWebhookView
# =============================================================================


class TestEmailReplyWebhook(CRMTestCase):
    """Test EmailReplyWebhookView."""

    URL = '/api/crm/webhooks/reply/'

    def setUp(self):
        self.brand = self._create_brand()
        self.pipeline = self._create_pipeline(self.brand)
        self.stage1 = self._create_stage(self.pipeline, 'Follow Up 1', 0)
        self.responded_stage = self._create_stage(
            self.pipeline, 'Responded', 1,
        )

    def _post(self, data=None, raw=None):
        body = raw if raw is not None else json.dumps(data)
        return self.client.post(self.URL, body, content_type='application/json')

    def test_invalid_json(self):
        resp = self._post(raw='bad json')
        self.assertEqual(resp.status_code, 400)

    def test_missing_from_email(self):
        resp = self._post({'subject': 'Re: Hello', 'body': 'Hi'})
        self.assertEqual(resp.status_code, 400)

    def test_unknown_contact(self):
        resp = self._post({
            'from_email': 'nobody@nowhere.com',
            'subject': 'Re: test',
        })
        data = resp.json()
        self.assertEqual(data['status'], 'ignored')

    def test_no_active_deal(self):
        contact = self._create_contact(self.brand, email='inactive@test.com')
        resp = self._post({
            'from_email': 'inactive@test.com',
            'subject': 'Re: hello',
        })
        data = resp.json()
        self.assertEqual(data['status'], 'contact_updated')
        contact.refresh_from_db()
        self.assertEqual(contact.status, 'replied')

    def test_pauses_autopilot(self):
        contact = self._create_contact(self.brand, email='replier@test.com')
        deal = self._create_deal(
            contact, self.pipeline, self.stage1, autopilot_paused=False,
        )
        self._post({
            'from_email': 'replier@test.com',
            'subject': 'Re: proposal',
            'body': 'Sounds interesting!',
        })
        deal.refresh_from_db()
        self.assertTrue(deal.autopilot_paused)

    def test_moves_to_responded_stage(self):
        contact = self._create_contact(self.brand, email='responder@test.com')
        deal = self._create_deal(contact, self.pipeline, self.stage1)
        self._post({
            'from_email': 'responder@test.com',
            'subject': 'Re: hello',
            'body': 'Thanks!',
        })
        deal.refresh_from_db()
        self.assertEqual(deal.current_stage, self.responded_stage)

    def test_creates_activity_and_email_log(self):
        contact = self._create_contact(self.brand, email='activity@test.com')
        deal = self._create_deal(contact, self.pipeline, self.stage1)
        self._post({
            'from_email': 'activity@test.com',
            'subject': 'Re: test',
            'body': 'Reply body',
        })
        self.assertTrue(deal.activities.exists())
        self.assertTrue(
            EmailLog.objects.filter(deal=deal, replied=True).exists()
        )

    def test_appends_to_ai_notes(self):
        contact = self._create_contact(self.brand, email='notes@test.com')
        deal = self._create_deal(
            contact, self.pipeline, self.stage1, ai_notes='Previous notes',
        )
        self._post({
            'from_email': 'notes@test.com',
            'subject': 'Re: check this',
            'body': 'Unique reply content',
        })
        deal.refresh_from_db()
        self.assertIn('REPLY RECEIVED', deal.ai_notes)
        self.assertIn('Unique reply content', deal.ai_notes)


# =============================================================================
# ZeptoMailBounceWebhookView
# =============================================================================


@override_settings(ZEPTOMAIL_WEBHOOK_KEY='')
class TestZeptoMailBounceWebhook(CRMTestCase):
    """Test ZeptoMailBounceWebhookView."""

    URL = '/api/crm/webhooks/bounce/'

    def setUp(self):
        self.brand = self._create_brand()
        self.pipeline = self._create_pipeline(self.brand)
        self.stage = self._create_stage(self.pipeline)

    def _post(self, data, auth=None):
        headers = {}
        if auth is not None:
            headers['HTTP_AUTHORIZATION'] = auth
        return self.client.post(
            self.URL, json.dumps(data), content_type='application/json', **headers,
        )

    def _bounce_payload(self, email, event_type='hardbounce'):
        """Build a ZeptoMail-style bounce payload."""
        return {
            'event_name': [event_type],
            'event_message': [{
                'event_data': [{
                    'details': [{
                        'bounced_recipient': email,
                    }],
                }],
            }],
        }

    def _spam_payload(self, email):
        return {
            'event_name': ['feedback_loop'],
            'event_message': [{
                'event_data': [{
                    'details': [{
                        'recipient': email,
                    }],
                }],
            }],
        }

    # --- Auth ---

    @override_settings(ZEPTOMAIL_WEBHOOK_KEY='bounce-key')
    def test_invalid_auth_returns_401(self):
        resp = self._post(
            self._bounce_payload('t@t.com'), auth='wrong-key',
        )
        self.assertEqual(resp.status_code, 401)

    @override_settings(ZEPTOMAIL_WEBHOOK_KEY='')
    def test_no_key_configured_passes(self):
        # No auth required when key is empty
        resp = self._post(self._bounce_payload('nobody@example.com'))
        self.assertEqual(resp.status_code, 200)

    # --- Validation ---

    def test_invalid_json(self):
        resp = self.client.post(
            self.URL, 'bad json', content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)

    def test_missing_event_message(self):
        resp = self._post({'event_name': ['hardbounce']})
        self.assertEqual(resp.status_code, 400)

    # --- Hard bounce ---

    def test_hard_bounce_marks_contact(self):
        contact = self._create_contact(self.brand, email='bounced@test.com')
        deal = self._create_deal(contact, self.pipeline, self.stage)

        resp = self._post(self._bounce_payload('bounced@test.com'))
        self.assertEqual(resp.status_code, 200)
        contact.refresh_from_db()
        self.assertTrue(contact.email_bounced)
        self.assertIsNotNone(contact.bounced_at)

    def test_hard_bounce_closes_deals(self):
        contact = self._create_contact(self.brand, email='deals@test.com')
        deal1 = self._create_deal(contact, self.pipeline, self.stage)
        deal2 = self._create_deal(contact, self.pipeline, self.stage)

        self._post(self._bounce_payload('deals@test.com'))
        deal1.refresh_from_db()
        deal2.refresh_from_db()
        self.assertEqual(deal1.status, 'lost')
        self.assertEqual(deal1.lost_reason, 'invalid_email')
        self.assertEqual(deal2.status, 'lost')

    def test_hard_bounce_idempotent(self):
        contact = self._create_contact(
            self.brand, email='idem@test.com', email_bounced=True,
            bounced_at=timezone.now(),
        )
        resp = self._post(self._bounce_payload('idem@test.com'))
        data = resp.json()
        result = data['results'][0]
        self.assertEqual(result['action'], 'already_bounced')

    def test_hard_bounce_unknown_email(self):
        resp = self._post(self._bounce_payload('unknown@nowhere.com'))
        data = resp.json()
        result = data['results'][0]
        self.assertEqual(result['action'], 'ignored')

    # --- Soft bounce ---

    def test_soft_bounce_increments_count(self):
        contact = self._create_contact(self.brand, email='soft@test.com')
        self._post(self._bounce_payload('soft@test.com', 'softbounce'))
        contact.refresh_from_db()
        self.assertEqual(contact.soft_bounce_count, 1)
        self.assertFalse(contact.email_bounced)

    def test_soft_bounce_escalates_at_threshold(self):
        """3 soft bounces should escalate to hard bounce."""
        contact = self._create_contact(
            self.brand, email='escalate@test.com', soft_bounce_count=2,
        )
        deal = self._create_deal(contact, self.pipeline, self.stage)
        # This is the 3rd soft bounce
        self._post(self._bounce_payload('escalate@test.com', 'softbounce'))
        contact.refresh_from_db()
        self.assertTrue(contact.email_bounced)
        deal.refresh_from_db()
        self.assertEqual(deal.status, 'lost')

    # --- Spam report ---

    def test_spam_marks_unsubscribed(self):
        contact = self._create_contact(self.brand, email='spam@test.com')
        self._post(self._spam_payload('spam@test.com'))
        contact.refresh_from_db()
        self.assertTrue(contact.spam_reported)
        self.assertTrue(contact.is_unsubscribed)

    def test_spam_closes_deals(self):
        contact = self._create_contact(self.brand, email='spamdeal@test.com')
        deal = self._create_deal(contact, self.pipeline, self.stage)
        self._post(self._spam_payload('spamdeal@test.com'))
        deal.refresh_from_db()
        self.assertEqual(deal.status, 'lost')
        self.assertEqual(deal.lost_reason, 'unsubscribed')
