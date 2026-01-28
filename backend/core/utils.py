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
    from django.utils import timezone
    from datetime import timedelta
    import pytz

    from .models import (
        ChatLead, ContactInquiry, SiteAudit, BlogPost,
        Service, HeroSection, Testimonial
    )

    # Import CRM models
    try:
        from crm.models import Deal, Contact, EmailDraft, EmailLog, Pipeline
        crm_available = True
    except ImportError:
        crm_available = False

    # Server time in Melbourne timezone
    melbourne = pytz.timezone('Australia/Melbourne')
    server_time = timezone.now().astimezone(melbourne)
    context["server_time"] = server_time.strftime('%I:%M %p')
    context["server_date"] = server_time.strftime('%a, %d %b %Y')

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

    # CRM Stats
    if crm_available:
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        active_deals = Deal.objects.filter(status='active').count()
        total_contacts = Contact.objects.count()
        scheduled_emails = EmailDraft.objects.filter(schedule_status='scheduled').count()
        emails_sent_today = EmailLog.objects.filter(sent_at__date=today).count()
        emails_sent_week = EmailLog.objects.filter(sent_at__date__gte=week_ago).count()

        context["crm_cards"] = [
            {
                "title": "Active Deals",
                "value": active_deals,
                "icon": "handshake",
                "color": "success" if active_deals > 0 else "default",
                "url": reverse('admin:crm_deal_changelist') + '?status=active',
            },
            {
                "title": "Total Contacts",
                "value": total_contacts,
                "icon": "contacts",
                "color": "info",
                "url": reverse('admin:crm_contact_changelist'),
            },
            {
                "title": "Scheduled Emails",
                "value": scheduled_emails,
                "icon": "schedule_send",
                "color": "warning" if scheduled_emails > 0 else "default",
                "url": reverse('admin:crm_emaildraft_changelist') + '?schedule_status=scheduled',
            },
            {
                "title": "Emails This Week",
                "value": emails_sent_week,
                "icon": "mark_email_read",
                "color": "success" if emails_sent_week > 0 else "default",
                "url": reverse('admin:crm_emaillog_changelist'),
            },
        ]

        # Recent deals activity
        recent_deals = []
        for deal in Deal.objects.select_related('contact', 'current_stage').order_by("-updated_at")[:5]:
            recent_deals.append({
                'id': deal.pk,
                'contact_name': deal.contact.name if deal.contact else 'Unknown',
                'contact_email': deal.contact.email if deal.contact else '',
                'stage': deal.current_stage.name if deal.current_stage else 'No Stage',
                'status': deal.status,
                'updated_at': deal.updated_at,
            })
        context["recent_deals"] = recent_deals

        # Pipeline stats
        pipeline_stats = []
        for pipeline in Pipeline.objects.filter(is_active=True)[:4]:
            pipeline_stats.append({
                'name': pipeline.name,
                'active_deals': Deal.objects.filter(pipeline=pipeline, status='active').count(),
                'url': f"/admin/crm/board/{pipeline.id}/",
            })
        context["pipeline_stats"] = pipeline_stats

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
