# Django Unfold Admin Theme Guide

A comprehensive guide to implementing a modern, Tailwind-based Django admin using **Django Unfold**. This theme is used in Codeteki and can be replicated for Desifirms and future client projects.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Settings Configuration](#settings-configuration)
4. [Admin Class Structure](#admin-class-structure)
5. [Sidebar Navigation](#sidebar-navigation)
6. [Dashboard Customization](#dashboard-customization)
7. [Fieldsets with Emoji Icons](#fieldsets-with-emoji-icons)
8. [Inline Models](#inline-models)
9. [Custom Actions](#custom-actions)
10. [Badge Callbacks](#badge-callbacks)
11. [Color Scheme](#color-scheme)
12. [Loading States & Toast Notifications](#loading-states--toast-notifications)
13. [Deployment Loading Page](#deployment-loading-page)
14. [Static Files](#static-files)
15. [Complete Example](#complete-example)

---

## Overview

Django Unfold is a modern admin theme that replaces Django's default admin with a beautiful Tailwind CSS-based interface. Key features:

- Modern Tailwind CSS design
- Collapsible sidebar navigation
- Custom dashboard with cards
- Environment indicators
- Custom color schemes
- Material icons support
- Responsive design

**Package:** `django-unfold`
**Docs:** https://unfoldadmin.com/

---

## Installation

```bash
pip install django-unfold
```

Add to `INSTALLED_APPS` **before** `django.contrib.admin`:

```python
INSTALLED_APPS = [
    # Unfold must come BEFORE django.contrib.admin
    "unfold",
    "unfold.contrib.filters",  # Optional: enhanced filters
    "unfold.contrib.forms",    # Optional: enhanced forms

    "django.contrib.admin",
    "django.contrib.auth",
    # ... rest of apps
]
```

---

## Settings Configuration

Add the `UNFOLD` dict to your settings.py:

```python
from django.templatetags.static import static
from django.urls import reverse_lazy

UNFOLD = {
    # =========================================
    # SITE BRANDING
    # =========================================
    "SITE_TITLE": "My Project CMS",
    "SITE_HEADER": "My Project",
    "SITE_SUBHEADER": "Content Management System",

    # Dropdown menu in header
    "SITE_DROPDOWN": [
        {
            "icon": "public",
            "title": "View Live Site",
            "link": "/",
        },
    ],

    # =========================================
    # LOGOS & FAVICON
    # =========================================
    "SITE_LOGO": {
        "light": lambda request: static("images/logo.png"),
        "dark": lambda request: static("images/logo-dark.png"),
    },
    "SITE_SYMBOL": "rocket_launch",  # Material icon for collapsed sidebar
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": lambda request: static("favicon.ico"),
        },
    ],

    # =========================================
    # FEATURES
    # =========================================
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,

    # Environment badge (Development/Production)
    "ENVIRONMENT": "myapp.utils.environment_callback",

    # Custom dashboard
    "DASHBOARD_CALLBACK": "myapp.utils.dashboard_callback",

    # Login page background
    "LOGIN": {
        "image": lambda request: static("images/login-bg.jpg"),
    },

    # =========================================
    # CUSTOM CSS/JS
    # =========================================
    "STYLES": [
        lambda request: static("css/admin-custom.css"),
    ],
    "SCRIPTS": [
        lambda request: static("admin/js/custom.js"),
    ],

    # =========================================
    # COLOR SCHEME (Amber/Yellow Brand)
    # =========================================
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",
            "subtle-dark": "156 163 175",
            "default-light": "75 85 99",
            "default-dark": "209 213 219",
            "important-light": "17 24 39",
            "important-dark": "243 244 246",
        },
        "primary": {
            "50": "255 251 235",
            "100": "254 243 199",
            "200": "253 230 138",
            "300": "252 211 77",
            "400": "251 191 36",
            "500": "245 158 11",   # Main brand color
            "600": "217 119 6",
            "700": "180 83 9",
            "800": "146 64 14",
            "900": "120 53 15",
            "950": "69 26 3",
        },
    },

    # =========================================
    # SIDEBAR NAVIGATION
    # =========================================
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,  # Hide default app list
        "navigation": [
            # See Sidebar Navigation section below
        ],
    },
}
```

---

## Admin Class Structure

Import and extend from Unfold:

```python
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import action, display

@admin.register(MyModel)
class MyModelAdmin(ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title',)

    # Use emoji-prefixed fieldsets for visual organization
    fieldsets = (
        ('📝 Basic Info', {
            'fields': ('title', 'slug', 'description'),
            'description': 'Main content fields for this item.'
        }),
        ('🎨 Styling', {
            'fields': ('color', 'icon'),
            'classes': ('collapse',),  # Collapsible section
        }),
        ('⚙️ Settings', {
            'fields': ('is_active', 'order'),
        }),
    )
```

---

## Sidebar Navigation

Structure your sidebar by page/section for intuitive navigation:

```python
"SIDEBAR": {
    "show_search": True,
    "show_all_applications": False,
    "navigation": [
        # Dashboard
        {
            "title": "Dashboard",
            "separator": True,
            "collapsible": False,
            "items": [
                {
                    "title": "Dashboard",
                    "icon": "dashboard",
                    "link": reverse_lazy("admin:index"),
                },
            ],
        },

        # Home Page Sections
        {
            "title": "Home Page Sections",
            "separator": True,
            "collapsible": True,
            "items": [
                {
                    "title": "1. Hero Section",
                    "icon": "flag",
                    "link": reverse_lazy("admin:myapp_herosection_changelist"),
                    "badge": "myapp.utils.home_page_badge",  # Optional badge
                },
                {
                    "title": "2. Business Impact",
                    "icon": "trending_up",
                    "link": reverse_lazy("admin:myapp_businessimpact_changelist"),
                },
                {
                    "title": "3. Services",
                    "icon": "build",
                    "link": reverse_lazy("admin:myapp_service_changelist"),
                },
            ],
        },

        # SEO Management
        {
            "title": "SEO Management",
            "separator": True,
            "collapsible": True,
            "items": [
                {
                    "title": "Page SEO Tags",
                    "icon": "sell",
                    "link": reverse_lazy("admin:myapp_pageseo_changelist"),
                },
                {
                    "title": "SEO Uploads",
                    "icon": "upload_file",
                    "link": reverse_lazy("admin:myapp_seodataupload_changelist"),
                },
            ],
        },

        # Site Settings
        {
            "title": "Site Settings",
            "separator": True,
            "collapsible": True,
            "items": [
                {
                    "title": "General Settings",
                    "icon": "settings",
                    "link": reverse_lazy("admin:myapp_sitesettings_changelist"),
                },
                {
                    "title": "Footer",
                    "icon": "view_agenda",
                    "link": reverse_lazy("admin:myapp_footersection_changelist"),
                },
            ],
        },
    ],
}
```

### Common Material Icons

| Icon | Use Case |
|------|----------|
| `dashboard` | Dashboard/Home |
| `flag` | Hero sections |
| `trending_up` | Stats/Impact |
| `build` | Services |
| `smart_toy` | AI Tools |
| `calculate` | Calculator |
| `verified` | Why Choose Us |
| `contact_mail` | Contact |
| `help` | FAQ |
| `article` | Blog posts |
| `sell` | SEO/Tags |
| `upload_file` | Uploads |
| `settings` | Settings |
| `inbox` | Inquiries |
| `person_add` | Leads |
| `fact_check` | Audits |

Full list: https://fonts.google.com/icons

---

## Dashboard Customization

### Hide Default App List

In `admin.py`:

```python
# Hide the default "Site administration" app list
admin.site.get_app_list = lambda request, app_label=None: []
```

### Dashboard Callback

In `utils.py`:

```python
def dashboard_callback(request, context):
    """Custom dashboard with stats cards."""
    from django.urls import reverse
    from .models import Lead, Inquiry, Service

    # Quick stats cards
    new_leads = Lead.objects.filter(status="new").count()
    context["cards"] = [
        {
            "title": "New Leads",
            "value": new_leads,
            "icon": "person_add",
            "color": "success" if new_leads > 0 else "default",
            "url": reverse('admin:myapp_lead_changelist') + '?status=new',
        },
        {
            "title": "Inquiries",
            "value": Inquiry.objects.count(),
            "icon": "inbox",
            "color": "info",
            "url": reverse('admin:myapp_inquiry_changelist'),
        },
    ]

    # Content stats
    context["content_stats"] = {
        "services": Service.objects.count(),
    }

    # Recent activity
    context["recent_leads"] = Lead.objects.order_by("-created_at")[:5]

    return context
```

### Dashboard Template

Create `templates/admin/index.html`:

```html
{% extends "admin/base_site.html" %}
{% load i18n %}

{% block breadcrumbs %}{% endblock %}

{% block content %}
<div style="padding: 20px;">
    <!-- Welcome Section -->
    <div style="background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; border: 1px solid #e5e7eb;">
        <h1 style="font-size: 24px; font-weight: 700; margin-bottom: 8px; color: #111827;">
            Welcome to Admin
        </h1>
        <p style="color: #6b7280;">
            Manage your content from the sidebar navigation.
        </p>
    </div>

    <!-- Stats Cards -->
    {% if cards %}
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
        {% for card in cards %}
        <a href="{{ card.url }}" style="text-decoration: none;">
            <div style="background: white; border-radius: 12px; padding: 20px; border: 1px solid #e5e7eb; transition: all 0.15s;"
                 onmouseover="this.style.borderColor='#f9cb07'; this.style.boxShadow='0 4px 12px rgba(249,203,7,0.15)';"
                 onmouseout="this.style.borderColor='#e5e7eb'; this.style.boxShadow='none';">
                <p style="font-size: 14px; color: #6b7280; margin-bottom: 4px;">{{ card.title }}</p>
                <p style="font-size: 32px; font-weight: 700; color: #111827;">{{ card.value }}</p>
            </div>
        </a>
        {% endfor %}
    </div>
    {% endif %}

    <!-- Quick Actions -->
    <div style="background: white; border-radius: 12px; padding: 24px; border: 1px solid #e5e7eb;">
        <h2 style="font-size: 18px; font-weight: 600; margin-bottom: 16px;">Quick Actions</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">
            <a href="{% url 'admin:myapp_sitesettings_changelist' %}"
               style="display: flex; align-items: center; gap: 8px; padding: 12px; border-radius: 8px; background: #f9fafb; text-decoration: none; color: #374151; transition: all 0.15s;"
               onmouseover="this.style.background='#fffbeb';"
               onmouseout="this.style.background='#f9fafb';">
                ⚙️ Site Settings
            </a>
        </div>
    </div>
</div>
{% endblock %}
```

---

## Fieldsets with Emoji Icons

Use emoji prefixes for visual organization:

```python
fieldsets = (
    ('📄 Page Selection', {
        'fields': ('page', 'custom_url'),
        'description': 'Select page type or enter custom URL'
    }),
    ('🔗 Link to Content', {
        'fields': ('service', 'blog_post'),
        'classes': ('collapse',),
    }),
    ('🎯 Target Keyword', {
        'fields': ('target_keyword', 'source_recommendation'),
    }),
    ('🔍 Meta Tags', {
        'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url'),
    }),
    ('📱 Open Graph', {
        'fields': ('og_title', 'og_description', 'og_image'),
        'description': 'Controls social media sharing appearance',
    }),
)
```

### Common Emoji Prefixes

| Emoji | Use Case |
|-------|----------|
| 📄 | Page/Document selection |
| 🔗 | Links/URLs |
| 🎯 | Target/Focus items |
| 🔍 | Search/SEO |
| 📱 | Social/Mobile |
| 🎨 | Styling/Design |
| 🖼️ | Images/Media |
| ⚙️ | Settings/Config |
| 📝 | Content/Text |
| 💬 | Comments/Testimonials |
| 📊 | Stats/Analytics |
| 🤖 | AI/Automation |
| 📋 | Lists/Features |
| ✅ | Checkmarks/Features |
| 💪 | Capabilities |
| 🔄 | Process/Steps |

---

## Inline Models

### TabularInline (Compact rows)

```python
class ServiceFeatureInline(TabularInline):
    model = ServiceFeature
    extra = 1
    fields = ('text', 'order')
    verbose_name = "Feature"
    verbose_name_plural = "✅ Features (aim for 6-8 items)"
```

### StackedInline (Full forms)

```python
class ServiceCapabilityInline(StackedInline):
    model = ServiceCapability
    extra = 1
    fields = ('icon', 'title', 'description', 'order')
    verbose_name = "Capability"
    verbose_name_plural = "💪 Capabilities (cards with icon + description)"
```

---

## Custom Actions

Use the `@action` decorator from Unfold:

```python
from unfold.decorators import action

@admin.register(SEODataUpload)
class SEODataUploadAdmin(ModelAdmin):
    actions = ['process_upload', 'generate_ai_recommendations']

    @action(description="🔄 Process Upload")
    def process_upload(self, request, queryset):
        for upload in queryset:
            # Process logic
            pass
        self.message_user(request, f"Processed {queryset.count()} uploads")

    @action(description="🤖 Generate AI Recommendations")
    def generate_ai_recommendations(self, request, queryset):
        # AI logic
        pass
```

---

## Badge Callbacks

Show counts/alerts in sidebar:

```python
# utils.py
def leads_badge(request):
    """Badge showing new leads count."""
    from .models import Lead
    count = Lead.objects.filter(status="new").count()
    return count if count else None

def audit_badge(request):
    """Badge showing pending audits."""
    from .models import SiteAudit
    count = SiteAudit.objects.filter(status__in=["pending", "running"]).count()
    return count if count else None
```

Use in sidebar:

```python
{
    "title": "Leads",
    "icon": "person_add",
    "link": reverse_lazy("admin:myapp_lead_changelist"),
    "badge": "myapp.utils.leads_badge",  # Shows count
},
```

---

## Color Scheme

### Amber/Yellow (Codeteki)

```python
"primary": {
    "50": "255 251 235",
    "100": "254 243 199",
    "200": "253 230 138",
    "300": "252 211 77",
    "400": "251 191 36",
    "500": "245 158 11",
    "600": "217 119 6",
    "700": "180 83 9",
    "800": "146 64 14",
    "900": "120 53 15",
    "950": "69 26 3",
},
```

### Blue (Alternative)

```python
"primary": {
    "50": "239 246 255",
    "100": "219 234 254",
    "200": "191 219 254",
    "300": "147 197 253",
    "400": "96 165 250",
    "500": "59 130 246",
    "600": "37 99 235",
    "700": "29 78 216",
    "800": "30 64 175",
    "900": "30 58 138",
    "950": "23 37 84",
},
```

### Green (Alternative)

```python
"primary": {
    "50": "240 253 244",
    "100": "220 252 231",
    "200": "187 247 208",
    "300": "134 239 172",
    "400": "74 222 128",
    "500": "34 197 94",
    "600": "22 163 74",
    "700": "21 128 61",
    "800": "22 101 52",
    "900": "20 83 45",
    "950": "5 46 22",
},
```

---

## Loading States & Toast Notifications

For long-running admin actions (AI generation, audits, file processing), show a loading overlay and convert Django messages to toast notifications.

### Loading Overlay JavaScript

Create `static/admin/js/admin-loading.js`:

```javascript
/**
 * Admin Loading Overlay with Toast Notifications
 * Compatible with Django Unfold admin (HTMX-based)
 */
(function() {
    'use strict';

    // Actions that should show loading overlay
    const LOADING_ACTIONS = [
        'run_lighthouse_audit',
        'generate_ai_analysis',
        'generate_ai_recommendations',
        'process_uploads',
        'apply_meta_to_page',
        // Add your action names here
    ];

    // Loading messages for each action
    const LOADING_MESSAGES = {
        'run_lighthouse_audit': 'Running Lighthouse Audit... This may take 30-60 seconds.',
        'generate_ai_analysis': 'Generating AI Analysis with ChatGPT...',
        'generate_ai_recommendations': 'Generating AI Recommendations...',
        'process_uploads': 'Processing CSV Upload...',
        'apply_meta_to_page': 'Applying Meta Kit to pages...',
    };

    let isLoading = false;

    // Inject styles
    function injectStyles() {
        if (document.getElementById('admin-loading-styles')) return;

        const style = document.createElement('style');
        style.id = 'admin-loading-styles';
        style.textContent = `
            /* Loading Overlay */
            #admin-loading-overlay {
                display: none;
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(8px);
                z-index: 999999;
                justify-content: center;
                align-items: center;
            }
            #admin-loading-overlay.active {
                display: flex !important;
            }
            .loading-content {
                text-align: center;
                color: white;
                padding: 2.5rem;
                max-width: 28rem;
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.98) 0%, rgba(15, 23, 42, 0.98) 100%);
                border-radius: 1rem;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .loading-spinner {
                width: 3.5rem;
                height: 3.5rem;
                border: 3px solid rgba(255, 255, 255, 0.2);
                border-top-color: #f9cb07;  /* Brand color */
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                margin: 0 auto 1.5rem;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .loading-title {
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 0.75rem;
            }
            .loading-message {
                font-size: 0.875rem;
                color: #94a3b8;
                margin-bottom: 1rem;
            }
            .loading-warning {
                font-size: 0.75rem;
                color: #fbbf24;
                font-weight: 500;
            }
            body.loading-active {
                overflow: hidden !important;
            }
            body.loading-active * {
                pointer-events: none !important;
            }
            body.loading-active #admin-loading-overlay,
            body.loading-active #admin-loading-overlay * {
                pointer-events: auto !important;
            }

            /* Toast Container */
            #toast-container {
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 1000000;
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
                max-width: 28rem;
            }

            /* Toast Styles */
            .toast {
                display: flex;
                align-items: flex-start;
                gap: 0.75rem;
                padding: 1rem 1.25rem;
                border-radius: 0.75rem;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
                transform: translateX(120%);
                transition: transform 0.3s ease;
                border: 1px solid;
            }
            .toast.active {
                transform: translateX(0);
            }
            .toast.success {
                background: linear-gradient(135deg, #065f46 0%, #047857 100%);
                border-color: #10b981;
                color: #ecfdf5;
            }
            .toast.error {
                background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
                border-color: #ef4444;
                color: #fef2f2;
            }
            .toast.warning {
                background: linear-gradient(135deg, #78350f 0%, #92400e 100%);
                border-color: #f59e0b;
                color: #fffbeb;
            }
            .toast.info {
                background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%);
                border-color: #3b82f6;
                color: #eff6ff;
            }
        `;
        document.head.appendChild(style);
    }

    // Create loading overlay
    function createOverlay() {
        if (document.getElementById('admin-loading-overlay')) return;

        const overlay = document.createElement('div');
        overlay.id = 'admin-loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <h2 class="loading-title">Processing...</h2>
                <p class="loading-message">Please wait while we process your request.</p>
                <p class="loading-warning">Do not close or navigate away</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    // Show loading
    function showLoading(action) {
        if (isLoading) return;
        isLoading = true;

        createOverlay();
        const overlay = document.getElementById('admin-loading-overlay');
        const message = overlay.querySelector('.loading-message');

        message.textContent = LOADING_MESSAGES[action] || 'Please wait...';

        overlay.classList.add('active');
        document.body.classList.add('loading-active');
    }

    // Hide loading
    function hideLoading() {
        isLoading = false;
        const overlay = document.getElementById('admin-loading-overlay');
        if (overlay) overlay.classList.remove('active');
        document.body.classList.remove('loading-active');
    }

    // Show toast notification
    function showToast(type, title, message) {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div>
                <div style="font-weight: 600; margin-bottom: 0.25rem;">${title}</div>
                ${message ? `<div style="font-size: 0.8125rem; opacity: 0.9;">${message}</div>` : ''}
            </div>
        `;

        container.appendChild(toast);
        requestAnimationFrame(() => toast.classList.add('active'));

        setTimeout(() => {
            toast.classList.remove('active');
            setTimeout(() => toast.remove(), 300);
        }, 6000);
    }

    // Get selected action
    function getSelectedAction() {
        const actionSelect = document.querySelector('select[name="action"]');
        return actionSelect ? actionSelect.value : null;
    }

    // Check if items selected
    function hasSelectedItems() {
        return document.querySelectorAll('input[name="_selected_action"]:checked').length > 0;
    }

    // Initialize
    function init() {
        injectStyles();
        createOverlay();

        // Handle form submission
        document.addEventListener('submit', function(e) {
            const form = e.target;
            if (form.querySelector('select[name="action"]')) {
                const action = getSelectedAction();
                if (action && LOADING_ACTIONS.includes(action) && hasSelectedItems()) {
                    showLoading(action);
                }
            }
        }, true);

        // HTMX events (Unfold uses HTMX)
        document.body.addEventListener('htmx:afterSwap', function() {
            hideLoading();
            // Parse Django messages and show as toasts
            const messages = document.querySelectorAll('.messagelist li');
            messages.forEach(msg => {
                let type = 'info';
                if (msg.classList.contains('success')) type = 'success';
                if (msg.classList.contains('error')) type = 'error';
                if (msg.classList.contains('warning')) type = 'warning';

                showToast(type, type.charAt(0).toUpperCase() + type.slice(1), msg.textContent);
            });
        });

        // Hide on page load (in case of redirect after action)
        window.addEventListener('load', hideLoading);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose globally
    window.AdminLoading = { show: showLoading, hide: hideLoading, toast: showToast };
})();
```

### Include in Settings

```python
UNFOLD = {
    # ... other settings ...
    "SCRIPTS": [
        lambda request: static("admin/js/admin-loading.js"),
    ],
}
```

### Usage

The loading overlay automatically shows for actions in `LOADING_ACTIONS` array. Add your action names there.

Toast notifications automatically convert Django messages to styled popups.

---

## Deployment Loading Page

Show a branded loading page during deployments/builds.

### Create `templates/loading.html`

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Updating Site</title>
    <style>
      body {
        font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        background: radial-gradient(circle at top, rgba(249,203,7,0.25), #0f172a 65%);
        color: #fefefe;
        margin: 0;
        overflow: hidden;
      }
      .card {
        background: rgba(15, 23, 42, 0.85);
        padding: 3rem;
        border-radius: 1.75rem;
        box-shadow: 0 35px 80px rgba(15, 23, 42, 0.35);
        max-width: 32rem;
        width: 90%;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.08);
        position: relative;
        overflow: hidden;
      }
      h1 {
        font-size: 2rem;
        margin-bottom: 1.25rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }
      .pulse {
        position: absolute;
        inset: 0;
        pointer-events: none;
      }
      .pulse::before,
      .pulse::after {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 50%;
        border: 1px solid rgba(249, 203, 7, 0.3);
        animation: ripple 2.5s infinite;
      }
      .pulse::after {
        animation-delay: 1.25s;
      }
      p {
        margin: 0 auto 0.9rem;
        color: rgba(248, 250, 252, 0.8);
        line-height: 1.6;
      }
      .ticker {
        margin-top: 2rem;
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.95rem;
        color: rgba(248, 250, 252, 0.75);
      }
      .loader {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        border: 3px solid rgba(248, 250, 252, 0.15);
        border-top-color: #f9cb07;  /* Brand color */
        animation: spin 1.1s linear infinite;
        margin: 0 auto 1.5rem;
      }
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
      @keyframes ripple {
        0% { transform: scale(0.9); opacity: 1; }
        100% { transform: scale(1.5); opacity: 0; }
      }
    </style>
  </head>
  <body>
    <div class="card">
      <div class="pulse" aria-hidden="true"></div>
      <div class="loader" aria-hidden="true"></div>
      <h1>Updating Site</h1>
      <p>We're rolling out the latest experience. Hang tight while we refresh the UI.</p>
      <p>Your page will update automatically once ready.</p>
      <div class="ticker">
        <span aria-hidden="true">⚡</span>
        <span>Deploying... almost there</span>
      </div>
    </div>
  </body>
</html>
```

### Usage with Nginx

During deployments, configure nginx to serve this page:

```nginx
# In your deployment script, before stopping the app:
cp /path/to/loading.html /var/www/maintenance.html

# In nginx config:
location / {
    if (-f /var/www/maintenance.html) {
        return 503;
    }
    # ... normal proxy config
}

error_page 503 @maintenance;
location @maintenance {
    root /var/www;
    rewrite ^(.*)$ /maintenance.html break;
}
```

---

## Static Files

### Custom CSS (`static/css/admin-custom.css`)

```css
/* Hide default app list on dashboard */
body.dashboard #content-main > .module {
    display: none !important;
}

body.dashboard #content-related {
    display: none !important;
}

body.dashboard #content {
    margin-right: 0 !important;
}

/* Custom card styles */
.dashboard-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.dashboard-card {
    background: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

---

## Complete Example

### File Structure

```
backend/
├── myapp/
│   ├── admin.py          # Admin classes
│   ├── models.py         # Models
│   └── utils.py          # Dashboard callbacks, badges
├── static/
│   ├── css/
│   │   └── admin-custom.css
│   └── images/
│       ├── logo.png
│       └── login-bg.jpg
├── templates/
│   └── admin/
│       └── index.html    # Custom dashboard
└── settings.py           # UNFOLD config
```

### Minimal admin.py

```python
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action
from .models import Service, ServiceFeature, PageSEO

# Hide default app list
admin.site.get_app_list = lambda request, app_label=None: []


class ServiceFeatureInline(TabularInline):
    model = ServiceFeature
    extra = 1
    fields = ('text', 'order')
    verbose_name_plural = "✅ Features"


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ServiceFeatureInline]

    fieldsets = (
        ('📝 Basic Info', {
            'fields': ('title', 'slug', 'description', 'icon'),
        }),
        ('🎨 Styling', {
            'fields': ('gradient_from', 'gradient_to'),
            'classes': ('collapse',),
        }),
        ('⚙️ Settings', {
            'fields': ('is_active', 'order'),
        }),
    )


@admin.register(PageSEO)
class PageSEOAdmin(ModelAdmin):
    list_display = ('page', 'meta_title', 'updated_at')
    search_fields = ('page', 'meta_title')

    fieldsets = (
        ('📄 Page Selection', {
            'fields': ('page', 'custom_url'),
        }),
        ('🔍 Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url'),
        }),
        ('📱 Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'classes': ('collapse',),
        }),
    )
```

---

## Requirements

```
django-unfold>=0.40.0
```

---

## Tips

1. **Use emojis in fieldset titles** - Makes forms scannable
2. **Group by page/section** - Organize sidebar logically
3. **Hide default app list** - Cleaner dashboard
4. **Add help_text to fields** - Guides content editors
5. **Use collapsible sections** - Keep forms clean
6. **Add badges for alerts** - Show pending items
7. **Custom dashboard** - Show relevant stats
8. **Consistent icons** - Use Material icons throughout

---

## Adapting for Client Projects

1. **Copy this structure** to new project
2. **Change `SITE_TITLE`** and branding
3. **Adjust color scheme** to client brand
4. **Customize sidebar** for their content types
5. **Update dashboard** with their metrics

The admin will look professional and consistent across all projects.
