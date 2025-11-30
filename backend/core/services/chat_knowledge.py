from __future__ import annotations

from dataclasses import dataclass

from ..models import (
    AITool,
    AIToolsSection,
    FAQCategory,
    HeroSection,
    Service,
    SiteSettings,
    Testimonial,
)


@dataclass
class ChatKnowledgeBuilder:
    """Collects marketing data so the chatbot stays in sync with admin content."""

    def build(self) -> dict:
        hero = HeroSection.objects.filter(is_active=True).order_by("-updated_at").first()
        services = Service.objects.prefetch_related("outcomes").order_by("order")
        faq_categories = FAQCategory.objects.prefetch_related("items").order_by("order")
        testimonials = Testimonial.objects.filter(is_active=True).order_by("-is_featured", "order")
        site = SiteSettings.objects.order_by("-updated_at").first()

        # Get AI Tools from ALL active sections (not just the first one)
        tools = [
            {
                "title": tool.title,
                "description": tool.description,
                "status": tool.status,
                "category": tool.category,
            }
            for tool in AITool.objects.filter(
                is_active=True,
                section__is_active=True
            ).select_related("section").order_by("section__id", "order")
        ]

        # Get business hours
        business_hours = []
        if site:
            hours_from_model = site.hours.all().order_by('order')
            if hours_from_model.exists():
                business_hours = [
                    {"day": hour.get_day_display(), "hours": "Closed" if hour.is_closed else hour.hours}
                    for hour in hours_from_model
                ]

        return {
            "hero": {
                "title": hero.title if hero else "",
                "highlighted": getattr(hero, "highlighted_text", ""),
                "description": hero.description if hero else "",
                "primaryCta": getattr(hero, "primary_cta_label", ""),
                "secondaryCta": getattr(hero, "secondary_cta_label", ""),
            },
            "services": [
                {
                    "title": service.title,
                    "description": service.description,
                    "outcomes": [outcome.text for outcome in service.outcomes.all()],
                }
                for service in services
            ],
            "aiTools": tools,
            "faqs": [
                {"question": item.question, "answer": item.answer}
                for category in faq_categories
                for item in category.items.all()
            ],
            "testimonials": [
                {
                    "name": testimonial.name,
                    "company": testimonial.company,
                    "content": testimonial.content,
                }
                for testimonial in testimonials
            ],
            "contact": {
                "email": site.primary_email if site else "",
                "phone": site.primary_phone if site else "",
                "address": site.address if site else "",
            },
            "businessHours": business_hours,
        }

    def to_prompt_block(self, data: dict | None = None) -> str:
        data = data or self.build()
        sections: list[str] = []

        hero = data.get("hero") or {}
        if hero.get("title"):
            sections.append(
                "Hero Messaging:\n"
                f"Title: {hero['title']} {hero.get('highlighted', '')}\n"
                f"Description: {hero.get('description', '')}\n"
                f"Primary CTA: {hero.get('primaryCta') or 'Book a Codeteki strategy call'}\n"
            )

        services = data.get("services") or []
        if services:
            lines = ["Services & Outcomes:"]
            for service in services:
                outcomes = ", ".join(service.get("outcomes") or [])
                lines.append(f"- {service['title']}: {service['description']} (Outcomes: {outcomes})")
            sections.append("\n".join(lines))

        ai_tools = data.get("aiTools") or []
        if ai_tools:
            tool_lines = ["AI Tools Available:"]
            for tool in ai_tools:
                status = tool.get("status", "free").capitalize()
                tool_lines.append(f"- {tool['title']} ({status}): {tool['description']}")
            sections.append("\n".join(tool_lines))

        faqs = data.get("faqs") or []
        if faqs:
            faq_lines = ["Top FAQs:"]
            for item in faqs:
                faq_lines.append(f"Q: {item['question']}\nA: {item['answer']}")
            sections.append("\n".join(faq_lines))

        testimonials = data.get("testimonials") or []
        if testimonials:
            testimonial_lines = ["Customer Proof:"]
            for quote in testimonials:
                testimonial_lines.append(
                    f"{quote['name']} ({quote.get('company', 'Client')}): {quote['content']}"
                )
            sections.append("\n".join(testimonial_lines))

        contact = data.get("contact") or {}
        if contact.get("email") or contact.get("phone"):
            sections.append(
                "Contact Info:\n"
                f"Email: {contact.get('email', 'info@codeteki.au')}\n"
                f"Phone: {contact.get('phone', '+61 469 754 386')}\n"
                f"Address: {contact.get('address', 'Melbourne, Australia')}"
            )

        hours = data.get("businessHours") or []
        if hours:
            hours_lines = ["Business Hours (AEDT):"]
            for slot in hours:
                hours_lines.append(f"- {slot['day']}: {slot['hours']}")
            sections.append("\n".join(hours_lines))

        return "\n\n".join(sections)
