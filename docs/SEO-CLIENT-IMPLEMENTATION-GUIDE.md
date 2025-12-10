# SEO Client Implementation Guide

How to use Codeteki's SEO system to manage your own sites (Desifirms) and client websites.

---

## Table of Contents

1. [Two Approaches](#two-approaches)
2. [Approach A: Manage from Codeteki (Recommended)](#approach-a-manage-from-codeteki-recommended)
3. [Approach B: Full Implementation on Client Site](#approach-b-full-implementation-on-client-site)
4. [AI Alternatives (No OpenAI)](#ai-alternatives-no-openai)
5. [Quick Reference: Admin Actions](#quick-reference-admin-actions)
6. [Files to Copy for Client Implementation](#files-to-copy-for-client-implementation)

---

## Two Approaches

| Approach | Best For | AI Cost | Complexity |
|----------|----------|---------|------------|
| **A: Manage from Codeteki** | Most clients, Desifirms | Your API key only | Low |
| **B: Full Implementation** | Clients who want self-service | Their API key (or none) | Medium |

---

## Approach A: Manage from Codeteki (Recommended)

You generate all SEO data in YOUR Codeteki admin, then manually apply it to the client's site.

### Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                   YOUR CODETEKI ADMIN                        │
├─────────────────────────────────────────────────────────────┤
│  1. Upload client's Ubersuggest CSV                         │
│  2. Process → Generate AI Playbooks                         │
│  3. Review Meta Kit recommendations                          │
│  4. Copy the generated SEO data                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Copy/Paste
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   CLIENT'S WEBSITE                           │
├─────────────────────────────────────────────────────────────┤
│  Add to their HTML <head>:                                   │
│  • <title>                                                   │
│  • <meta name="description">                                │
│  • <meta name="keywords">                                   │
│  • <link rel="canonical">                                   │
│  • Open Graph tags                                          │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step

#### Step 1: Upload Client's Keyword Data

1. Go to **Admin → SEO: Data Uploads → Add**
2. Name it clearly: `Client - Desifirms - Dec 2025`
3. Upload Ubersuggest CSV
4. Save

#### Step 2: Process the Upload

1. Select the upload
2. Action: **"🔄 Process Ubersuggest Export (All Types)"**
3. Click Go

#### Step 3: Generate AI Playbooks

1. Select the same upload
2. Action: **"🤖 Generate AI playbooks (Top 3 clusters)"**
3. Wait for completion

#### Step 4: View Meta Kit Results

1. Go to **Admin → SEO: AI Recommendations**
2. Filter by Category: **"Meta Tags"**
3. Click on a recommendation to view full response

#### Step 5: Copy to Client Site

From the AI Response, copy:

```html
<!-- Title -->
<title>Professional Accounting Services Melbourne | Desifirms</title>

<!-- Meta Description -->
<meta name="description" content="Expert accounting and tax services for Australian businesses. BAS, tax returns, bookkeeping. Melbourne-based accountants.">

<!-- Keywords -->
<meta name="keywords" content="accountant melbourne, tax services, BAS agent, bookkeeping, small business accountant">

<!-- Canonical URL -->
<link rel="canonical" href="https://desifirms.com.au/services/accounting">

<!-- Open Graph -->
<meta property="og:title" content="Professional Accounting Services Melbourne">
<meta property="og:description" content="Expert accounting and tax services for Australian businesses.">
<meta property="og:url" content="https://desifirms.com.au/services/accounting">
<meta property="og:image" content="https://desifirms.com.au/images/og-accounting.jpg">
<meta property="og:type" content="website">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Professional Accounting Services Melbourne">
<meta name="twitter:description" content="Expert accounting and tax services for Australian businesses.">
```

### Advantages of Approach A

- ✅ No setup on client site
- ✅ AI costs on your account only
- ✅ Client doesn't need technical knowledge
- ✅ You control the quality
- ✅ Works with any CMS/platform

---

## Approach B: Full Implementation on Client Site

Add the complete SEO management system to the client's website.

### Required Components

```
Client's Django Project
├── models.py      → PageSEO model
├── admin.py       → PageSEOAdmin with actions
├── views.py       → API endpoint
├── urls.py        → Route for /api/seo/
└── services/
    └── ai_client.py → AI integration (optional)
```

### Step 1: Add PageSEO Model

```python
# client_project/core/models.py

class PageSEO(models.Model):
    """SEO settings for each page."""

    PAGE_CHOICES = [
        ('home', 'Home Page'),
        ('services', 'Services Page'),
        ('about', 'About Page'),
        ('contact', 'Contact Page'),
        ('custom', 'Custom URL'),
    ]

    # Page identification
    page = models.CharField(max_length=50, choices=PAGE_CHOICES, default='custom')
    custom_url = models.CharField(max_length=255, blank=True)

    # Core SEO fields
    meta_title = models.CharField(max_length=160)
    meta_description = models.TextField(max_length=320)
    meta_keywords = models.TextField(blank=True, help_text="Comma separated")
    canonical_url = models.URLField(blank=True)

    # Open Graph
    og_title = models.CharField(max_length=160, blank=True)
    og_description = models.TextField(max_length=320, blank=True)
    og_image = models.ImageField(upload_to='seo/', blank=True, null=True)

    # Tracking
    target_keyword = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page SEO"
        verbose_name_plural = "Page SEO Settings"

    def __str__(self):
        return f"SEO - {self.get_page_display()}"

    @property
    def target_url(self):
        """Get the URL this SEO applies to."""
        if self.custom_url:
            return self.custom_url
        return f"/{self.page}" if self.page != 'home' else "/"
```

### Step 2: Add Admin Interface

```python
# client_project/core/admin.py

from django.contrib import admin
from .models import PageSEO

@admin.register(PageSEO)
class PageSEOAdmin(admin.ModelAdmin):
    list_display = ('page', 'meta_title', 'target_url', 'has_keywords', 'updated_at')
    list_filter = ('page',)
    search_fields = ('meta_title', 'meta_description', 'meta_keywords')

    fieldsets = (
        ('Page', {
            'fields': ('page', 'custom_url')
        }),
        ('Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url')
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('target_keyword',),
            'classes': ('collapse',)
        }),
    )

    def has_keywords(self, obj):
        return "✅" if obj.meta_keywords else "❌"
    has_keywords.short_description = "Keywords"
```

### Step 3: Add API Endpoint

```python
# client_project/core/views.py

from django.http import JsonResponse
from .models import PageSEO

def seo_api(request):
    """Return SEO data for a page."""
    page = request.GET.get('page', 'home')

    # Try to find by page type first
    seo = PageSEO.objects.filter(page=page).first()

    # If not found and it's a custom URL, try that
    if not seo and page not in dict(PageSEO.PAGE_CHOICES):
        seo = PageSEO.objects.filter(custom_url__icontains=page).first()

    if not seo:
        return JsonResponse({'error': 'SEO not found'}, status=404)

    return JsonResponse({
        'metaTitle': seo.meta_title,
        'metaDescription': seo.meta_description,
        'metaKeywords': seo.meta_keywords,
        'canonicalUrl': seo.canonical_url,
        'ogTitle': seo.og_title or seo.meta_title,
        'ogDescription': seo.og_description or seo.meta_description,
        'ogImage': seo.og_image.url if seo.og_image else None,
        'targetKeyword': seo.target_keyword,
    })


# client_project/core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('seo/', views.seo_api, name='seo-api'),
]


# client_project/urls.py (main)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    # ... other routes
]
```

### Step 4: Frontend Integration

#### Option A: React with react-helmet

```jsx
// components/SEOHead.jsx
import { Helmet } from "react-helmet-async";
import { useEffect, useState } from "react";

export default function SEOHead({ page }) {
    const [seo, setSeo] = useState(null);

    useEffect(() => {
        fetch(`/api/seo/?page=${page}`)
            .then(r => r.json())
            .then(data => setSeo(data))
            .catch(() => setSeo(null));
    }, [page]);

    if (!seo) return null;

    return (
        <Helmet>
            <title>{seo.metaTitle}</title>
            <meta name="description" content={seo.metaDescription} />
            <meta name="keywords" content={seo.metaKeywords} />
            <link rel="canonical" href={seo.canonicalUrl} />

            <meta property="og:title" content={seo.ogTitle} />
            <meta property="og:description" content={seo.ogDescription} />
            <meta property="og:url" content={seo.canonicalUrl} />
            {seo.ogImage && <meta property="og:image" content={seo.ogImage} />}

            <meta name="twitter:card" content="summary_large_image" />
            <meta name="twitter:title" content={seo.ogTitle} />
            <meta name="twitter:description" content={seo.ogDescription} />
        </Helmet>
    );
}

// Usage in pages:
// <SEOHead page="home" />
// <SEOHead page="services" />
// <SEOHead page="contact" />
```

#### Option B: Django Templates (No React)

```html
<!-- base.html -->
{% load seo_tags %}

<!DOCTYPE html>
<html>
<head>
    {% get_seo page_name as seo %}

    <title>{{ seo.meta_title }}</title>
    <meta name="description" content="{{ seo.meta_description }}">
    <meta name="keywords" content="{{ seo.meta_keywords }}">
    <link rel="canonical" href="{{ seo.canonical_url }}">

    <meta property="og:title" content="{{ seo.og_title|default:seo.meta_title }}">
    <meta property="og:description" content="{{ seo.og_description|default:seo.meta_description }}">
    {% if seo.og_image %}
    <meta property="og:image" content="{{ seo.og_image.url }}">
    {% endif %}
</head>
```

```python
# templatetags/seo_tags.py
from django import template
from core.models import PageSEO

register = template.Library()

@register.simple_tag
def get_seo(page_name):
    return PageSEO.objects.filter(page=page_name).first()
```

---

## AI Alternatives (No OpenAI)

If client doesn't want to pay for OpenAI:

### Option 1: No AI - Manual Entry Only

Just use the admin without AI actions. Client enters meta tags manually.

```python
# Remove these actions from admin.py:
# - generate_ai_meta
# - generate_quick_meta
# - apply_meta_to_page
```

### Option 2: Use Your API Key Temporarily

1. Set your OPENAI_API_KEY on client's server
2. Generate all SEO once
3. Remove the API key
4. Client manages manually after that

### Option 3: Free Self-Hosted LLM (Ollama)

```python
# services/ai_client.py
import requests

class AIContentEngine:
    def __init__(self):
        self.enabled = True
        self.model = "llama2"
        self.base_url = "http://localhost:11434"

    def generate(self, prompt, system_prompt=None, temperature=0.3):
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt or ''}\n\n{prompt}",
                    "stream": False
                },
                timeout=60
            )
            data = response.json()
            return {
                "success": True,
                "output": data.get("response", ""),
                "model": self.model
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
```

**Setup Ollama on server:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2
# or for better results:
ollama pull mistral
```

### Option 4: Claude API (Alternative to OpenAI)

```python
# services/ai_client.py
from anthropic import Anthropic

class AIContentEngine:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.enabled = bool(settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-haiku-20240307"  # Cheapest option

    def generate(self, prompt, system_prompt=None, temperature=0.3):
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt or "You are an SEO expert.",
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "success": True,
                "output": response.content[0].text,
                "model": self.model
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
```

---

## Quick Reference: Admin Actions

### SEO Data Upload Actions

| Action | What It Does |
|--------|--------------|
| **Process Ubersuggest Export** | Parse CSV → Create keywords & clusters |
| **Generate AI Playbooks** | Create recommendations for top 3 clusters |

### AI Recommendation Actions

| Action | What It Does |
|--------|--------------|
| **Auto-Apply Meta Kit to Best Matching Page** | Find matching PageSEO, apply title/desc/keywords/OG/canonical |
| **Apply to ALL Matching Services** | Apply to all matching service pages at once |

### Page SEO Actions

| Action | What It Does |
|--------|--------------|
| **Generate AI Meta Tags (Ubersuggest)** | Uses uploaded keyword data for context |
| **Quick AI Meta Tags (No Ubersuggest)** | Direct AI generation, no keywords needed |

---

## Files to Copy for Client Implementation

### Minimal (No AI)

```
Copy from Codeteki:
────────────────────
backend/core/models.py     → PageSEO class only
backend/core/admin.py      → PageSEOAdmin class (remove AI actions)
backend/core/views.py      → _serialize_page_seo function
```

### Full (With AI)

```
Copy from Codeteki:
────────────────────
backend/core/models.py            → PageSEO, SEODataUpload, SEOKeyword,
                                    SEOKeywordCluster, AISEORecommendation
backend/core/admin.py             → All SEO-related admin classes
backend/core/views.py             → SEO API endpoints
backend/core/services/ai_client.py → AIContentEngine
backend/core/services/seo_ai.py   → SEOAutomationEngine
backend/core/sitemaps.py          → Dynamic sitemap classes

frontend/src/components/SEOHead.jsx → React SEO component
```

---

## Summary: Which Approach for Desifirms?

### Recommended: Approach A (Manage from Codeteki)

1. Upload Desifirms keywords to Codeteki admin
2. Generate Meta Kits using your OpenAI key
3. Copy SEO data to Desifirms HTML/templates
4. Update whenever needed

**Why?**
- No additional setup on Desifirms
- No recurring AI costs for Desifirms
- Centralized management
- You control quality

### Later: Approach B (If Desifirms Grows)

If Desifirms becomes a major project with frequent updates:
1. Add PageSEO model
2. Add API endpoint
3. Use Ollama for free AI (self-hosted)

---

## Checklist for Client SEO Setup

- [ ] Upload client's Ubersuggest CSV to Codeteki
- [ ] Process the upload
- [ ] Generate AI playbooks
- [ ] Review Meta Kit recommendations
- [ ] Copy to client site:
  - [ ] Meta title
  - [ ] Meta description
  - [ ] Meta keywords
  - [ ] Canonical URL
  - [ ] OG title
  - [ ] OG description
  - [ ] OG image
- [ ] Test with Google Rich Results Test
- [ ] Submit sitemap to Search Console

---

*Last updated: December 2025*
