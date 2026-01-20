# SEO Engine & Background Processing Setup Guide
## For Desifirms - Business Listings, Deals, Events & AI Tools Platform

This document provides a complete guide to implementing the SEO audit engine with Redis background processing, based on the Codeteki implementation.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Install Dependencies](#step-1-install-dependencies)
4. [Step 2: Celery Configuration](#step-2-celery-configuration)
5. [Step 3: Django Settings](#step-3-django-settings)
6. [Step 4: Database Models](#step-4-database-models)
7. [Step 5: Background Tasks](#step-5-background-tasks)
8. [Step 6: Services](#step-6-services)
9. [Step 7: Admin Integration](#step-7-admin-integration)
10. [Step 8: API Endpoints](#step-8-api-endpoints)
11. [Step 9: Production Deployment](#step-9-production-deployment)
12. [Step 10: Monitoring & Troubleshooting](#step-10-monitoring--troubleshooting)
13. [Environment Variables](#environment-variables)
14. [Quick Start Checklist](#quick-start-checklist)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DESIFIRMS ADMIN PANEL                              │
│  Create Audit → Trigger Background Task → View Results → Generate Report     │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                              ▼
    ┌─────────────────┐            ┌─────────────────┐
    │   Django Admin  │            │   REST API      │
    │   (Manual)      │            │   (Automated)   │
    └────────┬────────┘            └────────┬────────┘
             │                              │
             └──────────────┬───────────────┘
                            ▼
                  ┌─────────────────┐
                  │   Redis Broker  │◄─── Message Queue
                  │   localhost:6379│     (Tasks wait here)
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Celery Worker  │◄─── Background Processor
                  │  (1-4 workers)  │     (Runs tasks asynchronously)
                  └────────┬────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ PageSpeed API   │ │ Lighthouse CLI  │ │   OpenAI API    │
│ (Google)        │ │ (Local Node.js) │ │   (ChatGPT)     │
│                 │ │                 │ │                 │
│ • Lab Data      │ │ • Full Audit    │ │ • AI Analysis   │
│ • Field Data    │ │ • Localhost OK  │ │ • Recommendations│
│ • Core Web      │ │ • Staging OK    │ │ • Fix Guides    │
│   Vitals        │ │                 │ │                 │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └─────────────────┬─┴───────────────────┘
                           ▼
              ┌─────────────────────────────┐
              │    PostgreSQL / SQLite      │
              │                             │
              │  • SiteAudit (container)    │
              │  • PageAudit (page scores)  │
              │  • AuditIssue (issues)      │
              │  • PageSpeedResult          │
              │  • SEOKeyword (keywords)    │
              │  • SEOKeywordCluster        │
              │  • AISEORecommendation      │
              │  • django_celery_results    │
              └─────────────────────────────┘
```

### Why This Architecture?

| Problem | Solution |
|---------|----------|
| SEO audits take 5-30 minutes | Background tasks with Celery |
| Web requests timeout after 30s | Async processing, immediate response |
| Single audit blocks everything | Multiple concurrent workers |
| Audit fails midway | Automatic retry with exponential backoff |
| Need progress tracking | Task ID stored in database |
| Need multiple data sources | Combine PageSpeed + Lighthouse + Search Console |

---

## Prerequisites

### Development
- Python 3.9+
- Node.js 18+ (for Lighthouse CLI)
- Redis (local or Docker)
- Chrome/Chromium (for Lighthouse)

### Production
- Ubuntu 20.04+ or similar
- Redis server (apt install redis-server)
- Systemd for service management
- PostgreSQL recommended

---

## Step 1: Install Dependencies

### Python Packages

Add to `requirements.txt`:

```txt
# Background Tasks
celery>=5.3.0
redis>=5.0.0
django-celery-results>=2.5.0

# OpenAI for AI Analysis
openai>=1.0.0

# PDF Reports
reportlab>=4.0.0
Pillow>=10.0.0

# API Requests
requests>=2.31.0
```

Install:

```bash
pip install celery redis django-celery-results openai reportlab Pillow requests
```

### Lighthouse CLI

```bash
# Install globally
npm install -g lighthouse

# Verify installation
lighthouse --version
```

---

## Step 2: Celery Configuration

### Create `project_name/celery.py`

```python
"""
Celery configuration for Desifirms.

This module configures Celery for background task processing,
primarily used for long-running SEO audits that would otherwise
timeout in the web request/response cycle.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desifirms.settings')

app = Celery('desifirms')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f'Request: {self.request!r}')
```

### Update `project_name/__init__.py`

```python
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)
```

---

## Step 3: Django Settings

Add to `settings.py`:

```python
import os

# =============================================================================
# INSTALLED APPS
# =============================================================================
INSTALLED_APPS = [
    # ... existing apps ...
    'django_celery_results',  # Store task results in database
]

# =============================================================================
# CELERY CONFIGURATION
# =============================================================================
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes max per task
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# =============================================================================
# OPENAI CONFIGURATION
# =============================================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_SEO_MODEL = os.getenv("OPENAI_SEO_MODEL", "gpt-4o-mini")

# =============================================================================
# GOOGLE API CONFIGURATION
# =============================================================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")
GOOGLE_SEARCH_CONSOLE_PROPERTY = os.getenv("GOOGLE_SEARCH_CONSOLE_PROPERTY", "")

# =============================================================================
# UPLOAD LIMITS (for large keyword CSV imports)
# =============================================================================
DATA_UPLOAD_MAX_NUMBER_FIELDS = 50000
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
```

Run migrations:

```bash
python manage.py migrate django_celery_results
```

---

## Step 4: Database Models

Create `seo/models.py`:

```python
"""
SEO Audit Models for Desifirms.

Handles:
- Site-wide audits (container)
- Page-level audits (scores)
- Individual issues (problems found)
- PageSpeed API results
- SEO keywords and clusters
- AI recommendations
"""

from django.db import models
from django.utils import timezone


class SiteAudit(models.Model):
    """
    Container for a complete site audit.

    Tracks overall status, aggregated scores, and links to page audits.
    """
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

    STRATEGY_MOBILE = "mobile"
    STRATEGY_DESKTOP = "desktop"
    STRATEGY_CHOICES = [
        (STRATEGY_MOBILE, "Mobile"),
        (STRATEGY_DESKTOP, "Desktop"),
    ]

    # Basic info
    name = models.CharField(max_length=200, help_text="Descriptive name for this audit")
    domain = models.CharField(max_length=255, help_text="Domain to audit (e.g., desifirms.com.au)")
    strategy = models.CharField(max_length=10, choices=STRATEGY_CHOICES, default=STRATEGY_MOBILE)

    # URLs to audit (JSON list)
    target_urls = models.JSONField(
        default=list,
        blank=True,
        help_text="List of URLs to audit. Leave empty to audit homepage only."
    )

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Aggregated scores (0-100)
    avg_performance = models.FloatField(null=True, blank=True)
    avg_seo = models.FloatField(null=True, blank=True)
    avg_accessibility = models.FloatField(null=True, blank=True)
    avg_best_practices = models.FloatField(null=True, blank=True)

    # Issue counts
    total_pages = models.IntegerField(default=0)
    total_issues = models.IntegerField(default=0)
    critical_issues = models.IntegerField(default=0)

    # AI Analysis
    ai_analysis = models.TextField(blank=True, help_text="ChatGPT-generated analysis")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Site Audit"
        verbose_name_plural = "Site Audits"

    def __str__(self):
        return f"{self.name} - {self.domain} ({self.get_status_display()})"

    @property
    def duration(self):
        """Calculate audit duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    def get_issues(self):
        """Get all issues for this audit, ordered by severity."""
        return AuditIssue.objects.filter(
            page_audit__site_audit=self
        ).order_by('severity', '-savings_ms')


class PageAudit(models.Model):
    """
    Individual page audit within a site audit.

    Stores Lighthouse/PageSpeed scores and Core Web Vitals.
    """
    site_audit = models.ForeignKey(
        SiteAudit,
        on_delete=models.CASCADE,
        related_name='page_audits'
    )
    url = models.URLField(max_length=2000)
    strategy = models.CharField(max_length=10, default="mobile")

    # Lighthouse scores (0-100)
    performance_score = models.IntegerField(null=True, blank=True)
    seo_score = models.IntegerField(null=True, blank=True)
    accessibility_score = models.IntegerField(null=True, blank=True)
    best_practices_score = models.IntegerField(null=True, blank=True)

    # Core Web Vitals
    lcp = models.FloatField(null=True, blank=True, help_text="Largest Contentful Paint (seconds)")
    cls = models.FloatField(null=True, blank=True, help_text="Cumulative Layout Shift")
    fcp = models.FloatField(null=True, blank=True, help_text="First Contentful Paint (seconds)")
    tbt = models.FloatField(null=True, blank=True, help_text="Total Blocking Time (ms)")
    ttfb = models.FloatField(null=True, blank=True, help_text="Time to First Byte (ms)")
    si = models.FloatField(null=True, blank=True, help_text="Speed Index (seconds)")

    # Status
    status = models.CharField(max_length=20, default="pending")
    error_message = models.TextField(blank=True)

    # Raw Lighthouse/PageSpeed data
    raw_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-performance_score']
        unique_together = ['site_audit', 'url', 'strategy']

    def __str__(self):
        return f"{self.url} - Performance: {self.performance_score}"


class AuditIssue(models.Model):
    """
    Individual issue found during audit.

    Represents a specific problem like "Reduce unused JavaScript"
    with affected files and potential savings.
    """
    SEVERITY_ERROR = "error"
    SEVERITY_WARNING = "warning"
    SEVERITY_INFO = "info"
    SEVERITY_PASSED = "passed"
    SEVERITY_CHOICES = [
        (SEVERITY_ERROR, "Error"),
        (SEVERITY_WARNING, "Warning"),
        (SEVERITY_INFO, "Info"),
        (SEVERITY_PASSED, "Passed"),
    ]

    CATEGORY_CHOICES = [
        ("performance", "Performance"),
        ("seo", "SEO"),
        ("accessibility", "Accessibility"),
        ("best-practices", "Best Practices"),
    ]

    STATUS_OPEN = "open"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_FIXED = "fixed"
    STATUS_IGNORED = "ignored"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_FIXED, "Fixed"),
        (STATUS_IGNORED, "Ignored"),
    ]

    page_audit = models.ForeignKey(
        PageAudit,
        on_delete=models.CASCADE,
        related_name='issues'
    )

    # Issue identification
    audit_id = models.CharField(max_length=200, help_text="Lighthouse audit ID")
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)

    # Classification
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)

    # Metrics
    score = models.FloatField(null=True, blank=True, help_text="0-1 score from Lighthouse")
    display_value = models.CharField(max_length=200, blank=True)
    savings_ms = models.FloatField(default=0, help_text="Potential time savings in ms")
    savings_bytes = models.FloatField(default=0, help_text="Potential size savings in bytes")

    # Detailed data (affected files, elements, etc.)
    details = models.JSONField(default=dict, blank=True)

    # AI recommendation for this specific issue
    ai_fix_recommendation = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['severity', '-savings_ms']

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"


class PageSpeedResult(models.Model):
    """
    Google PageSpeed Insights API results.

    Stores both lab data (Lighthouse) and field data (CrUX real user metrics).
    """
    page_audit = models.ForeignKey(
        PageAudit,
        on_delete=models.CASCADE,
        related_name='pagespeed_results',
        null=True,
        blank=True
    )
    url = models.URLField(max_length=2000)
    strategy = models.CharField(max_length=10, default="mobile")

    # Lab data (Lighthouse)
    lab_performance_score = models.IntegerField(null=True, blank=True)
    lab_lcp = models.FloatField(null=True, blank=True)
    lab_fcp = models.FloatField(null=True, blank=True)
    lab_cls = models.FloatField(null=True, blank=True)
    lab_tbt = models.FloatField(null=True, blank=True)
    lab_si = models.FloatField(null=True, blank=True)

    # Field data (Chrome User Experience Report - real users)
    field_lcp = models.FloatField(null=True, blank=True)
    field_fid = models.FloatField(null=True, blank=True)
    field_inp = models.FloatField(null=True, blank=True)
    field_cls = models.FloatField(null=True, blank=True)
    field_fcp = models.FloatField(null=True, blank=True)
    field_ttfb = models.FloatField(null=True, blank=True)

    # Origin-level metrics (site-wide from CrUX)
    origin_lcp = models.FloatField(null=True, blank=True)
    origin_inp = models.FloatField(null=True, blank=True)
    origin_cls = models.FloatField(null=True, blank=True)

    # Overall category from CrUX
    overall_category = models.CharField(max_length=50, blank=True)

    # Raw API response (trimmed)
    raw_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"PageSpeed: {self.url} ({self.strategy})"


class SEODataUpload(models.Model):
    """
    Container for SEO keyword data uploads (CSV from Ubersuggest, etc.).
    """
    SOURCE_UBERSUGGEST = "ubersuggest"
    SOURCE_SEMRUSH = "semrush"
    SOURCE_AHREFS = "ahrefs"
    SOURCE_MANUAL = "manual"
    SOURCE_CHOICES = [
        (SOURCE_UBERSUGGEST, "Ubersuggest"),
        (SOURCE_SEMRUSH, "SEMrush"),
        (SOURCE_AHREFS, "Ahrefs"),
        (SOURCE_MANUAL, "Manual Entry"),
    ]

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_PROCESSED = "processed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_PROCESSED, "Processed"),
        (STATUS_FAILED, "Failed"),
    ]

    name = models.CharField(max_length=200)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default=SOURCE_UBERSUGGEST)
    file = models.FileField(upload_to='seo_uploads/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Processed data insights
    insights = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_source_display()})"


class SEOKeyword(models.Model):
    """
    Individual keyword from SEO data upload.
    """
    INTENT_INFORMATIONAL = "informational"
    INTENT_TRANSACTIONAL = "transactional"
    INTENT_COMMERCIAL = "commercial"
    INTENT_NAVIGATIONAL = "navigational"
    INTENT_CHOICES = [
        (INTENT_INFORMATIONAL, "Informational"),
        (INTENT_TRANSACTIONAL, "Transactional"),
        (INTENT_COMMERCIAL, "Commercial"),
        (INTENT_NAVIGATIONAL, "Navigational"),
    ]

    TYPE_SHORT = "short_tail"
    TYPE_MID = "mid_tail"
    TYPE_LONG = "long_tail"
    TYPE_CHOICES = [
        (TYPE_SHORT, "Short Tail"),
        (TYPE_MID, "Mid Tail"),
        (TYPE_LONG, "Long Tail"),
    ]

    upload = models.ForeignKey(SEODataUpload, on_delete=models.CASCADE, related_name='keywords')
    cluster = models.ForeignKey(
        'SEOKeywordCluster',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='keywords'
    )

    keyword = models.CharField(max_length=500)
    search_volume = models.IntegerField(default=0)
    seo_difficulty = models.IntegerField(default=0)
    paid_difficulty = models.IntegerField(default=0)
    cpc = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    intent = models.CharField(max_length=20, choices=INTENT_CHOICES, blank=True)
    keyword_type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True)
    priority_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority_score', '-search_volume']

    def __str__(self):
        return f"{self.keyword} (Vol: {self.search_volume})"


class SEOKeywordCluster(models.Model):
    """
    Cluster of related keywords for content strategy.
    """
    upload = models.ForeignKey(SEODataUpload, on_delete=models.CASCADE, related_name='clusters')

    label = models.CharField(max_length=200)
    seed_keyword = models.CharField(max_length=500, blank=True)
    intent = models.CharField(max_length=20, blank=True)

    avg_volume = models.IntegerField(default=0)
    avg_difficulty = models.IntegerField(default=0)
    priority_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority_score', '-avg_volume']

    def __str__(self):
        return f"{self.label} ({self.keywords.count()} keywords)"


class AISEORecommendation(models.Model):
    """
    AI-generated SEO recommendation.
    """
    CATEGORY_OPPORTUNITY = "opportunity"
    CATEGORY_CLUSTER_BRIEF = "content_brief"
    CATEGORY_METADATA = "metadata"
    CATEGORY_FAQ = "faq"
    CATEGORY_CHOICES = [
        (CATEGORY_OPPORTUNITY, "Opportunity Overview"),
        (CATEGORY_CLUSTER_BRIEF, "Content Brief"),
        (CATEGORY_METADATA, "Metadata Kit"),
        (CATEGORY_FAQ, "FAQ Ideas"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_GENERATED = "generated"
    STATUS_ERROR = "error"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_GENERATED, "Generated"),
        (STATUS_ERROR, "Error"),
    ]

    upload = models.ForeignKey(
        SEODataUpload,
        on_delete=models.CASCADE,
        related_name='recommendations',
        null=True,
        blank=True
    )
    cluster = models.ForeignKey(
        SEOKeywordCluster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    keyword = models.ForeignKey(
        SEOKeyword,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=300)

    # AI interaction
    prompt = models.TextField(blank=True)
    response = models.TextField(blank=True)

    # Tracking
    ai_model = models.CharField(max_length=50, blank=True)
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_category_display()}: {self.title}"
```

Run migrations:

```bash
python manage.py makemigrations seo
python manage.py migrate
```

---

## Step 5: Background Tasks

Create `seo/tasks.py`:

```python
"""
Celery tasks for background processing of SEO audits.

These tasks run asynchronously to prevent request timeouts when
auditing multiple URLs with Lighthouse.
"""

import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_lighthouse_audit_task(self, audit_id: int) -> dict:
    """
    Run Lighthouse audit for a SiteAudit in the background.

    Args:
        audit_id: ID of the SiteAudit to process

    Returns:
        dict with audit results
    """
    from .models import SiteAudit
    from .services.lighthouse import LighthouseService

    try:
        audit = SiteAudit.objects.get(id=audit_id)
        logger.info(f"Starting background Lighthouse audit for {audit.name} (ID: {audit_id})")

        # Update task ID on the audit for tracking
        audit.celery_task_id = self.request.id
        audit.status = SiteAudit.STATUS_RUNNING
        audit.started_at = timezone.now()
        audit.save(update_fields=['celery_task_id', 'status', 'started_at'])

        # Run the audit
        service = LighthouseService(audit)

        if not service.check_lighthouse_installed():
            audit.status = SiteAudit.STATUS_FAILED
            audit.save(update_fields=['status'])
            return {
                "success": False,
                "error": "Lighthouse CLI not installed on server"
            }

        result = service.run_audit()

        logger.info(f"Completed Lighthouse audit for {audit.name}: {result.get('pages_audited', 0)} pages")
        return result

    except SiteAudit.DoesNotExist:
        logger.error(f"SiteAudit with ID {audit_id} not found")
        return {"success": False, "error": f"Audit {audit_id} not found"}

    except Exception as e:
        logger.exception(f"Error in Lighthouse audit task: {e}")

        # Update audit status to failed
        try:
            audit = SiteAudit.objects.get(id=audit_id)
            audit.status = SiteAudit.STATUS_FAILED
            audit.save(update_fields=['status'])
        except:
            pass

        # Retry on transient errors
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_pagespeed_audit_task(self, audit_id: int) -> dict:
    """
    Run PageSpeed analysis for a SiteAudit in the background.

    Args:
        audit_id: ID of the SiteAudit to process

    Returns:
        dict with audit results
    """
    from .models import SiteAudit, PageAudit, AuditIssue
    from .services.pagespeed import PageSpeedService
    from django.db.models import Avg

    try:
        audit = SiteAudit.objects.get(id=audit_id)
        logger.info(f"Starting background PageSpeed audit for {audit.name} (ID: {audit_id})")

        # Update task ID and status
        audit.celery_task_id = self.request.id
        audit.status = SiteAudit.STATUS_RUNNING
        audit.started_at = timezone.now()
        audit.save(update_fields=['celery_task_id', 'status', 'started_at'])

        service = PageSpeedService()
        urls = audit.target_urls or [f"https://{audit.domain}/"]

        pages_done = 0
        errors = []

        for url in urls:
            try:
                data = service.analyze_url(url, audit.strategy)
                if not data or not data.get('success'):
                    errors.append({"url": url, "error": "PageSpeed API failed"})
                    continue

                # Save to PageAudit
                page_audit, created = PageAudit.objects.update_or_create(
                    site_audit=audit,
                    url=url,
                    defaults={
                        'strategy': audit.strategy,
                        'performance_score': data.get('lab_performance_score'),
                        'seo_score': data.get('seo_score'),
                        'accessibility_score': data.get('accessibility_score'),
                        'best_practices_score': data.get('best_practices_score'),
                        'lcp': data.get('lab_lcp'),
                        'cls': data.get('lab_cls'),
                        'fcp': data.get('lab_fcp'),
                        'tbt': data.get('lab_tbt'),
                        'si': data.get('lab_si'),
                        'ttfb': data.get('field_ttfb'),
                        'status': 'completed',
                        'raw_data': data.get('raw_data', {})
                    }
                )

                # Create issues from opportunities and diagnostics
                if created:
                    for issue_data in data.get('issues', []):
                        AuditIssue.objects.create(
                            page_audit=page_audit,
                            audit_id=issue_data.get('id', ''),
                            title=issue_data.get('title', ''),
                            description=issue_data.get('description', ''),
                            category=issue_data.get('category', 'performance'),
                            severity=issue_data.get('severity', 'info'),
                            score=issue_data.get('score'),
                            display_value=issue_data.get('display_value', ''),
                            savings_ms=issue_data.get('savings_ms', 0),
                            savings_bytes=issue_data.get('savings_bytes', 0),
                            details=issue_data.get('details', {}),
                        )

                pages_done += 1
                logger.info(f"Completed PageSpeed for {url} ({pages_done}/{len(urls)})")

            except Exception as e:
                logger.error(f"Error analyzing {url}: {e}")
                errors.append({"url": url, "error": str(e)})

        # Update audit with results
        page_audits = audit.page_audits.all()
        if page_audits.exists():
            averages = page_audits.aggregate(
                avg_perf=Avg('performance_score'),
                avg_seo=Avg('seo_score'),
                avg_acc=Avg('accessibility_score'),
                avg_bp=Avg('best_practices_score'),
            )
            audit.avg_performance = averages['avg_perf']
            audit.avg_seo = averages['avg_seo']
            audit.avg_accessibility = averages['avg_acc']
            audit.avg_best_practices = averages['avg_bp']

        audit.status = SiteAudit.STATUS_COMPLETED
        audit.completed_at = timezone.now()
        audit.total_pages = pages_done
        audit.total_issues = AuditIssue.objects.filter(page_audit__site_audit=audit).count()
        audit.critical_issues = AuditIssue.objects.filter(
            page_audit__site_audit=audit,
            severity='error'
        ).count()
        audit.save()

        logger.info(f"Completed PageSpeed audit for {audit.name}: {pages_done} pages")

        return {
            "success": True,
            "pages_audited": pages_done,
            "total_issues": audit.total_issues,
            "errors": errors
        }

    except SiteAudit.DoesNotExist:
        logger.error(f"SiteAudit with ID {audit_id} not found")
        return {"success": False, "error": f"Audit {audit_id} not found"}

    except Exception as e:
        logger.exception(f"Error in PageSpeed audit task: {e}")

        try:
            audit = SiteAudit.objects.get(id=audit_id)
            audit.status = SiteAudit.STATUS_FAILED
            audit.save(update_fields=['status'])
        except:
            pass

        raise self.retry(exc=e)


@shared_task(bind=True)
def generate_ai_analysis_task(self, audit_id: int) -> dict:
    """
    Generate AI analysis for completed audit in the background.

    Args:
        audit_id: ID of the SiteAudit to analyze

    Returns:
        dict with analysis status
    """
    from .models import SiteAudit
    from .services.seo_audit_ai import SEOAuditAIEngine

    try:
        audit = SiteAudit.objects.get(id=audit_id)
        logger.info(f"Starting AI analysis for {audit.name}")

        engine = SEOAuditAIEngine(audit)
        result = engine.analyze()

        if result.get('success'):
            logger.info(f"Completed AI analysis for {audit.name}")
            return {"success": True, "tokens": result.get('tokens', {})}
        else:
            return {"success": False, "error": result.get('error', 'AI analysis failed')}

    except SiteAudit.DoesNotExist:
        return {"success": False, "error": f"Audit {audit_id} not found"}
    except Exception as e:
        logger.exception(f"Error generating AI analysis: {e}")
        return {"success": False, "error": str(e)}


@shared_task(bind=True)
def process_seo_upload_task(self, upload_id: int) -> dict:
    """
    Process SEO keyword upload and generate clusters/recommendations.

    Args:
        upload_id: ID of the SEODataUpload to process

    Returns:
        dict with processing status
    """
    from .models import SEODataUpload
    from .services.seo_ai import SEOAutomationEngine

    try:
        upload = SEODataUpload.objects.get(id=upload_id)
        logger.info(f"Processing SEO upload: {upload.name}")

        upload.status = SEODataUpload.STATUS_PROCESSING
        upload.save(update_fields=['status'])

        # Process the file (implement based on your CSV format)
        # upload.ingest_from_file()

        # Generate AI recommendations
        engine = SEOAutomationEngine(upload)
        result = engine.generate()

        upload.status = SEODataUpload.STATUS_PROCESSED
        upload.processed_at = timezone.now()
        upload.save()

        logger.info(f"Completed processing SEO upload: {upload.name}")
        return {"success": True, "recommendations": result.get('recommendations', 0)}

    except SEODataUpload.DoesNotExist:
        return {"success": False, "error": f"Upload {upload_id} not found"}
    except Exception as e:
        logger.exception(f"Error processing SEO upload: {e}")
        try:
            upload = SEODataUpload.objects.get(id=upload_id)
            upload.status = SEODataUpload.STATUS_FAILED
            upload.save(update_fields=['status'])
        except:
            pass
        return {"success": False, "error": str(e)}
```

---

## Step 6: Services

### Create `seo/services/__init__.py`

```python
# Services package
```

### Create `seo/services/ai_client.py`

```python
"""
AI Content Engine - OpenAI Wrapper.

Centralized AI client for all SEO automation features.
"""

from __future__ import annotations
from django.conf import settings


class AIContentEngine:
    """
    Lightweight wrapper around OpenAI chat completions.
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are an AI strategist working for Desifirms. You help summarise data, "
        "draft marketing insights, and respond with confident, actionable copy."
    )

    def __init__(self, model: str | None = None):
        self.model = model or getattr(settings, "OPENAI_SEO_MODEL", "gpt-4o-mini")
        self.api_key = getattr(settings, "OPENAI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                self.client = None

    @property
    def enabled(self) -> bool:
        return bool(self.client)

    def generate(
        self,
        *,
        prompt: str,
        temperature: float = 0.2,
        system_prompt: str | None = None,
    ) -> dict:
        """Execute a chat completion and return normalized payload."""
        if not self.enabled:
            return {
                "success": False,
                "output": "AI generation disabled. Set OPENAI_API_KEY.",
                "model": self.model,
                "usage": {},
                "error": "missing_api_key",
            }

        system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )
        except Exception as exc:
            return {
                "success": False,
                "output": "",
                "model": self.model,
                "usage": {},
                "error": str(exc),
            }

        message = response.choices[0].message.content if response.choices else ""
        usage = getattr(response, "usage", None)
        return {
            "success": True,
            "output": (message or "").strip(),
            "model": self.model,
            "usage": {
                "prompt_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
                "completion_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
            },
        }
```

### Create `seo/services/pagespeed.py`

```python
"""
PageSpeed Insights API Service.

Uses Google's PageSpeed Insights API to get:
- Lab data (Lighthouse results)
- Field data (Real User Metrics from Chrome User Experience Report)
- Origin-level metrics (site-wide performance)

Benefits:
- Real user data (CrUX) - actual visitor experience
- No server-side Chrome required
- Origin-level metrics for overall site health

Limitations:
- ~400 queries/day free tier
- Public URLs only (no localhost/staging)
"""

from __future__ import annotations
import requests
import logging
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class PageSpeedService:
    """Service for running PageSpeed Insights analysis."""

    API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    def __init__(self):
        self.api_key = getattr(settings, "GOOGLE_API_KEY", "")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def analyze_url(self, url: str, strategy: str = "mobile") -> dict:
        """
        Analyze a URL using PageSpeed Insights API.

        Args:
            url: URL to analyze
            strategy: "mobile" or "desktop"

        Returns:
            dict with analysis results
        """
        result = {
            "success": False,
            "url": url,
            "strategy": strategy,
        }

        if not self.enabled:
            result["error"] = "PageSpeed API not configured. Set GOOGLE_API_KEY."
            return result

        try:
            params = {
                "url": url,
                "key": self.api_key,
                "strategy": strategy,
                "category": ["performance", "accessibility", "best-practices", "seo"],
            }

            logger.info(f"Running PageSpeed analysis for {url}")
            response = requests.get(self.API_URL, params=params, timeout=60)

            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("error", {}).get("message", response.text[:200])
                result["error"] = f"API error ({response.status_code}): {error_msg}"
                return result

            data = response.json()

            # Extract lab data (Lighthouse)
            lighthouse = data.get("lighthouseResult", {})
            categories = lighthouse.get("categories", {})
            audits = lighthouse.get("audits", {})

            result["lab_performance_score"] = self._extract_score(categories.get("performance"))
            result["seo_score"] = self._extract_score(categories.get("seo"))
            result["accessibility_score"] = self._extract_score(categories.get("accessibility"))
            result["best_practices_score"] = self._extract_score(categories.get("best-practices"))

            # Extract lab metrics
            result["lab_lcp"] = self._extract_metric(audits, "largest-contentful-paint", ms_to_s=True)
            result["lab_fcp"] = self._extract_metric(audits, "first-contentful-paint", ms_to_s=True)
            result["lab_cls"] = self._extract_metric(audits, "cumulative-layout-shift")
            result["lab_tbt"] = self._extract_metric(audits, "total-blocking-time")
            result["lab_si"] = self._extract_metric(audits, "speed-index", ms_to_s=True)

            # Extract field data (CrUX)
            loading_exp = data.get("loadingExperience", {})
            if loading_exp.get("metrics"):
                result["has_field_data"] = True
                field_metrics = loading_exp.get("metrics", {})
                result["field_lcp"] = self._extract_crux_metric(field_metrics, "LARGEST_CONTENTFUL_PAINT_MS", ms_to_s=True)
                result["field_fid"] = self._extract_crux_metric(field_metrics, "FIRST_INPUT_DELAY_MS")
                result["field_inp"] = self._extract_crux_metric(field_metrics, "INTERACTION_TO_NEXT_PAINT")
                result["field_cls"] = self._extract_crux_metric(field_metrics, "CUMULATIVE_LAYOUT_SHIFT_SCORE")
                result["field_fcp"] = self._extract_crux_metric(field_metrics, "FIRST_CONTENTFUL_PAINT_MS", ms_to_s=True)
                result["field_ttfb"] = self._extract_crux_metric(field_metrics, "EXPERIMENTAL_TIME_TO_FIRST_BYTE")
                result["overall_category"] = loading_exp.get("overall_category", "")
            else:
                result["has_field_data"] = False
                result["overall_category"] = "NO_DATA"

            # Extract issues from Lighthouse data
            result["issues"] = self._extract_issues(lighthouse)

            # Store raw data (trimmed)
            result["raw_data"] = self._trim_raw_data(data)

            result["success"] = True

        except requests.Timeout:
            result["error"] = "PageSpeed API request timed out"
        except requests.RequestException as e:
            result["error"] = f"Network error: {str(e)}"
        except Exception as e:
            result["error"] = str(e)
            logger.exception(f"Error analyzing {url}")

        return result

    def _extract_score(self, category_data: Optional[dict]) -> Optional[int]:
        """Extract score from category data (0-100)."""
        if not category_data:
            return None
        score = category_data.get("score")
        if score is not None:
            return int(score * 100)
        return None

    def _extract_metric(self, audits: dict, audit_id: str, ms_to_s: bool = False) -> Optional[float]:
        """Extract metric value from audits."""
        audit = audits.get(audit_id, {})
        value = audit.get("numericValue")
        if value is not None and ms_to_s:
            return value / 1000
        return value

    def _extract_crux_metric(self, metrics: dict, metric_id: str, ms_to_s: bool = False) -> Optional[float]:
        """Extract metric from CrUX data (75th percentile)."""
        metric = metrics.get(metric_id, {})
        percentile = metric.get("percentile")
        if percentile is not None:
            if ms_to_s:
                return percentile / 1000
            return percentile
        return None

    def _extract_issues(self, lighthouse_data: dict) -> list:
        """Extract issues/opportunities from Lighthouse data."""
        issues = []
        audits = lighthouse_data.get("audits", {})
        categories = lighthouse_data.get("categories", {})

        # Map audit IDs to categories
        audit_to_category = {}
        for cat_id, cat_data in categories.items():
            for audit_ref in cat_data.get("auditRefs", []):
                audit_to_category[audit_ref.get("id")] = cat_id

        for audit_id, audit_data in audits.items():
            score = audit_data.get("score")
            if score is None or score == 1:
                continue

            if score == 0:
                severity = "error"
            elif score < 0.5:
                severity = "warning"
            else:
                severity = "info"

            category = audit_to_category.get(audit_id, "performance")

            details = audit_data.get("details", {})
            savings_ms = details.get("overallSavingsMs", 0) or 0
            savings_bytes = details.get("overallSavingsBytes", 0) or 0

            issues.append({
                "id": audit_id,
                "title": audit_data.get("title", ""),
                "description": audit_data.get("description", ""),
                "category": category,
                "severity": severity,
                "score": score,
                "display_value": audit_data.get("displayValue", ""),
                "savings_ms": savings_ms,
                "savings_bytes": savings_bytes,
                "details": self._trim_details(details),
            })

        # Sort by severity and savings
        severity_order = {"error": 0, "warning": 1, "info": 2}
        issues.sort(key=lambda x: (severity_order.get(x["severity"], 3), -x["savings_ms"]))

        return issues

    def _trim_details(self, details: dict) -> dict:
        """Trim details while preserving important diagnostic data."""
        if not details:
            return {}

        trimmed = {"type": details.get("type")}

        if "overallSavingsMs" in details:
            trimmed["overallSavingsMs"] = details["overallSavingsMs"]
        if "overallSavingsBytes" in details:
            trimmed["overallSavingsBytes"] = details["overallSavingsBytes"]

        if "items" in details:
            trimmed_items = []
            for item in details["items"][:20]:
                trimmed_item = {}
                important_keys = ["url", "totalBytes", "wastedBytes", "wastedMs", "cacheLifetimeMs"]
                for key in important_keys:
                    if key in item:
                        trimmed_item[key] = item[key]

                if "node" in item:
                    node = item["node"]
                    trimmed_item["node"] = {
                        "selector": node.get("selector", "")[:300],
                        "snippet": node.get("snippet", "")[:400],
                    }

                if trimmed_item:
                    trimmed_items.append(trimmed_item)

            trimmed["items"] = trimmed_items

        return trimmed

    def _trim_raw_data(self, data: dict) -> dict:
        """Trim raw API response."""
        lighthouse = data.get("lighthouseResult", {})

        return {
            "id": data.get("id"),
            "analysisUTCTimestamp": data.get("analysisUTCTimestamp"),
            "loadingExperience": {
                "overall_category": data.get("loadingExperience", {}).get("overall_category"),
            },
            "lighthouseResult": {
                "lighthouseVersion": lighthouse.get("lighthouseVersion"),
                "fetchTime": lighthouse.get("fetchTime"),
                "requestedUrl": lighthouse.get("requestedUrl"),
                "finalUrl": lighthouse.get("finalUrl"),
            },
        }
```

### Create `seo/services/seo_audit_ai.py`

```python
"""
SEO Audit AI Engine.

Uses ChatGPT to analyze audit results and generate:
- Prioritized fix recommendations
- Technical implementation guidance
- Impact assessments
- Executive summaries
"""

from __future__ import annotations
import json
import logging
from typing import Optional
from .ai_client import AIContentEngine

logger = logging.getLogger(__name__)


class SEOAuditAIEngine:
    """AI-powered analysis engine for SEO audit results."""

    SYSTEM_PROMPT = """You are an expert SEO specialist analyzing technical audit data
for Desifirms, a business listings and classifieds platform running Django backend.

Your role is to:
1. Analyze audit issues and prioritize them by impact
2. Provide specific, actionable fix recommendations
3. Include code examples when applicable (Django/Python)
4. Focus on Core Web Vitals and SEO best practices
5. Consider the platform architecture when suggesting fixes

Always format your responses with clear sections and bullet points."""

    def __init__(self, site_audit=None, ai_engine: Optional[AIContentEngine] = None):
        self.site_audit = site_audit
        self.ai = ai_engine or AIContentEngine()

    def analyze(self) -> dict:
        """Generate comprehensive AI analysis of audit results."""
        if not self.site_audit:
            return {"success": False, "error": "No site audit provided"}

        if not self.ai.enabled:
            return {"success": False, "error": "AI engine not enabled"}

        result = {"success": False}

        try:
            audit_data = self._gather_audit_data()
            prompt = self._build_analysis_prompt(audit_data)

            response = self.ai.generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3,
            )

            if response.get("success"):
                analysis = response.get("output", "")

                # Save to site audit
                self.site_audit.ai_analysis = analysis
                self.site_audit.save(update_fields=["ai_analysis", "updated_at"])

                result["success"] = True
                result["analysis"] = analysis
                result["tokens"] = response.get("usage", {})
            else:
                result["error"] = response.get("error", "AI generation failed")

        except Exception as e:
            result["error"] = str(e)
            logger.exception("Error generating audit analysis")

        return result

    def _gather_audit_data(self) -> dict:
        """Gather comprehensive audit data for analysis."""
        from ..models import PageAudit, AuditIssue

        page_audits = self.site_audit.page_audits.all()

        data = {
            "site_audit": {
                "name": self.site_audit.name,
                "domain": self.site_audit.domain,
                "strategy": self.site_audit.strategy,
                "total_pages": self.site_audit.total_pages,
                "total_issues": self.site_audit.total_issues,
                "avg_performance": self.site_audit.avg_performance,
                "avg_seo": self.site_audit.avg_seo,
                "avg_accessibility": self.site_audit.avg_accessibility,
                "avg_best_practices": self.site_audit.avg_best_practices,
            },
            "pages": [],
            "issues": [],
        }

        for page in page_audits[:10]:
            data["pages"].append({
                "url": page.url,
                "performance": page.performance_score,
                "seo": page.seo_score,
                "lcp": page.lcp,
                "cls": page.cls,
                "tbt": page.tbt,
            })

        issues = AuditIssue.objects.filter(
            page_audit__site_audit=self.site_audit,
            severity__in=["error", "warning"],
        ).order_by("severity", "-savings_ms")[:20]

        for issue in issues:
            data["issues"].append({
                "title": issue.title,
                "category": issue.category,
                "severity": issue.severity,
                "url": issue.page_audit.url,
                "savings_ms": issue.savings_ms,
                "display_value": issue.display_value,
            })

        return data

    def _build_analysis_prompt(self, audit_data: dict) -> str:
        """Build analysis prompt from audit data."""
        return f"""Analyze this SEO audit for {audit_data['site_audit']['domain']}:

## SITE OVERVIEW
- Domain: {audit_data['site_audit']['domain']}
- Strategy: {audit_data['site_audit']['strategy']}
- Pages Audited: {audit_data['site_audit']['total_pages']}
- Total Issues: {audit_data['site_audit']['total_issues']}

## CURRENT SCORES
- Performance: {audit_data['site_audit'].get('avg_performance', 'N/A')}
- SEO: {audit_data['site_audit'].get('avg_seo', 'N/A')}
- Accessibility: {audit_data['site_audit'].get('avg_accessibility', 'N/A')}
- Best Practices: {audit_data['site_audit'].get('avg_best_practices', 'N/A')}

## PAGE DATA
{json.dumps(audit_data['pages'][:5], indent=2)}

## ISSUES FOUND
{json.dumps(audit_data['issues'][:15], indent=2)}

---

Provide:

## 1. EXECUTIVE SUMMARY
2-3 sentences summarizing overall site health.

## 2. CRITICAL ISSUES (Fix Immediately)
List with specific fixes and code examples.

## 3. QUICK WINS (Easy Improvements)
Low-effort, high-impact fixes.

## 4. CORE WEB VITALS ANALYSIS
- LCP status and fixes
- CLS status and fixes
- TBT/FID status and fixes

## 5. PRIORITY ACTION PLAN
Numbered list of fixes by impact.

## 6. MONITORING TARGETS
Score targets to aim for."""
```

---

## Step 7: Admin Integration

Create `seo/admin.py`:

```python
"""
Django Admin for SEO Engine.

Provides:
- Site audit management with background task actions
- Page audit viewing
- Issue tracking
- Keyword management
"""

from django.contrib import admin, messages
from django.utils.html import format_html
from .models import (
    SiteAudit, PageAudit, AuditIssue, PageSpeedResult,
    SEODataUpload, SEOKeyword, SEOKeywordCluster, AISEORecommendation
)


@admin.register(SiteAudit)
class SiteAuditAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'domain', 'strategy', 'status_badge',
        'avg_performance', 'avg_seo', 'total_issues', 'created_at'
    ]
    list_filter = ['status', 'strategy', 'created_at']
    search_fields = ['name', 'domain']
    readonly_fields = ['celery_task_id', 'started_at', 'completed_at', 'created_at', 'updated_at']
    actions = ['run_pagespeed_audit', 'run_lighthouse_audit', 'generate_ai_analysis']

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'domain', 'strategy', 'target_urls')
        }),
        ('Status', {
            'fields': ('status', 'celery_task_id', 'started_at', 'completed_at')
        }),
        ('Scores', {
            'fields': (
                ('avg_performance', 'avg_seo'),
                ('avg_accessibility', 'avg_best_practices'),
                ('total_pages', 'total_issues', 'critical_issues'),
            )
        }),
        ('AI Analysis', {
            'fields': ('ai_analysis',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'pending': '#6b7280',
            'running': '#3b82f6',
            'completed': '#22c55e',
            'failed': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    @admin.action(description="Run PageSpeed Audit (Background)")
    def run_pagespeed_audit(self, request, queryset):
        from .tasks import run_pagespeed_audit_task

        for audit in queryset:
            if audit.status == 'running':
                self.message_user(
                    request,
                    f"Audit '{audit.name}' is already running",
                    messages.WARNING
                )
                continue

            audit.status = 'pending'
            audit.save(update_fields=['status'])

            task = run_pagespeed_audit_task.delay(audit.id)

            audit.celery_task_id = task.id
            audit.save(update_fields=['celery_task_id'])

            self.message_user(
                request,
                f"PageSpeed audit '{audit.name}' queued. Task ID: {task.id}",
                messages.SUCCESS
            )

    @admin.action(description="Run Lighthouse Audit (Background)")
    def run_lighthouse_audit(self, request, queryset):
        from .tasks import run_lighthouse_audit_task

        for audit in queryset:
            if audit.status == 'running':
                self.message_user(
                    request,
                    f"Audit '{audit.name}' is already running",
                    messages.WARNING
                )
                continue

            audit.status = 'pending'
            audit.save(update_fields=['status'])

            task = run_lighthouse_audit_task.delay(audit.id)

            audit.celery_task_id = task.id
            audit.save(update_fields=['celery_task_id'])

            self.message_user(
                request,
                f"Lighthouse audit '{audit.name}' queued. Task ID: {task.id}",
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


@admin.register(PageAudit)
class PageAuditAdmin(admin.ModelAdmin):
    list_display = [
        'url', 'site_audit', 'performance_score', 'seo_score',
        'lcp', 'cls', 'status'
    ]
    list_filter = ['status', 'site_audit', 'strategy']
    search_fields = ['url']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AuditIssue)
class AuditIssueAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'severity_badge', 'category', 'page_audit',
        'savings_ms', 'status'
    ]
    list_filter = ['severity', 'category', 'status']
    search_fields = ['title', 'description']

    def severity_badge(self, obj):
        colors = {
            'error': '#ef4444',
            'warning': '#f59e0b',
            'info': '#3b82f6',
            'passed': '#22c55e',
        }
        color = colors.get(obj.severity, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 10px;">{}</span>',
            color, obj.severity.upper()
        )
    severity_badge.short_description = 'Severity'


@admin.register(SEODataUpload)
class SEODataUploadAdmin(admin.ModelAdmin):
    list_display = ['name', 'source', 'status', 'created_at', 'processed_at']
    list_filter = ['status', 'source']
    actions = ['process_upload']

    @admin.action(description="Process Upload (Background)")
    def process_upload(self, request, queryset):
        from .tasks import process_seo_upload_task

        for upload in queryset:
            if upload.status == 'processing':
                self.message_user(
                    request,
                    f"Upload '{upload.name}' is already processing",
                    messages.WARNING
                )
                continue

            task = process_seo_upload_task.delay(upload.id)
            self.message_user(
                request,
                f"Processing queued for '{upload.name}'",
                messages.SUCCESS
            )


@admin.register(SEOKeyword)
class SEOKeywordAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'search_volume', 'seo_difficulty', 'intent', 'priority_score']
    list_filter = ['intent', 'keyword_type', 'upload']
    search_fields = ['keyword']


@admin.register(SEOKeywordCluster)
class SEOKeywordClusterAdmin(admin.ModelAdmin):
    list_display = ['label', 'intent', 'avg_volume', 'avg_difficulty', 'priority_score']
    list_filter = ['intent', 'upload']


@admin.register(AISEORecommendation)
class AISEORecommendationAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'ai_model', 'created_at']
    list_filter = ['category', 'status']
    search_fields = ['title', 'response']
```

---

## Step 8: API Endpoints

Create `seo/views.py`:

```python
"""
REST API Views for SEO Engine.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SiteAudit, PageAudit, AuditIssue
from .tasks import run_pagespeed_audit_task, generate_ai_analysis_task


class SiteAuditViewSet(viewsets.ModelViewSet):
    """API ViewSet for Site Audits."""
    queryset = SiteAudit.objects.all()
    # Add serializer_class when implemented

    @action(detail=True, methods=['post'])
    def run_audit(self, request, pk=None):
        """Trigger background audit for a site."""
        audit = self.get_object()

        if audit.status == 'running':
            return Response(
                {"error": "Audit is already running"},
                status=status.HTTP_400_BAD_REQUEST
            )

        audit.status = 'pending'
        audit.save(update_fields=['status'])

        task = run_pagespeed_audit_task.delay(audit.id)

        audit.celery_task_id = task.id
        audit.save(update_fields=['celery_task_id'])

        return Response({
            "message": "Audit queued",
            "task_id": task.id
        })

    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Trigger AI analysis for completed audit."""
        audit = self.get_object()

        if audit.status != 'completed':
            return Response(
                {"error": "Audit must be completed first"},
                status=status.HTTP_400_BAD_REQUEST
            )

        task = generate_ai_analysis_task.delay(audit.id)

        return Response({
            "message": "AI analysis queued",
            "task_id": task.id
        })

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get audit results with issues."""
        audit = self.get_object()

        pages = []
        for page in audit.page_audits.all():
            page_data = {
                "url": page.url,
                "performance": page.performance_score,
                "seo": page.seo_score,
                "accessibility": page.accessibility_score,
                "best_practices": page.best_practices_score,
                "lcp": page.lcp,
                "cls": page.cls,
                "issues": []
            }

            for issue in page.issues.filter(severity__in=['error', 'warning'])[:10]:
                page_data["issues"].append({
                    "title": issue.title,
                    "severity": issue.severity,
                    "category": issue.category,
                    "savings_ms": issue.savings_ms,
                })

            pages.append(page_data)

        return Response({
            "audit": {
                "name": audit.name,
                "domain": audit.domain,
                "status": audit.status,
                "avg_performance": audit.avg_performance,
                "avg_seo": audit.avg_seo,
                "total_issues": audit.total_issues,
            },
            "pages": pages,
            "ai_analysis": audit.ai_analysis if audit.ai_analysis else None,
        })
```

Add to `seo/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiteAuditViewSet

router = DefaultRouter()
router.register(r'audits', SiteAuditViewSet)

urlpatterns = [
    path('api/seo/', include(router.urls)),
]
```

---

## Step 9: Production Deployment

### Create Celery Worker Service

Create `/etc/systemd/system/celery-worker.service`:

```ini
[Unit]
Description=Celery Worker for Desifirms SEO Audits
After=network.target redis.service

[Service]
Type=forking
User=desifirms
Group=desifirms
WorkingDirectory=/var/www/desifirms/backend

# Adjust paths to match your server setup
Environment="PATH=/var/www/desifirms/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=desifirms.settings"
Environment="CELERY_BROKER_URL=redis://localhost:6379/0"

ExecStart=/var/www/desifirms/venv/bin/celery -A desifirms worker \
    --loglevel=info \
    --concurrency=2 \
    --logfile=/var/log/celery/worker.log \
    --pidfile=/var/run/celery/worker.pid \
    --detach

ExecStop=/bin/kill -TERM $MAINPID
ExecReload=/bin/kill -HUP $MAINPID

# Restart on failure
Restart=on-failure
RestartSec=10

# Create necessary directories
RuntimeDirectory=celery
LogsDirectory=celery

[Install]
WantedBy=multi-user.target
```

### Setup Commands

```bash
# Create directories
sudo mkdir -p /var/log/celery /var/run/celery
sudo chown desifirms:desifirms /var/log/celery /var/run/celery

# Install Redis
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Enable Celery service
sudo systemctl daemon-reload
sudo systemctl enable celery-worker
sudo systemctl start celery-worker

# Check status
sudo systemctl status celery-worker
```

---

## Step 10: Monitoring & Troubleshooting

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
celery -A desifirms flower --port=5555
```

Access at `http://localhost:5555`

### Common Issues

| Issue | Solution |
|-------|----------|
| Task stuck in PENDING | Celery worker not running. Check `systemctl status celery-worker` |
| Connection refused | Redis not running. Check `systemctl status redis-server` |
| Serialization error | Non-JSON-serializable data in task args. Use primitive types only. |
| Task timeout | Increase `CELERY_TASK_TIME_LIMIT` in settings |
| Memory issues | Use `celery -A desifirms worker --max-tasks-per-child=100` |
| Lighthouse not found | Install globally: `npm install -g lighthouse` |

### Logs

```bash
# Celery worker logs
tail -f /var/log/celery/worker.log

# Redis logs
sudo tail -f /var/log/redis/redis-server.log

# Django logs
tail -f /var/log/django/error.log
```

---

## Environment Variables

Create `.env` file:

```bash
# =============================================================================
# CELERY & REDIS
# =============================================================================
CELERY_BROKER_URL=redis://localhost:6379/0

# =============================================================================
# OPENAI (for AI Analysis)
# =============================================================================
OPENAI_API_KEY=sk-...
OPENAI_SEO_MODEL=gpt-4o-mini

# =============================================================================
# GOOGLE APIS
# =============================================================================
# PageSpeed Insights API (get from Google Cloud Console)
GOOGLE_API_KEY=AIza...

# Search Console (optional)
GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/service-account.json
GOOGLE_SEARCH_CONSOLE_PROPERTY=https://www.desifirms.com.au/

# =============================================================================
# DJANGO
# =============================================================================
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=desifirms.com.au,www.desifirms.com.au
```

---

## Quick Start Checklist

### Development Setup

- [ ] Install Python dependencies: `pip install celery redis django-celery-results openai`
- [ ] Install Lighthouse: `npm install -g lighthouse`
- [ ] Start Redis: `redis-server` or `docker run -p 6379:6379 redis`
- [ ] Create `celery.py` configuration
- [ ] Update `__init__.py` with celery import
- [ ] Add Celery settings to `settings.py`
- [ ] Run migrations: `python manage.py migrate django_celery_results`
- [ ] Create SEO models and migrate
- [ ] Create background tasks in `tasks.py`
- [ ] Create services (PageSpeed, AI)
- [ ] Register admin classes
- [ ] Start Celery worker: `celery -A desifirms worker -l INFO`
- [ ] Test: Create audit in admin, run action, check results

### Production Setup

- [ ] Install Redis on server: `apt install redis-server`
- [ ] Create Celery systemd service
- [ ] Enable and start service: `systemctl enable celery-worker`
- [ ] Configure log rotation for `/var/log/celery/`
- [ ] Set environment variables in production
- [ ] Set up monitoring (Flower or custom)
- [ ] Configure backup for audit data

---

## Desifirms-Specific Considerations

### Business Listings Integration

You may want to audit individual business listing pages. Add a field to link audits:

```python
class SiteAudit(models.Model):
    # ... existing fields ...
    business_listing = models.ForeignKey(
        'listings.BusinessListing',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optionally link to a specific business listing"
    )
```

### Scheduled Audits

Use Celery Beat for scheduled audits:

```python
# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'weekly-homepage-audit': {
        'task': 'seo.tasks.run_pagespeed_audit_task',
        'schedule': crontab(day_of_week=1, hour=2, minute=0),  # Monday 2 AM
        'args': (1,),  # Audit ID 1
    },
}
```

Start beat scheduler:

```bash
celery -A desifirms beat -l INFO
```

---

## Cost Estimation

| Service | Free Tier | Paid |
|---------|-----------|------|
| PageSpeed API | 400/day | $200 for 50k queries |
| Lighthouse CLI | Unlimited | Free (runs locally) |
| OpenAI GPT-4o-mini | - | ~$0.01-0.02 per audit analysis |
| Redis | Unlimited | Free (self-hosted) |

**Recommended Strategy:**
1. Use Lighthouse CLI for unlimited local audits
2. Use PageSpeed API for real-user CrUX data
3. Only trigger AI analysis when scores < 70 or for first audit
4. Batch multiple pages per audit to reduce AI calls

---

This documentation provides everything needed to implement the SEO engine in Desifirms. Copy the relevant sections and adapt the code to your specific Django project structure.
