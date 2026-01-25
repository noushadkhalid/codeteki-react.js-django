from __future__ import annotations

import json

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.http import JsonResponse
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from .models import (
    AIToolsSection,
    BlogPost,
    BusinessImpactSection,
    ChatConversation,
    ContactMethod,
    ContactInquiry,
    CTASection,
    DemoShowcase,
    FAQCategory,
    FooterSection,
    HeroSection,
    KnowledgeArticle,
    NavigationMenu,
    PageSEO,
    PricingPlan,
    ROICalculatorSection,
    SEODataUpload,
    Service,
    ServiceFeature,
    ServiceCapability,
    ServiceBenefit,
    ServiceProcess,
    ServiceProcessStep,
    SiteSettings,
    StatMetric,
    Testimonial,
    WhyChooseSection,
)
from .services.chatbot import ChatbotService
from .services.chat_knowledge import ChatKnowledgeBuilder

BRAND_TOKENS = {
    "name": "Codeteki Digital Services",
    "tagline": "AI-Powered Business Solutions",
    "colors": {
        "yellow": "#f9cb07",
        "yellowHover": "#e6b800",
        "yellowLight": "#ffcd3c",
        "black": "#000000",
        "gray": "#666666",
        "white": "#ffffff",
        "lightGray": "#fdfdfd",
    },
    "fonts": {"primary": "Inter"},
}


def _serialize_page_seo(page: str) -> dict:
    seo = PageSEO.objects.filter(page=page).first()
    if not seo:
        return {}

    # Use effective properties that fall back to defaults
    og_image = seo.effective_og_image
    return {
        "metaTitle": seo.meta_title,
        "metaDescription": seo.meta_description,
        "metaKeywords": seo.meta_keywords,
        "ogTitle": seo.effective_og_title,
        "ogDescription": seo.effective_og_description,
        "ogImage": og_image.url if og_image else None,
        "canonicalUrl": seo.canonical_url,
        "targetKeyword": seo.target_keyword,
    }


def _serialize_hero_section(page: str = "home") -> dict | None:
    normalized_page = (page or "home").strip().lower()
    hero = (
        HeroSection.objects.filter(page=normalized_page, is_active=True)
        .prefetch_related("metrics", "partner_logos")
        .order_by("-updated_at")
        .first()
    )
    if not hero and normalized_page != "home":
        hero = (
            HeroSection.objects.filter(page="home", is_active=True)
            .prefetch_related("metrics", "partner_logos")
            .order_by("-updated_at")
            .first()
        )
    if not hero:
        return None
    return {
        "badge": hero.badge,
        "badgeEmoji": hero.badge_emoji,
        "title": hero.title,
        "highlighted": hero.highlighted_text,
        "highlightGradientFrom": hero.highlight_gradient_from,
        "highlightGradientTo": hero.highlight_gradient_to,
        "subheading": getattr(hero, "subheading", ""),
        "description": hero.description,
        "primaryCta": {
            "label": hero.primary_cta_label,
            "href": hero.primary_cta_href,
        },
        "secondaryCta": {
            "label": hero.secondary_cta_label,
            "href": hero.secondary_cta_href,
        },
        "image": getattr(hero, "image_url", None),
        "media": hero.media_url,
        "metrics": [
            {"label": metric.label, "value": metric.value}
            for metric in hero.metrics.all()
        ],
        "logos": [
            {"name": logo.name, "logo": logo.logo_url}
            for logo in hero.partner_logos.all()
        ],
    }


def _serialize_business_impact_section() -> dict:
    section = (
        BusinessImpactSection.objects.prefetch_related("metrics", "logos")
        .order_by("-updated_at")
        .first()
    )
    if not section:
        return {}
    return {
        "title": section.title,
        "description": section.description,
        "cta": {
            "label": section.cta_label,
            "href": section.cta_href,
        },
        "metrics": [
            {
                "value": metric.value,
                "label": metric.label,
                "caption": metric.caption,
                "icon": metric.icon,
                "theme": {
                    "bg": metric.theme_bg_class,
                    "text": metric.theme_text_class,
                },
            }
            for metric in section.metrics.all()
        ],
        "logos": [
            {"name": logo.name, "logo": logo.logo_url}
            for logo in section.logos.all()
        ],
    }


def _serialize_services_section(featured_only: bool = False, include_details: bool = False) -> dict:
    """
    Serialize services for API response.

    Args:
        featured_only: If True, only return featured services
        include_details: If True, include full detail page content (features, capabilities, etc.)
    """
    services_qs = (
        Service.objects.prefetch_related(
            "outcomes", "features", "capabilities", "benefits", "process_steps"
        )
        .order_by("order")
    )
    if featured_only:
        services_qs = services_qs.filter(is_featured=True)
    services = services_qs.all()

    service_payload = []
    for service in services:
        service_data = {
            "id": service.slug,
            "title": service.title,
            "description": service.description,
            "badge": service.badge,
            "icon": service.icon,
            "outcomes": [item.text for item in service.outcomes.all()],
        }

        # Include detail page content if requested
        if include_details:
            service_data.update({
                # Detail page fields
                "tagline": service.tagline or service.badge,
                "subtitle": service.subtitle or service.description[:150],
                "fullDescription": service.full_description or service.description,
                "heroImage": service.hero_image_src,
                "gradient": f"from-{service.gradient_from} to-{service.gradient_to}",
                "gradientFrom": service.gradient_from,
                "gradientTo": service.gradient_to,
                # Related content
                "features": [item.text for item in service.features.all()],
                "capabilities": [
                    {
                        "icon": cap.icon,
                        "title": cap.title,
                        "description": cap.description,
                    }
                    for cap in service.capabilities.all()
                ],
                "benefits": [item.text for item in service.benefits.all()],
                "process": [
                    {
                        "step": step.step_number,
                        "title": step.title,
                        "description": step.description,
                    }
                    for step in service.process_steps.all()
                ],
            })

        service_payload.append(service_data)

    stats_payload = [
        {
            "value": stat.value,
            "label": stat.label,
            "icon": stat.icon,
            "color": stat.color,
        }
        for stat in StatMetric.objects.filter(section="services", is_active=True).order_by("order")
    ]
    process_steps = [
        {
            "title": step.title,
            "description": step.description,
            "icon": step.icon,
            "accent": step.accent,
        }
        for step in ServiceProcessStep.objects.order_by("order")
    ]
    return {
        "services": service_payload,
        "stats": stats_payload,
        "process": process_steps,
    }


def _serialize_single_service(slug: str) -> dict | None:
    """Serialize a single service with full detail page content."""
    try:
        service = Service.objects.prefetch_related(
            "outcomes", "features", "capabilities", "benefits", "process_steps"
        ).get(slug=slug)
    except Service.DoesNotExist:
        return None

    return {
        "id": service.slug,
        "title": service.title,
        "description": service.description,
        "badge": service.badge,
        "icon": service.icon,
        "outcomes": [item.text for item in service.outcomes.all()],
        # Detail page fields
        "tagline": service.tagline or service.badge,
        "subtitle": service.subtitle or service.description[:150],
        "fullDescription": service.full_description or service.description,
        "heroImage": service.hero_image_src,
        "gradient": f"from-{service.gradient_from} to-{service.gradient_to}",
        "gradientFrom": service.gradient_from,
        "gradientTo": service.gradient_to,
        # Related content
        "features": [item.text for item in service.features.all()],
        "capabilities": [
            {
                "icon": cap.icon,
                "title": cap.title,
                "description": cap.description,
            }
            for cap in service.capabilities.all()
        ],
        "benefits": [item.text for item in service.benefits.all()],
        "process": [
            {
                "step": step.step_number,
                "title": step.title,
                "description": step.description,
            }
            for step in service.process_steps.all()
        ],
    }


def _serialize_roi_calculator_content() -> dict:
    section = (
        ROICalculatorSection.objects.prefetch_related("stats")
        .order_by("-updated_at")
        .first()
    )
    if not section:
        return {}
    return {
        "badge": section.badge,
        "title": section.title,
        "highlighted": section.highlighted_text,
        "description": section.description,
        "subtitle": section.subtitle,
        "stats": [
            {
                "label": stat.label,
                "value": stat.value,
                "detail": stat.detail,
            }
            for stat in section.stats.all()
        ],
        "tools": [
            {
                "id": tool.tool_id,
                "label": tool.label,
                "description": tool.description,
            }
            for tool in section.tools.all()
        ],
    }


def _serialize_ai_tools_section() -> dict:
    section = (
        AIToolsSection.objects.filter(is_active=True)
        .prefetch_related("tools")
        .order_by("-updated_at")
        .first()
    )
    if not section:
        return {}
    return {
        "badge": section.badge,
        "title": section.title,
        "description": section.description,
        "tools": [
            {
                "title": tool.title,
                "slug": tool.slug,
                "description": tool.description,
                "icon": tool.icon,
                "color": tool.color,
                "emoji": tool.emoji,
                "category": tool.category,
                "status": tool.status,
                "badge": tool.badge,
                "externalUrl": tool.external_url,
                "previewUrl": tool.preview_url,
                "cta": {
                    "label": tool.cta_label,
                    "url": tool.cta_url,
                },
                "secondaryCta": {
                    "label": tool.secondary_cta_label,
                    "url": tool.secondary_cta_url,
                },
                "minCredits": tool.min_credits,
                "creditCost": tool.credit_cost,
                "comingSoon": tool.is_coming_soon,
            }
            for tool in section.tools.filter(is_active=True).order_by("order")
        ],
    }


def _serialize_why_choose_section() -> dict:
    section = (
        WhyChooseSection.objects.filter(is_active=True)
        .prefetch_related("reasons")
        .order_by("-updated_at")
        .first()
    )
    if not section:
        return {}
    return {
        "badge": section.badge,
        "title": section.title,
        "description": section.description,
        "reasons": [
            {
                "title": reason.title,
                "description": reason.description,
                "icon": reason.icon,
            }
            for reason in section.reasons.all()
        ],
    }


def _serialize_testimonials() -> list:
    testimonials = Testimonial.objects.filter(is_active=True).order_by("-is_featured", "order")
    return [
        {
            "name": t.name,
            "position": t.position,
            "company": t.company,
            "image": t.image.url if t.image else None,
            "rating": t.rating,
            "content": t.content,
            "isFeatured": t.is_featured,
        }
        for t in testimonials
    ]


def _serialize_cta_sections(placement: str = "global") -> list:
    sections = CTASection.objects.filter(
        is_active=True,
        placement__in=[placement, "global"],
    ).order_by("order")
    return [
        {
            "title": cta.title,
            "subtitle": cta.subtitle,
            "description": cta.description,
            "primaryButton": {
                "text": cta.primary_button_text,
                "url": cta.primary_button_url,
            },
            "secondaryButton": {
                "text": cta.secondary_button_text,
                "url": cta.secondary_button_url,
            }
            if cta.secondary_button_text
            else None,
            "backgroundColor": cta.background_color,
            "textColor": cta.text_color,
        }
        for cta in sections
    ]


def _serialize_demos() -> list:
    demos = (
        DemoShowcase.objects.filter(is_active=True)
        .prefetch_related("images")
        .order_by("-is_featured", "order")
    )
    return [
        {
            "title": demo.title,
            "slug": demo.slug,
            "shortDescription": demo.short_description,
            "fullDescription": demo.full_description,
            "thumbnail": demo.thumbnail.url if demo.thumbnail else None,
            "demoUrl": demo.demo_url,
            "videoUrl": demo.video_url,
            "clientName": demo.client_name,
            "clientLogo": demo.client_logo.url if demo.client_logo else None,
            "technologies": demo.technologies_used.split(",") if demo.technologies_used else [],
            "completionDate": demo.completion_date.isoformat() if demo.completion_date else None,
            "isFeatured": demo.is_featured,
            "industry": demo.industry,
            "icon": demo.icon,
            "colorClass": demo.color_class,
            "status": demo.get_status_display(),
            "statusValue": demo.status,
            "features": demo.feature_list(),
            "featureCount": demo.feature_count,
            "badge": demo.highlight_badge,
            "screenshot": demo.screenshot.url if demo.screenshot else None,
            "gallery": [
                {"image": img.image.url, "caption": img.caption}
                for img in demo.images.all()
            ],
        }
        for demo in demos
    ]


def _serialize_stats(section: str = "home") -> list:
    stats = StatMetric.objects.filter(section=section, is_active=True).order_by("order")
    return [
        {
            "value": stat.value,
            "label": stat.label,
            "icon": stat.icon,
            "color": stat.color,
        }
        for stat in stats
    ]


def _serialize_faq_page_section() -> dict:
    """Serialize FAQ page hero/header section"""
    from .models import FAQPageSection

    section = FAQPageSection.objects.filter(is_active=True).first()
    if not section:
        return {
            "title": "FAQ Hub",
            "description": "Answers for every stage of your AI journey",
            "badge": "",
            "searchPlaceholder": "Search FAQs...",
            "ctaText": "Book strategy call",
            "ctaUrl": "/contact",
            "secondaryCtaText": "Still stuck? Message the team",
            "stats": [
                {"value": "< 24 hrs", "label": "Average response time", "detail": "Based on care plan"},
                {"value": "80+", "label": "Documented answers", "detail": ""},
                {"value": "14", "label": "Industries supported", "detail": ""},
            ]
        }

    return {
        "title": section.title,
        "description": section.description,
        "badge": section.badge,
        "searchPlaceholder": section.search_placeholder,
        "ctaText": section.cta_text,
        "ctaUrl": section.cta_url,
        "secondaryCtaText": section.secondary_cta_text,
        "stats": [
            {
                "value": stat.value,
                "label": stat.label,
                "detail": stat.detail
            }
            for stat in section.stats.all().order_by('order')
        ]
    }


def _serialize_faq_categories() -> list:
    from .models import FAQCategory

    categories = FAQCategory.objects.prefetch_related("items").order_by("order")
    return [
        {
            "title": category.title,
            "description": category.description,
            "icon": category.icon,
            "items": [
                {"question": item.question, "answer": item.answer}
                for item in category.items.all()
            ],
        }
        for category in categories
    ]


def _parse_business_hours(settings_obj) -> list:
    """
    Get business hours from the new BusinessHours model,
    falling back to old JSON field and then defaults.
    """
    default_hours = [
        {"day": "Monday - Friday", "hours": "9:00 AM - 6:00 PM AEDT"},
        {"day": "Saturday", "hours": "10:00 AM - 4:00 PM AEDT"},
        {"day": "Sunday", "hours": "By appointment"},
    ]

    if not settings_obj:
        return default_hours

    # First, try the new BusinessHours model
    hours_from_model = settings_obj.hours.all().order_by('order')
    if hours_from_model.exists():
        return [
            {
                "day": hour.get_day_display(),
                "hours": "Closed" if hour.is_closed else hour.hours
            }
            for hour in hours_from_model
        ]

    # Fall back to old JSON field
    raw = settings_obj.business_hours
    if not raw:
        return default_hours
    try:
        parsed = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        parsed = None
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        return [
            {"day": key.replace("_", " ").title(), "hours": value}
            for key, value in parsed.items()
        ]
    hours = []
    for line in raw.splitlines():
        if ":" in line:
            day, value = line.split(":", 1)
            hours.append({"day": day.strip(), "hours": value.strip()})
    return hours or default_hours


def _serialize_contact_details(include_inquiries: bool = False) -> dict:
    methods = [
        {
            "title": method.title,
            "description": method.description,
            "value": method.value,
            "cta": method.cta_label,
            "icon": method.icon,
        }
        for method in ContactMethod.objects.order_by("order")
    ]
    settings_obj = SiteSettings.objects.prefetch_related('hours').order_by("-updated_at").first()
    info = {
        "primaryEmail": settings_obj.primary_email if settings_obj else "",
        "secondaryEmail": settings_obj.secondary_email if settings_obj else "",
        "primaryPhone": settings_obj.primary_phone if settings_obj else "",
        "secondaryPhone": settings_obj.secondary_phone if settings_obj else "",
        "address": settings_obj.address if settings_obj else "",
    }
    business_hours = _parse_business_hours(settings_obj)
    payload = {
        "methods": methods,
        "info": info,
        "businessHours": business_hours,
        "stats": {
            "totalInquiries": ContactInquiry.objects.count(),
        },
    }
    if include_inquiries:
        inquiries = ContactInquiry.objects.order_by("-created_at")[:5]
        payload["recentInquiries"] = [
            {
                "name": inquiry.name,
                "service": inquiry.service,
                "createdAt": inquiry.created_at.isoformat(),
                "status": inquiry.status,
            }
            for inquiry in inquiries
        ]
    return payload


class JSONAPIView(View):
    """Tiny helper for consistent JSON payloads."""

    payload_key = "data"

    def render(self, payload, status=200):
        return JsonResponse({self.payload_key: payload}, status=status, safe=False)


@method_decorator(cache_page(getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)), name='dispatch')
class ServicesAPIView(JSONAPIView):
    def get(self, request):
        featured_flag = (request.GET.get("featured") or "").strip().lower()
        featured_only = featured_flag in {"1", "true", "yes", "on"}
        details_flag = (request.GET.get("details") or "").strip().lower()
        include_details = details_flag in {"1", "true", "yes", "on"}
        return self.render(_serialize_services_section(
            featured_only=featured_only,
            include_details=include_details
        ))


@method_decorator(cache_page(getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)), name='dispatch')
class ServiceDetailAPIView(JSONAPIView):
    """Get a single service with full detail page content."""
    def get(self, request, slug):
        service_data = _serialize_single_service(slug)
        if not service_data:
            return self.render({"error": "Service not found"}, status=404)
        return self.render({"service": service_data})


@method_decorator(cache_page(getattr(settings, 'CACHE_TIMEOUT_LONG', 900)), name='dispatch')
class FAQAPIView(JSONAPIView):
    def get(self, request):
        return self.render({
            "pageSection": _serialize_faq_page_section(),
            "categories": _serialize_faq_categories()
        })


@method_decorator(csrf_exempt, name='dispatch')
class ContactAPIView(JSONAPIView):
    def get(self, request):
        return self.render(_serialize_contact_details(include_inquiries=False))

    def post(self, request):
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return self.render({"error": "Invalid JSON payload"}, status=400)

        name = data.get("name") or data.get("fullName")
        email = data.get("email")
        if not name or not email:
            return self.render({"error": "Name and email are required"}, status=400)

        inquiry = ContactInquiry.objects.create(
            name=name.strip(),
            email=email.strip(),
            phone=(data.get("phone") or "").strip(),
            service=(data.get("service") or data.get("topic") or "").strip(),
            message=(data.get("message") or "").strip(),
            source=data.get("source", "website"),
            metadata={k: v for k, v in data.items() if k not in {"name", "fullName", "email", "phone", "service", "topic", "message", "source"}},
        )

        # Auto-add to CRM pipeline for follow-up
        try:
            from crm.services.lead_integration import LeadIntegrationService
            LeadIntegrationService.create_lead_from_inquiry(inquiry, auto_create_deal=True)
        except Exception:
            pass  # Don't fail the form submission if CRM integration fails

        return self.render({"message": "Thanks! We'll be in touch shortly.", "id": inquiry.id}, status=201)


@method_decorator(cache_page(getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)), name='dispatch')
class HeroContentAPIView(JSONAPIView):
    def get(self, request):
        page = request.GET.get("page", "home")
        hero_payload = _serialize_hero_section(page) or {}
        return self.render({"hero": hero_payload, "brand": BRAND_TOKENS})


class BusinessImpactAPIView(JSONAPIView):
    def get(self, request):
        payload = _serialize_business_impact_section()
        return self.render({"impact": payload})


@method_decorator(csrf_exempt, name='dispatch')
class ROICalculateAPIView(View):
    """Calculate ROI based on business metrics."""

    def post(self, request):
        try:
            data = json.loads(request.body)

            # Extract form data
            monthly_calls = float(data.get('monthlyCalls', 0))
            missed_calls = float(data.get('missedCalls', 0))
            call_duration = float(data.get('callDuration', 0))
            hourly_rate = float(data.get('hourlyRate', 0))
            conversion_rate = float(data.get('conversionRate', 0)) / 100
            order_value = float(data.get('orderValue', 0))

            monthly_tickets = float(data.get('monthlyTickets', 0))
            ticket_handle_time = float(data.get('ticketHandleTime', 0))
            ticket_resolution_cost = float(data.get('ticketResolutionCost', 0))

            manual_tasks_per_day = float(data.get('manualTasksPerDay', 0))
            minutes_per_task = float(data.get('minutesPerTask', 0))
            systems_used = float(data.get('systemsUsed', 1))

            # Calculate savings based on different scenarios

            # Voice & Chat AI savings
            call_handling_cost = (monthly_calls * call_duration / 60) * hourly_rate
            missed_revenue = missed_calls * conversion_rate * order_value
            voice_savings = call_handling_cost * 0.6 + missed_revenue * 0.8

            # Support Desk savings
            support_cost = monthly_tickets * ticket_resolution_cost
            support_time_cost = (monthly_tickets * ticket_handle_time / 60) * hourly_rate
            support_savings = (support_cost + support_time_cost) * 0.5

            # Back-office Automation savings
            automation_time_monthly = manual_tasks_per_day * minutes_per_task * 22  # 22 working days
            automation_cost = (automation_time_monthly / 60) * hourly_rate
            efficiency_multiplier = min(1 + (systems_used * 0.1), 2)  # Cap at 2x
            automation_savings = automation_cost * 0.7 * efficiency_multiplier

            # Combine all savings
            monthly_savings = voice_savings + support_savings + automation_savings
            annual_savings = monthly_savings * 12

            # Estimated implementation cost (conservative estimate)
            estimated_cost = 15000  # Base implementation cost

            # Calculate ROI
            annual_roi = ((annual_savings - estimated_cost) / estimated_cost * 100) if estimated_cost > 0 else 0
            payback_period = round(estimated_cost / monthly_savings) if monthly_savings > 0 else 0

            return JsonResponse({
                'monthlySavings': round(monthly_savings, 2),
                'annualSavings': round(annual_savings, 2),
                'annualROI': round(annual_roi, 0),
                'paybackPeriod': payback_period,
                'breakdown': {
                    'voiceSavings': round(voice_savings, 2),
                    'supportSavings': round(support_savings, 2),
                    'automationSavings': round(automation_savings, 2),
                }
            })

        except (ValueError, json.JSONDecodeError) as e:
            return JsonResponse(
                {'error': 'Invalid input data', 'detail': str(e)},
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {'error': 'Calculation error', 'detail': str(e)},
                status=500
            )


class ROICalculatorContentAPIView(JSONAPIView):
    """ROI Calculator section content."""
    def get(self, request):
        return self.render({"calculator": _serialize_roi_calculator_content()})


class AIToolsContentAPIView(JSONAPIView):
    """AI Tools section content."""
    def get(self, request):
        return self.render({"aiTools": _serialize_ai_tools_section()})


class WhyChooseContentAPIView(JSONAPIView):
    """Why Choose Us section content."""
    def get(self, request):
        return self.render({"whyChoose": _serialize_why_choose_section()})


@method_decorator(cache_page(getattr(settings, 'CACHE_TIMEOUT_LONG', 900)), name='dispatch')
class FooterContentAPIView(JSONAPIView):
    """Footer section content."""
    def get(self, request):
        section = FooterSection.objects.prefetch_related("links", "social_links").order_by("-updated_at").first()
        if not section:
            return self.render({"footer": {}})

        # Group links by column
        links_by_column = {}
        for link in section.links.all():
            if link.column not in links_by_column:
                links_by_column[link.column] = []
            links_by_column[link.column].append({
                "title": link.title,
                "url": link.url,
            })

        # Get dynamic social links
        social_links = [
            {
                "platform": social.platform,
                "url": social.url,
                "label": social.custom_label or social.get_platform_display(),
            }
            for social in section.social_links.filter(is_active=True).order_by('order')
        ]

        payload = {
            "company": section.company_name,
            "description": section.company_description,
            "logo": section.logo.url if section.logo else None,
            "abn": section.abn,
            "socialLinks": social_links,
            "copyright": section.copyright_text,
            "links": links_by_column,
        }
        return self.render({"footer": payload})


@method_decorator(cache_page(getattr(settings, 'CACHE_TIMEOUT_LONG', 900)), name='dispatch')
class SiteSettingsAPIView(JSONAPIView):
    """Site-wide settings."""
    def get(self, request):
        settings_obj = SiteSettings.objects.prefetch_related('hours').order_by("-updated_at").first()
        if not settings_obj:
            return self.render({"settings": {}})

        payload = {
            "siteName": settings_obj.site_name,
            "siteTagline": settings_obj.site_tagline,
            "siteDescription": settings_obj.site_description,
            "logos": {
                "main": settings_obj.logo.url if settings_obj.logo else None,
                "dark": settings_obj.logo_dark.url if settings_obj.logo_dark else None,
                "favicon": settings_obj.favicon.url if settings_obj.favicon else None,
            },
            "contact": {
                "primaryEmail": settings_obj.primary_email,
                "secondaryEmail": settings_obj.secondary_email,
                "primaryPhone": settings_obj.primary_phone,
                "secondaryPhone": settings_obj.secondary_phone,
                "address": settings_obj.address,
            },
            "support": {
                "badge": settings_obj.support_badge,
                "responseValue": settings_obj.support_response_value,
                "responseLabel": settings_obj.support_response_label,
                "responseHelper": settings_obj.support_response_helper,
                "responseMessage": settings_obj.support_response_message,
                "responseConfirmation": settings_obj.support_response_confirmation,
            },
            "social": {
                "facebook": settings_obj.facebook,
                "twitter": settings_obj.twitter,
                "linkedin": settings_obj.linkedin,
                "instagram": settings_obj.instagram,
                "youtube": settings_obj.youtube,
                "github": settings_obj.github,
            },
            "business": {
                "abn": settings_obj.abn,
                "hours": _parse_business_hours(settings_obj),
            },
            "analytics": {
                "googleAnalyticsId": settings_obj.google_analytics_id,
                "facebookPixelId": settings_obj.facebook_pixel_id,
            },
        }
        return self.render({"settings": payload})


class PageSEOAPIView(JSONAPIView):
    """SEO metadata for a specific page."""
    def get(self, request):
        page = request.GET.get('page', 'home')
        return self.render({"seo": _serialize_page_seo(page)})


class SEOAutomationInsightsAPIView(JSONAPIView):
    """Expose processed SEO upload insights + AI recommendations."""

    def get(self, request):
        upload_id = request.GET.get("upload")
        uploads = SEODataUpload.objects.filter(status=SEODataUpload.STATUS_PROCESSED)
        if upload_id:
            uploads = uploads.filter(id=upload_id)
        upload = (
            uploads.order_by("-processed_at", "-created_at")
            .prefetch_related("keywords", "clusters", "recommendations")
            .first()
        )
        if not upload:
            return self.render({"upload": None})

        top_keywords = [
            {
                "keyword": keyword.keyword,
                "intent": keyword.intent,
                "searchVolume": keyword.search_volume,
                "priorityScore": float(keyword.priority_score),
            }
            for keyword in upload.keywords.order_by("-priority_score")[:10]
        ]
        clusters = [
            {
                "label": cluster.label,
                "intent": cluster.intent,
                "keywordCount": cluster.keyword_count,
                "avgVolume": cluster.avg_volume,
                "priorityScore": float(cluster.priority_score),
            }
            for cluster in upload.clusters.order_by("-priority_score")[:8]
        ]
        recommendations = [
            {
                "title": recommendation.title,
                "category": recommendation.get_category_display(),
                "status": recommendation.status,
                "cluster": recommendation.cluster.label if recommendation.cluster else None,
                "content": recommendation.response,
            }
            for recommendation in upload.recommendations.order_by("-created_at")[:10]
        ]

        return self.render(
            {
                "upload": {
                    "id": upload.id,
                    "name": upload.name,
                    "processedAt": upload.processed_at,
                    "rowCount": upload.row_count,
                    "insights": upload.insights,
                },
                "topKeywords": top_keywords,
                "clusters": clusters,
                "recommendations": recommendations,
            }
        )


class TestimonialsAPIView(JSONAPIView):
    """Customer testimonials."""
    def get(self, request):
        return self.render({"testimonials": _serialize_testimonials()})


class CTASectionsAPIView(JSONAPIView):
    """Call-to-action sections."""
    def get(self, request):
        placement = request.GET.get('placement', 'global')
        return self.render({"ctaSections": _serialize_cta_sections(placement)})


class DemosAPIView(JSONAPIView):
    """Demo showcases."""
    def get(self, request):
        return self.render({"demos": _serialize_demos()})


class PricingAPIView(JSONAPIView):
    """Pricing plans."""
    def get(self, request):
        plans = (
            PricingPlan.objects.filter(is_active=True)
            .prefetch_related("features")
            .order_by("order")
        )

        payload = [
            {
                "name": plan.name,
                "slug": plan.slug,
                "tagline": plan.tagline,
                "price": str(plan.price),
                "currency": plan.currency,
                "billingPeriod": plan.billing_period,
                "description": plan.description,
                "isPopular": plan.is_popular,
                "buttonText": plan.button_text,
                "buttonUrl": plan.button_url,
                "features": [
                    {
                        "text": f.text,
                        "isIncluded": f.is_included,
                    }
                    for f in plan.features.all()
                ],
            }
            for plan in plans
        ]
        return self.render({"plans": payload})


class StatsAPIView(JSONAPIView):
    """Statistics for different sections."""
    def get(self, request):
        section = request.GET.get('section', 'home')
        return self.render({"stats": _serialize_stats(section)})


class NavigationAPIView(JSONAPIView):
    """Navigation menus."""
    def get(self, request):
        location = request.GET.get('location', 'header')
        menu = (
            NavigationMenu.objects.filter(location=location, is_active=True)
            .prefetch_related("items")
            .first()
        )

        if not menu:
            return self.render({"navigation": []})

        # Build hierarchical structure
        items_dict = {}
        root_items = []

        for item in menu.items.filter(is_active=True):
            item_data = {
                "id": item.id,
                "title": item.title,
                "url": item.url,
                "icon": item.icon,
                "openInNewTab": item.open_in_new_tab,
                "children": [],
            }
            items_dict[item.id] = item_data

            if item.parent_id:
                # Will add to parent later
                pass
            else:
                root_items.append(item_data)

        # Add children to their parents
        for item in menu.items.filter(is_active=True):
            if item.parent_id and item.parent_id in items_dict:
                items_dict[item.parent_id]["children"].append(items_dict[item.id])

        return self.render({"navigation": root_items})


@method_decorator(cache_page(getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)), name='dispatch')
class HomePageAPIView(JSONAPIView):
    """Aggregate payload for the marketing home page."""

    def get(self, request):
        services_data = _serialize_services_section()
        return self.render(
            {
                "seo": _serialize_page_seo("home"),
                "hero": _serialize_hero_section() or {},
                "brand": BRAND_TOKENS,
                "impact": _serialize_business_impact_section(),
                "services": services_data.get("services", []),
                "serviceStats": services_data.get("stats", []),
                "serviceProcess": services_data.get("process", []),
                "aiTools": _serialize_ai_tools_section(),
                "roiCalculator": _serialize_roi_calculator_content(),
                "whyChoose": _serialize_why_choose_section(),
                "stats": _serialize_stats("home"),
                "testimonials": _serialize_testimonials(),
                "ctaSections": _serialize_cta_sections("home"),
                "demos": _serialize_demos(),
            }
        )


@method_decorator(cache_page(getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)), name='dispatch')
class ServicesPageAPIView(JSONAPIView):
    """Aggregate payload for the services page."""

    def get(self, request):
        services_data = _serialize_services_section()
        return self.render(
            {
                "seo": _serialize_page_seo("services"),
                "services": services_data.get("services", []),
                "stats": services_data.get("stats", []),
                "process": services_data.get("process", []),
                "ctaSections": _serialize_cta_sections("services"),
                "testimonials": _serialize_testimonials(),
            }
        )


@method_decorator(cache_page(getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)), name='dispatch')
class AIToolsPageAPIView(JSONAPIView):
    """Aggregate payload for the AI tools showcase page."""

    def get(self, request):
        return self.render(
            {
                "seo": _serialize_page_seo("ai-tools"),
                "aiTools": _serialize_ai_tools_section(),
                "ctaSections": _serialize_cta_sections("ai-tools"),
                "roiCalculator": _serialize_roi_calculator_content(),
            }
        )


@method_decorator(cache_page(getattr(settings, 'CACHE_TIMEOUT_MEDIUM', 300)), name='dispatch')
class DemosPageAPIView(JSONAPIView):
    """Aggregate payload for the demos page."""

    def get(self, request):
        return self.render(
            {
                "seo": _serialize_page_seo("demos"),
                "demos": _serialize_demos(),
                "ctaSections": _serialize_cta_sections("demos"),
            }
        )


class ContactPageAPIView(JSONAPIView):
    """Aggregate payload for the contact page, including FAQs."""

    def get(self, request):
        return self.render(
            {
                "seo": _serialize_page_seo("contact"),
                "contact": _serialize_contact_details(include_inquiries=True),
                "faqs": _serialize_faq_categories(),
            }
        )


class BlogAPIView(JSONAPIView):
    """Blog posts."""
    def get(self, request):
        # Filter by status='published' (new field) for consistency
        posts = BlogPost.objects.filter(status='published').order_by("-published_at")

        # Optional filtering by category
        category = request.GET.get('category')
        if category:
            posts = posts.filter(
                models.Q(blog_category__name__icontains=category) |
                models.Q(blog_category__slug__icontains=category) |
                models.Q(category__icontains=category)  # Legacy field
            )

        featured_only = request.GET.get('featured')
        if featured_only:
            posts = posts.filter(is_featured=True)

        payload = [
            {
                "title": post.title,
                "slug": post.slug,
                "excerpt": post.excerpt,
                "content": post.content,
                "featuredImage": post.featured_image.url if post.featured_image else None,
                "author": post.author,
                "category": post.blog_category.name if post.blog_category else post.category,
                "tags": post.tags.split(",") if post.tags else [],
                "isFeatured": post.is_featured,
                "publishedAt": post.published_at.isoformat() if post.published_at else None,
                "viewsCount": post.views_count,
            }
            for post in posts.select_related('blog_category')[:20]  # Limit to 20 posts
        ]
        return self.render({"posts": payload})


class KnowledgeBaseAPIView(JSONAPIView):
    """Knowledge-base articles for the chatbot and frontend."""

    def get(self, request):
        query = request.GET.get("q")
        category_slug = request.GET.get("category")
        articles = KnowledgeArticle.objects.filter(status=KnowledgeArticle.STATUS_PUBLISHED).select_related("category")
        if category_slug:
            articles = articles.filter(category__slug=category_slug)
        if query:
            articles = articles.filter(
                models.Q(title__icontains=query)
                | models.Q(summary__icontains=query)
                | models.Q(content__icontains=query)
                | models.Q(tags__icontains=query)
            )
        limit = int(request.GET.get("limit", 6))
        articles = articles.order_by("-is_featured", "-published_at")[:limit]
        payload = [
            {
                "title": article.title,
                "slug": article.slug,
                "summary": article.summary,
                "category": article.category.name,
                "tags": article.tag_list(),
                "cta": article.call_to_action,
                "ctaUrl": article.call_to_action_url,
            }
            for article in articles
        ]
        return self.render({"articles": payload})


class ChatbotKnowledgeAPIView(JSONAPIView):
    """Aggregated marketing knowledge for the chatbot widget."""

    def get(self, request):
        builder = ChatKnowledgeBuilder()
        data = builder.build()
        return self.render({"knowledge": data})


class ChatbotConfigAPIView(JSONAPIView):
    """Public chatbot configuration (greeting, quick replies, etc.)."""

    def get(self, request):
        return self.render(ChatbotService.public_config())


@method_decorator(csrf_exempt, name='dispatch')
class ChatConversationAPIView(JSONAPIView):
    """Create a new chat conversation."""

    def post(self, request):
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            data = {}
        conversation = ChatConversation.objects.create(
            visitor_name=data.get("name", ""),
            visitor_email=data.get("email", ""),
            visitor_company=data.get("company", ""),
            source=data.get("source", ""),
        )
        payload = {
            "conversationId": str(conversation.conversation_id),
            "config": ChatbotService.public_config(),
        }
        return self.render(payload, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class ChatbotMessageAPIView(JSONAPIView):
    """Handle user messages and stream back AI replies."""

    def post(self, request):
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return self.render({"error": "Invalid JSON payload"}, status=400)

        conversation_id = data.get("conversationId")
        message = data.get("message")
        if not message:
            return self.render({"error": "message is required"}, status=400)

        if conversation_id:
            try:
                conversation = ChatConversation.objects.get(conversation_id=conversation_id)
            except ChatConversation.DoesNotExist:
                return self.render({"error": "Conversation not found"}, status=404)
        else:
            conversation = ChatConversation.objects.create(
                visitor_name=data.get("name", ""),
                visitor_email=data.get("email", ""),
                source="chat-api",
            )

        service = ChatbotService(conversation)
        payload = service.reply(message)
        return self.render(payload)


class ReactAppView(TemplateView):
    """
    Serves the compiled React SPA (frontend/dist/index.html).

    Injects SEO meta tags server-side so Google sees them immediately,
    before JavaScript loads.

    If the build is missing we show a helpful reminder template instead.
    """

    template_name = "loading.html"

    def get_template_names(self):
        react_index = settings.FRONTEND_BUILD / "index.html"
        if react_index.exists():
            return ["index.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["brand"] = BRAND_TOKENS

        # Inject SEO from database
        path = self.request.path
        seo = self._get_seo_for_path(path)
        context["seo"] = seo

        return context

    def _get_seo_for_path(self, path):
        """Get SEO data for the current URL path."""
        from .models import PageSEO, Service, BlogPost

        site_url = getattr(settings, 'SITE_URL', 'https://codeteki.au').rstrip('/')

        # Default SEO
        default_seo = {
            'title': 'Codeteki - AI Business Solutions Melbourne',
            'description': 'Transform your business with AI-powered chatbots, voice assistants, and custom automation. Melbourne-based AI development team.',
            'keywords': 'AI business solutions, chatbot development, voice AI, business automation, Melbourne',
            'canonical': f'{site_url}{path.rstrip("/")}' if path != '/' else site_url,
            'og_title': 'Codeteki - AI Business Solutions',
            'og_description': 'Transform your business with AI-powered solutions.',
            'og_image': f'{site_url}/favicon.png',
        }

        # Map URL paths to page types
        path_clean = path.rstrip('/')

        # Check for service detail pages: /services/slug
        if path_clean.startswith('/services/') and path_clean.count('/') == 2:
            slug = path_clean.split('/')[-1]
            service = Service.objects.filter(slug=slug).first()
            if service:
                seo = PageSEO.objects.filter(service=service).first()
                if seo:
                    return self._seo_to_dict(seo, site_url, path)

        # Check for blog pages: /blog/slug
        if path_clean.startswith('/blog/') and path_clean.count('/') == 2:
            slug = path_clean.split('/')[-1]
            post = BlogPost.objects.filter(slug=slug).first()
            if post:
                seo = PageSEO.objects.filter(blog_post=post).first()
                if seo:
                    return self._seo_to_dict(seo, site_url, path)

        # Map static pages
        page_map = {
            '/': 'home',
            '': 'home',
            '/services': 'services',
            '/ai-tools': 'ai-tools',
            '/demos': 'demos',
            '/faq': 'faq',
            '/contact': 'contact',
            '/blog': 'blog',
        }

        page_type = page_map.get(path_clean)
        if page_type:
            seo = PageSEO.objects.filter(page=page_type).first()
            if seo:
                return self._seo_to_dict(seo, site_url, path)

        # Try custom URL match
        seo = PageSEO.objects.filter(custom_url=path_clean).first()
        if seo:
            return self._seo_to_dict(seo, site_url, path)

        return default_seo

    def _seo_to_dict(self, seo, site_url, path):
        """Convert PageSEO model to template context dict."""
        return {
            'title': seo.meta_title or 'Codeteki',
            'description': seo.meta_description or '',
            'keywords': seo.meta_keywords or '',
            'canonical': seo.canonical_url or f'{site_url}{path.rstrip("/")}',
            'og_title': seo.effective_og_title or seo.meta_title,
            'og_description': seo.effective_og_description or seo.meta_description,
            'og_image': seo.effective_og_image.url if seo.effective_og_image else f'{site_url}/favicon.png',
        }
