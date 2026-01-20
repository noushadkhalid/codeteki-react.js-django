"""
URL configuration for codeteki_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap as django_sitemap
from django.urls import include, path, re_path
from django.views.static import serve

from core.views import ReactAppView
from core.sitemaps import sitemaps


def sitemap_view(request, sitemaps, **kwargs):
    """Custom sitemap view that removes the X-Robots-Tag header.

    Django adds 'X-Robots-Tag: noindex' by default which can cause
    Google Search Console to fail fetching the sitemap.
    """
    response = django_sitemap(request, sitemaps=sitemaps, **kwargs)
    # Remove the noindex header so Google can properly index our sitemap
    if 'X-Robots-Tag' in response.headers:
        del response.headers['X-Robots-Tag']
    return response

from crm.views import pipeline_dashboard, pipeline_board, move_deal_stage, UnsubscribeView
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect

urlpatterns = [
    # CRM Dashboard (before admin to avoid catch-all)
    path('admin/crm/dashboard/', staff_member_required(pipeline_dashboard), name='crm_dashboard'),
    path('admin/crm/board/<int:pipeline_id>/', staff_member_required(pipeline_board), name='crm_board'),
    path('admin/crm/board/move-deal/', staff_member_required(move_deal_stage), name='crm_move_deal'),
    # Redirect /admin/crm/ to dashboard (fixes 404 on nav clicks)
    path('admin/crm/', lambda r: redirect('/admin/crm/dashboard/')),

    # Public CRM pages (no /api/ prefix for user-facing URLs)
    path('crm/unsubscribe/', UnsubscribeView.as_view(), name='public_unsubscribe'),

    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/crm/', include('crm.urls')),  # CRM API endpoints

    # Sitemap for SEO - dynamically updates with new content (custom view removes X-Robots-Tag)
    path('sitemap.xml', sitemap_view, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Serve static files from build root (images, manifest, etc.)
    re_path(
        r'^(?P<path>(?:navbar-logo|footer-logo|favicon|manifest|robots|logo192|logo512|hero-desktop|hero-mobile)\.(?:png|jpg|svg|ico|json|txt|webp))$',
        serve,
        {'document_root': settings.FRONTEND_BUILD}
    ),
]

# Media files MUST come before the catch-all React route
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Catch-all for React SPA routing (must be LAST after all other routes)
urlpatterns += [
    re_path(r'^.*$', ReactAppView.as_view(), name='react-app'),
]
