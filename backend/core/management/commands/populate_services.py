"""
Management command to populate services with rich detail page content.
Run with: python manage.py populate_services
"""
from django.core.management.base import BaseCommand
from core.models import (
    Service, ServiceFeature, ServiceCapability, ServiceBenefit, ServiceProcess
)


# Complete service data for all services
SERVICE_DATA = {
    "ai-workforce": {
        "tagline": "Enterprise Ready",
        "subtitle": "Domain-trained AI agents that collaborate with your team and eliminate repetitive work",
        "full_description": "Deploy domain-trained AI agents that collaborate with your team, manage workflows, and eliminate repetitive busy work. Our AI workforce solutions include intelligent chatbots, voice agents, and automation tools that work 24/7 to engage customers, qualify leads, and handle routine inquiries with human-like conversations. Every solution includes human-in-the-loop guardrails for quality assurance.",
        "hero_image_url": "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?auto=format&fit=crop&w=1200&q=80",
        "gradient_from": "purple-600",
        "gradient_to": "indigo-600",
        "features": [
            "Human-in-the-loop guardrails",
            "Secure knowledge base integrations",
            "Real-time analytics and alerts",
            "24/7 automated customer engagement",
            "Intelligent lead qualification",
            "Multi-language support",
            "Custom training on your data",
            "Seamless CRM integration"
        ],
        "capabilities": [
            {"icon": "Bot", "title": "Smart AI Agents", "description": "Domain-trained agents that understand your business context and communicate naturally"},
            {"icon": "Shield", "title": "Guardrailed Operations", "description": "Human oversight built into every workflow for quality and compliance"},
            {"icon": "Database", "title": "Knowledge Integration", "description": "Secure connections to your existing knowledge bases and documentation"},
            {"icon": "Activity", "title": "Real-time Monitoring", "description": "Live dashboards and instant alerts for complete operational visibility"},
            {"icon": "Users", "title": "Team Collaboration", "description": "AI that works alongside your team, not as a replacement"},
            {"icon": "TrendingUp", "title": "Continuous Learning", "description": "Agents improve over time based on interactions and feedback"}
        ],
        "benefits": [
            "Reduce response time from hours to seconds",
            "Handle unlimited simultaneous conversations",
            "Maintain quality with human oversight",
            "Free your team for strategic work",
            "Scale operations without scaling headcount",
            "24/7 availability for customers"
        ],
        "process": [
            {"step": 1, "title": "Discovery", "description": "Understand your workflows and automation opportunities"},
            {"step": 2, "title": "Design", "description": "Create AI agents tailored to your business needs"},
            {"step": 3, "title": "Deploy", "description": "Implement with guardrails and monitoring"},
            {"step": 4, "title": "Optimize", "description": "Continuous improvement based on real data"}
        ]
    },
    "custom-tools": {
        "tagline": "Tailored Builds",
        "subtitle": "Bespoke internal tools, portals, and dashboards for your business",
        "full_description": "Design and ship bespoke internal tools, portals, and dashboards that plug straight into your existing ecosystem. We build custom software solutions that solve your specific business challenges, from employee portals to customer-facing applications, all with pixel-perfect interfaces and seamless integrations.",
        "hero_image_url": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=1200&q=80",
        "gradient_from": "orange-500",
        "gradient_to": "red-600",
        "features": [
            "Pixel-perfect UI/UX design",
            "First-party API integrations",
            "Ongoing roadmap partnership",
            "Custom business logic",
            "Role-based access control",
            "Mobile-responsive interfaces",
            "Real-time data sync",
            "Comprehensive documentation"
        ],
        "capabilities": [
            {"icon": "Wrench", "title": "Custom Development", "description": "Purpose-built tools designed specifically for your unique business requirements"},
            {"icon": "Layers", "title": "Seamless Integration", "description": "Direct connections to your existing systems, databases, and third-party services"},
            {"icon": "Eye", "title": "Intuitive Design", "description": "User-centered interfaces that your team will actually want to use"},
            {"icon": "RefreshCw", "title": "Roadmap Partnership", "description": "We evolve your tools as your business grows and needs change"},
            {"icon": "Shield", "title": "Enterprise Security", "description": "Built with security best practices and compliance requirements in mind"},
            {"icon": "FileText", "title": "Documentation", "description": "Complete technical documentation and user guides for your team"}
        ],
        "benefits": [
            "Tools built exactly for your workflow",
            "Eliminate workarounds and manual processes",
            "Improve team productivity and satisfaction",
            "Own your software - no vendor lock-in",
            "Scale as your business grows",
            "Ongoing partnership for future needs"
        ],
        "process": [
            {"step": 1, "title": "Discovery", "description": "Deep dive into your requirements and current pain points"},
            {"step": 2, "title": "Design", "description": "UI/UX mockups and technical architecture planning"},
            {"step": 3, "title": "Build", "description": "Agile development with regular demos and feedback"},
            {"step": 4, "title": "Launch", "description": "Deployment, training, and ongoing support"}
        ]
    },
    "automation": {
        "tagline": "Process Automation",
        "subtitle": "Orchestrated workflows that automate approvals, reporting, and daily operations",
        "full_description": "Automate approvals, reporting, compliance, and daily operations with orchestrated workflows across your entire tech stack. Our automation solutions eliminate repetitive manual tasks, reduce errors, and give your team back hours every week. Every automation includes our governance layer for visibility and control.",
        "hero_image_url": "https://images.unsplash.com/photo-1518186285589-2f7649de83e0?auto=format&fit=crop&w=1200&q=80",
        "gradient_from": "amber-500",
        "gradient_to": "orange-600",
        "features": [
            "Unified task orchestration",
            "Governance and compliance layer",
            "ROI tracking and reporting",
            "Multi-system workflows",
            "Approval chain automation",
            "Scheduled task execution",
            "Error handling and alerts",
            "Audit trail logging"
        ],
        "capabilities": [
            {"icon": "Cog", "title": "Workflow Orchestration", "description": "Complex multi-step processes automated across all your business systems"},
            {"icon": "Shield", "title": "Governance Layer", "description": "Built-in compliance, approval workflows, and audit trails"},
            {"icon": "BarChart", "title": "ROI Reporting", "description": "Track time saved, errors prevented, and return on automation investment"},
            {"icon": "RefreshCw", "title": "System Integration", "description": "Connect CRM, accounting, HR, and any system with an API"},
            {"icon": "Clock", "title": "Scheduled Tasks", "description": "Automated reports, backups, and maintenance on your schedule"},
            {"icon": "Lock", "title": "Error Handling", "description": "Graceful failure recovery with alerts and manual override options"}
        ],
        "benefits": [
            "Save 10-20+ hours per week on manual tasks",
            "Eliminate errors in repetitive processes",
            "Complete visibility with audit trails",
            "Scale without adding headcount",
            "Faster turnaround on routine work",
            "Focus your team on strategic activities"
        ],
        "process": [
            {"step": 1, "title": "Audit", "description": "Map your processes and identify automation opportunities"},
            {"step": 2, "title": "Design", "description": "Create workflow architecture with governance built in"},
            {"step": 3, "title": "Build", "description": "Implement and test automations thoroughly"},
            {"step": 4, "title": "Monitor", "description": "Ongoing optimization and ROI tracking"}
        ]
    },
    "daily-ai": {
        "tagline": "Personal Copilots",
        "subtitle": "Personalized AI copilots for sales, support, HR, and finance teams",
        "full_description": "Personalized AI copilots for sales, support, HR, and finance that meet your policies and tone of voice from day one. These tools integrate with your existing workspace, provide role-based access, and eliminate context switching so your team can focus on high-value work instead of repetitive tasks.",
        "hero_image_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=1200&q=80",
        "gradient_from": "cyan-500",
        "gradient_to": "blue-600",
        "features": [
            "Secure workspace libraries",
            "Role-based access and auditing",
            "No context switching required",
            "Custom tone and policies",
            "Team-specific training",
            "Privacy-first architecture",
            "Seamless tool integration",
            "Usage analytics dashboard"
        ],
        "capabilities": [
            {"icon": "Repeat", "title": "Daily Task Automation", "description": "AI handles routine tasks like email drafts, data lookups, and report generation"},
            {"icon": "Users", "title": "Role-Based Tools", "description": "Different AI capabilities for sales, support, HR, and finance teams"},
            {"icon": "Shield", "title": "Policy Compliance", "description": "AI follows your company policies, tone guidelines, and approval workflows"},
            {"icon": "Database", "title": "Workspace Integration", "description": "Works with your existing tools - Slack, Teams, Gmail, and more"},
            {"icon": "Lock", "title": "Privacy First", "description": "Your data stays yours - no training on your proprietary information"},
            {"icon": "BarChart", "title": "Usage Insights", "description": "See how teams use AI tools and measure productivity gains"}
        ],
        "benefits": [
            "Eliminate repetitive daily tasks",
            "Consistent communication that matches your brand",
            "Faster response times across all teams",
            "Reduced context switching",
            "Measurable productivity improvements",
            "Team adoption without steep learning curve"
        ],
        "process": [
            {"step": 1, "title": "Assess", "description": "Identify high-impact daily tasks for each team"},
            {"step": 2, "title": "Configure", "description": "Set up AI tools with your policies and tone"},
            {"step": 3, "title": "Train", "description": "Onboard teams with hands-on guidance"},
            {"step": 4, "title": "Scale", "description": "Expand to more teams and use cases"}
        ]
    },
    "mcp-integration": {
        "tagline": "MCP Experts",
        "subtitle": "Connect Model Context Protocol to your knowledge bases and tooling",
        "full_description": "Connect the Model Context Protocol to your proprietary knowledge bases and tooling to unlock trustworthy automation. We specialize in MCP implementations that give AI models secure, controlled access to your business data while maintaining strict governance and observability across all interactions.",
        "hero_image_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
        "gradient_from": "violet-600",
        "gradient_to": "purple-700",
        "features": [
            "Source-of-truth syncing",
            "Guardrailed data pipelines",
            "Observability dashboards",
            "Secure API connections",
            "Real-time data access",
            "Custom MCP servers",
            "Access control policies",
            "Audit logging"
        ],
        "capabilities": [
            {"icon": "Cable", "title": "MCP Implementation", "description": "Expert setup and configuration of Model Context Protocol for your systems"},
            {"icon": "Database", "title": "Knowledge Base Connection", "description": "Secure access to your documentation, databases, and proprietary data"},
            {"icon": "Shield", "title": "Guardrailed Access", "description": "Fine-grained permissions and data filtering for safe AI interactions"},
            {"icon": "Eye", "title": "Full Observability", "description": "Complete visibility into what data AI accesses and how it's used"},
            {"icon": "RefreshCw", "title": "Real-time Sync", "description": "Keep AI models updated with the latest information automatically"},
            {"icon": "Settings", "title": "Custom Servers", "description": "Purpose-built MCP servers for your specific integration needs"}
        ],
        "benefits": [
            "AI with access to your actual business data",
            "Maintain control over what AI can see and do",
            "Trustworthy automation with audit trails",
            "Eliminate hallucinations with grounded context",
            "Faster AI adoption with proper governance",
            "Future-proof integration architecture"
        ],
        "process": [
            {"step": 1, "title": "Audit", "description": "Assess your data sources and integration requirements"},
            {"step": 2, "title": "Architect", "description": "Design secure MCP implementation with guardrails"},
            {"step": 3, "title": "Build", "description": "Implement MCP servers and data pipelines"},
            {"step": 4, "title": "Monitor", "description": "Ongoing observability and optimization"}
        ]
    },
    "web-dev": {
        "tagline": "Full Stack",
        "subtitle": "Full-stack teams delivering marketing sites, portals, and web apps",
        "full_description": "Full-stack product teams that deliver marketing sites, customer portals, and high-performance web applications. We specialize in React and Django development, creating accessible, fast-loading websites that look great on any device. Every project includes comprehensive documentation and training for your team.",
        "hero_image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
        "gradient_from": "blue-600",
        "gradient_to": "cyan-600",
        "features": [
            "React + Django specialists",
            "Accessibility-grade builds",
            "Training and documentation",
            "Mobile-first responsive design",
            "SEO optimization built-in",
            "Performance optimized",
            "Content management systems",
            "Analytics integration"
        ],
        "capabilities": [
            {"icon": "Code", "title": "Full-Stack Development", "description": "React frontends with Django backends - a proven, scalable stack"},
            {"icon": "Eye", "title": "Accessibility First", "description": "WCAG-compliant builds that work for all users and improve SEO"},
            {"icon": "Zap", "title": "Performance", "description": "Fast-loading sites optimized for Core Web Vitals and search rankings"},
            {"icon": "FileText", "title": "Documentation", "description": "Comprehensive guides so your team can manage and update content"},
            {"icon": "Search", "title": "SEO Built-in", "description": "Technical SEO best practices implemented from the start"},
            {"icon": "Layers", "title": "Scalable Architecture", "description": "Built to grow with your business and handle increased traffic"}
        ],
        "benefits": [
            "Professional online presence that converts",
            "Fast, accessible sites that rank well",
            "Your team can manage content independently",
            "Modern tech stack with long-term support",
            "Mobile-friendly design for all devices",
            "Ongoing partnership for future features"
        ],
        "process": [
            {"step": 1, "title": "Strategy", "description": "Define goals, audience, and key features"},
            {"step": 2, "title": "Design", "description": "Create mockups and get your approval"},
            {"step": 3, "title": "Build", "description": "Develop with regular demos and feedback"},
            {"step": 4, "title": "Launch", "description": "Go live with training and support"}
        ]
    },
    "seo-engine": {
        "tagline": "New",
        "subtitle": "Comprehensive SEO auditing with Lighthouse, PageSpeed, and AI recommendations",
        "full_description": "Comprehensive SEO auditing platform with Lighthouse, PageSpeed Insights, Search Console integration, and AI-powered recommendations. Get real-time performance audits, actionable insights, and competitor analysis to improve your search rankings and drive more organic traffic to your business.",
        "hero_image_url": "https://images.unsplash.com/photo-1432888622747-4eb9a8efeb07?auto=format&fit=crop&w=1200&q=80",
        "gradient_from": "emerald-600",
        "gradient_to": "teal-600",
        "features": [
            "Real-time site performance audits",
            "AI-powered SEO recommendations",
            "Competitor analysis and tracking",
            "Automated reporting and alerts",
            "Core Web Vitals monitoring",
            "Search Console integration",
            "Keyword tracking",
            "Technical SEO checks"
        ],
        "capabilities": [
            {"icon": "Search", "title": "SEO Auditing", "description": "Comprehensive technical audits using Lighthouse and PageSpeed Insights"},
            {"icon": "Bot", "title": "AI Analysis", "description": "Intelligent recommendations prioritized by impact and effort"},
            {"icon": "LineChart", "title": "Performance Tracking", "description": "Monitor Core Web Vitals and performance metrics over time"},
            {"icon": "Target", "title": "Competitor Insights", "description": "See how you stack up against competitors in search results"},
            {"icon": "Activity", "title": "Real-time Alerts", "description": "Get notified when issues arise that could impact rankings"},
            {"icon": "PieChart", "title": "Automated Reports", "description": "Regular performance reports delivered to your inbox"}
        ],
        "benefits": [
            "Understand exactly what's hurting your rankings",
            "Prioritized recommendations you can action",
            "Track progress over time with clear metrics",
            "Stay ahead of competitor SEO strategies",
            "Automated monitoring saves manual audit time",
            "Data-driven decisions for SEO investment"
        ],
        "process": [
            {"step": 1, "title": "Connect", "description": "Link your site and Search Console for full data access"},
            {"step": 2, "title": "Audit", "description": "Comprehensive scan of your site's SEO health"},
            {"step": 3, "title": "Analyze", "description": "AI generates prioritized recommendations"},
            {"step": 4, "title": "Improve", "description": "Implement fixes and track improvements"}
        ]
    }
}


class Command(BaseCommand):
    help = 'Populate services with rich detail page content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing detail content before populating',
        )

    def handle(self, *args, **options):
        clear = options.get('clear', False)

        self.stdout.write(self.style.NOTICE('Populating service details...'))

        for slug, data in SERVICE_DATA.items():
            try:
                service = Service.objects.get(slug=slug)
            except Service.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Service "{slug}" not found, skipping...'))
                continue

            self.stdout.write(f'  Updating {service.title}...')

            # Update service fields
            service.tagline = data.get('tagline', '')
            service.subtitle = data.get('subtitle', '')
            service.full_description = data.get('full_description', '')
            service.hero_image_url = data.get('hero_image_url', '')
            service.gradient_from = data.get('gradient_from', 'purple-600')
            service.gradient_to = data.get('gradient_to', 'indigo-600')
            service.save()

            # Clear existing related content if requested
            if clear:
                service.features.all().delete()
                service.capabilities.all().delete()
                service.benefits.all().delete()
                service.process_steps.all().delete()

            # Only add if not already populated
            if not service.features.exists():
                for i, text in enumerate(data.get('features', [])):
                    ServiceFeature.objects.create(
                        service=service,
                        text=text,
                        order=i
                    )
                self.stdout.write(f'    Added {len(data.get("features", []))} features')

            if not service.capabilities.exists():
                for i, cap in enumerate(data.get('capabilities', [])):
                    ServiceCapability.objects.create(
                        service=service,
                        icon=cap['icon'],
                        title=cap['title'],
                        description=cap['description'],
                        order=i
                    )
                self.stdout.write(f'    Added {len(data.get("capabilities", []))} capabilities')

            if not service.benefits.exists():
                for i, text in enumerate(data.get('benefits', [])):
                    ServiceBenefit.objects.create(
                        service=service,
                        text=text,
                        order=i
                    )
                self.stdout.write(f'    Added {len(data.get("benefits", []))} benefits')

            if not service.process_steps.exists():
                for i, step in enumerate(data.get('process', [])):
                    ServiceProcess.objects.create(
                        service=service,
                        step_number=step['step'],
                        title=step['title'],
                        description=step['description'],
                        order=i
                    )
                self.stdout.write(f'    Added {len(data.get("process", []))} process steps')

        self.stdout.write(self.style.SUCCESS('\nService details populated successfully!'))
        self.stdout.write(self.style.NOTICE('Visit admin to review and customize the content.'))
