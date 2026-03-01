"""
Messaging Service

Handles SMS and WhatsApp sending for CRM outreach:
- Send WhatsApp via Meta Cloud API (direct, no Twilio markup)
- Send SMS via Twilio (for contacts without WhatsApp)
- Smart routing: WhatsApp first, SMS fallback
- Pre-send opt-out checks
- Auto-append opt-out text for SMS
"""

import json
import logging
import requests
from typing import Optional, TYPE_CHECKING
from django.conf import settings

if TYPE_CHECKING:
    from crm.models import Brand

logger = logging.getLogger(__name__)

META_GRAPH_URL = 'https://graph.facebook.com/v21.0'


class MetaWhatsAppService:
    """
    Send WhatsApp messages via Meta Cloud API (direct).

    No Twilio middleman — all WhatsApp goes through Meta.
    Requires approved templates for business-initiated messages.
    """

    def __init__(self, brand: Optional['Brand'] = None):
        import os
        from dotenv import load_dotenv
        load_dotenv()

        self.brand = brand
        self.token = os.environ.get('META_WHATSAPP_TOKEN', '')
        self.phone_id = os.environ.get('META_WHATSAPP_PHONE_ID', '')
        self.template_name = os.environ.get('META_WHATSAPP_TEMPLATE_NAME', '')

    @property
    def enabled(self) -> bool:
        return bool(self.token and self.phone_id)

    def _headers(self):
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }

    def _api_url(self):
        return f'{META_GRAPH_URL}/{self.phone_id}/messages'

    def send_template(self, to: str, template_name: str = '',
                      contact_name: str = 'there',
                      business_name: str = 'your business',
                      language: str = 'en') -> dict:
        """
        Send approved template message (business-initiated).

        Args:
            to: Phone in E.164 format (e.g. +61400000000)
            template_name: Meta template name (falls back to env var)
            contact_name: Variable {{1}} value
            business_name: Variable {{2}} value
            language: Template language code

        Returns:
            {success, message_id, error, is_recipient_issue}
        """
        template = template_name or self.template_name
        if not template:
            return {
                'success': False,
                'message_id': None,
                'error': 'No WhatsApp template configured.',
                'is_recipient_issue': False,
            }

        wa_id = to.lstrip('+')

        payload = {
            'messaging_product': 'whatsapp',
            'to': wa_id,
            'type': 'template',
            'template': {
                'name': template,
                'language': {'code': language},
                'components': [
                    {
                        'type': 'body',
                        'parameters': [
                            {'type': 'text', 'text': contact_name},
                            {'type': 'text', 'text': business_name},
                        ],
                    }
                ],
            },
        }

        try:
            resp = requests.post(self._api_url(), headers=self._headers(), json=payload, timeout=30)
            data = resp.json()

            if resp.status_code == 200 and 'messages' in data:
                msg_id = data['messages'][0]['id']
                msg_status = data['messages'][0].get('message_status', 'accepted')
                logger.info(f"Meta WhatsApp template sent to {to}: id={msg_id}, status={msg_status}")
                return {
                    'success': True,
                    'message_id': msg_id,
                    'error': None,
                    'is_recipient_issue': False,
                }

            error_msg = self._parse_error(data)
            is_recipient = self._is_recipient_error(data)
            logger.warning(f"Meta WhatsApp template failed for {to}: {error_msg}")
            return {
                'success': False,
                'message_id': None,
                'error': error_msg,
                'is_recipient_issue': is_recipient,
            }
        except Exception as e:
            logger.error(f"Meta WhatsApp send failed to {to}: {e}")
            return {
                'success': False,
                'message_id': None,
                'error': str(e),
                'is_recipient_issue': False,
            }

    def send_text_with_links(self, to: str, body: str, buttons: list) -> dict:
        """
        Send a text message followed by clickable link messages.

        WhatsApp auto-generates rich link previews for URLs sent as plain text.
        CTA URL buttons are only available in approved templates, so for
        free-form AI responses we send text + separate link messages.

        Args:
            to: Phone in E.164 format
            body: Message body text (no URLs)
            buttons: List of dicts with 'title' and 'url' keys
        """
        # Send the main message first
        result = self.send_text(to=to, body=body)
        if not result['success']:
            return result

        # Send each link as a separate short message (gets rich preview)
        for btn in buttons[:3]:
            link_text = f"{btn['title']}: {btn['url']}"
            self.send_text(to=to, body=link_text)

        return result

    def send_text(self, to: str, body: str) -> dict:
        """
        Send free-form text message (only within 24h user-initiated window).
        """
        wa_id = to.lstrip('+')

        payload = {
            'messaging_product': 'whatsapp',
            'to': wa_id,
            'type': 'text',
            'text': {'body': body},
        }

        try:
            resp = requests.post(self._api_url(), headers=self._headers(), json=payload, timeout=30)
            data = resp.json()

            if resp.status_code == 200 and 'messages' in data:
                msg_id = data['messages'][0]['id']
                logger.info(f"Meta WhatsApp text sent to {to}: id={msg_id}")
                return {
                    'success': True,
                    'message_id': msg_id,
                    'error': None,
                    'is_recipient_issue': False,
                }

            error_msg = self._parse_error(data)
            is_recipient = self._is_recipient_error(data)
            logger.warning(f"Meta WhatsApp text failed for {to}: {error_msg}")
            return {
                'success': False,
                'message_id': None,
                'error': error_msg,
                'is_recipient_issue': is_recipient,
            }
        except Exception as e:
            logger.error(f"Meta WhatsApp text send failed to {to}: {e}")
            return {
                'success': False,
                'message_id': None,
                'error': str(e),
                'is_recipient_issue': False,
            }

    def _parse_error(self, data: dict) -> str:
        error = data.get('error', {})
        if error:
            code = error.get('code', '')
            msg = error.get('message', 'Unknown error')
            return f'Meta API error {code}: {msg}'
        return f'Unknown Meta API error: {json.dumps(data)}'

    def _is_recipient_error(self, data: dict) -> bool:
        """Check if error is due to recipient (not on WhatsApp, invalid number)."""
        error = data.get('error', {})
        code = error.get('code', 0)
        # 131026 = message undeliverable (not on WhatsApp)
        # 100 with subcode 2018109 = invalid phone number
        if code == 131026:
            return True
        if code == 100:
            sub = error.get('error_subcode', 0)
            if sub == 2018109:
                return True
        return False


class MessagingService:
    """
    CRM Messaging Service.

    WhatsApp: Meta Cloud API only (no Twilio WhatsApp).
    SMS: Twilio only.

    Smart routing:
    - has_whatsapp=True  -> send via Meta WhatsApp
    - has_whatsapp=False -> send via Twilio SMS
    - has_whatsapp=None  -> try Meta WhatsApp, cache result, SMS fallback
    """

    def __init__(self, brand: Optional['Brand'] = None):
        import os
        from dotenv import load_dotenv
        load_dotenv()

        self.brand = brand
        self.meta_whatsapp = MetaWhatsAppService(brand=brand)

        # Twilio for SMS only
        if brand and brand.twilio_account_sid:
            self.account_sid = brand.twilio_account_sid
            self.auth_token = brand.twilio_auth_token
            self.phone_number = brand.twilio_phone_number
        else:
            self.account_sid = os.environ.get(
                'TWILIO_ACCOUNT_SID',
                getattr(settings, 'TWILIO_ACCOUNT_SID', '')
            )
            self.auth_token = os.environ.get(
                'TWILIO_AUTH_TOKEN',
                getattr(settings, 'TWILIO_AUTH_TOKEN', '')
            )
            self.phone_number = os.environ.get(
                'TWILIO_PHONE_NUMBER',
                getattr(settings, 'TWILIO_PHONE_NUMBER', '')
            )

        self._client = None

    @property
    def enabled(self) -> bool:
        """SMS (Twilio) is configured."""
        return bool(self.account_sid and self.auth_token and self.phone_number)

    @property
    def whatsapp_enabled(self) -> bool:
        """WhatsApp (Meta Cloud API) is configured."""
        return self.meta_whatsapp.enabled

    def _get_client(self):
        if self._client is None:
            from twilio.rest import Client
            self._client = Client(self.account_sid, self.auth_token)
        return self._client

    def _lookup_contact(self, phone: str):
        """Find Contact by phone number."""
        from crm.models import Contact
        contact = Contact.objects.filter(phone=phone).first()
        if not contact:
            contact = Contact.objects.filter(phone__endswith=phone[-10:]).first()
        return contact

    def _check_opt_out(self, to: str) -> tuple:
        """Check if contact has opted out. Returns (contact, opted_out)."""
        contact = self._lookup_contact(to)
        if contact and contact.sms_opted_out:
            return contact, True
        return contact, False

    def send_sms(self, to: str, body: str) -> dict:
        """
        Send SMS via Twilio.

        Returns:
            {success, message_sid, error}
        """
        if not self.enabled:
            brand_info = f" for {self.brand.name}" if self.brand else ""
            return {
                'success': False,
                'message_sid': None,
                'error': f'Twilio not configured{brand_info}.',
            }

        contact, opted_out = self._check_opt_out(to)
        if opted_out:
            return {
                'success': False,
                'message_sid': None,
                'error': f'Recipient {to} has opted out of SMS.',
            }

        # Auto-append opt-out text
        opt_out_text = "\nReply STOP to opt out"
        if opt_out_text.strip().lower() not in body.lower():
            body = body.rstrip() + opt_out_text

        try:
            client = self._get_client()
            message = client.messages.create(
                body=body,
                from_=self.phone_number,
                to=to,
            )
            logger.info(f"SMS sent to {to}: SID={message.sid}")
            return {
                'success': True,
                'message_sid': message.sid,
                'error': None,
            }
        except Exception as e:
            logger.error(f"Twilio SMS send failed to {to}: {e}")
            return {
                'success': False,
                'message_sid': None,
                'error': str(e),
            }

    def send_whatsapp(self, to: str, body: str, contact_name: str = '', business_name: str = '') -> dict:
        """
        Send WhatsApp message via Meta Cloud API only.

        Business-initiated messages use approved templates.
        Free-form text only works within 24h user-initiated window.

        Returns:
            {success, message_sid, error, is_recipient_issue}
        """
        if not self.whatsapp_enabled:
            return {
                'success': False,
                'message_sid': None,
                'error': 'Meta WhatsApp not configured.',
                'is_recipient_issue': False,
            }

        contact, opted_out = self._check_opt_out(to)
        if opted_out:
            return {
                'success': False,
                'message_sid': None,
                'error': f'Recipient {to} has opted out of messages.',
                'is_recipient_issue': False,
            }

        # Resolve template variables from contact
        if not contact_name and contact:
            contact_name = (contact.name or '').split()[0] if contact.name else 'there'
        if not business_name and contact:
            business_name = contact.company or 'your business'

        result = self.meta_whatsapp.send_template(
            to=to,
            contact_name=contact_name or 'there',
            business_name=business_name or 'your business',
        )

        if result['success']:
            return {
                'success': True,
                'message_sid': result['message_id'],
                'error': None,
                'is_recipient_issue': False,
            }

        return {
            'success': False,
            'message_sid': None,
            'error': result['error'],
            'is_recipient_issue': result.get('is_recipient_issue', False),
        }

    def send_smart(self, to: str, body: str, sms_body: str = '') -> dict:
        """
        Smart send: SMS first, WhatsApp only for confirmed users.

        Meta silently drops marketing templates to recipients who haven't
        messaged the business first. So we SMS by default, and only use
        WhatsApp once the contact has replied on WhatsApp (has_whatsapp=True).

        - has_whatsapp=True  -> Meta WhatsApp (they've messaged us)
        - has_whatsapp=False -> Twilio SMS (confirmed no WhatsApp)
        - has_whatsapp=None  -> Twilio SMS (unknown, first contact)

        Returns:
            {success, message_sid, channel_used, error}
        """
        contact = self._lookup_contact(to)

        # Confirmed WhatsApp user -> send via Meta WhatsApp
        # Skip WhatsApp for Codeteki brand (SMS + email only)
        brand_slug = self.brand.slug if self.brand else ''
        if brand_slug != 'codeteki' and contact and contact.has_whatsapp is True and self.whatsapp_enabled:
            logger.info(f"Contact {to} confirmed on WhatsApp -> Meta WhatsApp.")
            result = self.send_whatsapp(to, body)
            if result['success']:
                result['channel_used'] = 'whatsapp'
                return result
            # WhatsApp failed — fall through to SMS
            logger.warning(f"WhatsApp failed for confirmed user {to}: {result.get('error')}. Falling back to SMS.")

        # Default: send SMS (unknown contacts, no-WhatsApp, or WhatsApp failed)
        if self.enabled:
            result = self.send_sms(to, sms_body or body)
            result['channel_used'] = 'sms'
            return result

        brand_info = f" for {self.brand.name}" if self.brand else ""
        return {
            'success': False,
            'message_sid': None,
            'channel_used': None,
            'error': f'No messaging channel configured{brand_info}.',
        }


# Backwards-compatible alias
TwilioMessagingService = MessagingService


def get_messaging_service(brand: Optional['Brand'] = None) -> MessagingService:
    """Factory function to get messaging service for a brand."""
    return MessagingService(brand=brand)
