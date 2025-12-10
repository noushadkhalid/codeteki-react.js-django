# Client Site SEO Setup: Django + React Single Server

How to inject dynamic SEO meta tags server-side for Django + React apps.

---

## The Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REQUEST                              │
│                  /services/accounting                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      DJANGO                                  │
│  1. Catches ALL routes (catch-all view)                     │
│  2. Looks up PageSEO for this URL                           │
│  3. Renders index.html WITH meta tags injected              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    BROWSER                                   │
│  1. Receives HTML with correct <title>, <meta> tags         │
│  2. Google sees the meta tags immediately                   │
│  3. React loads and hydrates the page                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Steps

### Step 1: Create PageSEO Model

```python
# core/models.py

from django.db import models

class PageSEO(models.Model):
    """SEO settings for each page."""

    # URL matching - can be exact path or pattern
    url_path = models.CharField(
        max_length=255,
        unique=True,
        help_text="URL path like '/' or '/services/accounting'. Use '*' for patterns."
    )

    # Core SEO
    meta_title = models.CharField(max_length=160)
    meta_description = models.TextField(max_length=320)
    meta_keywords = models.TextField(blank=True)
    canonical_url = models.URLField(blank=True)

    # Open Graph
    og_title = models.CharField(max_length=160, blank=True)
    og_description = models.TextField(max_length=320, blank=True)
    og_image = models.URLField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page SEO"
        ordering = ['url_path']

    def __str__(self):
        return f"{self.url_path} - {self.meta_title[:30]}"

    @classmethod
    def get_for_path(cls, path):
        """Get SEO for a URL path, with fallback to defaults."""
        # Try exact match first
        seo = cls.objects.filter(url_path=path, is_active=True).first()

        # Try pattern match (e.g., /services/* matches /services/accounting)
        if not seo:
            parts = path.rstrip('/').split('/')
            while parts:
                pattern = '/'.join(parts) + '/*'
                seo = cls.objects.filter(url_path=pattern, is_active=True).first()
                if seo:
                    break
                parts.pop()

        # Fallback to homepage
        if not seo:
            seo = cls.objects.filter(url_path='/', is_active=True).first()

        return seo
```

### Step 2: Create Admin Interface

```python
# core/admin.py

from django.contrib import admin
from .models import PageSEO

@admin.register(PageSEO)
class PageSEOAdmin(admin.ModelAdmin):
    list_display = ('url_path', 'meta_title', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('url_path', 'meta_title', 'meta_description')

    fieldsets = (
        ('URL', {
            'fields': ('url_path', 'is_active'),
            'description': 'Use exact paths like "/" or "/contact", or patterns like "/services/*"'
        }),
        ('Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url')
        }),
        ('Open Graph (Social Sharing)', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'classes': ('collapse',)
        }),
    )
```

### Step 3: Create React App View with SEO Injection

```python
# core/views.py

from django.views.generic import TemplateView
from django.conf import settings
from .models import PageSEO

class ReactAppView(TemplateView):
    """
    Serves React app with server-side SEO injection.

    Django injects meta tags into the HTML before sending to browser,
    so Google sees the correct meta tags immediately.
    """
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get current URL path
        path = self.request.path

        # Look up SEO for this path
        seo = PageSEO.get_for_path(path)

        if seo:
            context['seo'] = {
                'title': seo.meta_title,
                'description': seo.meta_description,
                'keywords': seo.meta_keywords,
                'canonical': seo.canonical_url or f"{settings.SITE_URL}{path}",
                'og_title': seo.og_title or seo.meta_title,
                'og_description': seo.og_description or seo.meta_description,
                'og_image': seo.og_image or f"{settings.SITE_URL}/og-image.jpg",
            }
        else:
            # Default SEO
            context['seo'] = {
                'title': 'Desifirms - Professional Services',
                'description': 'Your default description here.',
                'keywords': 'default, keywords',
                'canonical': f"{settings.SITE_URL}{path}",
                'og_title': 'Desifirms',
                'og_description': 'Your default description here.',
                'og_image': f"{settings.SITE_URL}/og-image.jpg",
            }

        return context
```

### Step 4: Create the HTML Template

Create a Django template that wraps your React app:

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- SEO Meta Tags (Injected by Django) -->
    <title>{{ seo.title }}</title>
    <meta name="description" content="{{ seo.description }}">
    <meta name="keywords" content="{{ seo.keywords }}">
    <link rel="canonical" href="{{ seo.canonical }}">

    <!-- Open Graph -->
    <meta property="og:title" content="{{ seo.og_title }}">
    <meta property="og:description" content="{{ seo.og_description }}">
    <meta property="og:image" content="{{ seo.og_image }}">
    <meta property="og:url" content="{{ seo.canonical }}">
    <meta property="og:type" content="website">

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{{ seo.og_title }}">
    <meta name="twitter:description" content="{{ seo.og_description }}">
    <meta name="twitter:image" content="{{ seo.og_image }}">

    <!-- Robots -->
    <meta name="robots" content="index, follow">

    <!-- Favicon -->
    <link rel="icon" type="image/png" href="/favicon.png">

    <!-- React App CSS (from build) -->
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
</head>
<body>
    <!-- React App Root -->
    <div id="root"></div>

    <!-- React App JS (from build) -->
    <script src="{% static 'js/main.js' %}"></script>
</body>
</html>
```

### Step 5: Configure URLs

```python
# urls.py

from django.contrib import admin
from django.urls import path, re_path
from core.views import ReactAppView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API routes (if any)
    path('api/', include('core.api_urls')),

    # Catch-all for React SPA (MUST be last)
    re_path(r'^.*$', ReactAppView.as_view(), name='react-app'),
]
```

### Step 6: Configure Settings

```python
# settings.py

SITE_URL = 'https://desifirms.com.au'

# Template directory
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Your templates folder
        ...
    },
]
```

---

## How It Works

### When User Visits /services/accounting:

1. **Django receives request** for `/services/accounting`
2. **Looks up PageSEO** with `url_path="/services/accounting"` or pattern `/services/*`
3. **Injects meta tags** into template context
4. **Renders index.html** with correct:
   - `<title>Accounting Services | Desifirms</title>`
   - `<meta name="description" content="...">`
   - `<link rel="canonical" href="https://desifirms.com.au/services/accounting">`
5. **Browser receives HTML** with SEO already in `<head>`
6. **Google crawls** and sees correct meta tags immediately
7. **React loads** and takes over for interactivity

---

## Setting Up SEO in Admin

### Example Entries:

| URL Path | Meta Title | Meta Description |
|----------|------------|------------------|
| `/` | Home - Desifirms | Professional accounting services... |
| `/services` | Our Services - Desifirms | Tax, BAS, bookkeeping services... |
| `/services/*` | Services - Desifirms | (Pattern for all service pages) |
| `/services/accounting` | Accounting - Desifirms | Expert accounting services... |
| `/contact` | Contact Us - Desifirms | Get in touch with our team... |

### Pattern Matching:

- `/` = Exact match for homepage
- `/services` = Exact match for services page
- `/services/*` = Matches any `/services/anything` URL
- `/blog/*` = Matches any `/blog/anything` URL

---

## React Side (Optional)

If you also want React to update meta tags for client-side navigation:

```jsx
// components/SEOHead.jsx
import { Helmet } from "react-helmet-async";
import { useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

export default function SEOHead() {
    const location = useLocation();

    // Fetch SEO from API for client-side updates
    const { data: seo } = useQuery({
        queryKey: ['seo', location.pathname],
        queryFn: () =>
            fetch(`/api/seo/?path=${location.pathname}`)
                .then(r => r.json()),
        staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    });

    if (!seo) return null;

    return (
        <Helmet>
            <title>{seo.title}</title>
            <meta name="description" content={seo.description} />
            <link rel="canonical" href={seo.canonical} />
            <meta property="og:title" content={seo.og_title} />
            <meta property="og:description" content={seo.og_description} />
        </Helmet>
    );
}
```

### API Endpoint:

```python
# core/api_views.py

from django.http import JsonResponse
from .models import PageSEO

def seo_api(request):
    path = request.GET.get('path', '/')
    seo = PageSEO.get_for_path(path)

    if not seo:
        return JsonResponse({'error': 'Not found'}, status=404)

    return JsonResponse({
        'title': seo.meta_title,
        'description': seo.meta_description,
        'keywords': seo.meta_keywords,
        'canonical': seo.canonical_url,
        'og_title': seo.og_title or seo.meta_title,
        'og_description': seo.og_description or seo.meta_description,
        'og_image': seo.og_image,
    })
```

---

## Summary

| Layer | What It Does |
|-------|--------------|
| **Django Template** | Injects meta tags server-side (Google sees this) |
| **React Helmet** | Updates meta tags on client-side navigation |
| **PageSEO Model** | Stores all SEO data in database |
| **Admin Interface** | Easy editing of SEO for each page |

This gives you:
- ✅ **Server-side meta tags** (Google sees them immediately)
- ✅ **Easy admin editing** (no code changes needed)
- ✅ **Pattern matching** (one entry for `/services/*` covers all services)
- ✅ **Client-side updates** (for smooth SPA navigation)

---

## Quick Setup Checklist

- [ ] Add PageSEO model
- [ ] Run migrations
- [ ] Add admin interface
- [ ] Create index.html template with `{{ seo.* }}` variables
- [ ] Update ReactAppView to inject SEO context
- [ ] Add default SEO entry for `/`
- [ ] Add SEO entries for main pages
- [ ] Test with Google Rich Results Test

---

*Last updated: December 2025*
