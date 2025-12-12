# Desifirms SEO Audit Implementation Guide

Quick implementation guide for adding the SEO audit system with AI analysis to Desifirms.

## Files to Copy/Adapt

From Codeteki project, copy these files to Desifirms:

```
backend/
├── desifirms/
│   ├── celery.py              # NEW - Celery configuration
│   ├── __init__.py            # MODIFY - Add celery import
│   └── settings.py            # MODIFY - Add Celery settings
├── seo/                       # NEW APP
│   ├── __init__.py
│   ├── admin.py               # Admin with audit actions
│   ├── models.py              # SiteAudit, PageAudit, AuditIssue
│   ├── tasks.py               # Celery background tasks
│   └── services/
│       ├── __init__.py
│       ├── pagespeed.py       # Google PageSpeed API
│       ├── ai_engine.py       # OpenAI analysis
│       └── pdf_report.py      # PDF generator
└── requirements.txt           # Add celery, redis, etc.
```

---

## Step 1: Install Dependencies

```bash
cd desifirms
pip install celery redis django-celery-results openai reportlab
pip freeze > requirements.txt
```

---

## Step 2: Create Celery Config

**`desifirms/celery.py`:**
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desifirms.settings')

app = Celery('desifirms')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**`desifirms/__init__.py`:**
```python
from .celery import app as celery_app
__all__ = ('celery_app',)
```

---

## Step 3: Update Settings

**`desifirms/settings.py`:**
```python
INSTALLED_APPS = [
    # ... existing apps
    'django_celery_results',
    'seo',  # New SEO app
]

# Celery Configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_PAGESPEED_API_KEY = os.getenv("GOOGLE_PAGESPEED_API_KEY", "")
```

---

## Step 4: Create SEO App

```bash
python manage.py startapp seo
```

**`seo/models.py`:**
```python
from django.db import models

class SiteAudit(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=255)
    strategy = models.CharField(max_length=10, default='mobile',
                                choices=[('mobile', 'Mobile'), ('desktop', 'Desktop')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # URLs to audit
    target_urls = models.JSONField(default=list, blank=True)

    # Aggregate scores
    avg_performance = models.FloatField(null=True, blank=True)
    avg_seo = models.FloatField(null=True, blank=True)
    avg_accessibility = models.FloatField(null=True, blank=True)
    avg_best_practices = models.FloatField(null=True, blank=True)

    # Issue counts
    total_pages = models.IntegerField(default=0)
    total_issues = models.IntegerField(default=0)
    critical_issues = models.IntegerField(default=0)
    warning_issues = models.IntegerField(default=0)

    # AI Analysis
    ai_analysis = models.TextField(blank=True)

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Task tracking
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.status})"


class PageAudit(models.Model):
    site_audit = models.ForeignKey(SiteAudit, on_delete=models.CASCADE, related_name='page_audits')
    url = models.URLField(max_length=2000)
    strategy = models.CharField(max_length=10, default='mobile')
    status = models.CharField(max_length=20, default='pending')

    # Scores (0-100)
    performance_score = models.FloatField(null=True, blank=True)
    seo_score = models.FloatField(null=True, blank=True)
    accessibility_score = models.FloatField(null=True, blank=True)
    best_practices_score = models.FloatField(null=True, blank=True)

    # Core Web Vitals
    lcp = models.FloatField(null=True, blank=True, help_text="Largest Contentful Paint (seconds)")
    cls = models.FloatField(null=True, blank=True, help_text="Cumulative Layout Shift")
    tbt = models.FloatField(null=True, blank=True, help_text="Total Blocking Time (ms)")
    fcp = models.FloatField(null=True, blank=True, help_text="First Contentful Paint (seconds)")
    si = models.FloatField(null=True, blank=True, help_text="Speed Index (seconds)")
    ttfb = models.FloatField(null=True, blank=True, help_text="Time to First Byte (ms)")

    # Raw data
    raw_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.url} ({self.performance_score or 'N/A'})"


class AuditIssue(models.Model):
    SEVERITY_CHOICES = [
        ('error', 'Error'),
        ('warning', 'Warning'),
        ('info', 'Info'),
        ('passed', 'Passed'),
    ]

    page_audit = models.ForeignKey(PageAudit, on_delete=models.CASCADE, related_name='issues')
    audit_id = models.CharField(max_length=200)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, default='general')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='warning')
    score = models.FloatField(null=True, blank=True)
    display_value = models.CharField(max_length=200, blank=True)
    savings_ms = models.FloatField(default=0)
    details = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-severity', '-savings_ms']

    def __str__(self):
        return f"[{self.severity}] {self.title}"
```

---

## Step 5: Create Services

**`seo/services/pagespeed.py`:**
```python
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class PageSpeedService:
    BASE_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    def __init__(self):
        self.api_key = settings.GOOGLE_PAGESPEED_API_KEY

    def analyze_url(self, url: str, strategy: str = "mobile") -> dict:
        """Analyze a URL using Google PageSpeed Insights API."""
        params = {
            "url": url,
            "strategy": strategy,
            "category": ["performance", "seo", "accessibility", "best-practices"],
        }
        if self.api_key:
            params["key"] = self.api_key

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=120)
            response.raise_for_status()
            data = response.json()

            lighthouse = data.get("lighthouseResult", {})
            categories = lighthouse.get("categories", {})
            audits = lighthouse.get("audits", {})

            return {
                "success": True,
                "performance_score": self._get_score(categories, "performance"),
                "seo_score": self._get_score(categories, "seo"),
                "accessibility_score": self._get_score(categories, "accessibility"),
                "best_practices_score": self._get_score(categories, "best-practices"),
                "lcp": self._get_metric(audits, "largest-contentful-paint"),
                "cls": self._get_metric(audits, "cumulative-layout-shift"),
                "tbt": self._get_metric(audits, "total-blocking-time"),
                "fcp": self._get_metric(audits, "first-contentful-paint"),
                "si": self._get_metric(audits, "speed-index"),
                "opportunities": self._get_opportunities(audits),
                "diagnostics": self._get_diagnostics(audits),
                "raw_data": data,
            }

        except Exception as e:
            logger.error(f"PageSpeed API error for {url}: {e}")
            return {"success": False, "error": str(e)}

    def _get_score(self, categories, key):
        cat = categories.get(key, {})
        score = cat.get("score")
        return round(score * 100) if score else None

    def _get_metric(self, audits, key):
        audit = audits.get(key, {})
        value = audit.get("numericValue")
        if value and key in ["largest-contentful-paint", "first-contentful-paint", "speed-index"]:
            return round(value / 1000, 2)  # Convert ms to seconds
        return value

    def _get_opportunities(self, audits):
        opportunities = []
        opportunity_ids = [
            "render-blocking-resources", "unused-css-rules", "unused-javascript",
            "modern-image-formats", "uses-responsive-images", "offscreen-images",
            "efficiently-encode-images", "uses-text-compression", "server-response-time",
        ]
        for oid in opportunity_ids:
            audit = audits.get(oid, {})
            if audit.get("score", 1) < 1:
                opportunities.append({
                    "id": oid,
                    "title": audit.get("title", ""),
                    "description": audit.get("description", ""),
                    "score": audit.get("score"),
                    "displayValue": audit.get("displayValue", ""),
                    "numericValue": audit.get("numericValue"),
                })
        return opportunities

    def _get_diagnostics(self, audits):
        diagnostics = []
        diag_ids = [
            "dom-size", "mainthread-work-breakdown", "bootup-time",
            "font-display", "uses-passive-event-listeners",
        ]
        for did in diag_ids:
            audit = audits.get(did, {})
            if audit.get("score", 1) < 1:
                diagnostics.append({
                    "id": did,
                    "title": audit.get("title", ""),
                    "description": audit.get("description", ""),
                    "score": audit.get("score"),
                    "displayValue": audit.get("displayValue", ""),
                })
        return diagnostics
```

**`seo/services/ai_engine.py`:**
```python
import openai
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class SEOAIEngine:
    def __init__(self, audit):
        self.audit = audit
        openai.api_key = settings.OPENAI_API_KEY

    def generate_analysis(self) -> str:
        """Generate comprehensive AI analysis of audit results."""
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            return ""

        context = self._build_context()

        prompt = f"""
You are an expert SEO consultant analyzing a website audit for {self.audit.domain}.

## Audit Data:
{context}

## Your Task:
Provide a comprehensive SEO analysis report with:

# Executive Summary
2-3 sentence overview of the site's SEO health.

# Critical Issues (Priority Fixes)
List the most impactful issues that need immediate attention.

# Quick Wins
Easy improvements that can be implemented quickly.

# Performance Recommendations
Specific technical recommendations to improve Core Web Vitals.

# SEO Recommendations
On-page SEO improvements.

# Accessibility Notes
Key accessibility improvements needed.

# Estimated Impact
Expected improvement if recommendations are implemented.

Format in clean markdown. Be specific and actionable.
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert SEO analyst providing detailed, actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.7
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return ""

    def _build_context(self) -> str:
        """Build context from audit data for AI analysis."""
        lines = [
            f"Domain: {self.audit.domain}",
            f"Strategy: {self.audit.strategy}",
            f"Total Pages: {self.audit.total_pages}",
            f"Total Issues: {self.audit.total_issues}",
            f"Critical Issues: {self.audit.critical_issues}",
            f"Warnings: {self.audit.warning_issues}",
            "",
            "## Average Scores:",
            f"- Performance: {self.audit.avg_performance or 'N/A'}/100",
            f"- SEO: {self.audit.avg_seo or 'N/A'}/100",
            f"- Accessibility: {self.audit.avg_accessibility or 'N/A'}/100",
            f"- Best Practices: {self.audit.avg_best_practices or 'N/A'}/100",
            "",
            "## Page Details:",
        ]

        for page in self.audit.page_audits.all()[:10]:
            lines.append(f"\n### {page.url}")
            lines.append(f"- Performance: {page.performance_score}")
            lines.append(f"- SEO: {page.seo_score}")
            if page.lcp:
                lines.append(f"- LCP: {page.lcp}s")
            if page.cls:
                lines.append(f"- CLS: {page.cls}")
            if page.tbt:
                lines.append(f"- TBT: {page.tbt}ms")

        # Top issues
        from ..models import AuditIssue
        issues = AuditIssue.objects.filter(
            page_audit__site_audit=self.audit
        ).exclude(severity='passed').order_by('-severity', '-savings_ms')[:25]

        if issues:
            lines.append("\n## Top Issues:")
            for issue in issues:
                lines.append(f"- [{issue.severity.upper()}] {issue.title}")
                if issue.display_value:
                    lines.append(f"  Value: {issue.display_value}")

        return "\n".join(lines)
```

---

## Step 6: Create Tasks

**`seo/tasks.py`:**
```python
import logging
from celery import shared_task
from django.utils import timezone
from django.db.models import Avg

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_pagespeed_audit_task(self, audit_id: int) -> dict:
    """Run PageSpeed audit in background."""
    from .models import SiteAudit, PageAudit, AuditIssue
    from .services.pagespeed import PageSpeedService

    try:
        audit = SiteAudit.objects.get(id=audit_id)
        logger.info(f"Starting audit for {audit.domain}")

        audit.celery_task_id = self.request.id
        audit.status = 'running'
        audit.started_at = timezone.now()
        audit.save(update_fields=['celery_task_id', 'status', 'started_at'])

        service = PageSpeedService()
        urls = audit.target_urls or [f"https://{audit.domain}/"]

        pages_done = 0
        for url in urls:
            try:
                data = service.analyze_url(url, audit.strategy)
                if not data.get('success'):
                    continue

                page_audit, created = PageAudit.objects.update_or_create(
                    site_audit=audit,
                    url=url,
                    defaults={
                        'strategy': audit.strategy,
                        'performance_score': data.get('performance_score'),
                        'seo_score': data.get('seo_score'),
                        'accessibility_score': data.get('accessibility_score'),
                        'best_practices_score': data.get('best_practices_score'),
                        'lcp': data.get('lcp'),
                        'cls': data.get('cls'),
                        'tbt': data.get('tbt'),
                        'fcp': data.get('fcp'),
                        'si': data.get('si'),
                        'status': 'completed',
                        'raw_data': data.get('raw_data', {}),
                    }
                )

                # Create issues
                if created:
                    for item in data.get('opportunities', []) + data.get('diagnostics', []):
                        AuditIssue.objects.create(
                            page_audit=page_audit,
                            audit_id=item.get('id', ''),
                            title=item.get('title', ''),
                            description=item.get('description', ''),
                            category='performance',
                            severity='warning' if item.get('score', 1) < 0.9 else 'info',
                            score=item.get('score'),
                            display_value=item.get('displayValue', ''),
                        )

                pages_done += 1
                logger.info(f"Completed {url} ({pages_done}/{len(urls)})")

            except Exception as e:
                logger.error(f"Error on {url}: {e}")

        # Calculate averages
        page_audits = audit.page_audits.all()
        if page_audits.exists():
            avgs = page_audits.aggregate(
                avg_perf=Avg('performance_score'),
                avg_seo=Avg('seo_score'),
                avg_acc=Avg('accessibility_score'),
                avg_bp=Avg('best_practices_score'),
            )
            audit.avg_performance = avgs['avg_perf']
            audit.avg_seo = avgs['avg_seo']
            audit.avg_accessibility = avgs['avg_acc']
            audit.avg_best_practices = avgs['avg_bp']

        audit.status = 'completed'
        audit.completed_at = timezone.now()
        audit.total_pages = pages_done
        audit.total_issues = AuditIssue.objects.filter(page_audit__site_audit=audit).count()
        audit.critical_issues = AuditIssue.objects.filter(
            page_audit__site_audit=audit, severity='error'
        ).count()
        audit.warning_issues = AuditIssue.objects.filter(
            page_audit__site_audit=audit, severity='warning'
        ).count()
        audit.save()

        return {"success": True, "pages": pages_done}

    except SiteAudit.DoesNotExist:
        return {"success": False, "error": "Audit not found"}
    except Exception as e:
        logger.exception(f"Audit error: {e}")
        try:
            audit = SiteAudit.objects.get(id=audit_id)
            audit.status = 'failed'
            audit.save(update_fields=['status'])
        except:
            pass
        raise self.retry(exc=e)


@shared_task(bind=True)
def generate_ai_analysis_task(self, audit_id: int) -> dict:
    """Generate AI analysis for audit."""
    from .models import SiteAudit
    from .services.ai_engine import SEOAIEngine

    try:
        audit = SiteAudit.objects.get(id=audit_id)
        engine = SEOAIEngine(audit)
        analysis = engine.generate_analysis()

        if analysis:
            audit.ai_analysis = analysis
            audit.save(update_fields=['ai_analysis'])
            return {"success": True}

        return {"success": False, "error": "AI generation failed"}

    except Exception as e:
        logger.exception(f"AI error: {e}")
        return {"success": False, "error": str(e)}
```

---

## Step 7: Create Admin

**`seo/admin.py`:**
```python
from django.contrib import admin, messages
from .models import SiteAudit, PageAudit, AuditIssue

@admin.register(SiteAudit)
class SiteAuditAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'status', 'avg_performance', 'avg_seo', 'total_issues', 'created_at']
    list_filter = ['status', 'strategy']
    search_fields = ['name', 'domain']
    readonly_fields = ['celery_task_id', 'started_at', 'completed_at', 'avg_performance',
                       'avg_seo', 'avg_accessibility', 'avg_best_practices',
                       'total_pages', 'total_issues', 'critical_issues', 'warning_issues']
    actions = ['run_pagespeed_audit', 'generate_ai_analysis', 'generate_pdf_report']

    @admin.action(description="Run PageSpeed Audit (Background)")
    def run_pagespeed_audit(self, request, queryset):
        from .tasks import run_pagespeed_audit_task

        for audit in queryset:
            audit.status = 'running'
            audit.save(update_fields=['status'])

            task = run_pagespeed_audit_task.delay(audit.id)
            audit.celery_task_id = task.id
            audit.save(update_fields=['celery_task_id'])

            self.message_user(request, f"Audit '{audit.name}' queued. Task: {task.id}", messages.SUCCESS)

    @admin.action(description="Generate AI Analysis")
    def generate_ai_analysis(self, request, queryset):
        from .tasks import generate_ai_analysis_task

        for audit in queryset:
            if audit.status != 'completed':
                self.message_user(request, f"'{audit.name}' must be completed first", messages.WARNING)
                continue

            task = generate_ai_analysis_task.delay(audit.id)
            self.message_user(request, f"AI analysis queued for '{audit.name}'", messages.SUCCESS)

    @admin.action(description="Generate PDF Report")
    def generate_pdf_report(self, request, queryset):
        # TODO: Implement PDF generation
        pass


@admin.register(PageAudit)
class PageAuditAdmin(admin.ModelAdmin):
    list_display = ['url', 'site_audit', 'performance_score', 'seo_score', 'status']
    list_filter = ['status', 'site_audit']


@admin.register(AuditIssue)
class AuditIssueAdmin(admin.ModelAdmin):
    list_display = ['title', 'page_audit', 'severity', 'category', 'score']
    list_filter = ['severity', 'category']
```

---

## Step 8: Run Migrations

```bash
python manage.py makemigrations seo
python manage.py migrate
```

---

## Step 9: Server Setup

**Install Redis:**
```bash
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

**Celery Service (`/etc/systemd/system/celery-desifirms.service`):**
```ini
[Unit]
Description=Celery Worker for Desifirms
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/desifirms
Environment="PATH=/var/www/desifirms/venv/bin"
ExecStart=/var/www/desifirms/venv/bin/celery -A desifirms worker -l INFO --detach --pidfile=/var/run/celery/desifirms.pid
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo mkdir -p /var/run/celery
sudo chown www-data:www-data /var/run/celery
sudo systemctl enable celery-desifirms
sudo systemctl start celery-desifirms
```

---

## Environment Variables

Add to `.env`:
```
CELERY_BROKER_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-your-key
GOOGLE_PAGESPEED_API_KEY=AIza-your-key  # Optional but recommended
```

---

## Usage

1. Go to Django Admin > SEO > Site Audits
2. Create new audit with domain and target URLs
3. Select audit and run "Run PageSpeed Audit (Background)"
4. Refresh to see progress
5. Once completed, run "Generate AI Analysis"
6. Generate PDF report

---

## Quick Test

```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Redis (if not running as service)
redis-server

# Terminal 3: Celery worker
celery -A desifirms worker -l INFO
```
