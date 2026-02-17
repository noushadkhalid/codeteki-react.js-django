# CRM System Status - What's Built & What's Left

**Last Updated:** February 17, 2026

---

## System Overview

Multi-brand CRM with AI-powered outreach automation for **Codeteki** and **Desi Firms**. Handles contact management, pipeline automation, email sending with engagement tracking, and intelligent follow-up decisions.

**Two brands, completely isolated:**
- **Codeteki** (codeteki.au) — Sales, backlinks, partnerships. Uses Zoho Mail.
- **Desi Firms** (desifirms.com.au) — Business directory, real estate agents, events. Uses ZeptoMail.

---

## What's Built (Complete)

### 1. Contact Management
- Contact model with per-brand isolation
- Smart name extraction from email/domain
- Per-brand unsubscribe tracking (unsubscribe from Desi Firms doesn't affect Codeteki)
- Proxy admin views: Codeteki Contacts, Desi Firms Contacts, All Contacts
- CSV bulk import with auto-deal creation
- AI lead scoring (0-100)

### 2. Pipeline System (11 pipelines)

**Codeteki:**
| Pipeline | Stages | Templates |
|----------|--------|-----------|
| Sales | Prospect Found > Intro Sent > FU1 > FU2 > Responded > Discovery Call > Proposal > Negotiating > Client > Lost | 9 templates |
| Backlink Outreach | Target Found > Pitch Sent > FU1 > FU2 > Responded > Link Placed > Rejected | 2 templates |

**Desi Firms:**
| Pipeline | Stages | Templates |
|----------|--------|-----------|
| Real Estate | Agent Found > Invited > FU1 > FU2 > FU3 (Final) > Responded > Registered > Listing Properties > Not Interested | 10 templates |
| Business Listings | Business Found > Invited > FU1 > FU2 > FU3 (Final) > Responded > Signed Up > Listed > Not Interested | 9 templates |
| Events | Organizer Found > Invited > FU1 > FU2 > FU3 (Final) > Responded > Signed Up > Event Listed > Not Interested | 9 templates |
| Classifieds | Lead Found > Invited > FU1 > FU2 > FU3 (Final) > Responded > Ad Posted > Not Interested | Similar |
| Backlink Outreach | Same as Codeteki backlink | 2 templates |
| Registered Users - Business | Registered > Nudge 1 > Nudge 2 > Responded > Listed > Not Interested | 2 templates |
| Registered Users - Real Estate | Registered > Nudge 1 > Nudge 2 > Responded > Agent Profile Created > Not Interested | 2 templates |
| Registered Users - Events | Registered > Nudge 1 > Nudge 2 > Responded > Event Posted > Not Interested | 2 templates |
| Agents & Agencies | Registered > Profile Complete > Agency Created > Team Invited > First Listing > Active Lister | 5 templates |

**50+ pre-designed HTML email templates** across both brands.

### 3. Intelligent Autopilot (NEW - Feb 2026)

The autopilot sits on top of ALL pipelines and makes engagement-aware decisions:

**How it works (hourly, Mon-Fri 9AM-5PM):**
```
Deal ready for action?
  |
  +-- Unsubscribed? --> Auto-close deal (NEVER email)
  +-- Final follow-up expired? --> Move to Not Interested
  +-- Ghost (3+ emails, 0 opens)? --> Auto-close deal
  +-- Burnout risk (3+ consecutive unopened)? --> Wait 7 days
  |
  +-- OK --> AI analyzes with engagement data
       |
       +-- send_email --> Sends branded template, auto-advances to next stage
       +-- wait --> Extends next_action_date
       +-- change_approach --> Waits + notes for different angle
       +-- pause --> Pauses the deal
```

**Engagement Tiers** (auto-computed from EmailLog data):
| Tier | Criteria | Action |
|------|----------|--------|
| Engaged | Replied | Priority - short wait times |
| Hot | Opened/clicked last 7 days, >50% open rate | Send promptly |
| Warm | Opened recently (within 14 days) | Normal cadence |
| Lurker | Opened 1-2 ever, but went quiet | Change approach |
| Cold | 2+ emails, zero opens | Extend waits |
| Ghost | 3+ emails, zero opens | Stop emailing, auto-close |

**Auto-stage progression:** After sending, deals advance automatically:
- Invited --> Follow Up 1 --> Follow Up 2 --> Follow Up 3 (Final) --> STOP
- Never auto-advances into Responded/Registered (those only via reply detection)

**A/B Testing:** Set `Subject Variant B` on any pipeline stage. Half get subject A, half get B. Track results in Email Logs.

**Daily Scan (8:30 AM weekdays):** Updates engagement tiers on all active deals before emails go out.

### 4. Email Sending

**Dual provider:**
- ZeptoMail (Desi Firms - high volume)
- Zoho Mail (Codeteki)

**Template priority system:**
1. Pre-designed HTML template for brand + pipeline + stage --> Use it
2. No template found --> AI generates body --> Wraps in branded HTML

**Tracking:** Open pixel, click tracking, reply detection (AI classifies intent: interested, not interested, unsubscribe, out of office).

**Office hours only:** Mon-Fri 9AM-5PM. Reply checking runs 24/7.

### 5. Email Composer (Bulk Send Tool)

- Select brand, pipeline, email type, tone
- Add recipients: search contacts, paste emails, or select from existing
- AI generates draft with brand context
- Edit final version
- Schedule for later (timezone-aware, Australia/Sydney)
- Send & auto-create deals in pipeline

### 6. AI Agent

All AI decisions are logged with reasoning, tokens used, and model info.

| Function | What it does |
|----------|-------------|
| `analyze_deal()` | Engagement-aware deal analysis, recommends next action |
| `compose_email()` | Personalized email with brand/engagement context |
| `classify_reply()` | Intent detection (interested, not interested, OOO, unsubscribe) |
| `score_lead()` | Lead scoring 0-100 |
| `generate_backlink_pitch()` | Backlink outreach angle + email |
| `get_smart_salutation()` | Personalized greeting from name/email/domain |

### 7. Backlink Outreach

- Import opportunities from Ubersuggest/Ahrefs/Semrush CSV
- AI generates pitch angles
- Pipeline tracking through outreach stages
- Link verification tracking

### 8. Admin Interface (Unfold Theme)

**Sidebar - CRM & Outreach:**
- Pipeline Board (Kanban view)
- Codeteki Contacts / Desi Firms Contacts / All Contacts
- Email Composer
- Deals (with engagement tier badges, filters)
- Import Contacts
- Brands
- Pipeline Settings (with A/B subject variant field)
- Backlinks
- Email Logs (opens, clicks, replies, A/B variants)
- AI Decisions (audit trail)

**Key admin actions on Deals:**
- Mark Won/Lost, Move to next stage
- Preview AI Email, Generate Draft Emails (bulk)
- Send Follow-up Email (with preview)
- Pause/Resume automation

### 9. Webhooks & Integrations

- Email open tracking pixel
- Reply webhook processing
- Unsubscribe/bounce webhook
- ChatLead auto-conversion to Contact + Deal (via signals)
- ContactInquiry auto-conversion to Contact + Deal (via signals)

### 10. Scheduled Tasks (Celery Beat)

| Task | Schedule | Purpose |
|------|----------|---------|
| `process_pending_deals` | Hourly, Mon-Fri 9-5 | Autopilot: engagement checks + AI decisions |
| `send_scheduled_emails` | Every 15 min, Mon-Fri 9-5 | Send queued emails |
| `check_scheduled_drafts` | Every 5 min, Mon-Fri 9-5 | Check for scheduled Email Composer sends |
| `check_email_replies` | Every 30 min, 24/7 | Poll inbox, classify replies |
| `daily_ai_review` | 9 AM weekdays | Review stale deals, score new contacts |
| `autopilot_engagement_scan` | 8:30 AM weekdays | Update engagement tiers on all deals |

---

## What's Partially Built

### Email Sequences (Model exists, not actively used)
- `EmailSequence` and `SequenceStep` models exist with admin
- No task currently uses them - the system uses pre-designed templates + AI instead
- Could be useful for custom reusable sequences in the future

### Lead Integration Service
- `lead_integration.py` service exists
- Unclear if actively connected to external lead sources

---

## What's Left to Build

### High Priority

1. **Analytics Dashboard**
   - Pipeline conversion rates (how many Invited --> Signed Up per pipeline?)
   - Email performance metrics (open rates by template, by brand, by stage)
   - A/B test results comparison view
   - Engagement tier distribution across pipelines
   - Ghost/burnout trend over time
   - Currently: stats API exists but limited frontend dashboard

2. **Classifieds Pipeline Templates**
   - Pipeline stages exist but no pre-designed email templates
   - Currently falls back to AI generation with generic wrapper
   - Need: invitation, followup 1-3 templates matching Desi Firms style

3. **Deal Value / ROI Tracking**
   - `Deal.value` field exists but not actively used
   - No reporting on deal values or conversion revenue
   - Would be useful for Codeteki sales pipeline especially

### Medium Priority

4. **Click Tracking**
   - `EmailLog.clicked` and `clicked_at` fields exist
   - Open tracking pixel works
   - Click tracking may not have URL rewriting implemented
   - Need to verify: are clicks actually being recorded?

5. **Partnership Pipeline (Codeteki)**
   - Pipeline type defined, templates exist (partnership_intro, collaboration)
   - No stages seeded in database?
   - Need to verify and seed if missing

6. **Engagement-Aware Email Content**
   - AI gets engagement context but pre-designed templates don't adapt
   - Could add: different template variants for cold vs warm contacts
   - E.g., shorter emails for cold contacts, more value-heavy for lurkers

7. **Bulk Actions for Engagement Tiers**
   - Admin filter exists but no bulk actions specific to tiers
   - Could add: "Re-engage all Lurkers", "Archive all Ghosts", "Priority follow-up Hot leads"

### Low Priority / Nice to Have

8. **Email Sequence Active Use**
   - Wire up EmailSequence model to autopilot
   - Allow custom sequences per pipeline stage

9. **Mobile/Frontend Dashboard**
   - REST API is complete and ready
   - No React frontend for CRM (admin-only currently)

10. **Multi-timezone Support**
    - Office hours currently use server timezone
    - Could respect contact's timezone for optimal send times

11. **Email Deliverability Monitoring**
    - Track bounce rates per brand/domain
    - Automatic sender reputation scoring
    - Domain warmup tracking for new brands

12. **Automated A/B Test Analysis**
    - Currently manual: check Email Logs filtered by A/B variant
    - Could auto-detect winner after N sends and apply it

---

## File Reference

| File | Lines | Purpose |
|------|-------|---------|
| `models.py` | ~1210 | 23 models |
| `admin.py` | ~2600 | 17 admin classes, 50+ actions |
| `tasks.py` | ~1150 | 10+ Celery tasks |
| `views.py` | ~1200 | 21 API endpoints |
| `services/ai_agent.py` | ~2000 | AI orchestration |
| `services/email_service.py` | ~1200 | ZeptoMail + Zoho dual provider |
| `services/email_templates.py` | ~550 | Template routing + styling |
| `services/engagement_engine.py` | ~250 | Engagement profiling |
| `services/csv_importer.py` | ~320 | Contact bulk import |
| `services/backlink_importer.py` | ~280 | Backlink opportunity import |
| `templates/crm/emails/` | 50+ files | Pre-designed HTML email templates |
| `migrations/` | 24 files | Database schema history |

---

## Architecture

```
                     Admin (Unfold)          REST API
                         |                     |
                         v                     v
               +---------+---------+-----------+
               |         CRM Models            |
               | Brand, Contact, Pipeline,     |
               | Deal, EmailLog, EmailDraft    |
               +------+--------+-------+------+
                      |        |       |
           +----------+   +----+   +---+----------+
           |              |        |               |
     AI Agent        Email       Engagement     CSV/Backlink
   (analyze,        Service      Engine         Importers
    compose,       (ZeptoMail   (tier,
    classify)       + Zoho)     burnout)
           |              |        |
           +------+-------+-------+
                  |
            Celery Beat
         (hourly autopilot,
          daily scan,
          reply checking)
                  |
                  v
           Office Hours Guard
          (Mon-Fri 9AM-5PM)
```
