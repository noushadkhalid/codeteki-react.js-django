# CRM Implementation Guide

Internal documentation for implementing AI-Powered CRM for clients.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [CRM Types](#crm-types)
4. [Implementation Steps](#implementation-steps)
5. [Type 1: Real Estate CRM](#type-1-real-estate-crm)
6. [Type 2: Business Directory CRM](#type-2-business-directory-crm)
7. [Type 3: B2B Sales CRM](#type-3-b2b-sales-crm)
8. [AI Configuration](#ai-configuration)
9. [Email Setup](#email-setup)
10. [Go-Live Checklist](#go-live-checklist)
11. [Maintenance & Support](#maintenance--support)

---

## Overview

Our CRM system provides AI-powered sales automation with three distinct implementations:

| CRM Type | Target Industry | Primary Goal | Typical Pipeline Length |
|----------|----------------|--------------|------------------------|
| Real Estate | Real estate agents/agencies | Agent registrations | 6-8 stages |
| Business Directory | Local businesses | Free listings signup | 6-8 stages |
| B2B Sales | Service businesses | Client acquisition | 7-9 stages |

### Key Features (All Types)
- AI-powered email composition (problem-solving approach)
- Visual Kanban pipeline boards
- Multi-brand support from single dashboard
- Automated follow-up sequences
- Email tracking (opens, replies)
- Brand-specific unsubscribe management
- "Powered by Codeteki" footer with UTM tracking

---

## Prerequisites

### Technical Requirements

```bash
# Required environment variables
ZOHO_CLIENT_ID=xxx
ZOHO_CLIENT_SECRET=xxx
ZOHO_REFRESH_TOKEN=xxx
ZOHO_ACCOUNT_ID=xxx

# AI (already configured in main settings)
ANTHROPIC_API_KEY=xxx
```

### Client Requirements

Before starting implementation, collect:

1. **Brand Information**
   - Company name
   - Logo (PNG, min 200x200px)
   - Primary brand color (hex code)
   - Website URL
   - Contact email for sending

2. **Email Configuration**
   - Sender name (e.g., "John from CompanyName")
   - Reply-to email address
   - Email signature content

3. **Business Context for AI**
   - Business description (2-3 sentences)
   - Target audience description
   - Key value propositions
   - Any current promotions/updates
   - Preferred tone (professional, friendly, casual)

4. **Pipeline Requirements**
   - Number of stages needed
   - Stage names and order
   - Follow-up timing preferences
   - Lost deal reason categories

---

## CRM Types

### Type 1: Real Estate CRM
**Best for:** Real estate portals, agent directories, property platforms

**Use case:** Invite real estate agents to register on your platform, list properties, or partner with your service.

**Default stages:**
1. Identified → 2. Invitation Sent → 3. Follow-up 1 → 4. Follow-up 2 → 5. Responded → 6. Registered → 7. Listing → 8. Lost

---

### Type 2: Business Directory CRM
**Best for:** Business directories, local listing sites, review platforms

**Use case:** Invite local businesses to claim their free listing, upgrade to premium, or add their business to your directory.

**Default stages:**
1. Business Found → 2. Invited → 3. Follow Up 1 → 4. Follow Up 2 → 5. Responded → 6. Signed Up → 7. Listed → 8. Lost

---

### Type 3: B2B Sales CRM
**Best for:** Service agencies, consultancies, SaaS companies

**Use case:** Nurture leads from initial contact through discovery calls to becoming paying clients.

**Default stages:**
1. Lead Found → 2. Intro Sent → 3. Follow Up 1 → 4. Follow Up 2 → 5. Responded → 6. Discovery Call → 7. Proposal Sent → 8. Negotiating → 9. Client → 10. Lost

---

## Implementation Steps

### Step 1: Create Brand (15 mins)

```
Admin → CRM → Brands → Add Brand
```

**Required Fields:**

| Field | Description | Example |
|-------|-------------|---------|
| Name | Brand display name | "Sydney Business Hub" |
| Slug | URL-safe identifier | "sydney-biz-hub" |
| Website | Brand website | "https://sydneybusinesshub.com.au" |
| Primary Color | Hex color for emails | "#0093E9" |
| From Email | Sender email address | "hello@sydneybusinesshub.com.au" |
| From Name | Sender display name | "Sarah from Sydney Business Hub" |

**AI Configuration Fields:**

| Field | Description | Example |
|-------|-------------|---------|
| AI Business Updates | Recent news for AI context | "Just launched premium listings with Google Maps integration" |
| AI Target Context | Target audience description | "Local Sydney businesses, restaurants, tradies, retail shops" |
| AI Approach Style | Email approach | "problem_solving" (recommended) |

**Approach Style Options:**
- `problem_solving` - Focus on solving customer problems (recommended)
- `value_driven` - Emphasize value and benefits
- `relationship` - Build personal connections
- `direct` - Straightforward and concise

---

### Step 2: Create Pipeline (20 mins)

```
Admin → CRM → Pipelines → Add Pipeline
```

**Pipeline Fields:**

| Field | Value |
|-------|-------|
| Name | "Real Estate Outreach" or "Business Directory" or "Sales Pipeline" |
| Brand | Select brand created in Step 1 |
| Pipeline Type | real_estate / business_directory / sales |
| Is Active | ✓ Checked |

**Create Pipeline Stages:**

After saving the pipeline, add stages via inline form or:
```
Admin → CRM → Pipeline Stages → Add
```

#### Real Estate Pipeline Stages

| Order | Stage Name | Stage Type | Days Until Next | Auto Send Email |
|-------|------------|------------|-----------------|-----------------|
| 1 | Identified | regular | 0 | ✗ |
| 2 | Invitation Sent | regular | 3 | ✓ |
| 3 | Follow-up 1 | regular | 4 | ✓ |
| 4 | Follow-up 2 | regular | 5 | ✓ |
| 5 | Responded | regular | 0 | ✗ |
| 6 | Registered | won | 0 | ✓ (welcome) |
| 7 | Listing | won | 0 | ✗ |
| 8 | Lost | lost | 0 | ✗ |

#### Business Directory Pipeline Stages

| Order | Stage Name | Stage Type | Days Until Next | Auto Send Email |
|-------|------------|------------|-----------------|-----------------|
| 1 | Business Found | regular | 0 | ✗ |
| 2 | Invited | regular | 3 | ✓ |
| 3 | Follow Up 1 | regular | 4 | ✓ |
| 4 | Follow Up 2 | regular | 5 | ✓ |
| 5 | Responded | regular | 0 | ✗ |
| 6 | Signed Up | won | 0 | ✓ (welcome) |
| 7 | Listed | won | 0 | ✗ |
| 8 | Lost | lost | 0 | ✗ |

#### B2B Sales Pipeline Stages

| Order | Stage Name | Stage Type | Days Until Next | Auto Send Email |
|-------|------------|------------|-----------------|-----------------|
| 1 | Lead Found | regular | 0 | ✗ |
| 2 | Intro Sent | regular | 3 | ✓ |
| 3 | Follow Up 1 | regular | 4 | ✓ |
| 4 | Follow Up 2 | regular | 7 | ✓ |
| 5 | Responded | regular | 0 | ✗ |
| 6 | Discovery Call | regular | 0 | ✓ (confirmation) |
| 7 | Proposal Sent | regular | 3 | ✓ |
| 8 | Negotiating | regular | 0 | ✗ |
| 9 | Client | won | 0 | ✓ (welcome) |
| 10 | Lost | lost | 0 | ✗ |

---

### Step 3: Configure Email Templates (30 mins)

For each stage that sends emails, create or customize templates:

```
Admin → CRM → Email Templates → Add
```

**Template Fields:**

| Field | Description |
|-------|-------------|
| Brand | Select the brand |
| Pipeline Type | real_estate / business_directory / sales |
| Email Type | Stage-specific (e.g., agent_invitation, directory_followup_1) |
| Subject Template | Email subject with variables |
| Body Template | HTML template path or inline content |

**Available Template Variables:**

```
{{ recipient_name }} - Contact's name
{{ recipient_email }} - Contact's email
{{ recipient_company }} - Contact's company/business name
{{ brand_name }} - Your brand name
{{ brand_website }} - Your website URL
{{ unsubscribe_url }} - Auto-generated unsubscribe link
{{ current_year }} - Current year for copyright
```

**Email Type Mapping:**

| Pipeline | Stage | Email Type |
|----------|-------|------------|
| Real Estate | Invitation Sent | agent_invitation |
| Real Estate | Follow-up 1 | agent_followup_1 |
| Real Estate | Follow-up 2 | agent_followup_2 |
| Real Estate | Registered | agent_registered |
| Business | Invited | directory_invitation |
| Business | Follow Up 1 | directory_followup_1 |
| Business | Follow Up 2 | directory_followup_2 |
| Business | Signed Up | business_signedup |
| Sales | Intro Sent | services_intro |
| Sales | Follow Up 1 | sales_followup |
| Sales | Follow Up 2 | sales_followup_2 |
| Sales | Discovery Call | discovery_scheduled |
| Sales | Client | welcome_client |

---

### Step 4: Import Contacts (Variable)

#### Option A: Manual Entry
```
Admin → CRM → Contacts → Add Contact
```

#### Option B: Bulk Import via CSV

Prepare CSV with columns:
```csv
name,email,company,phone,source,tags
John Smith,john@example.com,ABC Realty,0412345678,website,real-estate;sydney
```

Run import command:
```bash
python manage.py import_contacts --brand=brand-slug --file=contacts.csv
```

#### Option C: API Integration

```python
POST /api/crm/contacts/
{
    "name": "John Smith",
    "email": "john@example.com",
    "company": "ABC Realty",
    "brand": "brand-slug",
    "source": "api"
}
```

---

### Step 5: Create Initial Deals (10 mins)

For each contact to enter the pipeline:

#### Option A: Admin Action (Bulk)
1. Go to `Admin → CRM → Contacts`
2. Select contacts
3. Choose action: "Add to Pipeline" or "Add to Pipeline (Follow-up Stage)"
4. Execute

#### Option B: Automatic on Contact Creation
Contacts with `auto_create_deal=True` will automatically create a deal in the brand's default pipeline.

#### Option C: Manual Deal Creation
```
Admin → CRM → Deals → Add Deal
```

| Field | Value |
|-------|-------|
| Contact | Select contact |
| Pipeline | Select pipeline |
| Stage | Starting stage (usually "Identified" or "Lead Found") |
| Status | active |

---

### Step 6: Test the Pipeline (30 mins)

1. **Create test contact** with your own email
2. **Create deal** in the pipeline
3. **Send test email** using admin action "Send AI Email"
4. **Verify email received** with correct branding
5. **Test unsubscribe link** - should mark deal as lost with reason "unsubscribed"
6. **Check pipeline board** at `/admin/crm/pipeline/{id}/board/`

---

## AI Configuration

### System Prompt Customization

The AI uses a context-aware system prompt. Key configurations per brand:

```python
# In Brand model
ai_business_updates = """
- Just launched: Premium listings with Google Maps
- New feature: Customer reviews and ratings
- Promotion: First month free for early adopters
"""

ai_target_context = """
Target: Local Sydney businesses including restaurants,
cafes, retail shops, tradies, and professional services.
Pain points: Low online visibility, no Google presence,
losing customers to competitors with better SEO.
"""

ai_approach_style = "problem_solving"  # Default
```

### AI Approach Styles

| Style | Best For | Tone |
|-------|----------|------|
| problem_solving | Most situations | "I noticed your business might be missing out on..." |
| value_driven | Premium services | "Here's what you'll get..." |
| relationship | Long-term nurturing | "I've been following your business..." |
| direct | Time-sensitive offers | "Quick question - would you like..." |

### Email Composition

The AI generates emails based on:
1. Brand context (from Brand model)
2. Contact information (name, company, previous interactions)
3. Pipeline stage (determines email purpose)
4. Approach style setting
5. Any custom instructions provided

**AI Rules (enforced in system prompt):**
- Never mention specific prices
- Use "FREE" or "affordable" instead
- Focus on solving problems, not selling
- Keep emails concise (under 150 words)
- Always personalize with recipient's name/company

---

## Email Setup

### Zoho Mail Configuration

1. **Create Zoho Mail account** for the brand
2. **Generate API credentials:**
   - Go to Zoho API Console
   - Create Server-based Application
   - Add scopes: `ZohoMail.messages.ALL`, `ZohoMail.accounts.READ`
   - Get Client ID, Client Secret
   - Generate Refresh Token

3. **Add to environment:**
```bash
ZOHO_CLIENT_ID=xxx
ZOHO_CLIENT_SECRET=xxx
ZOHO_REFRESH_TOKEN=xxx
ZOHO_ACCOUNT_ID=xxx
```

### Email Template Structure

All emails include:
- Brand-styled header with gradient
- Main content area
- Unsubscribe link (brand-specific)
- "Powered by Codeteki Digital Services" footer

```html
<!-- Footer automatically added -->
<p style="color: #9ca3af; font-size: 11px;">
    Powered by <a href="https://codeteki.au/?utm_source=crm_email&utm_medium=email&utm_campaign=powered_by"
    style="color: #f9cd15; font-weight: 600;">Codeteki Digital Services</a>
</p>
```

---

## Go-Live Checklist

### Pre-Launch

- [ ] Brand created with all fields populated
- [ ] AI context configured (business updates, target context, approach style)
- [ ] Pipeline created with correct stages
- [ ] Stage timing configured (days until next action)
- [ ] Email templates tested
- [ ] Zoho email credentials added
- [ ] Test email sent and received
- [ ] Unsubscribe flow tested
- [ ] Pipeline board view working

### Launch Day

- [ ] Import initial contact list
- [ ] Create deals for all contacts
- [ ] Verify deals appear on pipeline board
- [ ] Send first batch of emails (start small: 10-20)
- [ ] Monitor for bounces/errors
- [ ] Check email tracking is working

### Post-Launch (Week 1)

- [ ] Review email open rates
- [ ] Check for replies (move to "Responded" stage)
- [ ] Process unsubscribes (auto-handled)
- [ ] Adjust AI context based on response patterns
- [ ] Scale up email volume if successful

---

## Maintenance & Support

### Daily Tasks (Automated)
- Celery task: `process_pending_deals` - checks deals needing follow-up
- Celery task: `send_scheduled_emails` - sends queued emails
- Celery task: `check_email_replies` - processes incoming replies

### Weekly Tasks
- Review pipeline board for stuck deals
- Check lost deals by reason (unsubscribed vs no response)
- Update AI business context if needed
- Export analytics for client reporting

### Monthly Tasks
- Clean up old contacts (optional)
- Review and optimize email templates
- Analyze conversion rates by stage
- Client performance review meeting

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Emails not sending | Check Zoho credentials, verify quota |
| AI generating poor emails | Update brand AI context fields |
| Duplicate contacts | Run deduplication: `python manage.py dedupe_contacts` |
| Pipeline board empty | Verify deals exist and are in active status |
| Unsubscribe not working | Check brand slug matches in email |

### Support Contacts

- Technical issues: dev@codeteki.au
- Client onboarding: support@codeteki.au
- AI tuning requests: Create ticket in project management

---

## Appendix

### A. Management Commands

```bash
# Add CRM service to website
python manage.py add_crm_service

# Seed default pipelines (internal use)
python manage.py seed_crm_pipelines

# Import contacts from CSV
python manage.py import_contacts --brand=slug --file=path.csv

# Deduplicate contacts
python manage.py dedupe_contacts --brand=slug

# Process pending deals manually
python manage.py process_deals --pipeline=id
```

### B. API Endpoints

```
GET  /api/crm/pipelines/           - List pipelines
GET  /api/crm/pipelines/{id}/      - Pipeline detail
GET  /api/crm/deals/               - List deals
POST /api/crm/deals/               - Create deal
POST /api/crm/deals/{id}/move/     - Move deal to stage
GET  /api/crm/contacts/            - List contacts
POST /api/crm/contacts/            - Create contact
GET  /api/crm/email-logs/          - Email history
```

### C. Database Models

```
Brand (multi-tenant support)
├── Pipeline (sales workflow)
│   ├── PipelineStage (workflow stages)
│   └── Deal (contact in pipeline)
│       ├── EmailLog (sent emails)
│       └── AIDecisionLog (AI audit)
├── Contact (leads/prospects)
└── EmailTemplate (email content)
```

### D. Pricing Guidelines (Internal)

| CRM Type | Setup Fee | Monthly | Notes |
|----------|-----------|---------|-------|
| Real Estate | $500 | $99 | Up to 1,000 contacts |
| Business Directory | $500 | $99 | Up to 1,000 contacts |
| B2B Sales | $750 | $149 | Up to 500 contacts |
| Custom/Enterprise | Quote | Quote | Unlimited contacts |

*Never share pricing with clients via AI emails - use "affordable plans" or "contact us"*

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Author:** Codeteki Development Team
