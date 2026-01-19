# CRM App with AI Pipeline - Implementation Plan

## Overview
AI-controlled CRM pipeline for Codeteki and Desi Firms with automated email sending and follow-ups for sales and backlink outreach.

---

## Architecture

### Django App: `crm`

```
backend/crm/
├── __init__.py
├── admin.py              # Django Unfold admin interface
├── apps.py
├── models.py             # 10 core models
├── urls.py               # API endpoints
├── views.py              # API views
├── services/
│   ├── __init__.py
│   ├── ai_agent.py       # CRMAIAgent class
│   └── email_service.py  # ZohoEmailService class
├── tasks.py              # Celery background tasks
├── management/
│   └── commands/
│       └── seed_crm_pipelines.py
└── migrations/
```

---

## Models

### 1. Contact
Leads and backlink targets.
```python
- email (EmailField, unique)
- name (CharField)
- company (CharField, optional)
- website (URLField, optional)
- domain_authority (IntegerField, optional)
- contact_type: 'lead', 'backlink_target', 'partner'
- source (CharField) - where contact came from
- tags (JSONField) - flexible tagging
- ai_score (IntegerField) - AI lead scoring 0-100
- notes (TextField)
- created_at, updated_at
```

### 2. Pipeline
Different workflows.
```python
- name (CharField)
- pipeline_type: 'sales', 'backlink', 'partnership'
- description (TextField)
- is_active (BooleanField)
- created_at
```

### 3. PipelineStage
Stages within a pipeline.
```python
- pipeline (ForeignKey)
- name (CharField)
- order (IntegerField)
- auto_actions (JSONField) - AI triggers
- days_until_followup (IntegerField)
- is_terminal (BooleanField) - marks end states
```

### 4. Deal
Contact moving through pipeline.
```python
- contact (ForeignKey)
- pipeline (ForeignKey)
- current_stage (ForeignKey to PipelineStage)
- status: 'active', 'won', 'lost', 'paused'
- ai_notes (TextField) - AI observations
- next_action_date (DateTimeField)
- value (DecimalField) - deal value
- stage_entered_at (DateTimeField)
- created_at, updated_at
```

### 5. EmailSequence
Template sequences for outreach.
```python
- name (CharField)
- pipeline (ForeignKey)
- description (TextField)
- is_active (BooleanField)
```

### 6. SequenceStep
Individual email templates.
```python
- sequence (ForeignKey)
- order (IntegerField)
- delay_days (IntegerField) - days after previous step
- subject_template (CharField)
- body_template (TextField)
- ai_personalize (BooleanField) - AI should personalize
```

### 7. EmailLog
Track sent emails.
```python
- deal (ForeignKey)
- sequence_step (ForeignKey, nullable)
- subject (CharField)
- body (TextField)
- sent_at (DateTimeField)
- opened (BooleanField)
- opened_at (DateTimeField, nullable)
- clicked (BooleanField)
- replied (BooleanField)
- reply_content (TextField, nullable)
- ai_generated (BooleanField)
```

### 8. AIDecisionLog
Audit trail for AI decisions.
```python
- deal (ForeignKey)
- decision_type: 'compose_email', 'move_stage', 'classify_reply', 'score_lead'
- reasoning (TextField)
- action_taken (CharField)
- metadata (JSONField)
- created_at
```

### 9. BacklinkOpportunity
For backlink pipeline.
```python
- target_url (URLField)
- target_domain (CharField)
- domain_authority (IntegerField)
- relevance_score (IntegerField) - 0-100
- our_content_url (URLField) - content to promote
- anchor_text_suggestion (CharField)
- outreach_angle (TextField) - AI-generated pitch angle
- contact (ForeignKey, nullable)
- status: 'new', 'researching', 'outreaching', 'placed', 'rejected'
- created_at
```

### 10. AIPromptTemplate
Store AI prompts.
```python
- name (CharField)
- prompt_type: 'email_compose', 'reply_classify', 'lead_score', 'deal_analyze'
- prompt_text (TextField)
- variables (JSONField) - expected variables
- is_active (BooleanField)
```

---

## AI Agent Service

### CRMAIAgent (crm/services/ai_agent.py)

```python
class CRMAIAgent:
    def __init__(self):
        self.ai_engine = AIContentEngine()

    def analyze_deal(self, deal) -> dict:
        """
        Analyze deal and decide next action.
        Returns: {action: str, reasoning: str, metadata: dict}
        Actions: 'send_email', 'move_stage', 'wait', 'flag_for_review'
        """

    def compose_email(self, deal, template, context) -> dict:
        """
        Personalize email using AI.
        Returns: {subject: str, body: str}
        """

    def classify_reply(self, email_content) -> dict:
        """
        Classify incoming reply.
        Returns: {
            sentiment: 'positive', 'negative', 'neutral',
            intent: 'interested', 'not_interested', 'question', 'out_of_office',
            suggested_action: str
        }
        """

    def score_lead(self, contact) -> int:
        """
        AI lead scoring 0-100.
        Considers: company, website, domain_authority, engagement history
        """
```

---

## Email Service

### ZohoEmailService (crm/services/email_service.py)

```python
class ZohoEmailService:
    def __init__(self):
        self.client_id = settings.ZOHO_CLIENT_ID
        self.client_secret = settings.ZOHO_CLIENT_SECRET
        self.refresh_token = settings.ZOHO_REFRESH_TOKEN
        self.account_id = settings.ZOHO_ACCOUNT_ID

    def send(self, to, subject, body, from_name='Codeteki') -> dict:
        """Send email via Zoho Mail API."""

    def get_inbox_messages(self, since=None) -> list:
        """Fetch inbox messages for reply checking."""

    def track_open(self, email_log_id) -> str:
        """Generate tracking pixel URL."""
```

### Environment Variables
```
ZOHO_CLIENT_ID=xxx
ZOHO_CLIENT_SECRET=xxx
ZOHO_REFRESH_TOKEN=xxx
ZOHO_ACCOUNT_ID=xxx
ZOHO_FROM_EMAIL=outreach@codeteki.au
```

---

## Celery Tasks

### crm/tasks.py

```python
@shared_task
def process_pending_deals():
    """
    Runs hourly.
    - Find deals where next_action_date <= now
    - Call AI agent to decide action
    - Execute action (send email, move stage, etc.)
    """

@shared_task
def send_scheduled_emails():
    """
    Runs every 15 minutes.
    - Find deals with pending email sequences
    - Generate personalized emails
    - Send via Zoho
    - Log to EmailLog
    """

@shared_task
def check_email_replies():
    """
    Runs every 30 minutes.
    - Poll Zoho inbox for new replies
    - Match to EmailLog/Deal
    - Classify reply with AI
    - Update deal status/stage
    """

@shared_task
def daily_ai_review():
    """
    Runs at 9 AM daily.
    - Review all active deals
    - Update AI scores
    - Identify stuck deals
    - Generate daily summary
    """
```

### Celery Beat Schedule
```python
CELERY_BEAT_SCHEDULE = {
    'crm-process-pending-deals': {
        'task': 'crm.tasks.process_pending_deals',
        'schedule': crontab(minute=0),  # Every hour
    },
    'crm-send-scheduled-emails': {
        'task': 'crm.tasks.send_scheduled_emails',
        'schedule': crontab(minute='*/15'),  # Every 15 min
    },
    'crm-check-email-replies': {
        'task': 'crm.tasks.check_email_replies',
        'schedule': crontab(minute='*/30'),  # Every 30 min
    },
    'crm-daily-ai-review': {
        'task': 'crm.tasks.daily_ai_review',
        'schedule': crontab(hour=9, minute=0),  # 9 AM
    },
}
```

---

## Default Pipelines

### Sales Pipeline
| Stage | Order | Auto Action | Days Until Follow-up |
|-------|-------|-------------|---------------------|
| New Lead | 1 | send_initial_email | 0 |
| Contacted | 2 | wait_for_reply | 3 |
| Interested | 3 | schedule_call | 2 |
| Proposal Sent | 4 | send_followup | 3 |
| Negotiating | 5 | ai_monitor | 5 |
| Won | 6 | send_welcome | - |
| Lost | 7 | archive | - |

### Backlink Outreach Pipeline
| Stage | Order | Auto Action | Days Until Follow-up |
|-------|-------|-------------|---------------------|
| Opportunity Found | 1 | research_contact | 0 |
| Contact Found | 2 | send_pitch | 0 |
| Pitch Sent | 3 | wait_for_reply | 5 |
| Follow-up 1 | 4 | send_followup_1 | 5 |
| Follow-up 2 | 5 | send_followup_2 | 7 |
| Responded | 6 | classify_response | 0 |
| Link Placed | 7 | verify_link | - |
| Rejected | 8 | archive | - |

---

## API Endpoints

### Pipelines
- `GET /api/crm/pipelines/` - List all pipelines
- `POST /api/crm/pipelines/` - Create pipeline
- `GET /api/crm/pipelines/<id>/` - Pipeline detail with stages

### Deals
- `GET /api/crm/deals/` - List deals (filterable by pipeline, stage, status)
- `POST /api/crm/deals/` - Create deal
- `PATCH /api/crm/deals/<id>/` - Update deal
- `POST /api/crm/deals/<id>/move-stage/` - Move to specific stage

### Contacts
- `GET /api/crm/contacts/` - List contacts
- `POST /api/crm/contacts/` - Create contact
- `PATCH /api/crm/contacts/<id>/` - Update contact

### Email Sequences
- `GET /api/crm/email-sequences/` - List sequences with steps

### AI Activity
- `GET /api/crm/ai-activity/` - Recent AI decisions
- `GET /api/crm/ai-activity/<deal_id>/` - AI decisions for deal

### Stats
- `GET /api/crm/stats/` - Pipeline statistics

---

## Admin Interface (Django Unfold)

### Sidebar Navigation
```
CRM
├── Dashboard (custom view)
├── Pipelines
├── Stages
├── Deals
├── Contacts
├── Email Sequences
├── Email Log
├── AI Decisions
├── Backlink Opportunities
└── AI Prompts
```

### Key Features
- Pipeline admin with inline stages
- Deal list with filters (pipeline, stage, status, date)
- Contact list with search (name, email, company)
- Email log viewer (read-only)
- AI decision audit log
- Dashboard with pipeline funnel visualization

---

## Integration with Existing Models

### Signal Handlers
```python
# When ChatLead is created, create CRM Contact
@receiver(post_save, sender=ChatLead)
def create_contact_from_lead(sender, instance, created, **kwargs):
    if created and instance.email:
        Contact.objects.get_or_create(
            email=instance.email,
            defaults={
                'name': instance.name,
                'company': instance.company,
                'contact_type': 'lead',
                'source': 'chatbot'
            }
        )

# When ContactInquiry is created, create Deal
@receiver(post_save, sender=ContactInquiry)
def create_deal_from_inquiry(sender, instance, created, **kwargs):
    if created:
        # Create contact and deal in sales pipeline
        pass
```

---

## Environment Setup

Add to `.env`:
```
# Zoho Mail API
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
ZOHO_ACCOUNT_ID=your_account_id
ZOHO_FROM_EMAIL=outreach@codeteki.au
```

---

## Deployment Checklist

1. [ ] Create crm app: `python manage.py startapp crm`
2. [ ] Add 'crm' to INSTALLED_APPS
3. [ ] Create models and run migrations
4. [ ] Set up admin interface
5. [ ] Configure Celery beat schedule
6. [ ] Add Zoho credentials to .env
7. [ ] Run seed command: `python manage.py seed_crm_pipelines`
8. [ ] Test AI agent with sample data
9. [ ] Verify email sending
10. [ ] Monitor Celery tasks
