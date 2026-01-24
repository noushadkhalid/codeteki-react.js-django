# CRM AI Autopilot - Workflow Guide

A complete guide to the AI-powered CRM system for Codeteki and Desi Firms.

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Getting Started](#getting-started)
4. [Brands Configuration](#brands-configuration)
5. [Importing Contacts](#importing-contacts)
6. [Pipelines & Deals](#pipelines--deals)
7. [AI Email Automation](#ai-email-automation)
8. [Backlink Outreach](#backlink-outreach)
9. [Monitoring & Analytics](#monitoring--analytics)
10. [Celery Tasks](#celery-tasks)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The CRM AI Autopilot is a fully automated sales and backlink outreach system that:

- **Analyzes deals** using AI to determine the best next action
- **Composes personalized emails** based on contact and company context
- **Sends emails** via Zoho Mail API with open tracking
- **Monitors replies** and classifies them using AI
- **Supports multiple brands** with separate Zoho accounts

### Supported Brands

| Brand | Region | Email | Use Case |
|-------|--------|-------|----------|
| Codeteki | Australia (zoho.com.au) | sales@codeteki.au | AI/Web solutions sales |
| Desi Firms | US (zoho.com) | sales@desifirms.com.au | Business directory sales |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Django Admin                              │
│  (Brands, Contacts, Pipelines, Deals, Imports, Email Logs)      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Celery Beat Scheduler                       │
│  • process_pending_deals (hourly)                                │
│  • send_scheduled_emails (15 min)                                │
│  • check_email_replies (30 min)                                  │
│  • daily_ai_review (9 AM)                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Celery Worker                               │
│  Processes tasks asynchronously                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   AI Agent      │ │  Email Service  │ │  CSV Importer   │
│   (OpenAI)      │ │  (Zoho Mail)    │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## Getting Started

### Prerequisites

1. **Redis** - Message broker for Celery
2. **Zoho Mail API** - Credentials for each brand
3. **OpenAI API** - For AI email composition

### Start Services

```bash
# 1. Start Redis (if not running)
redis-server

# 2. Activate virtual environment
cd /Users/aptaa/2025-projects/Codeteki-django-react
source .venv/bin/activate
cd backend

# 3. Start Django
python manage.py runserver

# 4. Start Celery Worker (new terminal)
celery -A codeteki_site worker -l info

# 5. Start Celery Beat (new terminal)
celery -A codeteki_site beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Access Admin

**URL:** http://localhost:8000/admin/

**CRM Sections:**
- Brands - `/admin/crm/brand/`
- Contacts - `/admin/crm/contact/`
- Pipelines - `/admin/crm/pipeline/`
- Deals - `/admin/crm/deal/`
- Contact Imports - `/admin/crm/contactimport/`
- Email Logs - `/admin/crm/emaillog/`
- AI Decisions - `/admin/crm/aidecisionlog/`

---

## Brands Configuration

Each brand has its own:
- Zoho Mail credentials (different regions)
- Email templates and signatures
- AI context for personalization
- Pipelines and sequences

### Configure Brand

1. Go to **Admin → CRM → Brands**
2. Edit brand settings:

```
Email Configuration:
├── from_email: sales@codeteki.au
├── from_name: The Codeteki Team
└── reply_to_email: (optional)

Zoho Credentials:
├── zoho_client_id: 1000.XXX...
├── zoho_client_secret: XXX...
├── zoho_account_id: 692332000000002002
├── zoho_refresh_token: 1000.XXX...
└── zoho_api_domain: zoho.com.au (or zoho.com for US)

AI Configuration:
├── ai_company_description: "Codeteki is a digital agency..."
└── ai_value_proposition: "helping businesses grow..."
```

---

## Importing Contacts

### Method 1: Admin Interface

1. Go to **Admin → CRM → Contact Imports → Add**
2. Fill in:
   - **Brand:** Select brand
   - **File:** Upload CSV
   - **Contact Type:** lead, backlink_target, or partner
   - **Source:** Label for tracking (e.g., "LinkedIn Export")
   - **Create Deals:** ✓ Check to auto-create deals
   - **Pipeline:** Select pipeline for deals
3. Click **Save** - Import processes automatically

### Method 2: Command Line

```bash
# Preview CSV (dry run)
python manage.py import_contacts contacts.csv --brand codeteki --preview

# Import leads
python manage.py import_contacts contacts.csv --brand codeteki --type lead

# Import with deal creation
python manage.py import_contacts contacts.csv \
  --brand codeteki \
  --type lead \
  --source "Conference 2024" \
  --create-deals \
  --pipeline sales

# Import backlink targets
python manage.py import_contacts backlinks.csv \
  --brand codeteki \
  --type backlink_target \
  --create-deals \
  --pipeline backlink
```

### CSV Format

```csv
email,name,company,website,domain_authority,notes,tags
john@example.com,John Smith,Acme Corp,https://acme.com,45,Met at conference,"technology, startup"
sarah@cafe.com,Sarah Jones,Local Cafe,https://localcafe.com,28,Small business owner,"hospitality, local"
```

**Supported Columns:**
| Column | Variations Accepted |
|--------|---------------------|
| email | email, email_address, e-mail, contact_email |
| name | name, full_name, contact_name, first_name + last_name |
| company | company, company_name, organization, business |
| website | website, website_url, url, domain |
| domain_authority | domain_authority, da, dr, authority |
| notes | notes, note, comments, description |
| tags | tags, tag, labels, categories |

---

## Pipelines & Deals

### Default Pipelines

**Sales Pipeline (7 stages):**
1. New Lead
2. Contacted
3. Engaged
4. Qualified
5. Proposal Sent
6. Negotiation
7. Closed

**Backlink Pipeline (8 stages):**
1. Prospect
2. Researching
3. Initial Outreach
4. Follow Up 1
5. Follow Up 2
6. Interested
7. Link Placed
8. Verified

### Deal Workflow

```
Contact Imported
       │
       ▼
┌─────────────────┐
│  Deal Created   │ ← In first stage (e.g., "New Lead")
│  next_action_date = now
└─────────────────┘
       │
       ▼ (Celery: process_pending_deals)
       │
┌─────────────────┐
│  AI Analyzes    │ ← Decides: send_email, wait, move_stage, etc.
└─────────────────┘
       │
       ▼ (if action = send_email)
       │
┌─────────────────┐
│  AI Composes    │ ← Personalized email using brand context
│  Email          │
└─────────────────┘
       │
       ▼
┌─────────────────┐
│  Email Queued   │ ← EmailLog created with status='pending'
└─────────────────┘
       │
       ▼ (Celery: send_scheduled_emails)
       │
┌─────────────────┐
│  Email Sent     │ ← Via Zoho Mail API
│  via Zoho       │   Tracking pixel injected
└─────────────────┘
       │
       ▼
┌─────────────────┐
│  Deal Updated   │ ← emails_sent++, next_action_date set
└─────────────────┘
```

### Managing Deals

**Admin → CRM → Deals**

- **Filter by:** Pipeline, Stage, Status, Brand
- **Bulk Actions:** Move to stage, Pause deals
- **View:** Email history, AI decisions, Activities

---

## AI Email Automation

### How It Works

1. **Celery Beat** triggers `process_pending_deals` every hour
2. For each deal with `next_action_date <= now`:
   - AI analyzes deal context
   - Decides next action (send_email, wait, move_stage, etc.)
   - If send_email: Composes personalized email
3. Email is queued in `EmailLog`
4. **Celery Beat** triggers `send_scheduled_emails` every 15 min
5. Emails are sent via Zoho Mail API

### Email Personalization

The AI uses this context for emails:

```
SENDER INFORMATION:
- Sender Name: The Codeteki Team
- Company: Codeteki
- About Us: [ai_company_description]
- Value Proposition: [ai_value_proposition]

RECIPIENT INFORMATION:
- Name: John Smith
- Company: Tech Startup AU
- Website: https://techstartup.com.au
- Domain Authority: 35

CAMPAIGN CONTEXT:
- Pipeline: Sales Pipeline
- Current Stage: New Lead
- Emails Already Sent: 0
```

### Email Types

| Emails Sent | Type | Tone |
|-------------|------|------|
| 0 | Initial Outreach | Introduction, value prop |
| 1 | First Follow-up | Gentle reminder |
| 2 | Second Follow-up | Different angle |
| 3+ | Subsequent | Shorter, softer |

### Tracking

- **Open Tracking:** 1x1 pixel injected in emails
- **View Opens:** Admin → CRM → Email Logs → "Opened" column
- **Reply Detection:** Celery task polls inbox every 30 min

---

## Backlink Outreach

### Backlink-Specific Features

1. **Contact Type:** Set as `backlink_target`
2. **Domain Authority:** Tracked for prioritization
3. **AI Pitch:** Focuses on mutual benefit, collaboration

### Sample Backlink Email

```
Hi Sarah,

I'm reaching out from Codeteki. We admire the work you're
doing at Australian Tech Blog and believe there's a great
opportunity for us to collaborate.

We'd love to explore the possibility of contributing a
guest post that could benefit both our audiences.

Best regards,
The Codeteki Team
```

### Backlink Pipeline Stages

1. **Prospect** - Identified, not contacted
2. **Researching** - AI generating pitch angles
3. **Initial Outreach** - First email sent
4. **Follow Up 1/2** - Follow-up emails
5. **Interested** - Positive response received
6. **Link Placed** - Backlink published
7. **Verified** - Link confirmed active

---

## Monitoring & Analytics

### Admin Dashboards

**Email Logs** (`/admin/crm/emaillog/`)
- View all sent emails
- Track opens
- See Zoho message IDs

**AI Decisions** (`/admin/crm/aidecisionlog/`)
- Every AI decision logged
- Reasoning recorded
- Tokens used tracked

**Deal Activities** (`/admin/crm/dealactivity/`)
- Stage changes
- Emails sent/opened
- AI actions

### Celery Monitoring

**Task Results** (`/admin/django_celery_results/taskresult/`)
- View task history
- See success/failure
- Check execution time

**Periodic Tasks** (`/admin/django_celery_beat/periodictask/`)
- View schedules
- Enable/disable tasks
- Modify intervals

---

## Celery Tasks

### Scheduled Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `process_pending_deals` | Every hour | AI analyzes deals, queues actions |
| `send_scheduled_emails` | Every 15 min | Sends pending emails via Zoho |
| `check_email_replies` | Every 30 min | Polls inbox for replies |
| `daily_ai_review` | 9:00 AM | Daily deal review, scoring |

### Manual Task Execution

```python
# Django shell
from crm.tasks import process_pending_deals, send_scheduled_emails

# Run immediately
process_pending_deals.delay()
send_scheduled_emails.delay()

# Process specific deal
from crm.tasks import queue_deal_email
queue_deal_email.delay(deal_id='uuid-here', email_type='followup')

# Process CSV import
from crm.tasks import process_contact_import
process_contact_import.delay(import_id='uuid-here')
```

### View Task Logs

```bash
# Watch Celery worker output
tail -f /tmp/claude/.../bc5a96f.output

# Or in terminal where worker is running
celery -A codeteki_site worker -l info
```

---

## Troubleshooting

### Common Issues

**1. Emails not sending**
```bash
# Check Zoho credentials
python manage.py shell -c "
from crm.services.email_service import get_email_service
from crm.models import Brand
brand = Brand.objects.get(slug='codeteki')
service = get_email_service(brand)
print(f'Enabled: {service.enabled}')
print(f'Token: {service._get_access_token()[:20] if service._get_access_token() else \"FAILED\"}')"
```

**2. Celery tasks not running**
```bash
# Check Redis
redis-cli ping

# Check Celery worker
ps aux | grep celery

# Restart worker
pkill -f "celery.*worker"
celery -A codeteki_site worker -l info
```

**3. AI not generating emails**
```bash
# Check OpenAI API key
python manage.py shell -c "
from django.conf import settings
print(f'API Key: {settings.OPENAI_API_KEY[:10]}...')"
```

**4. Import failing**
- Check CSV encoding (UTF-8 with BOM supported)
- Ensure email column exists
- Check for duplicate emails

### Refresh Zoho Token

If Zoho token expires:

```bash
# Generate new authorization code from Zoho API Console
# Then exchange for refresh token:

curl -X POST "https://accounts.zoho.com.au/oauth/v2/token" \
  -d "grant_type=authorization_code" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_SECRET" \
  -d "code=NEW_AUTH_CODE"

# Update in Admin → Brands → [Brand] → Zoho Credentials
```

---

## Environment Variables

```bash
# .env file

# Zoho Mail (Codeteki - default)
ZOHO_CLIENT_ID=1000.XXX
ZOHO_CLIENT_SECRET=XXX
ZOHO_REFRESH_TOKEN=1000.XXX
ZOHO_ACCOUNT_ID=692332000000002002
ZOHO_FROM_EMAIL=sales@codeteki.au
ZOHO_API_DOMAIN=zoho.com.au

# OpenAI
OPENAI_API_KEY=sk-XXX

# Site
SITE_URL=https://www.codeteki.au
```

---

## Quick Reference

### URLs

| Resource | URL |
|----------|-----|
| Admin Home | http://localhost:8000/admin/ |
| Brands | http://localhost:8000/admin/crm/brand/ |
| Contacts | http://localhost:8000/admin/crm/contact/ |
| Deals | http://localhost:8000/admin/crm/deal/ |
| Imports | http://localhost:8000/admin/crm/contactimport/ |
| Email Logs | http://localhost:8000/admin/crm/emaillog/ |
| Periodic Tasks | http://localhost:8000/admin/django_celery_beat/periodictask/ |

### Commands

```bash
# Start all services
redis-server &
python manage.py runserver &
celery -A codeteki_site worker -l info &
celery -A codeteki_site beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

# Import contacts
python manage.py import_contacts file.csv --brand codeteki --type lead

# Seed default pipelines
python manage.py seed_crm_pipelines

# Test email
python manage.py shell -c "
from crm.models import Brand
from crm.services.email_service import get_email_service
brand = Brand.objects.get(slug='codeteki')
service = get_email_service(brand)
result = service.send('test@example.com', 'Test', '<p>Test email</p>')
print(result)"
```

---

## Support

For issues or questions:
- Check logs in Django admin
- Review Celery worker output
- Verify Zoho credentials in brand settings

---

*Last updated: January 2026*
