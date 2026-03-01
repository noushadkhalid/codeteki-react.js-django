# ZeptoMail Migration Guide — Replacing Mailgun with ZeptoMail

> For Desi Firms project. Based on the working ZeptoMail implementation in Codeteki CRM.

---

## Why ZeptoMail

- Already verified `desifirms.com.au` domain in ZeptoMail (used by Codeteki CRM)
- Significantly cheaper than Mailgun for transactional email
- Part of Zoho ecosystem (same account, single dashboard)
- Simple API key auth — no complex OAuth flows
- Built-in bounce/spam webhooks

---

## 1. ZeptoMail Account Setup

### Get Your API Key

1. Log in to [ZeptoMail](https://zeptomail.zoho.com.au/)
2. Go to **Mail Agents** → select or create a mail agent for Desi Firms
3. Copy the **API key** — it looks like: `Zoho-enczapikey PHtE6r0...`
4. The key goes in the `Authorization` header (no `Bearer` prefix)

### Domain Verification (Already Done)

The `desifirms.com.au` domain is already verified via DNS records:
- **SPF** — `include:zeptomail.com.au` in your SPF record
- **DKIM** — CNAME records added during Zoho setup
- **DMARC** — `_dmarc.desifirms.com.au` TXT record

If you're adding a new domain, go to **Mail Agents → Sending Domains → Add Domain** and follow the DNS verification steps.

### Regional API Host

| Region    | API Host                  |
|-----------|---------------------------|
| US        | `api.zeptomail.com`       |
| Australia | `api.zeptomail.com.au`    |

Use `api.zeptomail.com.au` for Desi Firms (Australian domain).

---

## 2. Environment Variables

Add these to your `.env` file:

```env
# ZeptoMail Configuration
ZEPTOMAIL_API_KEY=Zoho-enczapikey PHtE6r0...your-key-here
ZEPTOMAIL_HOST=api.zeptomail.com.au
ZEPTOMAIL_FROM_EMAIL=noreply@desifirms.com.au
ZEPTOMAIL_FROM_NAME=Desi Firms

# Webhook authentication (any random secret string)
ZEPTOMAIL_WEBHOOK_KEY=your-random-secret-key-here
```

---

## 3. Sending Email via ZeptoMail API

### API Endpoint

```
POST https://api.zeptomail.com.au/v1.1/email
```

### Headers

```python
headers = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'authorization': 'Zoho-enczapikey PHtE6r0...your-key-here',
}
```

### Request Payload — Single Email

```python
import requests

payload = {
    "from": {
        "address": "noreply@desifirms.com.au",
        "name": "Desi Firms"
    },
    "to": [
        {
            "email_address": {
                "address": "recipient@example.com",
                "name": "John Doe"  # optional
            }
        }
    ],
    "subject": "Welcome to Desi Firms",
    "htmlbody": "<html><body><h1>Hello!</h1></body></html>",
    # OR use "textbody" for plain text:
    # "textbody": "Hello!",
}

# Optional fields
payload["reply_to"] = [{"address": "support@desifirms.com.au"}]
payload["bcc"] = [{"email_address": {"address": "archive@desifirms.com.au"}}]
payload["cc"] = [{"email_address": {"address": "team@desifirms.com.au"}}]

response = requests.post(
    "https://api.zeptomail.com.au/v1.1/email",
    json=payload,
    headers=headers,
    timeout=30,
)
```

### Success Response (HTTP 200)

```json
{
    "message": "OK",
    "request_id": "abc123def456",
    "data": [
        {
            "code": "0",
            "additional_info": [],
            "message": "OK"
        }
    ]
}
```

### Error Response

```json
{
    "error": {
        "code": "552",
        "details": [
            {
                "code": "552",
                "message": "Mailbox not found",
                "target": "recipient@example.com"
            }
        ]
    }
}
```

### Python Send Function (Standalone)

```python
import requests
import os
import logging

logger = logging.getLogger(__name__)

ZEPTOMAIL_API_KEY = os.getenv("ZEPTOMAIL_API_KEY")
ZEPTOMAIL_HOST = os.getenv("ZEPTOMAIL_HOST", "api.zeptomail.com.au")
ZEPTOMAIL_FROM_EMAIL = os.getenv("ZEPTOMAIL_FROM_EMAIL", "noreply@desifirms.com.au")
ZEPTOMAIL_FROM_NAME = os.getenv("ZEPTOMAIL_FROM_NAME", "Desi Firms")


def send_email(to_email, subject, html_body, reply_to=None, from_name=None):
    """
    Send a single email via ZeptoMail API.

    Returns dict with 'success', 'message_id', 'error' keys.
    """
    url = f"https://{ZEPTOMAIL_HOST}/v1.1/email"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": ZEPTOMAIL_API_KEY,
    }

    payload = {
        "from": {
            "address": ZEPTOMAIL_FROM_EMAIL,
            "name": from_name or ZEPTOMAIL_FROM_NAME,
        },
        "to": [
            {
                "email_address": {
                    "address": to_email,
                }
            }
        ],
        "subject": subject,
        "htmlbody": html_body,
    }

    if reply_to:
        payload["reply_to"] = [{"address": reply_to}]

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()

        if response.status_code == 200 or data.get("message") == "OK":
            return {
                "success": True,
                "message_id": data.get("request_id", ""),
                "error": None,
            }
        else:
            error_msg = str(data.get("error", data.get("message", "Unknown error")))
            logger.error(f"ZeptoMail error sending to {to_email}: {error_msg}")
            return {
                "success": False,
                "message_id": None,
                "error": error_msg,
                "is_hard_bounce": _is_hard_bounce(error_msg),
            }

    except requests.exceptions.Timeout:
        return {"success": False, "message_id": None, "error": "ZeptoMail API timeout"}
    except Exception as e:
        return {"success": False, "message_id": None, "error": str(e)}


# --- Hard Bounce Detection ---

HARD_BOUNCE_PATTERNS = [
    "invalid email", "invalid address", "mailbox not found",
    "mailbox unavailable", "user unknown", "user not found",
    "no such user", "address rejected", "recipient rejected",
    "does not exist", "account disabled", "account has been disabled",
    "address not found", "invalid recipient", "undeliverable",
    "permanently rejected", "hard bounce", "bad destination",
    "unknown user", "550", "551", "552", "553", "554",
]


def _is_hard_bounce(error_msg):
    if not error_msg:
        return False
    error_lower = error_msg.lower()
    return any(pattern in error_lower for pattern in HARD_BOUNCE_PATTERNS)
```

---

## 4. Bounce & Spam Webhook

ZeptoMail can notify you when emails bounce or get reported as spam.

### Webhook Endpoint (Django Example)

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("webhooks/bounce/", views.ZeptoMailBounceWebhookView.as_view()),
]
```

```python
# views.py
import json
import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

SOFT_BOUNCE_THRESHOLD = 3  # auto-escalate after 3 soft bounces


@method_decorator(csrf_exempt, name="dispatch")
class ZeptoMailBounceWebhookView(View):
    """Handle ZeptoMail bounce and spam report webhooks."""

    def post(self, request):
        # --- Auth check ---
        webhook_key = os.getenv("ZEPTOMAIL_WEBHOOK_KEY", "")
        if webhook_key:
            auth_header = request.headers.get("Authorization", "")
            if auth_header != webhook_key:
                return JsonResponse({"error": "Unauthorized"}, status=401)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # --- Parse event ---
        event_names = data.get("event_name", [])
        event_messages = data.get("event_message", [])

        results = []
        for event_name in event_names:
            for msg in event_messages:
                email = self._extract_email(event_name, msg)
                if not email:
                    continue

                if event_name == "hardbounce":
                    result = self._handle_hard_bounce(email)
                elif event_name == "softbounce":
                    result = self._handle_soft_bounce(email)
                elif event_name in ("feedback_loop", "spam"):
                    result = self._handle_spam_report(email)
                else:
                    result = {"status": "ignored", "event": event_name}

                results.append(result)

        return JsonResponse({"results": results})

    def _extract_email(self, event_name, msg):
        """Extract recipient email from ZeptoMail webhook payload."""
        if event_name in ("hardbounce", "softbounce"):
            # Bounce events: nested under event_data.details
            for ed in msg.get("event_data", []):
                for detail in ed.get("details", []):
                    email = detail.get("bounced_recipient")
                    if email:
                        return email.strip().lower()
        elif event_name in ("feedback_loop", "spam"):
            # Spam reports: under to[].email_address.address
            for to in msg.get("to", []):
                email = to.get("email_address", {}).get("address")
                if email:
                    return email.strip().lower()
        return None

    def _handle_hard_bounce(self, email):
        """
        Mark contact as bounced. Close all active deals.
        Replace with your own model logic.
        """
        logger.warning(f"Hard bounce: {email}")
        # TODO: Your logic here — e.g.:
        # contact = Contact.objects.filter(email=email).first()
        # contact.email_bounced = True
        # contact.bounced_at = timezone.now()
        # contact.save()
        return {"email": email, "action": "hard_bounce"}

    def _handle_soft_bounce(self, email):
        """
        Track soft bounce count. Escalate to hard bounce after threshold.
        """
        logger.info(f"Soft bounce: {email}")
        # TODO: Your logic here — e.g.:
        # contact.soft_bounce_count += 1
        # if contact.soft_bounce_count >= SOFT_BOUNCE_THRESHOLD:
        #     return self._handle_hard_bounce(email)
        return {"email": email, "action": "soft_bounce"}

    def _handle_spam_report(self, email):
        """
        Recipient reported spam. Treat as unsubscribe.
        """
        logger.warning(f"Spam report: {email}")
        # TODO: Your logic here — e.g.:
        # contact.is_unsubscribed = True
        # contact.spam_reported = True
        # contact.save()
        return {"email": email, "action": "spam_report"}
```

### ZeptoMail Webhook Payload Examples

**Hard Bounce:**
```json
{
    "event_name": ["hardbounce"],
    "event_message": [{
        "event_data": [{
            "details": [{
                "bounced_recipient": "bad@example.com"
            }]
        }]
    }]
}
```

**Soft Bounce:**
```json
{
    "event_name": ["softbounce"],
    "event_message": [{
        "event_data": [{
            "details": [{
                "bounced_recipient": "full-inbox@example.com"
            }]
        }]
    }]
}
```

**Spam / Feedback Loop:**
```json
{
    "event_name": ["feedback_loop"],
    "event_message": [{
        "to": [{
            "email_address": {
                "address": "reporter@example.com"
            }
        }]
    }]
}
```

### Configure in ZeptoMail Dashboard

1. Go to **Mail Agents → your agent → Webhooks**
2. Add webhook URL: `https://your-domain.com/api/webhooks/bounce/`
3. Select events: **Hard bounced**, **Soft bounced**, **Feedback loop**
4. Set **Authorization headers** to your `ZEPTOMAIL_WEBHOOK_KEY` value
5. Save and test

---

## 5. Mailgun → ZeptoMail Migration Checklist

### Before Migration

- [ ] Verify `desifirms.com.au` domain is active in ZeptoMail (already done)
- [ ] Get ZeptoMail API key from dashboard
- [ ] Choose API host (`api.zeptomail.com.au` for Australia)
- [ ] Set up environment variables

### Code Changes

- [ ] Replace Mailgun API calls with ZeptoMail `send_email()` function
- [ ] Update `Authorization` header (Mailgun uses `api:key-xxx`, ZeptoMail uses raw API key)
- [ ] Update request payload format (see Section 3 above)
- [ ] Update response handling (ZeptoMail returns `request_id`, not `id`)
- [ ] Add bounce webhook endpoint
- [ ] Update error handling for ZeptoMail error format

### Key Differences: Mailgun vs ZeptoMail

| Feature | Mailgun | ZeptoMail |
|---------|---------|-----------|
| **Auth** | `api:key-xxx` (Basic Auth) | API key in `Authorization` header |
| **Endpoint** | `api.mailgun.net/v3/{domain}/messages` | `api.zeptomail.com.au/v1.1/email` |
| **From format** | `"Name <email>"` string | `{"address": "...", "name": "..."}` object |
| **To format** | Comma-separated string | Array of `email_address` objects |
| **HTML body** | `html` field | `htmlbody` field |
| **Text body** | `text` field | `textbody` field |
| **Reply-To** | `h:Reply-To` header | `reply_to` array |
| **Response ID** | `id` field (Message-ID) | `request_id` field |
| **Webhooks** | Signature-based verification | Authorization header key |
| **Bounce payload** | `event-data.recipient` | `event_message[].event_data[].details[].bounced_recipient` |

### DNS Changes

If your Mailgun SPF/DKIM records are separate from ZeptoMail, update:

- **SPF**: Replace `include:mailgun.org` with `include:zeptomail.com.au`
- **DKIM**: Remove Mailgun CNAME records, ensure ZeptoMail CNAME records are present
- Keep **DMARC** record as-is (it's provider-agnostic)

> If you already have ZeptoMail DNS records (which you do for desifirms.com.au), you only need to remove the Mailgun entries after migration.

### After Migration

- [ ] Send test email via ZeptoMail API
- [ ] Verify email lands in inbox (not spam)
- [ ] Test bounce webhook with a known invalid address
- [ ] Monitor delivery rates in ZeptoMail dashboard for first week
- [ ] Remove Mailgun API key from environment
- [ ] Cancel Mailgun subscription

---

## 6. ZeptoMail Pricing Reference

- **Free tier**: 100 emails/month
- **Pay-as-you-go**: Purchase email credits (no monthly subscription)
- ~10,000 emails for ~$2.50 USD (varies by region)
- No expiry on purchased credits
- Much cheaper than Mailgun's minimum $35/month plan

---

## 7. Rate Limits & Best Practices

- ZeptoMail rate limit: **Varies by plan** (typically 100-500 emails/minute)
- Add retry logic with exponential backoff for HTTP 429 responses
- Use `htmlbody` (not `textbody`) for styled emails — better deliverability
- Always include an unsubscribe link in marketing/outreach emails
- Monitor the ZeptoMail dashboard for deliverability metrics
- Use the webhook for bounce handling instead of polling

---

## 8. Quick Reference — Copy-Paste Snippets

### Minimal Send (Python)

```python
import requests

resp = requests.post(
    "https://api.zeptomail.com.au/v1.1/email",
    json={
        "from": {"address": "noreply@desifirms.com.au", "name": "Desi Firms"},
        "to": [{"email_address": {"address": "test@example.com"}}],
        "subject": "Test",
        "htmlbody": "<p>Hello from ZeptoMail!</p>",
    },
    headers={
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Zoho-enczapikey YOUR_KEY_HERE",
    },
    timeout=30,
)
print(resp.json())
```

### Django Settings

```python
# settings.py
ZEPTOMAIL_API_KEY = os.getenv("ZEPTOMAIL_API_KEY", "")
ZEPTOMAIL_HOST = os.getenv("ZEPTOMAIL_HOST", "api.zeptomail.com.au")
ZEPTOMAIL_FROM_EMAIL = os.getenv("ZEPTOMAIL_FROM_EMAIL", "noreply@desifirms.com.au")
ZEPTOMAIL_FROM_NAME = os.getenv("ZEPTOMAIL_FROM_NAME", "Desi Firms")
ZEPTOMAIL_WEBHOOK_KEY = os.getenv("ZEPTOMAIL_WEBHOOK_KEY", "")
```

### .env File

```env
ZEPTOMAIL_API_KEY=Zoho-enczapikey PHtE6r0...
ZEPTOMAIL_HOST=api.zeptomail.com.au
ZEPTOMAIL_FROM_EMAIL=noreply@desifirms.com.au
ZEPTOMAIL_FROM_NAME=Desi Firms
ZEPTOMAIL_WEBHOOK_KEY=your-webhook-secret
```
