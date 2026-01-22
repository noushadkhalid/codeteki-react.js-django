"""
Management command to add CRM service to Codeteki website.

Usage:
    python manage.py add_crm_service
"""

from django.core.management.base import BaseCommand
from core.models import Service, ServiceOutcome, ServiceFeature, ServiceCapability, ServiceBenefit, ServiceProcess


class Command(BaseCommand):
    help = 'Add AI-Powered CRM service to Codeteki website'

    def handle(self, *args, **options):
        # Check if service already exists
        if Service.objects.filter(slug='ai-crm').exists():
            self.stdout.write(self.style.WARNING('CRM service already exists. Updating...'))
            service = Service.objects.get(slug='ai-crm')
            # Clear existing related items
            service.outcomes.all().delete()
            service.features.all().delete()
            service.capabilities.all().delete()
            service.benefits.all().delete()
            service.process_steps.all().delete()
        else:
            service = Service()

        # Basic Service Info
        service.title = "AI-Powered CRM & Sales Automation"
        service.slug = "ai-crm"
        service.badge = "New Service"
        service.description = "Intelligent customer relationship management with AI-driven email automation, smart pipelines, and multi-brand support. Streamline your sales process and nurture leads effortlessly."
        service.icon = "Users"
        service.is_featured = True
        service.order = 2  # After main services

        # Detail Page Content
        service.tagline = "Smart Sales Automation"
        service.subtitle = "Transform your sales process with AI that writes emails, manages pipelines, and nurtures leads while you focus on closing deals."
        service.full_description = """Our AI-Powered CRM is built for modern businesses that want to scale their outreach without sacrificing personalization.

Unlike generic CRMs, our system uses advanced AI to understand your brand voice, craft compelling emails, and intelligently move prospects through your sales pipeline.

Whether you're managing real estate leads, business directory listings, or B2B sales, our CRM adapts to your workflow and delivers results.

**Key Highlights:**
- AI writes personalized emails that don't sound like templates
- Smart pipeline automation moves deals based on engagement
- Multi-brand support for agencies managing multiple clients
- Problem-solving approach - AI focuses on solving customer problems, not hard selling
- Complete email tracking with open rates and reply detection"""

        # Styling
        service.gradient_from = "blue-600"
        service.gradient_to = "cyan-500"

        service.save()
        self.stdout.write(self.style.SUCCESS(f'Created/Updated service: {service.title}'))

        # Service Outcomes (Card features - short list)
        outcomes = [
            "AI-powered email composition",
            "Smart sales pipeline automation",
            "Multi-brand & multi-tenant support",
            "Problem-solving approach, not sales pitch",
        ]
        for i, text in enumerate(outcomes):
            ServiceOutcome.objects.create(service=service, text=text, order=i)
        self.stdout.write(f'  Added {len(outcomes)} outcomes')

        # Service Features (Detail page - 8 items grid)
        features = [
            "AI Email Writer - Personalized emails that convert",
            "Smart Pipelines - Visual Kanban boards for every workflow",
            "Multi-Brand Support - Manage multiple businesses from one dashboard",
            "Automated Follow-ups - Never let a lead go cold",
            "Unsubscribe Management - Brand-specific opt-outs",
            "Contact Deduplication - Clean, organized contact lists",
            "Email Templates - Beautiful, responsive HTML emails",
            "Analytics Dashboard - Track opens, replies, and conversions",
        ]
        for i, text in enumerate(features):
            ServiceFeature.objects.create(service=service, text=text, order=i)
        self.stdout.write(f'  Added {len(features)} features')

        # Service Capabilities (Icon cards)
        capabilities = [
            {
                "icon": "Brain",
                "title": "AI Email Composition",
                "description": "Our AI understands your brand voice and writes emails that feel personal, not templated. It focuses on solving customer problems rather than hard selling."
            },
            {
                "icon": "GitBranch",
                "title": "Smart Sales Pipelines",
                "description": "Visual Kanban boards that automatically move deals based on engagement. Track real estate leads, business listings, or B2B sales with customizable stages."
            },
            {
                "icon": "Building2",
                "title": "Multi-Brand Management",
                "description": "Perfect for agencies managing multiple clients. Each brand gets its own email configuration, templates, and contact lists - all from one dashboard."
            },
            {
                "icon": "Mail",
                "title": "Email Automation",
                "description": "Automated follow-up sequences that respect unsubscribes. Beautiful HTML templates with your branding and 'Powered by Codeteki' footer."
            },
            {
                "icon": "BarChart3",
                "title": "Analytics & Tracking",
                "description": "Track email opens, replies, and conversions. See which pipelines perform best and where leads drop off."
            },
            {
                "icon": "Shield",
                "title": "Compliance Built-in",
                "description": "GDPR-friendly unsubscribe management. Brand-specific opt-outs so one unsubscribe doesn't affect other campaigns."
            },
        ]
        for i, cap in enumerate(capabilities):
            ServiceCapability.objects.create(
                service=service,
                icon=cap["icon"],
                title=cap["title"],
                description=cap["description"],
                order=i
            )
        self.stdout.write(f'  Added {len(capabilities)} capabilities')

        # Service Benefits (Why Choose Us)
        benefits = [
            "AI that writes like a human, not a robot",
            "Problem-solving approach increases response rates",
            "Multi-brand support for agencies and portfolios",
            "Beautiful email templates that work on all devices",
            "Automated follow-ups that respect boundaries",
            "Visual pipelines for any sales workflow",
            "Built on Django - reliable and scalable",
            "White-label options available",
        ]
        for i, text in enumerate(benefits):
            ServiceBenefit.objects.create(service=service, text=text, order=i)
        self.stdout.write(f'  Added {len(benefits)} benefits')

        # Service Process Steps
        process_steps = [
            {
                "step_number": 1,
                "title": "Discovery & Setup",
                "description": "We understand your sales process, target audience, and brand voice. Then we configure your pipelines, email templates, and AI settings."
            },
            {
                "step_number": 2,
                "title": "Brand Configuration",
                "description": "Set up your brand(s) with custom email signatures, colors, and AI context. Import your existing contacts or start fresh."
            },
            {
                "step_number": 3,
                "title": "Pipeline Creation",
                "description": "Create visual sales pipelines tailored to your workflow - whether it's real estate, business directory, or B2B sales."
            },
            {
                "step_number": 4,
                "title": "AI Training",
                "description": "Configure AI settings including business updates, target context, and approach style. The AI learns your brand voice."
            },
            {
                "step_number": 5,
                "title": "Launch & Automate",
                "description": "Start sending AI-crafted emails and let the system nurture your leads. Monitor performance and refine as needed."
            },
        ]
        for step in process_steps:
            ServiceProcess.objects.create(
                service=service,
                step_number=step["step_number"],
                title=step["title"],
                description=step["description"],
                order=step["step_number"]
            )
        self.stdout.write(f'  Added {len(process_steps)} process steps')

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ CRM Service added successfully!\n'
            f'   View at: /services/ai-crm/\n'
            f'   Admin: /admin/core/service/{service.id}/change/'
        ))
