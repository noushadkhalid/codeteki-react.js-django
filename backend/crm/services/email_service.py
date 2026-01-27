"""
Zoho Mail Email Service

Handles all email operations for CRM outreach:
- Sending emails via Zoho Mail API
- Tracking email opens
- Fetching inbox for reply detection
- Multi-brand support with per-brand Zoho accounts
"""

import logging
import requests
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

if TYPE_CHECKING:
    from crm.models import Brand, Deal

logger = logging.getLogger(__name__)

# Cache for brand-specific email services
_brand_service_cache = {}


class ZohoEmailService:
    """
    Email service using Zoho Mail API.

    Supports per-brand Zoho credentials for multi-brand CRM.
    If brand is provided, uses brand-specific credentials.
    Otherwise falls back to global settings.
    """

    def __init__(self, brand: Optional['Brand'] = None):
        import os
        from dotenv import load_dotenv
        load_dotenv()  # Ensure .env is loaded

        self.brand = brand

        if brand and brand.zoho_client_id:
            # Use brand-specific credentials from database
            self.client_id = brand.zoho_client_id
            self.client_secret = brand.zoho_client_secret
            self.refresh_token = brand.zoho_refresh_token
            self.account_id = brand.zoho_account_id
            self.from_email = brand.from_email
            self.from_name = brand.from_name
            api_domain = brand.zoho_api_domain or 'zoho.com'
            logger.debug(f"Using brand-specific Zoho credentials from DB for {brand.name}")
        elif brand:
            # Try brand-specific env vars (e.g., DESIFIRMS_ZOHO_CLIENT_ID)
            # Convert brand name to env prefix: "Desi Firms" -> "DESIFIRMS"
            env_prefix = brand.name.upper().replace(' ', '').replace('-', '').replace('_', '')

            self.client_id = os.environ.get(f'{env_prefix}_ZOHO_CLIENT_ID', '')
            self.client_secret = os.environ.get(f'{env_prefix}_ZOHO_CLIENT_SECRET', '')
            self.refresh_token = os.environ.get(f'{env_prefix}_ZOHO_REFRESH_TOKEN', '')
            self.account_id = os.environ.get(f'{env_prefix}_ZOHO_ACCOUNT_ID', '')
            self.from_email = os.environ.get(f'{env_prefix}_ZOHO_FROM_EMAIL', brand.from_email or '')
            self.from_name = brand.from_name or brand.name
            api_domain = os.environ.get(f'{env_prefix}_ZOHO_API_DOMAIN', 'zoho.com')

            if self.client_id:
                logger.debug(f"Using brand-specific Zoho credentials from env for {brand.name} (prefix: {env_prefix})")
            else:
                # Fall back to global settings
                self.client_id = getattr(settings, 'ZOHO_CLIENT_ID', '')
                self.client_secret = getattr(settings, 'ZOHO_CLIENT_SECRET', '')
                self.refresh_token = getattr(settings, 'ZOHO_REFRESH_TOKEN', '')
                self.account_id = getattr(settings, 'ZOHO_ACCOUNT_ID', '')
                self.from_email = getattr(settings, 'ZOHO_FROM_EMAIL', brand.from_email or 'sales@codeteki.au')
                self.from_name = brand.from_name or 'Codeteki'
                api_domain = getattr(settings, 'ZOHO_API_DOMAIN', 'zoho.com')
        else:
            # No brand - use global settings
            self.client_id = getattr(settings, 'ZOHO_CLIENT_ID', '')
            self.client_secret = getattr(settings, 'ZOHO_CLIENT_SECRET', '')
            self.refresh_token = getattr(settings, 'ZOHO_REFRESH_TOKEN', '')
            self.account_id = getattr(settings, 'ZOHO_ACCOUNT_ID', '')
            self.from_email = getattr(settings, 'ZOHO_FROM_EMAIL', 'sales@codeteki.au')
            self.from_name = 'Codeteki'
            api_domain = getattr(settings, 'ZOHO_API_DOMAIN', 'zoho.com')

        # Support regional Zoho domains (zoho.com, zoho.com.au, zoho.eu, zoho.in)
        self.api_domain = api_domain
        self.TOKEN_URL = f"https://accounts.{api_domain}/oauth/v2/token"
        self.API_BASE = f"https://mail.{api_domain}/api"

        self._access_token = None
        self._token_expiry = None

    @property
    def enabled(self) -> bool:
        """Check if Zoho integration is configured."""
        return all([
            self.client_id,
            self.client_secret,
            self.refresh_token,
            self.account_id
        ])

    def _get_access_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary."""
        if not self.enabled:
            logger.warning("Zoho Mail not configured")
            return None

        # Check if current token is still valid
        if self._access_token and self._token_expiry and timezone.now() < self._token_expiry:
            return self._access_token

        # Refresh the token
        try:
            response = requests.post(
                self.TOKEN_URL,
                data={
                    'refresh_token': self.refresh_token,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'refresh_token'
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if 'error' in data:
                logger.error(f"Zoho token refresh error: {data.get('error')}")
                return None

            self._access_token = data.get('access_token')
            # Token typically valid for 1 hour, refresh 5 minutes early
            self._token_expiry = timezone.now() + timedelta(minutes=55)

            return self._access_token

        except requests.RequestException as e:
            logger.error(f"Failed to refresh Zoho access token: {e}")
            return None

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[dict]:
        """Make an authenticated request to Zoho Mail API."""
        token = self._get_access_token()
        if not token:
            logger.error(f"Zoho Mail: Failed to get access token for {self.from_email}")
            return None

        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Zoho-oauthtoken {token}'
        headers['Content-Type'] = 'application/json'

        url = f"{self.API_BASE}/accounts/{self.account_id}/{endpoint}"

        try:
            logger.info(f"Zoho Mail: Making {method} request to {endpoint}")
            response = requests.request(
                method,
                url,
                headers=headers,
                timeout=kwargs.pop('timeout', 30),
                **kwargs
            )

            # Log response details for debugging
            logger.info(f"Zoho Mail: Response status {response.status_code}")

            # Try to parse response even if status is not 200
            try:
                response_data = response.json()
                logger.debug(f"Zoho Mail: Response data: {response_data}")
            except ValueError:
                logger.error(f"Zoho Mail: Invalid JSON response: {response.text[:500]}")
                return None

            # Check for Zoho-specific errors even in 200 responses
            if response_data.get('status', {}).get('code') != 200:
                error_desc = response_data.get('status', {}).get('description', 'Unknown error')
                logger.error(f"Zoho Mail: API error - {error_desc}")

            response.raise_for_status()
            return response_data

        except requests.RequestException as e:
            logger.error(f"Zoho Mail API request failed: {e}")
            # Try to get more details from the response
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.error(f"Zoho Mail: Error detail: {error_detail}")
                except ValueError:
                    logger.error(f"Zoho Mail: Error response: {e.response.text[:500]}")
            return None

    def send(
        self,
        to: str,
        subject: str,
        body: str,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        tracking_id: Optional[str] = None,
        bcc: Optional[List[str]] = None
    ) -> dict:
        """
        Send an email via Zoho Mail API.

        Args:
            to: Recipient email address (can be sender's own email for BCC-only sends)
            subject: Email subject
            body: Email body (plain text or HTML)
            from_name: Sender display name (defaults to brand's from_name)
            reply_to: Reply-to address (optional)
            tracking_id: UUID for open tracking (optional)
            bcc: List of BCC recipients (for bulk sends, recipients can't see each other)

        Returns:
            {
                'success': bool,
                'message_id': str or None,
                'error': str or None
            }
        """
        if not self.enabled:
            brand_info = f" for brand {self.brand.name}" if self.brand else ""
            logger.warning(f"Zoho Mail not configured{brand_info} - email not sent")
            return {
                'success': False,
                'message_id': None,
                'error': f'Zoho Mail not configured{brand_info}. Configure Zoho credentials in Brand settings or environment variables.'
            }

        # Check if recipient is unsubscribed (brand-specific)
        from crm.models import Contact
        contact = Contact.objects.filter(email__iexact=to).first()
        if contact:
            brand_slug = self.brand.slug if self.brand else None
            if contact.is_unsubscribed:
                logger.info(f"Skipping email to {to} - recipient is globally unsubscribed")
                return {
                    'success': False,
                    'message_id': None,
                    'error': f'Recipient {to} is unsubscribed and will not receive emails.'
                }
            elif brand_slug and contact.is_unsubscribed_from_brand(brand_slug):
                logger.info(f"Skipping email to {to} - recipient is unsubscribed from {brand_slug}")
                return {
                    'success': False,
                    'message_id': None,
                    'error': f'Recipient {to} is unsubscribed from {brand_slug} emails.'
                }

        # Use provided from_name or default to brand/service from_name
        sender_name = from_name or self.from_name

        # Add unsubscribe footer to email
        body = self._add_unsubscribe_footer(body, to)

        # Add tracking pixel if tracking_id provided
        if tracking_id:
            tracking_url = self._get_tracking_url(tracking_id)
            body = self._inject_tracking_pixel(body, tracking_url)

        # Prepare email data
        email_data = {
            'fromAddress': f"{sender_name} <{self.from_email}>",
            'toAddress': to,
            'subject': subject,
            'content': body,
            'mailFormat': 'html' if '<' in body and '>' in body else 'plaintext'
        }

        if reply_to:
            email_data['replyTo'] = reply_to

        # Add BCC recipients for bulk sends
        if bcc:
            email_data['bccAddress'] = ','.join(bcc)

        logger.info(f"Zoho Mail: Sending email to {to}, subject: {subject[:50]}...")
        result = self._make_request('POST', 'messages', json=email_data)

        if result and result.get('status', {}).get('code') == 200:
            message_id = result.get('data', {}).get('messageId', '')
            brand_info = f" ({self.brand.name})" if self.brand else ""
            bcc_count = len(bcc) if bcc else 0
            logger.info(f"Email sent successfully{brand_info} to {to} (BCC: {bcc_count}): {message_id}")
            return {
                'success': True,
                'message_id': message_id,
                'error': None,
                'bcc_count': bcc_count,
                'from_email': self.from_email,
            }
        else:
            # Build detailed error message
            if result is None:
                error_msg = 'Zoho API request failed - check server logs for details'
            elif result.get('status'):
                error_code = result.get('status', {}).get('code', 'unknown')
                error_desc = result.get('status', {}).get('description', 'Unknown error')
                error_msg = f"Zoho error {error_code}: {error_desc}"
            else:
                error_msg = f"Unexpected Zoho response: {str(result)[:200]}"

            logger.error(f"Failed to send email to {to}: {error_msg}")
            return {
                'success': False,
                'message_id': None,
                'error': error_msg,
                'from_email': self.from_email,
            }

    def _extract_first_name(self, text: str) -> str:
        """
        Extract first name from a string that might be concatenated names or have initials.
        Examples:
            'noushadkhalid' → 'Noushad'
            'satishph' → 'Satish' (ph = initials)
            'rajeshk' → 'Rajesh' (k = initial)
        """
        if not text or len(text) < 2:
            return text.title() if text else ''

        # Short names - use as-is
        if len(text) <= 6:
            return text.title()

        vowels = set('aeiou')
        text_lower = text.lower()

        # Check for trailing initials ONLY for reasonable length names (6-9 chars)
        # This catches: satishph (8), rajeshk (7), amitpk (6)
        if 6 <= len(text) <= 9:
            last = text_lower[-1]
            second_last = text_lower[-2]
            third_last = text_lower[-3] if len(text) >= 3 else ''

            # Single initial (e.g., rajeshk → rajesh + k)
            # Must have consonant at end, and removing it leaves 5-7 char name
            if last not in vowels and 5 <= len(text) - 1 <= 7:
                if second_last in vowels or second_last in 'hr':  # vowel or common endings
                    return text[:-1].title()

            # Double initials (e.g., satishph → satish + ph)
            if last not in vowels and second_last not in vowels and len(text) >= 7:
                if third_last in vowels or third_last in 'hrt':
                    if 4 <= len(text) - 2 <= 7:
                        return text[:-2].title()

        # For longer names (10+ chars), find consonant-consonant split
        if len(text) > 9:
            no_split = {'sh', 'ch', 'th', 'ph', 'wh', 'ck', 'gh', 'kh', 'ng', 'nk', 'nd', 'nt', 'st', 'sp', 'sk', 'sm', 'sn', 'sl', 'sw', 'sc', 'pr', 'tr', 'cr', 'br', 'dr', 'gr', 'fr'}

            for i in range(5, min(9, len(text))):
                prev = text_lower[i - 1]
                curr = text_lower[i]
                pair = prev + curr

                if pair in no_split:
                    continue

                if prev not in vowels and curr not in vowels:
                    return text[:i].title()

            # Fallback: use first 7 chars
            return text[:7].title()

        # Medium length (7-9 chars) without initials - probably full first name
        return text.title()

    def _get_smart_salutation(self, email: str) -> str:
        """
        Generate a smart salutation based on email address.
        - Generic emails (info@, admin@) → "Hi [Company] Team,"
        - Personal emails (john@, sana.patel@) → "Hi John," / "Hi Sana,"
        - Concatenated names (noushadkhalid@) → "Hi Noushad,"
        """
        GENERIC_PREFIXES = {
            'info', 'admin', 'sales', 'contact', 'hello', 'support', 'enquiry', 'enquiries',
            'team', 'office', 'marketing', 'hr', 'careers', 'jobs', 'accounts', 'billing',
            'help', 'service', 'services', 'general', 'mail', 'webmaster', 'noreply', 'no-reply',
            'reception', 'customerservice', 'customer-service', 'feedback', 'orders', 'booking',
            'bookings', 'reservations', 'press', 'media', 'partner', 'partners', 'enquire'
        }

        if not email or '@' not in email:
            return "Hi there,"

        email_prefix = email.split('@')[0].lower()
        email_domain = email.split('@')[1].lower()
        clean_prefix = email_prefix.replace('.', '').replace('_', '').replace('-', '')

        is_generic = email_prefix in GENERIC_PREFIXES or clean_prefix in GENERIC_PREFIXES

        if is_generic:
            # Extract company name from domain
            company = self._humanize_domain(email_domain)
            if company:
                return f"Hi {company} Team,"
            return "Hi Team,"

        # Personal email - extract first name
        # Check if there are separators
        if '.' in email_prefix or '_' in email_prefix or '-' in email_prefix:
            name_from_email = email_prefix.replace('.', ' ').replace('_', ' ').replace('-', ' ')
            first_name = name_from_email.split()[0].title()
        else:
            # No separators - might be concatenated name like "noushadkhalid"
            first_name = self._extract_first_name(email_prefix)

        if len(first_name) >= 2 and not first_name.isdigit():
            return f"Hi {first_name},"

        return "Hi there,"

    def _humanize_domain(self, domain: str) -> str:
        """Convert domain to human-readable company name."""
        if not domain:
            return ''

        parts = domain.lower().split('.')
        company_part = parts[0] if parts else domain

        # Check for RE/PM abbreviations at end
        re_abbrevs = [('re', ' RE'), ('pm', ' PM')]
        for abbrev, replacement in re_abbrevs:
            if company_part.endswith(abbrev) and len(company_part) > len(abbrev) + 2:
                return f"{company_part[:-len(abbrev)].title()}{replacement}"

        # Common patterns
        patterns = [
            ('realestate', 'Real Estate'), ('estateagents', 'Estate Agents'),
            ('properties', 'Properties'), ('property', 'Property'),
            ('homes', 'Homes'), ('group', 'Group'), ('agency', 'Agency'), ('agents', 'Agents'),
        ]

        for pattern, replacement in patterns:
            if pattern in company_part:
                before = company_part.split(pattern)[0]
                if before:
                    before = before.upper() if len(before) <= 4 else before.title()
                return f"{before} {replacement}".strip()

        return company_part.title()

    def _add_unsubscribe_footer(self, body: str, recipient_email: str) -> str:
        """
        Add unsubscribe footer to email body.

        Args:
            body: Original email body
            recipient_email: Recipient's email address for generating unsubscribe link

        Returns:
            Email body with unsubscribe footer added
        """
        from crm.views import generate_unsubscribe_token

        # Check if body already has unsubscribe link (from HTML templates)
        if 'unsubscribe' in body.lower() and ('href=' in body or 'http' in body):
            # HTML template already has unsubscribe link - skip adding footer
            return body

        # Generate unsubscribe URL using brand-aware function
        from crm.views import get_unsubscribe_url
        brand_slug = self.brand.slug if self.brand else 'desifirms'
        unsubscribe_url = get_unsubscribe_url(recipient_email, brand_slug, self.brand)

        # Check if body is HTML
        is_html = '<html' in body.lower() or '<body' in body.lower() or '<!doctype' in body.lower()

        if is_html:
            # For HTML emails, add a styled footer before </body>
            brand_name = self.brand.name if self.brand else 'Desi Firms'
            html_footer = f'''
<div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center;">
    <p style="color: #9ca3af; font-size: 12px; margin: 0;">
        <a href="{unsubscribe_url}" style="color: #9ca3af; text-decoration: underline;">Unsubscribe</a> from these emails
    </p>
    <p style="color: #9ca3af; font-size: 11px; margin: 8px 0 0 0;">
        This email was sent by {brand_name}. We respect your privacy.
    </p>
</div>
'''
            if '</body>' in body.lower():
                return body.replace('</body>', f'{html_footer}</body>')
            elif '</html>' in body.lower():
                return body.replace('</html>', f'{html_footer}</html>')
            else:
                return body + html_footer
        else:
            # Plain text footer
            brand_name = self.brand.name if self.brand else 'Desi Firms'
            footer = f"""

---
If you no longer wish to receive these emails, you can unsubscribe here:
{unsubscribe_url}

This email was sent by {brand_name}. We respect your privacy."""

            return body + footer

    def send_bulk(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> dict:
        """
        Send individual emails to each recipient (professional CRM approach).
        Each recipient sees their own email in "To" field - looks like personal 1-on-1 email.
        Automatically personalizes {{SALUTATION}} placeholder for each recipient.

        Args:
            recipients: List of email addresses
            subject: Email subject
            body: Email body (can contain {{SALUTATION}} placeholder)
            from_name: Sender display name
            reply_to: Reply-to address

        Returns:
            {
                'success': bool,
                'sent_count': int,
                'failed_count': int,
                'errors': list of error messages
            }
        """
        if not recipients:
            return {'success': False, 'error': 'No recipients', 'sent_count': 0, 'failed_count': 0}

        sent_count = 0
        failed_count = 0
        errors = []

        for recipient in recipients:
            # Personalize salutation for this recipient
            personalized_body = body
            if '{{SALUTATION}}' in body:
                salutation = self._get_smart_salutation(recipient)
                personalized_body = body.replace('{{SALUTATION}}', salutation)

            result = self.send(
                to=recipient,
                subject=subject,
                body=personalized_body,
                from_name=from_name,
                reply_to=reply_to
            )

            if result.get('success'):
                sent_count += 1
            else:
                failed_count += 1
                errors.append(f"{recipient}: {result.get('error', 'Unknown error')}")

        return {
            'success': sent_count > 0,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'errors': errors
        }

    def get_inbox_messages(
        self,
        since: Optional[datetime] = None,
        limit: int = 50,
        folder: str = 'inbox'
    ) -> List[dict]:
        """
        Fetch inbox messages for reply detection.

        Args:
            since: Only get messages after this datetime
            limit: Maximum number of messages to fetch
            folder: Folder to fetch from (inbox, sent, etc.)

        Returns:
            List of message dictionaries
        """
        if not self.enabled:
            return []

        params = {
            'limit': min(limit, 200),
            'sortorder': 'desc'
        }

        if since:
            # Zoho uses milliseconds since epoch
            params['receivedTime'] = int(since.timestamp() * 1000)

        # First get folder ID
        folders_result = self._make_request('GET', 'folders')
        if not folders_result:
            return []

        folder_id = None
        for f in folders_result.get('data', []):
            if f.get('path', '').lower() == folder.lower():
                folder_id = f.get('folderId')
                break

        if not folder_id:
            logger.warning(f"Folder '{folder}' not found")
            return []

        # Fetch messages
        result = self._make_request('GET', f'folders/{folder_id}/messages', params=params)

        if not result:
            return []

        messages = []
        for msg in result.get('data', []):
            messages.append({
                'message_id': msg.get('messageId', ''),
                'from_email': msg.get('fromAddress', ''),
                'to_email': msg.get('toAddress', ''),
                'subject': msg.get('subject', ''),
                'received_at': datetime.fromtimestamp(msg.get('receivedTime', 0) / 1000),
                'has_attachments': msg.get('hasAttachment', False),
                'is_read': msg.get('isRead', False),
                'summary': msg.get('summary', ''),
            })

        return messages

    def get_message_content(self, message_id: str) -> Optional[str]:
        """
        Get the full content of a specific message.

        Args:
            message_id: Zoho message ID

        Returns:
            Message body text or None
        """
        if not self.enabled:
            return None

        result = self._make_request('GET', f'messages/{message_id}/content')

        if result and result.get('data'):
            return result['data'].get('content', '')

        return None

    def _get_tracking_url(self, tracking_id: str) -> str:
        """Generate a tracking pixel URL."""
        if self.brand:
            site_url = self.brand.website
        else:
            site_url = getattr(settings, 'SITE_URL', 'https://www.codeteki.au')
        return f"{site_url}/api/crm/track/{tracking_id}/open.gif"

    def _inject_tracking_pixel(self, body: str, tracking_url: str) -> str:
        """Inject tracking pixel into email body."""
        tracking_pixel = f'<img src="{tracking_url}" width="1" height="1" style="display:none;" alt="" />'

        # If HTML email, inject before closing body tag
        if '</body>' in body.lower():
            return body.replace('</body>', f'{tracking_pixel}</body>')
        elif '<html>' in body.lower():
            # HTML but no body tag
            return body.replace('</html>', f'{tracking_pixel}</html>')
        else:
            # Plain text or simple HTML - wrap and add pixel
            return f"""<html>
<body>
{body}
{tracking_pixel}
</body>
</html>"""

    def match_reply_to_deal(self, from_email: str, subject: str = '') -> Optional['Deal']:
        """
        Try to match an incoming email to an existing deal.

        Args:
            from_email: Sender's email address
            subject: Email subject (for RE: matching)

        Returns:
            Deal object or None
        """
        from crm.models import Deal, EmailLog

        # Build query - filter by brand if this is a brand-specific service
        deal_filter = {
            'contact__email__iexact': from_email,
            'status': 'active'
        }
        if self.brand:
            deal_filter['pipeline__brand'] = self.brand

        deals = Deal.objects.filter(**deal_filter).order_by('-updated_at')

        if deals.exists():
            return deals.first()

        # Try to match by subject line (RE: Subject)
        if subject:
            # Remove RE:/FW: prefixes
            clean_subject = subject
            for prefix in ['RE:', 'Re:', 'FW:', 'Fw:', 'RE: RE:', 'Fwd:']:
                clean_subject = clean_subject.replace(prefix, '').strip()

            email_log_filter = {'subject__icontains': clean_subject}
            if self.brand:
                email_log_filter['deal__pipeline__brand'] = self.brand

            email_log = EmailLog.objects.filter(
                **email_log_filter
            ).select_related('deal').first()

            if email_log:
                return email_log.deal

        return None


class MockEmailService:
    """
    Mock email service for testing without Zoho credentials.
    Logs all email operations instead of sending.
    """

    def __init__(self, brand: Optional['Brand'] = None):
        self.brand = brand
        self.sent_emails = []
        self.from_name = brand.from_name if brand else 'Codeteki'
        self.from_email = brand.from_email if brand else 'test@example.com'

    @property
    def enabled(self) -> bool:
        return True

    def send(
        self,
        to: str,
        subject: str,
        body: str,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        tracking_id: Optional[str] = None,
        bcc: Optional[List[str]] = None
    ) -> dict:
        """Log email instead of sending."""
        sender_name = from_name or self.from_name
        email_record = {
            'to': to,
            'subject': subject,
            'body': body,
            'from_name': sender_name,
            'from_email': self.from_email,
            'reply_to': reply_to,
            'tracking_id': tracking_id,
            'bcc': bcc,
            'sent_at': timezone.now(),
            'brand': self.brand.name if self.brand else None
        }
        self.sent_emails.append(email_record)
        brand_info = f" ({self.brand.name})" if self.brand else ""
        bcc_count = len(bcc) if bcc else 0
        logger.info(f"[MOCK] Email logged{brand_info} to {to} (BCC: {bcc_count}): {subject}")

        return {
            'success': True,
            'message_id': f"mock-{len(self.sent_emails)}",
            'error': None,
            'bcc_count': bcc_count
        }

    def _extract_first_name(self, text: str) -> str:
        """Extract first name from concatenated names (e.g., 'noushadkhalid' → 'Noushad')."""
        if not text or len(text) < 2:
            return text.title() if text else ''
        if len(text) <= 8:
            return text.title()

        vowels = set('aeiou')
        no_split = {'sh', 'ch', 'th', 'ph', 'wh', 'ck', 'gh', 'kh', 'ng', 'nk', 'nd', 'nt', 'st', 'sp', 'sk', 'sm', 'sn', 'sl', 'sw', 'sc', 'pr', 'tr', 'cr', 'br', 'dr', 'gr', 'fr'}
        text_lower = text.lower()

        for i in range(4, min(9, len(text))):
            pair = text_lower[i-1:i+1]
            if pair in no_split:
                continue
            if text_lower[i-1] not in vowels and text_lower[i] not in vowels:
                return text[:i].title()

        return text[:6].title() if len(text) > 10 else text[:7].title()

    def _get_smart_salutation(self, email: str) -> str:
        """Generate smart salutation (same logic as ZohoEmailService)."""
        GENERIC_PREFIXES = {
            'info', 'admin', 'sales', 'contact', 'hello', 'support', 'enquiry', 'enquiries',
            'team', 'office', 'marketing', 'hr', 'accounts', 'billing', 'help', 'service',
            'general', 'mail', 'webmaster', 'noreply', 'reception', 'feedback', 'orders',
        }

        if not email or '@' not in email:
            return "Hi there,"

        email_prefix = email.split('@')[0].lower()
        email_domain = email.split('@')[1].lower()
        clean_prefix = email_prefix.replace('.', '').replace('_', '').replace('-', '')

        if email_prefix in GENERIC_PREFIXES or clean_prefix in GENERIC_PREFIXES:
            company = self._humanize_domain(email_domain)
            return f"Hi {company} Team," if company else "Hi Team,"

        # Check for separators
        if '.' in email_prefix or '_' in email_prefix or '-' in email_prefix:
            name_from_email = email_prefix.replace('.', ' ').replace('_', ' ').replace('-', ' ')
            first_name = name_from_email.split()[0].title()
        else:
            # Might be concatenated name like "noushadkhalid"
            first_name = self._extract_first_name(email_prefix)

        return f"Hi {first_name}," if len(first_name) >= 2 and not first_name.isdigit() else "Hi there,"

    def _humanize_domain(self, domain: str) -> str:
        """Convert domain to company name."""
        if not domain:
            return ''
        company_part = domain.lower().split('.')[0]
        for abbrev, repl in [('re', ' RE'), ('pm', ' PM')]:
            if company_part.endswith(abbrev) and len(company_part) > len(abbrev) + 2:
                return f"{company_part[:-len(abbrev)].title()}{repl}"
        for pattern, repl in [('realestate', 'Real Estate'), ('estateagents', 'Estate Agents'), ('agents', 'Agents')]:
            if pattern in company_part:
                before = company_part.split(pattern)[0]
                before = before.upper() if len(before) <= 4 else before.title() if before else ''
                return f"{before} {repl}".strip()
        return company_part.title()

    def send_bulk(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> dict:
        """Mock bulk send - logs individual personalized emails instead of sending."""
        if not recipients:
            return {'success': False, 'error': 'No recipients', 'sent_count': 0, 'failed_count': 0}

        sent_count = 0
        for recipient in recipients:
            # Personalize salutation
            personalized_body = body
            if '{{SALUTATION}}' in body:
                salutation = self._get_smart_salutation(recipient)
                personalized_body = body.replace('{{SALUTATION}}', salutation)

            self.send(
                to=recipient,
                subject=subject,
                body=personalized_body,
                from_name=from_name,
                reply_to=reply_to
            )
            sent_count += 1

        return {
            'success': True,
            'sent_count': sent_count,
            'failed_count': 0,
            'errors': []
        }

    def get_inbox_messages(self, since=None, limit=50, folder='inbox') -> List[dict]:
        """Return empty list for mock."""
        return []

    def get_message_content(self, message_id: str) -> Optional[str]:
        """Return None for mock."""
        return None


def get_email_service(brand: Optional['Brand'] = None) -> ZohoEmailService:
    """
    Factory function to get the appropriate email service for a brand.

    Args:
        brand: Optional Brand object. If provided, uses brand-specific Zoho credentials.

    Returns:
        ZohoEmailService if configured, otherwise MockEmailService.
    """
    global _brand_service_cache

    # Create cache key
    cache_key = brand.slug if brand else '__default__'

    # Return cached service if available
    if cache_key in _brand_service_cache:
        return _brand_service_cache[cache_key]

    # Create new service
    zoho_service = ZohoEmailService(brand=brand)
    if zoho_service.enabled:
        _brand_service_cache[cache_key] = zoho_service
        return zoho_service

    brand_info = f" for {brand.name}" if brand else ""
    logger.warning(f"Zoho Mail not configured{brand_info}, using MockEmailService")
    mock_service = MockEmailService(brand=brand)
    _brand_service_cache[cache_key] = mock_service
    return mock_service


def get_email_service_for_deal(deal: 'Deal') -> ZohoEmailService:
    """
    Get email service for a specific deal, using the deal's pipeline brand.

    Args:
        deal: Deal object

    Returns:
        ZohoEmailService configured for the deal's brand
    """
    brand = deal.pipeline.brand if deal.pipeline else None
    return get_email_service(brand=brand)


def send_styled_email(
    deal: 'Deal',
    subject: str,
    plain_body: str,
    email_type: Optional[str] = None,
    tracking_id: Optional[str] = None
) -> dict:
    """
    Send a styled HTML email for a deal, using the appropriate template.

    This function determines the brand, pipeline type, and email type from the deal,
    then renders the appropriate HTML template and sends the email.

    Args:
        deal: Deal object containing contact and pipeline info
        subject: Email subject
        plain_body: Plain text version of the email body
        email_type: Optional email type override (e.g., 'agent_invitation')
        tracking_id: Optional UUID for open tracking

    Returns:
        {
            'success': bool,
            'message_id': str or None,
            'error': str or None
        }
    """
    from crm.services.email_templates import (
        get_styled_email,
        get_email_type_for_stage,
        get_pipeline_type_from_name
    )

    # Get brand and pipeline info
    brand = deal.pipeline.brand if deal.pipeline else None
    brand_slug = brand.slug if brand else 'desifirms'
    pipeline_name = deal.pipeline.name if deal.pipeline else 'business'
    pipeline_type = get_pipeline_type_from_name(pipeline_name)

    # Get email type from stage if not provided
    if not email_type and deal.current_stage:
        email_type = get_email_type_for_stage(deal.current_stage.name)

    # If no email type found, use a generic template
    if not email_type:
        email_type = '_default'

    # Get contact info
    contact = deal.contact
    recipient_name = contact.first_name or contact.name.split()[0] if contact.name else 'there'
    recipient_email = contact.email
    recipient_company = contact.company or 'your business'

    # Get styled email content
    styled_content = get_styled_email(
        brand_slug=brand_slug,
        pipeline_type=pipeline_type,
        email_type=email_type,
        recipient_name=recipient_name,
        recipient_email=recipient_email,
        recipient_company=recipient_company,
        subject=subject,
        body=plain_body
    )

    # Get email service for the brand
    email_service = get_email_service(brand=brand)

    # Send the HTML version
    return email_service.send(
        to=recipient_email,
        subject=subject,
        body=styled_content['html'],
        tracking_id=tracking_id
    )


def clear_email_service_cache():
    """Clear the email service cache. Useful for testing or credential updates."""
    global _brand_service_cache
    _brand_service_cache = {}
