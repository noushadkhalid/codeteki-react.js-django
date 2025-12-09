"""
Utility functions for Codeteki CMS.
Used by Django Unfold for badges, environment indicators, etc.
"""

from django.conf import settings


def environment_callback(request):
    """
    Return environment name and color for Unfold header.
    """
    if settings.DEBUG:
        return ["Development", "warning"]
    return ["Production", "success"]


def home_page_badge(request):
    """Badge showing home page sections count."""
    from .models import HeroSection
    count = HeroSection.objects.filter(is_active=True).count()
    return count if count else None


def audit_badge(request):
    """Badge showing pending/running audits."""
    from .models import SiteAudit
    count = SiteAudit.objects.filter(status__in=["pending", "running"]).count()
    return count if count else None


def leads_badge(request):
    """Badge showing new leads count."""
    from .models import ChatLead
    count = ChatLead.objects.filter(status="new").count()
    return count if count else None


def issues_badge(request):
    """Badge showing open audit issues."""
    from .models import AuditIssue
    count = AuditIssue.objects.filter(status="open", severity="error").count()
    return count if count else None


def dashboard_callback(request, context):
    """
    Custom dashboard callback for Unfold.
    Returns stats cards instead of the default model list.
    """
    from django.urls import reverse
    from .models import (
        ChatLead, ContactInquiry, SiteAudit, BlogPost,
        Service, HeroSection, Testimonial
    )

    # Quick stats for dashboard - now with clickable URLs
    new_leads_count = ChatLead.objects.filter(status="new").count()
    context["cards"] = [
        {
            "title": "New Leads",
            "value": new_leads_count,
            "icon": "person_add",
            "color": "success" if new_leads_count > 0 else "default",
            "url": reverse('admin:core_chatlead_changelist') + '?status=new',
        },
        {
            "title": "Contact Inquiries",
            "value": ContactInquiry.objects.count(),
            "icon": "inbox",
            "color": "info",
            "url": reverse('admin:core_contactinquiry_changelist'),
        },
        {
            "title": "Site Audits",
            "value": SiteAudit.objects.count(),
            "icon": "fact_check",
            "color": "primary",
            "url": reverse('admin:core_siteaudit_changelist'),
        },
        {
            "title": "Blog Posts",
            "value": BlogPost.objects.filter(is_published=True).count(),
            "icon": "article",
            "color": "default",
            "url": reverse('admin:core_blogpost_changelist'),
        },
    ]

    # Recent activity - get conversation visitor name for leads with IDs for linking
    recent_leads = []
    for lead in ChatLead.objects.select_related('conversation').order_by("-created_at")[:5]:
        recent_leads.append({
            'id': lead.pk,
            'name': getattr(lead.conversation, 'visitor_name', None) or lead.conversation.visitor_email or 'Anonymous',
            'status': lead.status,
            'created_at': lead.created_at,
        })
    context["recent_leads"] = recent_leads
    context["recent_audits"] = SiteAudit.objects.order_by("-created_at")[:5]

    # Content counts for overview
    context["content_stats"] = {
        "services": Service.objects.count(),
        "hero_sections": HeroSection.objects.filter(is_active=True).count(),
        "testimonials": Testimonial.objects.filter(is_active=True).count(),
    }

    return context
