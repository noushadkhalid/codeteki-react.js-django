from django.db import migrations


def seed_content(apps, schema_editor):
    HeroSection = apps.get_model("core", "HeroSection")
    HeroMetric = apps.get_model("core", "HeroMetric")
    HeroPartnerLogo = apps.get_model("core", "HeroPartnerLogo")
    BusinessImpactSection = apps.get_model("core", "BusinessImpactSection")
    BusinessImpactMetric = apps.get_model("core", "BusinessImpactMetric")
    BusinessImpactLogo = apps.get_model("core", "BusinessImpactLogo")
    Service = apps.get_model("core", "Service")
    ServiceOutcome = apps.get_model("core", "ServiceOutcome")
    FAQCategory = apps.get_model("core", "FAQCategory")
    FAQItem = apps.get_model("core", "FAQItem")
    ContactMethod = apps.get_model("core", "ContactMethod")
    try:
        SiteSettings = apps.get_model("core", "SiteSettings")
    except LookupError:
        SiteSettings = None

    hero = HeroSection.objects.create(
        badge="🚀 AI-Powered Business Solutions",
        title="Transform Your Business with AI-Powered Solutions",
        highlighted_text="AI-Powered",
        subheading="Melbourne-based AI engineering & enablement partner",
        description=(
            "At Codeteki, we reimagine operations with human-centred automation, "
            "measurable ROI, and production-ready AI copilots."
        ),
        primary_cta_label="Talk to Us Today",
        primary_cta_href="/contact",
        secondary_cta_label="View Our Services",
        secondary_cta_href="/services",
        image_url="https://codeteki.au/assets/image_1750241082304-CG0Qm923.png",
    )

    for order, metric in enumerate(
        [
            {"label": "Avg. ROI", "value": "210%"},
            {"label": "Delivery Speed", "value": "6 Weeks"},
            {"label": "Client NPS", "value": "72"},
        ]
    ):
        HeroMetric.objects.create(
            hero=hero, label=metric["label"], value=metric["value"], order=order
        )

    for order, partner in enumerate(
        [
            {
                "name": "Desifirms AI",
                "logo": "https://codeteki.au/assets/logo_codeteki1_1750313736817-CyvEyPyd.png",
            },
            {"name": "Melbourne Partners", "logo": "https://codeteki.au/favicon.png"},
        ]
    ):
        HeroPartnerLogo.objects.create(
            hero=hero, name=partner["name"], logo_url=partner["logo"], order=order
        )

    impact = BusinessImpactSection.objects.create(
        title="Real Business Impact",
        description="Our AI-powered solutions deliver concrete business outcomes that transform how your business operates.",
        cta_label="Calculate Your ROI",
        cta_href="/contact",
    )

    impact_metrics = [
        {
            "value": "10x",
            "label": "Customer Inquiries Handled",
            "caption": "Tier-one AI concierges triage, resolve, and escalate without wait times.",
            "icon": "MessageCircle",
            "theme_bg": "bg-blue-100",
            "theme_text": "text-blue-600",
        },
        {
            "value": "24/7",
            "label": "Operation Capability",
            "caption": "Always-on virtual teams keep sales, support, and ops humming.",
            "icon": "Timer",
            "theme_bg": "bg-green-100",
            "theme_text": "text-green-600",
        },
        {
            "value": "60%",
            "label": "Cost Reduction",
            "caption": "Automate repetitive workflows and reinvest savings in growth.",
            "icon": "TrendingDown",
            "theme_bg": "bg-yellow-100",
            "theme_text": "text-yellow-600",
        },
        {
            "value": "<2s",
            "label": "Response Time",
            "caption": "Realtime answers powered by contextual knowledge bases.",
            "icon": "Zap",
            "theme_bg": "bg-purple-100",
            "theme_text": "text-purple-600",
        },
    ]

    for order, metric in enumerate(impact_metrics):
        BusinessImpactMetric.objects.create(
            section=impact,
            value=metric["value"],
            label=metric["label"],
            caption=metric["caption"],
            icon=metric["icon"],
            theme_bg_class=metric["theme_bg"],
            theme_text_class=metric["theme_text"],
            order=order,
        )

    for order, logo in enumerate(
        [
            {
                "name": "Codeteki Digital",
                "logo": "https://codeteki.au/assets/logo_codeteki1_1750313736817-CyvEyPyd.png",
            },
            {"name": "Desifirms AI", "logo": "https://codeteki.au/favicon.png"},
        ]
    ):
        BusinessImpactLogo.objects.create(
            section=impact, name=logo["name"], logo_url=logo["logo"], order=order
        )

    services = [
        {
            "slug": "ai-workforce",
            "title": "AI Workforce Solutions",
            "badge": "Enterprise Ready",
            "icon": "Bot",
            "description": "Deploy domain-trained AI agents that collaborate with your team, manage workflows, and eliminate repetitive busy work.",
            "outcomes": [
                "Human-in-the-loop guardrails",
                "Secure knowledge base integrations",
                "Realtime analytics + alerts",
            ],
        },
        {
            "slug": "custom-tools",
            "title": "Custom Tool Development",
            "badge": "Tailored Builds",
            "icon": "Wrench",
            "description": "Design and ship bespoke internal tools, portals, and dashboards that plug straight into your existing ecosystem.",
            "outcomes": [
                "Pixel-perfect UI/UX",
                "First-party API integrations",
                "Ongoing roadmap partnership",
            ],
        },
        {
            "slug": "automation",
            "title": "Business Automation Tools",
            "badge": "Process Automation",
            "icon": "Zap",
            "description": "Automate approvals, reporting, compliance, and daily operations with orchestrated workflows across your stack.",
            "outcomes": [
                "Unified task orchestration",
                "Codeteki governance layer",
                "Return on investment reporting",
            ],
        },
        {
            "slug": "daily-ai",
            "title": "AI Tools for Daily Tasks",
            "badge": "Personal Copilots",
            "icon": "Repeat",
            "description": "Personalized copilots for sales, support, HR, and finance that meet your policies and tone of voice from day one.",
            "outcomes": [
                "Secure workspace libraries",
                "Role-based access + auditing",
                "No more context switching",
            ],
        },
        {
            "slug": "mcp-integration",
            "title": "MCP Integration Services",
            "badge": "MCP Experts",
            "icon": "Cable",
            "description": "Connect the Model Context Protocol to your proprietary knowledge bases and tooling to unlock trustworthy automation.",
            "outcomes": [
                "Source-of-truth syncing",
                "Guardrailed data pipelines",
                "Observability dashboards",
            ],
        },
        {
            "slug": "web-dev",
            "title": "Professional Web Development",
            "badge": "Full Stack",
            "icon": "Code",
            "description": "Full-stack product teams that deliver marketing sites, customer portals, and high-performance web apps.",
            "outcomes": [
                "React + Django specialists",
                "Accessibility-grade builds",
                "Training + documentation",
            ],
        },
    ]

    for order, service_data in enumerate(services):
        service = Service.objects.create(
            title=service_data["title"],
            slug=service_data["slug"],
            badge=service_data["badge"],
            description=service_data["description"],
            icon=service_data["icon"],
            order=order,
        )
        for o_idx, outcome in enumerate(service_data["outcomes"]):
            ServiceOutcome.objects.create(
                service=service, text=outcome, order=o_idx
            )

    faq_categories = [
        {
            "title": "Our Capabilities & Approach",
            "items": [
                "What industries does Codeteki support?",
                "Do you replace teams with AI?",
                "Can you work with our in-house developers?",
                "How custom are the solutions?",
                "Where is the team located?",
            ],
            "answers": [
                "We work with professional services, finance, healthcare, government, and high-growth startups who need secure, explainable automation.",
                "We augment your existing teams. Every deployment includes training, guardrails, and tailored workflows so people stay in control.",
                "Absolutely. We embed with product, data, and IT stakeholders to co-design architecture and share implementation playbooks.",
                "Every engagement is bespoke. We reuse hardened accelerators but deliver a solution that fits your processes, compliance, and tech stack.",
                "The core team sits in Melbourne with satellite collaborators across Australia for timezone-aligned delivery.",
            ],
        },
        {
            "title": "Implementation & Timeline",
            "items": [
                "How fast can we go live?",
                "What does onboarding look like?",
                "Can you integrate with legacy systems?",
                "Do you offer training?",
            ],
            "answers": [
                "Discovery to pilot typically takes 3–4 weeks. Production rollouts follow in 6–10 weeks depending on integrations and change management.",
                "We run collaborative workshops, map workflows, define measurable outcomes, and deliver a detailed implementation plan.",
                "Yes. Our engineers have integrated with ERP, CRM, document management, and bespoke line-of-business systems.",
                "Every delivery includes live enablement, recorded walkthroughs, and quick-start guides tailored to each team.",
            ],
        },
        {
            "title": "Technical Integration",
            "items": [
                "Which AI models do you support?",
                "How is data secured?",
                "Do you offer SLAs?",
                "Can we host on-premises?",
            ],
            "answers": [
                "We are model-agnostic. Deployments can use OpenAI, Anthropic, local LLMs, or your preferred vendor with multi-tenant isolation.",
                "Data remains within your cloud boundary. We configure encryption in transit/at rest, role-based access, and logging that meets SOC2/ISO requirements.",
                "Yes. Production systems include response SLAs plus proactive monitoring dashboards handed over to your team.",
                "We support on-prem, private cloud, and hybrid deployments with Kubernetes, Docker, or serverless primitives.",
            ],
        },
        {
            "title": "Support & Training",
            "items": [
                "Do you stay engaged after launch?",
                "How do you handle feature requests?",
                "Can you train new team members?",
                "Is documentation included?",
            ],
            "answers": [
                "We offer managed services, retainer-based improvements, and quarterly roadmap reviews.",
                "Requests enter a transparent backlog. You get a delivery plan with impact scoring so stakeholders can prioritise.",
                "Yes, we provide refreshers, new-hire bootcamps, and helpdesk-style office hours.",
                "Every engagement ships with architecture diagrams, SOPs, and runbooks hosted in your knowledge base.",
            ],
        },
        {
            "title": "Getting Started",
            "items": [
                "What is the first step?",
                "How do you price projects?",
                "Can we start with a pilot?",
                "Do you work with startups?",
            ],
            "answers": [
                "Book a consultation. We align on objectives, data readiness, and a success plan before any build kicks off.",
                "Fixed-price discovery, milestone-based delivery, or retainers for rapid support. Every quote is transparent and scoped to outcomes.",
                "Yes. Many clients start with a single workflow pilot to capture ROI data before scaling.",
                "We partner with funded startups that need enterprise-grade craftsmanship without spinning up a full in-house team.",
            ],
        },
    ]

    for order, category in enumerate(faq_categories):
        cat = FAQCategory.objects.create(title=category["title"], order=order)
        for idx, question in enumerate(category["items"]):
            FAQItem.objects.create(
                category=cat,
                question=question,
                answer=category["answers"][idx],
                order=idx,
            )

    contacts = [
        {
            "title": "General Inquiries",
            "description": "Have a new idea or project? Our Melbourne HQ team will respond within one business day.",
            "value": "hello@codeteki.com.au",
            "cta_label": "Send an Email",
            "icon": "Mail",
        },
        {
            "title": "Support Team",
            "description": "Active client with a question? Reach the dedicated codeteki.help desk.",
            "value": "support@codeteki.com.au",
            "cta_label": "Open Support Ticket",
            "icon": "LifeBuoy",
        },
        {
            "title": "Call Us",
            "description": "Prefer to talk? Book a call and speak directly with our solution engineers.",
            "value": "+61 469 754 386",
            "cta_label": "Schedule a Call",
            "icon": "Phone",
        },
    ]

    for order, method in enumerate(contacts):
        ContactMethod.objects.create(order=order, **method)

    if SiteSettings is not None and not SiteSettings.objects.exists():
        SiteSettings.objects.create(
            site_name="Codeteki Digital Services",
            site_tagline="AI-Powered Business Solutions",
            site_description="AI-powered business solutions that reimagine operations with automation, copilots, and integrated tooling.",
            primary_email="hello@codeteki.com.au",
            secondary_email="support@codeteki.com.au",
            primary_phone="+61 469 754 386",
            secondary_phone="+61 424 538 777",
            address="Melbourne, Victoria, Australia",
        )


def remove_content(apps, schema_editor):
    apps.get_model("core", "HeroSection").objects.all().delete()
    apps.get_model("core", "BusinessImpactSection").objects.all().delete()
    apps.get_model("core", "Service").objects.all().delete()
    apps.get_model("core", "FAQCategory").objects.all().delete()
    apps.get_model("core", "ContactMethod").objects.all().delete()
    try:
        apps.get_model("core", "SiteSettings").objects.filter(
            site_name="Codeteki Digital Services",
            primary_email="hello@codeteki.com.au",
            primary_phone="+61 469 754 386",
        ).delete()
    except LookupError:
        pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_content, remove_content),
    ]
