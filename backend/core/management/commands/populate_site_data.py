"""
Management command to populate all site data from frontend content.
Makes the entire website fully dynamic and manageable from backend.

Usage: python manage.py populate_site_data
"""

from django.core.management.base import BaseCommand
from core.models import (
    # Home Page
    HeroSection, HeroMetric,
    BusinessImpactSection, BusinessImpactMetric,
    Service, ServiceOutcome, ServiceProcessStep,
    AIToolsSection, AITool,
    ROICalculatorSection, ROICalculatorStat, ROICalculatorTool,
    WhyChooseSection, WhyChooseReason,
    Testimonial,

    # Contact
    ContactMethod,

    # FAQ
    FAQPageSection, FAQPageStat, FAQCategory, FAQItem,

    # Site Settings
    SiteSettings, BusinessHours,

    # Other
    DemoShowcase,
    CTASection,
    StatMetric,
    PricingPlan, PricingFeature,
)


class Command(BaseCommand):
    help = 'Populate all site data to make website fully dynamic'

    def handle(self, *args, **options):
        self.stdout.write('Starting site data population...\n')

        self.populate_site_settings()
        self.populate_hero_sections()
        self.populate_business_impact()
        self.populate_services()
        self.populate_service_process_steps()
        self.populate_ai_tools()
        self.populate_roi_calculator()
        self.populate_why_choose()
        self.populate_contact_methods()
        self.populate_faq()
        self.populate_testimonials()
        self.populate_cta_sections()
        self.populate_pricing_plans()

        self.stdout.write(self.style.SUCCESS('\nAll site data populated successfully!'))

    def populate_site_settings(self):
        """Populate site settings and business hours."""
        self.stdout.write('  - Site Settings...')

        settings, created = SiteSettings.objects.get_or_create(
            site_name='Codeteki',
            defaults={
                'site_tagline': 'AI Business Solutions Melbourne',
                'site_description': 'Transform your business with AI-powered chatbots, custom tool development, and business automation.',
                'primary_email': 'info@codeteki.au',
                'secondary_email': 'support@codeteki.au',
                'primary_phone': '+61 469 754 386',
                'secondary_phone': '+61 424 538 777',
                'address': 'Melbourne, Victoria, Australia',
                'abn': '20 608 158 407',
                'support_badge': 'We respond within 24 hours',
            }
        )

        # Add business hours if none exist
        if not settings.hours.exists():
            hours_data = [
                ('monday_friday', '9:00 AM - 6:00 PM AEDT', 0),
                ('saturday', '10:00 AM - 4:00 PM AEDT', 1),
                ('sunday', 'By appointment', 2),
            ]
            for day, hours, order in hours_data:
                BusinessHours.objects.create(
                    site_settings=settings,
                    day=day,
                    hours=hours,
                    order=order
                )

        self.stdout.write(self.style.SUCCESS(' Done'))

    def populate_hero_sections(self):
        """Populate hero sections for all pages."""
        self.stdout.write('  - Hero Sections...')

        heroes = [
            {
                'page': 'home',
                'badge': 'AI-Powered Business Solutions',
                'badge_emoji': '🚀',
                'title': 'Transform Your Business with',
                'highlighted_text': 'Intelligent Automation',
                'subheading': 'Melbourne-based AI development team',
                'description': 'Deploy AI chatbots, voice assistants, and custom automation tools that work 24/7. One-time setup, no monthly AI fees.',
                'metrics': [
                    ('60%', 'Cost Reduction'),
                    ('24/7', 'Availability'),
                    ('< 24hrs', 'Response Time'),
                ]
            },
            {
                'page': 'services',
                'badge': 'Our Core Services',
                'title': 'From AI workforce to custom tools and MCP integration',
                'description': 'Comprehensive solutions tailored for your business with Melbourne-based delivery, transparent pricing, and fully managed operations after launch.',
                'subheading': 'Melbourne-based delivery, transparent pricing, and fully managed operations.',
                'metrics': [
                    ('4-6 weeks', 'Average delivery'),
                    ('70+', 'Projects delivered'),
                    ('20+', 'Live copilots'),
                ]
            },
            {
                'page': 'contact',
                'badge': 'Get in Touch',
                'title': 'Ready to Transform Your Business?',
                'description': 'Book a free consultation and discover how AI can revolutionize your operations.',
                'metrics': [
                    ('< 24 hrs', 'Response time'),
                    ('Free', 'Consultation'),
                    ('No obligation', 'Quote'),
                ]
            },
            {
                'page': 'faq',
                'badge': 'FAQ Hub',
                'title': 'Answers for Every Stage',
                'description': 'Find answers to common questions about our AI solutions, implementation process, and support.',
                'metrics': [
                    ('< 24 hrs', 'Average response time'),
                    ('80+', 'Documented answers'),
                    ('14', 'Industries supported'),
                ]
            },
        ]

        for hero_data in heroes:
            hero, created = HeroSection.objects.get_or_create(
                page=hero_data['page'],
                defaults={
                    'badge': hero_data.get('badge', ''),
                    'badge_emoji': hero_data.get('badge_emoji', ''),
                    'title': hero_data['title'],
                    'highlighted_text': hero_data.get('highlighted_text', ''),
                    'subheading': hero_data.get('subheading', ''),
                    'description': hero_data['description'],
                    'is_active': True,
                }
            )

            if created and 'metrics' in hero_data:
                for i, (value, label) in enumerate(hero_data['metrics']):
                    HeroMetric.objects.create(
                        hero=hero,
                        value=value,
                        label=label,
                        order=i
                    )

        self.stdout.write(self.style.SUCCESS(' Done'))

    def populate_business_impact(self):
        """Populate business impact section."""
        self.stdout.write('  - Business Impact...')

        section, created = BusinessImpactSection.objects.get_or_create(
            title='Trusted by Melbourne Businesses',
            defaults={
                'description': 'Join businesses already transforming their operations with AI-powered solutions.',
                'cta_label': 'See Case Studies',
                'cta_href': '/demos',
            }
        )

        if created or not section.metrics.exists():
            metrics = [
                ('60%', 'Average Cost Reduction', 'Compared to traditional staffing'),
                ('24/7', 'Availability', 'Your AI never sleeps'),
                ('< 2 sec', 'Response Time', 'Instant customer engagement'),
                ('99.9%', 'Uptime', 'Enterprise-grade reliability'),
            ]
            for i, (value, label, caption) in enumerate(metrics):
                BusinessImpactMetric.objects.get_or_create(
                    section=section,
                    label=label,
                    defaults={
                        'value': value,
                        'caption': caption,
                        'order': i,
                    }
                )

        self.stdout.write(self.style.SUCCESS(' Done'))

    def populate_services(self):
        """Populate services."""
        self.stdout.write('  - Services...')

        services_data = [
            {
                'title': 'AI Workforce Solutions',
                'slug': 'ai-workforce',
                'description': 'Deploy domain-trained AI agents that collaborate with your team, manage workflows, and eliminate repetitive busy work.',
                'badge': 'Enterprise Ready',
                'icon': 'Bot',
                'outcomes': [
                    'Human-in-the-loop guardrails',
                    'Secure knowledge base integrations',
                    'Realtime analytics + alerts',
                ],
                'is_featured': True,
            },
            {
                'title': 'Custom Tool Development',
                'slug': 'custom-tools',
                'description': 'Design and ship bespoke internal tools, portals, and dashboards that plug straight into your existing ecosystem.',
                'badge': 'Tailored Builds',
                'icon': 'Wrench',
                'outcomes': [
                    'Pixel-perfect UI/UX',
                    'First-party API integrations',
                    'Ongoing roadmap partnership',
                ],
                'is_featured': True,
            },
            {
                'title': 'Business Automation Tools',
                'slug': 'automation',
                'description': 'Automate approvals, reporting, compliance, and daily operations with orchestrated workflows across your stack.',
                'badge': 'Process Automation',
                'icon': 'Zap',
                'outcomes': [
                    'Unified task orchestration',
                    'Codeteki governance layer',
                    'Return on investment reporting',
                ],
                'is_featured': True,
            },
            {
                'title': 'AI Tools for Daily Tasks',
                'slug': 'daily-ai',
                'description': 'Personalized copilots for sales, support, HR, and finance that meet your policies and tone of voice from day one.',
                'badge': 'Personal Copilots',
                'icon': 'Repeat',
                'outcomes': [
                    'Secure workspace libraries',
                    'Role-based access + auditing',
                    'No more context switching',
                ],
                'is_featured': False,
            },
            {
                'title': 'MCP Integration Services',
                'slug': 'mcp-integration',
                'description': 'Connect the Model Context Protocol to your proprietary knowledge bases and tooling to unlock trustworthy automation.',
                'badge': 'MCP Experts',
                'icon': 'Cable',
                'outcomes': [
                    'Source-of-truth syncing',
                    'Guardrailed data pipelines',
                    'Observability dashboards',
                ],
                'is_featured': False,
            },
            {
                'title': 'Professional Web Development',
                'slug': 'web-dev',
                'description': 'Full-stack product teams that deliver marketing sites, customer portals, and high-performance web apps.',
                'badge': 'Full Stack',
                'icon': 'Code',
                'outcomes': [
                    'React + Django specialists',
                    'Accessibility-grade builds',
                    'Training + documentation',
                ],
                'is_featured': False,
            },
            {
                'title': 'AI-Powered SEO Engine',
                'slug': 'seo-engine',
                'description': 'Comprehensive SEO auditing platform with Lighthouse, PageSpeed Insights, Search Console integration, and AI-powered recommendations.',
                'badge': 'New',
                'icon': 'Search',
                'outcomes': [
                    'Real-time site performance audits',
                    'AI-powered SEO recommendations',
                    'Competitor analysis & tracking',
                    'Automated reporting & alerts',
                ],
                'is_featured': True,
            },
        ]

        for i, svc in enumerate(services_data):
            service, created = Service.objects.get_or_create(
                slug=svc['slug'],
                defaults={
                    'title': svc['title'],
                    'description': svc['description'],
                    'badge': svc['badge'],
                    'icon': svc['icon'],
                    'is_featured': svc['is_featured'],
                    'order': i,
                }
            )

            if created:
                for j, outcome in enumerate(svc['outcomes']):
                    ServiceOutcome.objects.create(
                        service=service,
                        text=outcome,
                        order=j
                    )

        self.stdout.write(self.style.SUCCESS(' Done'))

    def populate_service_process_steps(self):
        """Populate service process steps."""
        self.stdout.write('  - Service Process Steps...')

        steps = [
            ('Discovery Lab', 'Workshops + audits to map automation and AI opportunities.', 'Sparkles', 'blue'),
            ('Design & Build', 'UI, flows, and copilots crafted with our Codeteki system.', 'Layers', 'purple'),
            ('Launch & Train', 'QA, compliance, and handover with your playbooks.', 'ClipboardCheck', 'yellow'),
            ('Care Plans', 'Support tiers covering monitoring, improvements, and hosting.', 'Rocket', 'green'),
        ]

        for i, (title, desc, icon, accent) in enumerate(steps):
            ServiceProcessStep.objects.get_or_create(
                title=title,
                defaults={
                    'description': desc,
                    'icon': icon,
                    'accent': accent,
                    'order': i,
                }
            )

        self.stdout.write(self.style.SUCCESS(' Done'))

    def populate_ai_tools(self):
        """Populate AI Tools section with all DesiFirms tools."""
        self.stdout.write('  - AI Tools...')

        section, created = AIToolsSection.objects.get_or_create(
            title='AI Tools Gallery',
            defaults={
                'badge': 'Live AI Tools',
                'description': 'Production-ready AI tools we built for DesiFirms. See our capability in action.',
                'is_active': True,
            }
        )

        # All AI tools from DesiFirms
        tools_data = [
            # Free Tools
            {
                'title': 'Australian Trip Planner',
                'slug': 'australian-trip-planner',
                'description': 'Discover curated itineraries, verified attractions, and travel tips for every Australian city.',
                'emoji': '🧭',
                'status': 'free',
                'category': 'lifestyle',
                'external_url': 'https://www.desifirms.com.au/ai-tools/australian-trip-planner',
            },
            {
                'title': 'Baby Growth Tracker',
                'slug': 'baby-growth-tracker',
                'description': 'Track milestones, immunisation schedules, and growth charts aligned with Australian health data.',
                'emoji': '👶',
                'status': 'free',
                'category': 'health',
                'external_url': 'https://www.desifirms.com.au/ai-tools/baby-growth-tracker',
            },
            {
                'title': 'Pregnancy Due Date Calculator',
                'slug': 'pregnancy-due-date',
                'description': 'Plan trimester visits and due dates using conception or cycle data.',
                'emoji': '🍼',
                'status': 'free',
                'category': 'health',
                'external_url': 'https://www.desifirms.com.au/ai-tools/pregnancy-due-date',
            },
            {
                'title': 'Water Intake Calculator',
                'slug': 'water-intake-calculator',
                'description': 'Daily hydration goals tuned for local climate and lifestyle.',
                'emoji': '💧',
                'status': 'free',
                'category': 'health',
                'external_url': 'https://www.desifirms.com.au/ai-tools/water-intake-calculator',
            },
            {
                'title': 'Body Fat Percentage Calculator',
                'slug': 'body-fat-percentage',
                'description': 'Estimate body fat using multiple measurement formulas and guidance.',
                'emoji': '📊',
                'status': 'free',
                'category': 'health',
                'external_url': 'https://www.desifirms.com.au/ai-tools/body-fat-percentage',
            },
            {
                'title': 'Calorie Calculator',
                'slug': 'calorie-calculator',
                'description': 'Get personalised calorie targets for weight gain, maintenance, or loss.',
                'emoji': '🍎',
                'status': 'free',
                'category': 'health',
                'external_url': 'https://www.desifirms.com.au/ai-tools/calorie-calculator',
            },
            {
                'title': 'BMI Calculator',
                'slug': 'bmi-calculator',
                'description': 'BMI with imperial/metric inputs and health categories.',
                'emoji': '⚖️',
                'status': 'free',
                'category': 'health',
                'external_url': 'https://www.desifirms.com.au/ai-tools/bmi-calculator',
            },
            {
                'title': 'Mid-Market Exchange Rate Tool',
                'slug': 'exchange-rate-tool',
                'description': 'Live rates and fee guidance for sending money overseas.',
                'emoji': '💱',
                'status': 'free',
                'category': 'finance',
                'external_url': 'https://www.desifirms.com.au/ai-tools/exchange-rate-tool',
            },
            # Credit Tools
            {
                'title': 'Gift Ideas Generator',
                'slug': 'gift-ideas-generator',
                'description': 'Culture-aware gift suggestions for every occasion and relationship.',
                'emoji': '🎁',
                'status': 'credits',
                'category': 'lifestyle',
                'min_credits': 15,
                'external_url': 'https://www.desifirms.com.au/ai-tools/gift-ideas-generator',
            },
            {
                'title': 'Smart Invoice Builder',
                'slug': 'invoice-builder',
                'description': 'AI-powered invoices with summaries, PDF export, and compliance checks.',
                'emoji': '🧾',
                'status': 'credits',
                'category': 'business',
                'min_credits': 20,
                'external_url': 'https://www.desifirms.com.au/ai-tools/invoice-builder',
            },
            {
                'title': 'Product Description Generator',
                'slug': 'product-description-generator',
                'description': 'Create bilingual descriptions for marketplaces and catalogues.',
                'emoji': '🛍️',
                'status': 'credits',
                'category': 'business',
                'min_credits': 18,
                'external_url': 'https://www.desifirms.com.au/ai-tools/product-description-generator',
            },
            # Premium Tools
            {
                'title': 'Desi Party Food Planner',
                'slug': 'desi-food-planner',
                'description': 'Plan perfect South Asian food quantities for weddings and parties.',
                'emoji': '🍽️',
                'status': 'premium',
                'category': 'lifestyle',
                'credit_cost': 75,
                'external_url': 'https://www.desifirms.com.au/ai-tools/desi-food-planner',
            },
            {
                'title': 'Desi Diet & Weight Management',
                'slug': 'diet-planner',
                'description': 'Diet plans with Desi ingredient swaps and weekly shopping lists.',
                'emoji': '🥗',
                'status': 'premium',
                'category': 'health',
                'credit_cost': 65,
                'external_url': 'https://www.desifirms.com.au/ai-tools/diet-planner',
            },
            {
                'title': 'Visa Immigration Assistant',
                'slug': 'visa-guidance',
                'description': 'Analyse visa options and pathways with personalised scoring.',
                'emoji': '🛂',
                'status': 'premium',
                'category': 'immigration',
                'credit_cost': 40,
                'external_url': 'https://www.desifirms.com.au/ai-tools/visa-guidance',
            },
            {
                'title': 'Property Development Planner',
                'slug': 'property-development-planner',
                'description': 'See what you can build based on zoning law, setbacks, and council data.',
                'emoji': '🏗️',
                'status': 'premium',
                'category': 'property',
                'credit_cost': 90,
                'external_url': 'https://www.desifirms.com.au/ai-tools/property-development-planner',
            },
            {
                'title': 'Investment Property Analyzer',
                'slug': 'investment-property-analyzer',
                'description': 'Detailed feasibility reports that combine council data with AI recommendations.',
                'emoji': '📈',
                'status': 'premium',
                'category': 'property',
                'credit_cost': 70,
                'external_url': 'https://www.desifirms.com.au/ai-tools/investment-property-analyzer',
                'is_coming_soon': True,
            },
        ]

        for i, tool in enumerate(tools_data):
            AITool.objects.get_or_create(
                slug=tool['slug'],
                defaults={
                    'section': section,
                    'title': tool['title'],
                    'description': tool['description'],
                    'emoji': tool.get('emoji', ''),
                    'status': tool.get('status', 'free'),
                    'category': tool.get('category', 'general'),
                    'min_credits': tool.get('min_credits', 0),
                    'credit_cost': tool.get('credit_cost', 0),
                    'external_url': tool.get('external_url', ''),
                    'is_coming_soon': tool.get('is_coming_soon', False),
                    'is_active': True,
                    'order': i,
                }
            )

        self.stdout.write(self.style.SUCCESS(' Done'))

    def populate_roi_calculator(self):
        """Populate ROI Calculator section."""
        self.stdout.write('  - ROI Calculator...')

        section, created = ROICalculatorSection.objects.get_or_create(
            title='Calculate Your ROI',
            defaults={
                'badge': 'Smart Business Calculator',
                'highlighted_text': 'with AI Automation',
                'subtitle': 'See how much you could save',
                'description': 'Enter your current costs to estimate potential savings with our AI solutions.',
                'is_active': True,
            }
        )

        if created or not section.stats.exists():
            stats = [
                ('60%', 'Average Cost Savings'),
                ('3 months', 'Typical ROI Period'),
                ('24/7', 'Availability'),
            ]
            for i, (value, label) in enumerate(stats):
                ROICalculatorStat.objects.get_or_create(
                    section=section,
                    label=label,
                    defaults={
                        'value': value,
                        'order': i,
                    }
                )

        self.stdout.write(self.style.SUCCESS(' Done'))

    def populate_why_choose(self):
        """Populate Why Choose Us section."""
        self.stdout.write('  - Why Choose Us...')

        section, created = WhyChooseSection.objects.get_or_create(
            title='Why Choose Codeteki?',
            defaults={
                'badge': 'Why Choose Codeteki',
                'description': 'Melbourne-based AI experts committed to your success with enterprise-grade solutions.',
                'is_active': True,
            }
        )

        if created or not section.reasons.exists():
            reasons = [
                ('Melbourne pod', 'Designers + engineers in the same time zone.', 'MapPin'),
                ('Unlimited capabilities', 'Custom copilots, automation, and MCP integration.', 'Infinity'),
                ('Fast iterations', 'Concept to launch in weeks, not quarters.', 'Zap'),
                ('Care plans', 'Support tiers covering hosting, analytics, enhancements.', 'Shield'),
            ]
            for i, (title, desc, icon) in enumerate(reasons):
                WhyChooseReason.objects.get_or_create(
                    section=section,
                    title=title,
                    defaults={
                        'description': desc,
                        'icon': icon,
                        'order': i,
                    }
                )

        self.stdout.write(self.style.SUCCESS(' Done'))

    def populate_contact_methods(self):
        """Populate contact methods."""
        self.stdout.write('  - Contact Methods...')

        methods = [
            ('General Inquiries', 'Have a new idea or project? Our Melbourne HQ team will respond within one business day.', 'info@codeteki.au', 'Send an Email', 'Mail'),
            ('Support Team', 'Active client with a question? Reach the dedicated codeteki.help desk.', 'support@codeteki.au', 'Open Support Ticket', 'LifeBuoy'),
            ('Call Us', 'Prefer to talk? Book a call and speak directly with our solution engineers.', '+61 469 754 386', 'Schedule a Call', 'Phone'),
        ]

        for i, (title, desc, value, cta, icon) in enumerate(methods):
            ContactMethod.objects.get_or_create(
                title=title,
                defaults={
                    'description': desc,
                    'value': value,
                    'cta_label': cta,
                    'icon': icon,
                    'order': i,
                }
            )

        self.stdout.write(self.style.SUCCESS(' Done'))

    def populate_faq(self):
        """Populate FAQ page and categories."""
        self.stdout.write('  - FAQ Page...')

        # FAQ Page Section (header)
        FAQPageSection.objects.get_or_create(
            title='FAQ Hub',
            defaults={
                'description': 'Answers for every stage of your AI journey',
                'search_placeholder': 'Search FAQs...',
                'cta_text': 'Book strategy call',
                'cta_url': '/contact',
            }
        )

        # FAQ Categories and Items
        faq_data = {
            'Our Capabilities & Approach': [
                ('What industries does Codeteki support?', 'We work with professional services, finance, healthcare, government, and high-growth startups who need secure, explainable automation.'),
                ('Do you replace teams with AI?', 'We augment your existing teams. Every deployment includes training, guardrails, and tailored workflows so people stay in control.'),
                ('Can you work with our in-house developers?', 'Absolutely. We embed with product, data, and IT stakeholders to co-design architecture and share implementation playbooks.'),
                ('How custom are the solutions?', 'Every engagement is bespoke. We reuse hardened accelerators but deliver a solution that fits your processes, compliance, and tech stack.'),
            ],
            'Implementation & Timeline': [
                ('How fast can we go live?', 'Discovery to pilot typically takes 3–4 weeks. Production rollouts follow in 6–10 weeks depending on integrations and change management.'),
                ('What does onboarding look like?', 'We run collaborative workshops, map workflows, define measurable outcomes, and deliver a detailed implementation plan.'),
                ('Can you integrate with legacy systems?', 'Yes. Our engineers have integrated with ERP, CRM, document management, and bespoke line-of-business systems.'),
                ('Do you offer training?', 'Every delivery includes live enablement, recorded walkthroughs, and quick-start guides tailored to each team.'),
            ],
            'Technical Integration': [
                ('Which AI models do you support?', 'We are model-agnostic. Deployments can use OpenAI, Anthropic, local LLMs, or your preferred vendor with multi-tenant isolation.'),
                ('How is data secured?', 'Data remains within your cloud boundary. We configure encryption in transit/at rest, role-based access, and logging that meets SOC2/ISO requirements.'),
                ('Do you offer SLAs?', 'Yes. Production systems include response SLAs plus proactive monitoring dashboards handed over to your team.'),
                ('Can we host on-premises?', 'We support on-prem, private cloud, and hybrid deployments with Kubernetes, Docker, or serverless primitives.'),
            ],
            'Support & Training': [
                ('Do you stay engaged after launch?', 'We offer managed services, retainer-based improvements, and quarterly roadmap reviews.'),
                ('How do you handle feature requests?', 'Requests enter a transparent backlog. You get a delivery plan with impact scoring so stakeholders can prioritise.'),
                ('Can you train new team members?', 'Yes, we provide refreshers, new-hire bootcamps, and helpdesk-style office hours.'),
                ('Is documentation included?', 'Every engagement ships with architecture diagrams, SOPs, and runbooks hosted in your knowledge base.'),
            ],
            'Getting Started': [
                ('What is the first step?', 'Book a consultation. We align on objectives, data readiness, and a success plan before any build kicks off.'),
                ('How do you price projects?', 'Fixed-price discovery, milestone-based delivery, or retainers for rapid support. Every quote is transparent and scoped to outcomes.'),
                ('Can we start with a pilot?', 'Yes. Many clients start with a single workflow pilot to capture ROI data before scaling.'),
                ('Do you work with startups?', 'We partner with funded startups that need enterprise-grade craftsmanship without spinning up a full in-house team.'),
            ],
        }

        for i, (cat_title, items) in enumerate(faq_data.items()):
            category, _ = FAQCategory.objects.get_or_create(
                title=cat_title,
                defaults={'order': i}
            )
            for j, (question, answer) in enumerate(items):
                FAQItem.objects.get_or_create(
                    category=category,
                    question=question,
                    defaults={
                        'answer': answer,
                        'order': j,
                    }
                )

        self.stdout.write(self.style.SUCCESS(' Done'))

    def populate_testimonials(self):
        """Populate testimonials."""
        self.stdout.write('  - Testimonials...')

        testimonials = [
            ('Sarah Chen', 'CEO', 'TechStart Melbourne', 'Codeteki transformed our customer service. The AI chatbot handles 70% of inquiries automatically, letting our team focus on complex issues.', 5),
            ('Michael Roberts', 'Operations Director', 'Logistics Plus', 'The automation tools saved us 20 hours per week on manual data entry. ROI was achieved within the first month.', 5),
            ('Emma Wilson', 'Founder', 'Wilson Consulting', 'Professional, responsive, and delivered exactly what we needed. The voice assistant has been a game-changer for our client calls.', 5),
        ]

        for i, (name, position, company, content, rating) in enumerate(testimonials):
            Testimonial.objects.get_or_create(
                name=name,
                company=company,
                defaults={
                    'position': position,
                    'content': content,
                    'rating': rating,
                    'is_active': True,
                    'order': i,
                }
            )

        self.stdout.write(self.style.SUCCESS(' Done'))

    def populate_cta_sections(self):
        """Populate CTA sections."""
        self.stdout.write('  - CTA Sections...')

        ctas = [
            ('home', 'Ready to Transform Your Business?', 'Get started with a free consultation and custom quote.', 'Start Free Consultation', '/contact', 'View Our Portfolio', '/demos'),
            ('services', 'Ready to Transform Your Business?', 'Get started with a free consultation and custom quote.', 'Start Free Consultation', '/contact', 'View Our Portfolio', '/demos'),
            ('global', 'Start Your AI Journey Today', 'Book a free consultation and discover how AI can revolutionize your operations.', 'Book Consultation', '/contact', '', ''),
        ]

        for placement, title, desc, primary_text, primary_url, secondary_text, secondary_url in ctas:
            CTASection.objects.get_or_create(
                placement=placement,
                defaults={
                    'title': title,
                    'description': desc,
                    'primary_button_text': primary_text,
                    'primary_button_url': primary_url,
                    'secondary_button_text': secondary_text,
                    'secondary_button_url': secondary_url,
                }
            )

        self.stdout.write(self.style.SUCCESS(' Done'))

    def populate_pricing_plans(self):
        """Populate pricing plans."""
        self.stdout.write('  - Pricing Plans...')

        plans = [
            {
                'name': 'Voice AI Assistants',
                'slug': 'voice-ai',
                'price': 899,
                'tagline': 'Starting from $899 - 64% OFF',
                'description': 'Intelligent voice agents for phone support and customer service',
                'billing_period': 'one-time',
                'features': ['24/7 phone support', 'Natural language understanding', 'Call routing & transfers', 'Custom voice & tone', 'Analytics dashboard'],
            },
            {
                'name': 'AI Chatbots',
                'slug': 'ai-chatbots',
                'price': 999,
                'tagline': 'Starting from $999 - 67% OFF',
                'description': 'Custom AI chatbots trained on your business data',
                'billing_period': 'one-time',
                'is_popular': True,
                'features': ['Unlimited conversations', 'Multi-language support', 'Lead qualification', 'CRM integration', 'Custom training'],
            },
            {
                'name': 'Website Development',
                'slug': 'website-dev',
                'price': 499,
                'tagline': 'Starting from $499 - 75% OFF',
                'description': 'Professional websites with AI chatbot integration',
                'billing_period': 'one-time',
                'features': ['Mobile responsive', 'SEO optimized', 'AI chatbot included', 'Contact forms', 'Analytics setup'],
            },
        ]

        for i, plan in enumerate(plans):
            pricing, created = PricingPlan.objects.get_or_create(
                slug=plan['slug'],
                defaults={
                    'name': plan['name'],
                    'price': plan['price'],
                    'tagline': plan.get('tagline', ''),
                    'description': plan['description'],
                    'billing_period': plan.get('billing_period', 'one-time'),
                    'is_popular': plan.get('is_popular', False),
                    'order': i,
                }
            )

            if created:
                for j, feature in enumerate(plan['features']):
                    PricingFeature.objects.create(
                        plan=pricing,
                        text=feature,
                        order=j
                    )

        self.stdout.write(self.style.SUCCESS(' Done'))
