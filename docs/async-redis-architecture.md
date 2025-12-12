# Async SEO Audit Architecture with Redis & Celery

## Overview

This document describes the asynchronous architecture used for SEO auditing in Codeteki. This pattern can be reused for any long-running background tasks (desifirms, other projects).

## Architecture Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Django Admin  │────▶│   Redis Broker  │────▶│  Celery Worker  │
│  (Trigger Task) │     │  (Task Queue)   │     │ (Process Task)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                                               │
         │                                               ▼
         │                                      ┌─────────────────┐
         │                                      │  External APIs  │
         │                                      │  - PageSpeed    │
         │                                      │  - OpenAI       │
         │                                      │  - Lighthouse   │
         │                                      └─────────────────┘
         │                                               │
         ▼                                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                         │
│  - SiteAudit (status, celery_task_id, results)                  │
│  - PageAudit (individual page scores)                           │
│  - AuditIssue (detected issues)                                 │
│  - django_celery_results (task results)                         │
└─────────────────────────────────────────────────────────────────┘
```

## Why Async?

1. **Timeout Prevention**: Web requests timeout after ~30 seconds. Audits can take 5-30 minutes.
2. **User Experience**: Users can continue working while audits run in background.
3. **Scalability**: Multiple audits can run concurrently on separate workers.
4. **Reliability**: Failed tasks can be automatically retried.
5. **Monitoring**: Task progress can be tracked via task IDs.

---

## Implementation Guide

### Step 1: Install Dependencies

```bash
pip install celery redis django-celery-results
```

**requirements.txt:**
```
celery>=5.3.0
redis>=5.0.0
django-celery-results>=2.5.0
```

### Step 2: Configure Celery

**`project_name/celery.py`:**
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_name.settings')

app = Celery('project_name')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

**`project_name/__init__.py`:**
```python
from .celery import app as celery_app
__all__ = ('celery_app',)
```

### Step 3: Settings Configuration

**`settings.py`:**
```python
INSTALLED_APPS = [
    # ...
    'django_celery_results',
]

# Celery Configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes max
```

### Step 4: Create Database Models

```python
class SiteAudit(models.Model):
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Task tracking
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Results
    avg_performance = models.FloatField(null=True, blank=True)
    avg_seo = models.FloatField(null=True, blank=True)
    total_issues = models.IntegerField(default=0)

    # AI Analysis
    ai_analysis = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Step 5: Create Background Tasks

**`app/tasks.py`:**
```python
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_audit_task(self, audit_id: int) -> dict:
    """
    Run audit in background with automatic retry on failure.

    Args:
        audit_id: ID of the audit to process

    Returns:
        dict with audit results
    """
    from .models import SiteAudit
    from .services.pagespeed import PageSpeedService

    try:
        audit = SiteAudit.objects.get(id=audit_id)
        logger.info(f"Starting audit for {audit.domain} (ID: {audit_id})")

        # Update status and task ID
        audit.celery_task_id = self.request.id
        audit.status = SiteAudit.STATUS_RUNNING
        audit.started_at = timezone.now()
        audit.save(update_fields=['celery_task_id', 'status', 'started_at'])

        # Run the actual audit
        service = PageSpeedService()
        results = service.analyze_url(f"https://{audit.domain}/")

        # Save results
        audit.avg_performance = results.get('performance_score')
        audit.avg_seo = results.get('seo_score')
        audit.status = SiteAudit.STATUS_COMPLETED
        audit.completed_at = timezone.now()
        audit.save()

        logger.info(f"Completed audit for {audit.domain}")
        return {"success": True, "performance": audit.avg_performance}

    except SiteAudit.DoesNotExist:
        logger.error(f"Audit {audit_id} not found")
        return {"success": False, "error": f"Audit {audit_id} not found"}

    except Exception as e:
        logger.exception(f"Error in audit task: {e}")

        # Mark as failed
        try:
            audit = SiteAudit.objects.get(id=audit_id)
            audit.status = SiteAudit.STATUS_FAILED
            audit.save(update_fields=['status'])
        except:
            pass

        # Retry on transient errors
        raise self.retry(exc=e)


@shared_task(bind=True)
def generate_ai_analysis_task(self, audit_id: int) -> dict:
    """Generate AI analysis for completed audit."""
    from .models import SiteAudit
    from .services.ai_engine import AIAnalysisEngine

    try:
        audit = SiteAudit.objects.get(id=audit_id)
        logger.info(f"Generating AI analysis for {audit.domain}")

        engine = AIAnalysisEngine(audit)
        analysis = engine.generate()

        if analysis:
            audit.ai_analysis = analysis
            audit.save(update_fields=['ai_analysis'])
            return {"success": True}

        return {"success": False, "error": "AI analysis failed"}

    except Exception as e:
        logger.exception(f"Error generating AI analysis: {e}")
        return {"success": False, "error": str(e)}
```

### Step 6: Admin Actions

**`app/admin.py`:**
```python
from django.contrib import admin, messages

@admin.register(SiteAudit)
class SiteAuditAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'status', 'avg_performance', 'created_at']
    list_filter = ['status']
    actions = ['run_audit', 'generate_ai_analysis']

    @admin.action(description="Run Audit (Background)")
    def run_audit(self, request, queryset):
        from .tasks import run_audit_task

        for audit in queryset:
            audit.status = 'running'
            audit.save(update_fields=['status'])

            task = run_audit_task.delay(audit.id)

            audit.celery_task_id = task.id
            audit.save(update_fields=['celery_task_id'])

            self.message_user(
                request,
                f"Audit '{audit.name}' queued. Task ID: {task.id}",
                messages.SUCCESS
            )

    @admin.action(description="Generate AI Analysis")
    def generate_ai_analysis(self, request, queryset):
        from .tasks import generate_ai_analysis_task

        for audit in queryset:
            if audit.status != 'completed':
                self.message_user(
                    request,
                    f"Audit '{audit.name}' must be completed first",
                    messages.WARNING
                )
                continue

            task = generate_ai_analysis_task.delay(audit.id)
            self.message_user(
                request,
                f"AI analysis queued for '{audit.name}'",
                messages.SUCCESS
            )
```

---

## Running the System

### Development

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Django
python manage.py runserver

# Terminal 3: Celery Worker
celery -A project_name worker -l INFO
```

### Production (Systemd)

**`/etc/systemd/system/celery.service`:**
```ini
[Unit]
Description=Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/project
Environment="PATH=/var/www/project/venv/bin"
ExecStart=/var/www/project/venv/bin/celery -A project_name worker -l INFO --detach --pidfile=/var/run/celery/worker.pid
ExecStop=/bin/kill -TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable celery
sudo systemctl start celery
```

---

## AI Analysis Integration

### OpenAI Service

**`services/ai_engine.py`:**
```python
import openai
from django.conf import settings

class AIAnalysisEngine:
    def __init__(self, audit):
        self.audit = audit
        openai.api_key = settings.OPENAI_API_KEY

    def generate(self) -> str:
        """Generate AI-powered analysis of audit results."""

        # Build context from audit data
        context = self._build_context()

        prompt = f"""
        Analyze this SEO audit for {self.audit.domain}:

        {context}

        Provide:
        1. Executive Summary (2-3 sentences)
        2. Critical Issues (prioritized list)
        3. Quick Wins (easy improvements)
        4. Technical Recommendations
        5. Estimated Impact

        Format in markdown.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert SEO analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )

        return response.choices[0].message.content

    def _build_context(self) -> str:
        """Build context string from audit data."""
        lines = [
            f"Domain: {self.audit.domain}",
            f"Performance Score: {self.audit.avg_performance or 'N/A'}/100",
            f"SEO Score: {self.audit.avg_seo or 'N/A'}/100",
            f"Total Issues: {self.audit.total_issues}",
        ]

        # Add page-level data
        for page in self.audit.page_audits.all()[:10]:
            lines.append(f"\nPage: {page.url}")
            lines.append(f"  Performance: {page.performance_score}")
            lines.append(f"  LCP: {page.lcp}s, CLS: {page.cls}")

        # Add top issues
        issues = self.audit.get_issues()[:20]
        if issues:
            lines.append("\nTop Issues:")
            for issue in issues:
                lines.append(f"  - [{issue.severity}] {issue.title}")

        return "\n".join(lines)
```

---

## PDF Report Generation

See `backend/core/services/seo_report_pdf.py` for the premium PDF generator implementation with:
- Donut charts
- Progress bars
- Core Web Vitals tables
- AI analysis section
- Executive summary

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `project/celery.py` | Celery app configuration |
| `project/__init__.py` | Import celery app |
| `project/settings.py` | Redis/Celery settings |
| `app/tasks.py` | Background task definitions |
| `app/models.py` | Models with `celery_task_id` |
| `app/admin.py` | Admin actions to trigger tasks |
| `services/pagespeed.py` | PageSpeed API integration |
| `services/ai_engine.py` | OpenAI analysis |
| `services/seo_report_pdf.py` | PDF report generation |

---

## Desifirms Implementation Checklist

- [ ] Install dependencies (celery, redis, django-celery-results)
- [ ] Create `celery.py` configuration
- [ ] Update `__init__.py` to import celery app
- [ ] Add Celery settings to `settings.py`
- [ ] Create audit models with `celery_task_id` field
- [ ] Create `tasks.py` with background tasks
- [ ] Add admin actions for triggering audits
- [ ] Set up PageSpeed API service
- [ ] Set up AI analysis service (OpenAI)
- [ ] Create PDF report generator
- [ ] Configure systemd service for Celery worker
- [ ] Set up Redis on server

---

## Environment Variables

```bash
# .env
CELERY_BROKER_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
GOOGLE_PAGESPEED_API_KEY=AIza...
```

---

## Monitoring & Debugging

### Check Task Status
```python
from celery.result import AsyncResult
result = AsyncResult(task_id)
print(result.status)  # PENDING, STARTED, SUCCESS, FAILURE
print(result.result)  # Task return value
```

### View Redis Queue
```bash
redis-cli
> KEYS *
> LLEN celery
```

### Celery Flower (Web UI)
```bash
pip install flower
celery -A project_name flower --port=5555
```

---

## Common Issues

1. **Task stuck in PENDING**: Celery worker not running
2. **Connection refused**: Redis not running
3. **Serialization error**: Non-JSON-serializable data in task args
4. **Task timeout**: Increase `CELERY_TASK_TIME_LIMIT`
5. **Memory issues**: Use `celery -A project worker --max-tasks-per-child=100`
