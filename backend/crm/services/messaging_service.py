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

    def send_whatsapp(self, to: str, body: str) -> dict:
        """
        Send WhatsApp message via Twilio.

        Args:
            to: Recipient phone in E.164 format
            body: Message body (max ~1024 chars recommended)

        Returns:
            {success, message_sid, error}
        """
        if not self.whatsapp_enabled:
            brand_info = f" for {self.brand.name}" if self.brand else ""
            return {
                'success': False,
                'message_sid': None,
                'error': f'Twilio WhatsApp not configured{brand_info}.',
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
            }

        try:
            client = self._get_client()
            message = client.messages.create(
                body=body,
                from_=f'whatsapp:{self.whatsapp_number}',
                to=f'whatsapp:{to}',
            )
            logger.info(f"WhatsApp sent to {to}: SID={message.sid}")
            return {
                'success': True,
                'message_sid': message.sid,
                'error': None,
            }
        except Exception as e:
            logger.error(f"Twilio WhatsApp send failed to {to}: {e}")
            return {
                'success': False,
                'message_sid': None,
                'error': str(e),
            }


def get_messaging_service(brand: Optional['Brand'] = None) -> TwilioMessagingService:
    """Factory function to get TwilioMessagingService for a brand."""
    return TwilioMessagingService(brand=brand)
