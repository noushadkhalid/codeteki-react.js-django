# CRM Autopilot System - How It All Works

This doc explains how pipelines, stages, the engagement engine, and AI work together
to automatically email leads and move them through the sales funnel.

---

## The Big Picture (Simple Version)

```
Pipeline = A workflow (e.g. "Business Listings", "User Registration")
Stage    = A step in that workflow (e.g. "Invited", "Follow Up 1", "Follow Up 2")
Deal     = A contact placed into a pipeline, sitting at one stage

Every hour (Mon-Fri 9AM-5PM), the autopilot:
  1. Finds deals that are due for action
  2. Checks safety rules (bounced? unsubscribed? ghost?)
  3. Asks AI: "What should we do with this deal?"
  4. AI says: send email / wait / move stage / pause / stop
  5. If "send email" → compose + send, then advance to next stage
```

That's the core loop. Everything below adds detail to these 5 steps.

---

## 1. Pipelines & Stages

### What is a Pipeline?

A pipeline is a named workflow for a specific purpose. Examples:

| Pipeline | Type | Purpose |
|----------|------|---------|
| Codeteki Sales | sales | Cold outreach to potential web dev clients |
| Desi Firms Business Listings | business | Outreach to get businesses to list on Desi Firms |
| Desi Firms User Registration | user_registration | Track users who signed up via the website |
| Phone Campaign | phone_campaign | SMS/WhatsApp outreach |

Each pipeline belongs to a Brand (Codeteki or Desi Firms).

### What is a Stage?

Stages are ordered steps within a pipeline. Example for a typical outreach pipeline:

```
1. Invited          (days_until_followup: 3)  ← deal starts here
2. Follow Up 1      (days_until_followup: 4)
3. Follow Up 2      (days_until_followup: 5)
4. Follow Up 3      (days_until_followup: 7)
5. Signed Up         (terminal: no)           ← user took action
6. Listed            (terminal: yes)          ← goal achieved!
7. Not Interested    (terminal: yes)          ← gave up
```

### What does `days_until_followup` do?

This is the timer. When a deal moves to a stage:
- `next_action_date = now + days_until_followup`
- The autopilot won't touch this deal until that date arrives

Example: Deal moves to "Follow Up 1" (days_until_followup: 4)
→ Autopilot will check this deal again in 4 days.

### What does `is_terminal` mean?

Terminal stages are end states. Once a deal reaches a terminal stage,
the autopilot stops processing it. Examples: "Listed", "Not Interested", "Inactive".

### The New User Registration Pipeline

For Desi Firms users who sign up on the website:

```
1. Registered           (followup: 2 days)  ← just signed up
2. Business Listed      (followup: 3 days)  ← created a business listing
3. Event Posted         (followup: 3 days)  ← posted an event
4. Agent/Agency Created (followup: 3 days)  ← created real estate profile
5. Classified Posted    (followup: 3 days)  ← posted a classified
6. Listing Approved     (terminal)          ← admin approved their listing (won!)
7. Inactive             (terminal)          ← never listed anything (lost)
```

Deals jump directly to the relevant stage based on webhook events
(e.g. user creates a business → jumps to "Business Listed").

---

## 2. The Autopilot Loop (`process_pending_deals`)

Runs **every hour, Mon-Fri 9AM-5PM** via Celery Beat.

### Step-by-step:

```
Find all deals where:
  - status = 'active'
  - next_action_date <= now (timer expired)
  - autopilot_paused = False
  - Limit: 50 deals per run

For each deal:
  ┌─────────────────────────────────────────────┐
  │ SAFETY CHECKS (hard stops)                  │
  │                                             │
  │ 1. Email bounced? → close deal, move on     │
  │ 2. Unsubscribed?  → close deal, move on     │
  │ 3. Bad domain?    → pause deal, move on     │
  │    (3+ bounced/spam contacts at same domain) │
  │ 4. Final stage?   → close as "no response"  │
  │    (stage name contains "follow up 3/final") │
  └─────────────────────────────────────────────┘
            │
            ▼
  ┌─────────────────────────────────────────────┐
  │ ENGAGEMENT CHECK                            │
  │                                             │
  │ Calculate engagement profile:               │
  │  - How many emails sent/opened/clicked      │
  │  - Open rate, click rate                    │
  │  - Days since last open                     │
  │  - Consecutive unopened emails              │
  │                                             │
  │ Classify into tier:                         │
  │  engaged → hot → warm → lurker → cold → ghost│
  │                                             │
  │ Ghost? (3+ sent, 0 opened) → close deal     │
  │ Burnout risk? (3+ consecutive unopened       │
  │   AND not engaged/hot) → wait 7 days, skip  │
  └─────────────────────────────────────────────┘
            │
            ▼
  ┌─────────────────────────────────────────────┐
  │ AI DECISION                                 │
  │                                             │
  │ AI analyzes: deal context + engagement data │
  │                                             │
  │ Returns one of:                             │
  │  • send_email     → compose & send          │
  │  • move_stage     → advance to next stage   │
  │  • wait           → extend timer X days     │
  │  • change_approach→ try different angle      │
  │  • pause          → stop autopilot          │
  │  • flag_for_review→ needs human attention    │
  └─────────────────────────────────────────────┘
            │
            ▼
  ┌─────────────────────────────────────────────┐
  │ EXECUTE ACTION                              │
  │                                             │
  │ If send_email:                              │
  │  1. Check preferred send hour (defer if off) │
  │  2. Pick A/B variant (50% chance)           │
  │  3. Queue email (async)                     │
  │  4. After send: set next_action_date based  │
  │     on engagement tier                      │
  │  5. Auto-advance to next follow-up stage    │
  └─────────────────────────────────────────────┘
```

---

## 3. Engagement Tiers Explained

The engagement engine looks at ALL past emails for a deal and classifies the contact:

| Tier | Meaning | What Happens |
|------|---------|--------------|
| **engaged** | They replied to an email | Send immediately, high priority |
| **hot** | Opened recently + good open rate (>50%) | Send immediately |
| **warm** | Opened within last 14 days | Send now (or wait 7 days if burnout risk) |
| **lurker** | Opened 1-2 emails, but ages ago | Change approach - try different subject/angle |
| **cold** | Never opened any email | Wait longer, try different approach after 3 sends |
| **ghost** | 3+ emails sent, 0 opens | STOP - close the deal, they're not there |

### Burnout Risk

If a contact has **3+ consecutive unopened emails**, they're flagged as burnout risk.
This means: back off. Don't keep hammering them or they'll mark you as spam.

- Engaged/hot contacts: send anyway (they've shown interest before)
- Everyone else: wait 7 extra days before trying again

### How Tiers Affect Send Timing

After an email is sent, the next check-in is based on tier:

| Tier | Next check-in |
|------|---------------|
| engaged | 2 days |
| hot | 2 days |
| warm | 3 days |
| lurker | 5 days |
| cold | 7 days |
| ghost | N/A (deal closed) |

---

## 4. How AI Makes Decisions

### Step 1: AI Analyzes the Deal

The AI receives:
- Contact info (name, company, website)
- Pipeline and current stage
- How many emails sent, open rate, click rate
- Engagement tier and burnout risk
- The engagement engine's recommendation

It then decides the best action. Key rules it follows:
- Ghost tier → recommend stop
- Burnout risk → recommend wait
- Engaged/hot → recommend send now
- Lurker → recommend changing approach (different subject line, angle)
- Cold after 3+ sends → recommend changing approach or pausing

### Step 2: AI Composes the Email

If the action is "send_email", the AI writes the email with:
- **Brand-specific tone**: Codeteki = professional/consultative, Desi Firms = community-focused/humble
- **Engagement awareness**: If they haven't opened → try completely different subject. If they opened but didn't reply → add more value.
- **Word limits**: 100 words initial, 80 words follow-up
- **A/B testing**: 50% chance of using variant B subject line (if the stage has one)

### Pre-designed vs AI-generated

Some pipeline stages have **pre-designed email templates** (not AI-generated).
The system checks for a template first. If one exists, it uses that instead of AI.
This is common for initial outreach emails where we want consistent messaging.

---

## 5. The Email Sending Flow (`queue_deal_email`)

This runs as an async Celery task (separate from the main loop):

```
queue_deal_email(deal_id, email_type, ab_variant)
  │
  ├─ Safety checks (again):
  │   - Bounced? Unsubscribed? Spam reported? → abort
  │   - Contact got email from OTHER brand today? → defer to tomorrow
  │
  ├─ Determine email content:
  │   - Check for pre-designed template → use if exists
  │   - Otherwise → AI compose_email()
  │
  ├─ Create EmailLog record (not sent yet)
  │
  ├─ Send via email service (ZeptoMail or Zoho)
  │   │
  │   ├─ SUCCESS:
  │   │   - Mark EmailLog as sent
  │   │   - Set next_action_date based on engagement tier
  │   │   - Increment deal.emails_sent
  │   │   - Auto-advance to next follow-up stage
  │   │
  │   └─ HARD BOUNCE:
  │       - Mark contact as bounced
  │       - Close THIS deal
  │       - Close ALL other active deals for this contact
  │       - No more emails ever sent to this contact
  │
  └─ Log everything to DealActivity
```

---

## 6. Daily Schedule (What Runs When)

| Time | Task | What it does |
|------|------|-------------|
| 8:30 AM | `autopilot_engagement_scan` | Refresh ALL deal engagement tiers (runs BEFORE autopilot) |
| 9:00 AM | `process_pending_deals` | Main autopilot loop (repeats every hour until 5PM) |
| 9:00 AM | `daily_ai_review` | Review stale deals, score unscored contacts |
| Every 15 min | `send_scheduled_emails` | Send manually scheduled emails from admin |
| Every 5 min | `check_scheduled_drafts` | Check for drafts ready to send |
| Every 30 min (24/7) | `check_email_replies` | Detect replies, auto-pause autopilot |
| Monday 9 AM | `send_weekly_report` | Email stats summary |
| Monday 10 AM | `attempt_re_engagement` | Try to revive deals lost 30+ days ago |

---

## 7. Webhooks & the User Registration Pipeline

When Desi Firms sends webhook events (user signed up, created listing, etc.):

### `user_registered` event:
1. If contact already has an active deal (from outreach) → advance to "Signed Up" stage in THAT pipeline
2. If no existing deal → create new deal in **User Registration** pipeline at "Registered" stage

### Progress events (`business_created`, `event_approved`, etc.):
1. If deal is in **User Registration** pipeline → advance to the matching stage:
   - `business_created` → "Business Listed"
   - `event_created` → "Event Posted"
   - `agency_created` / `agent_created` → "Agent/Agency Created"
   - `business_approved` / `event_approved` / `property_approved` → "Listing Approved" (terminal, won!)
2. If deal is in an **outreach pipeline** (from email campaigns) → use outreach stage mapping (e.g. "Signed Up", "Listed")
3. Autopilot is **paused** on progress events (user is actively doing things on their own)

---

## 8. Summary: The Layers of Intelligence

```
Layer 1: PIPELINE STAGES
  └─ Define the workflow steps and timing (days_until_followup)
  └─ This is the basic structure - "what comes after what"

Layer 2: SAFETY CHECKS (hard rules)
  └─ Bounced emails, unsubscribes, bad domains, final stages
  └─ These ALWAYS override everything else

Layer 3: ENGAGEMENT ENGINE (data-driven)
  └─ Classifies contacts by actual behavior (opens, clicks, replies)
  └─ Detects ghosts (give up) and burnout risk (back off)
  └─ Adjusts timing based on engagement tier

Layer 4: AI AGENT (creative decisions)
  └─ Decides action: send, wait, change approach, pause
  └─ Composes personalized emails with brand tone
  └─ Adapts messaging based on engagement data

Layer 5: WEBHOOKS (external signals)
  └─ User actions on the website override autopilot
  └─ Registration, listing creation, approval events
  └─ Auto-pauses autopilot when user is active
```

Each layer builds on the one below it. The pipeline defines the structure,
safety checks prevent harm, engagement data informs timing, AI makes creative
decisions, and webhooks respond to real-world user actions.
