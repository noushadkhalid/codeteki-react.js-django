"""
Twilio Messaging Service

Handles SMS and WhatsApp sending for CRM outreach:
- Send SMS via Twilio
- Send WhatsApp via Twilio
- Pre-send opt-out checks
- Auto-append opt-out text for SMS
"""

import logging
from typing import Optional, TYPE_CHECKING
from django.conf import settings

if TYPE_CHECKING:
    from crm.models import Brand

logger = logging.getLogger(__name__)


class TwilioMessagingService:
    """
    Messaging service using Twilio for SMS and WhatsApp.

    Supports per-brand Twilio credentials for multi-brand CRM.
    Priority: Brand fields -> env vars -> settings.
    """

    def __init__(self, brand: Optional['Brand'] = None):
        import os
        from dotenv import load_dotenv
        load_dotenv()

        self.brand = brand

        if brand and brand.twilio_account_sid:
            self.account_sid = brand.twilio_account_sid
            self.auth_token = brand.twilio_auth_token
            self.phone_number = brand.twilio_phone_number
            self.whatsapp_number = brand.twilio_whatsapp_number
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
            self.whatsapp_number = os.environ.get(
                'TWILIO_WHATSAPP_NUMBER',
                getattr(settings, 'TWILIO_WHATSAPP_NUMBER', '')
            )

        self._client = None

    @property
    def enabled(self) -> bool:
        return bool(self.account_sid and self.auth_token and self.phone_number)

    @property
    def whatsapp_enabled(self) -> bool:
        return bool(self.account_sid and self.auth_token and self.whatsapp_number)

    def _get_client(self):
        if self._client is None:
            from twilio.rest import Client
            self._client = Client(self.account_sid, self.auth_token)
        return self._client

    def send_sms(self, to: str, body: str) -> dict:
        """
        Send SMS via Twilio.

        Args:
            to: Recipient phone in E.164 format
            body: Message body (max ~1600 chars, 160 per segment)

        Returns:
            {success, message_sid, error}
        """
        if not self.enabled:
            brand_info = f" for {self.brand.name}" if self.brand else ""
            return {
                'success': False,
                'message_sid': None,
                'error': f'Twilio not configured{brand_info}. Set Twilio credentials in Brand settings or environment.',
            }

        # Check opt-out
        from crm.models import Contact
        contact = Contact.objects.filter(phone=to).first()
        if not contact:
            contact = Contact.objects.filter(phone__endswith=to[-10:]).first()
        if contact and contact.sms_opted_out:
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
        Send WhatsApp message via Twilio using approved content template.

        Business-initiated WhatsApp requires pre-approved templates.
        Falls back to free-form body only if within a 24-hour user-initiated window.

        Args:
            to: Recipient phone in E.164 format
            body: Message body (used as fallback context)
            contact_name: Recipient name for template variable {{1}}
            business_name: Business name for template variable {{2}}

        Returns:
            {success, message_sid, error, is_recipient_issue}
        """
        if not self.whatsapp_enabled:
            brand_info = f" for {self.brand.name}" if self.brand else ""
            return {
                'success': False,
                'message_sid': None,
                'error': f'Twilio WhatsApp not configured{brand_info}.',
                'is_recipient_issue': False,
            }

        # Check opt-out
        from crm.models import Contact
        contact = Contact.objects.filter(phone=to).first()
        if not contact:
            contact = Contact.objects.filter(phone__endswith=to[-10:]).first()
        if contact and contact.sms_opted_out:
            return {
                'success': False,
                'message_sid': None,
                'error': f'Recipient {to} has opted out of messages.',
                'is_recipient_issue': False,
            }

        # Use contact/brand info for template variables
        if not contact_name and contact:
            contact_name = (contact.name or '').split()[0] if contact.name else 'there'
        if not business_name and contact:
            business_name = contact.company or 'your business'

        try:
            import time
            import json as _json
            client = self._get_client()

            # Get WhatsApp content template SID from brand or env
            import os
            content_sid = ''
            if self.brand:
                content_sid = getattr(self.brand, 'whatsapp_template_sid', '') or ''
            if not content_sid:
                content_sid = os.environ.get('WHATSAPP_CONTENT_SID', '')

            if content_sid:
                # Business-initiated: use approved template
                message = client.messages.create(
                    from_=f'whatsapp:{self.whatsapp_number}',
                    to=f'whatsapp:{to}',
                    content_sid=content_sid,
                    content_variables=_json.dumps({
                        '1': contact_name or 'there',
                        '2': business_name or 'your business',
                    }),
                )
            else:
                # No template configured — try free-form (works in 24h user-initiated window)
                message = client.messages.create(
                    body=body,
                    from_=f'whatsapp:{self.whatsapp_number}',
                    to=f'whatsapp:{to}',
                )

            logger.info(f"WhatsApp queued to {to}: SID={message.sid}, status={message.status}")

            # Twilio accepts WhatsApp messages as 'queued' even when they'll fail.
            # Wait and re-check status.
            if message.status in ('queued', 'accepted'):
                time.sleep(3)
                updated = client.messages(message.sid).fetch()
                if updated.status == 'failed':
                    error_code = str(updated.error_code or '')
                    logger.warning(f"WhatsApp failed after queue for {to}: error={error_code}")
                    # 63003 = not on WhatsApp, 63001 = channel not found
                    recipient_errors = {'63003', '63001'}
                    is_recipient_issue = error_code in recipient_errors
                    return {
                        'success': False,
                        'message_sid': message.sid,
                        'error': f'WhatsApp failed: error {error_code}',
                        'is_recipient_issue': is_recipient_issue,
                    }

            return {
                'success': True,
                'message_sid': message.sid,
                'error': None,
                'is_recipient_issue': False,
            }
        except Exception as e:
            logger.error(f"Twilio WhatsApp send failed to {to}: {e}")
            return {
                'success': False,
                'message_sid': None,
                'error': str(e),
                'is_recipient_issue': False,
            }


    def _lookup_contact(self, phone: str):
        """Find Contact by phone number for WhatsApp status check."""
        from crm.models import Contact
        contact = Contact.objects.filter(phone=phone).first()
        if not contact:
            contact = Contact.objects.filter(phone__endswith=phone[-10:]).first()
        return contact

    def send_smart(self, to: str, body: str, sms_body: str = '') -> dict:
        """
        Smart send: WhatsApp for confirmed users, SMS for rest.

        Filter logic:
        - has_whatsapp=True  → try WhatsApp, fall back to SMS on failure
        - has_whatsapp=False → skip WhatsApp, send SMS directly (saves money)
        - has_whatsapp=None  → try WhatsApp once to discover, then cache result

        Args:
            to: Recipient phone in E.164 format
            body: WhatsApp message (up to 1024 chars)
            sms_body: Shorter SMS fallback (up to 140 chars). Uses body if not provided.

        Returns:
            {success, message_sid, channel_used, error}
        """
        contact = self._lookup_contact(to)

        # Check if we know this contact's WhatsApp status
        skip_whatsapp = False
        if contact and contact.has_whatsapp is False:
            skip_whatsapp = True
            logger.info(f"Skipping WhatsApp for {to} — marked as no WhatsApp, sending SMS.")

        # Try WhatsApp if enabled and not known to be absent
        if self.whatsapp_enabled and not skip_whatsapp:
            result = self.send_whatsapp(to, body)
            if result['success']:
                result['channel_used'] = 'whatsapp'
                # Mark contact as confirmed WhatsApp user
                if contact and contact.has_whatsapp is not True:
                    contact.has_whatsapp = True
                    contact.save(update_fields=['has_whatsapp'])
                return result

            # WhatsApp failed — only mark no-WhatsApp if it's a RECIPIENT issue
            # (e.g. 63003 = not on WhatsApp). Don't cache if it's a sender/template issue
            # (e.g. 63112 = template not approved, 63016 = content rejected)
            is_recipient_issue = result.get('is_recipient_issue', False)
            if is_recipient_issue and contact:
                logger.info(f"WhatsApp failed for {to} — recipient not on WhatsApp. Caching for future SMS-only.")
                contact.has_whatsapp = False
                contact.save(update_fields=['has_whatsapp'])
            else:
                logger.info(f"WhatsApp failed for {to} — sender/config issue, not caching. Error: {result.get('error')}")

        # Fall back to SMS with shorter body
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


def get_messaging_service(brand: Optional['Brand'] = None) -> TwilioMessagingService:
    """Factory function to get TwilioMessagingService for a brand."""
    return TwilioMessagingService(brand=brand)
