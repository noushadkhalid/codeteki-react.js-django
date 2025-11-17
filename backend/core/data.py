"""
Static data used by Codeteki marketing pages.

These structures mirror the sections documented in CODETEKI_WEBSITE_COMPLETE_GUIDE.md
so the React frontend can stay light and simply render whatever the API sends back.
"""

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
        "orange": "#ff6b35",
        "blue": "#3B82F6",
        "green": "#10B981",
        "purple": "#8B5CF6",
    },
    "fonts": {"primary": "Inter"},
}

SERVICES = [
    {
        "id": "ai-workforce",
        "title": "AI Workforce Solutions",
        "description": "Deploy domain-trained AI agents that collaborate with your team, manage workflows, and eliminate repetitive busy work.",
        "badge": "Enterprise Ready",
        "icon": "Bot",
        "outcomes": [
            "Human-in-the-loop guardrails",
            "Secure knowledge base integrations",
            "Realtime analytics + alerts",
        ],
    },
    {
        "id": "custom-tools",
        "title": "Custom Tool Development",
        "description": "Design and ship bespoke internal tools, portals, and dashboards that plug straight into your existing ecosystem.",
        "badge": "Tailored Builds",
        "icon": "Wrench",
        "outcomes": [
            "Pixel-perfect UI/UX",
            "First-party API integrations",
            "Ongoing roadmap partnership",
        ],
    },
    {
        "id": "automation",
        "title": "Business Automation Tools",
        "description": "Automate approvals, reporting, compliance, and daily operations with orchestrated workflows across your stack.",
        "badge": "Process Automation",
        "icon": "Zap",
        "outcomes": [
            "Unified task orchestration",
            "Codeteki governance layer",
            "Return on investment reporting",
        ],
    },
    {
        "id": "daily-ai",
        "title": "AI Tools for Daily Tasks",
        "description": "Personalized copilots for sales, support, HR, and finance that meet your policies and tone of voice from day one.",
        "badge": "Personal Copilots",
        "icon": "Repeat",
        "outcomes": [
            "Secure workspace libraries",
            "Role-based access + auditing",
            "No more context switching",
        ],
    },
    {
        "id": "mcp-integration",
        "title": "MCP Integration Services",
        "description": "Connect the Model Context Protocol to your proprietary knowledge bases and tooling to unlock trustworthy automation.",
        "badge": "MCP Experts",
        "icon": "Cable",
        "outcomes": [
            "Source-of-truth syncing",
            "Guardrailed data pipelines",
            "Observability dashboards",
        ],
    },
    {
        "id": "web-dev",
        "title": "Professional Web Development",
        "description": "Full-stack product teams that deliver marketing sites, customer portals, and high-performance web apps.",
        "badge": "Full Stack",
        "icon": "Code",
        "outcomes": [
            "React + Django specialists",
            "Accessibility-grade builds",
            "Training + documentation",
        ],
    },
]

FAQ_CATEGORIES = [
    {
        "title": "Our Capabilities & Approach",
        "items": [
            {
                "question": "What industries does Codeteki support?",
                "answer": "We work with professional services, finance, healthcare, government, and high-growth startups who need secure, explainable automation.",
            },
            {
                "question": "Do you replace teams with AI?",
                "answer": "We augment your existing teams. Every deployment includes training, guardrails, and tailored workflows so people stay in control.",
            },
            {
                "question": "Can you work with our in-house developers?",
                "answer": "Absolutely. We embed with product, data, and IT stakeholders to co-design architecture and share implementation playbooks.",
            },
            {
                "question": "How custom are the solutions?",
                "answer": "Every engagement is bespoke. We reuse hardened accelerators but deliver a solution that fits your processes, compliance, and tech stack.",
            },
            {
                "question": "Where is the team located?",
                "answer": "The core team sits in Melbourne with satellite collaborators across Australia for timezone-aligned delivery.",
            },
        ],
    },
    {
        "title": "Implementation & Timeline",
        "items": [
            {
                "question": "How fast can we go live?",
                "answer": "Discovery to pilot typically takes 3–4 weeks. Production rollouts follow in 6–10 weeks depending on integrations and change management.",
            },
            {
                "question": "What does onboarding look like?",
                "answer": "We run collaborative workshops, map workflows, define measurable outcomes, and deliver a detailed implementation plan.",
            },
            {
                "question": "Can you integrate with legacy systems?",
                "answer": "Yes. Our engineers have integrated with ERP, CRM, document management, and bespoke line-of-business systems.",
            },
            {
                "question": "Do you offer training?",
                "answer": "Every delivery includes live enablement, recorded walkthroughs, and quick-start guides tailored to each team.",
            },
        ],
    },
    {
        "title": "Technical Integration",
        "items": [
            {
                "question": "Which AI models do you support?",
                "answer": "We are model-agnostic. Deployments can use OpenAI, Anthropic, local LLMs, or your preferred vendor with multi-tenant isolation.",
            },
            {
                "question": "How is data secured?",
                "answer": "Data remains within your cloud boundary. We configure encryption in transit/at rest, role-based access, and logging that meets SOC2/ISO requirements.",
            },
            {
                "question": "Do you offer SLAs?",
                "answer": "Yes. Production systems include response SLAs plus proactive monitoring dashboards handed over to your team.",
            },
            {
                "question": "Can we host on-premises?",
                "answer": "We support on-prem, private cloud, and hybrid deployments with Kubernetes, Docker, or serverless primitives.",
            },
        ],
    },
    {
        "title": "Support & Training",
        "items": [
            {
                "question": "Do you stay engaged after launch?",
                "answer": "We offer managed services, retainer-based improvements, and quarterly roadmap reviews.",
            },
            {
                "question": "How do you handle feature requests?",
                "answer": "Requests enter a transparent backlog. You get a delivery plan with impact scoring so stakeholders can prioritise.",
            },
            {
                "question": "Can you train new team members?",
                "answer": "Yes, we provide refreshers, new-hire bootcamps, and helpdesk-style office hours.",
            },
            {
                "question": "Is documentation included?",
                "answer": "Every engagement ships with architecture diagrams, SOPs, and runbooks hosted in your knowledge base.",
            },
        ],
    },
    {
        "title": "Getting Started",
        "items": [
            {
                "question": "What is the first step?",
                "answer": "Book a consultation. We align on objectives, data readiness, and a success plan before any build kicks off.",
            },
            {
                "question": "How do you price projects?",
                "answer": "Fixed-price discovery, milestone-based delivery, or retainers for rapid support. Every quote is transparent and scoped to outcomes.",
            },
            {
                "question": "Can we start with a pilot?",
                "answer": "Yes. Many clients start with a single workflow pilot to capture ROI data before scaling.",
            },
            {
                "question": "Do you work with startups?",
                "answer": "We partner with funded startups that need enterprise-grade craftsmanship without spinning up a full in-house team.",
            },
        ],
    },
]

CONTACT_METHODS = [
    {
        "title": "General Inquiries",
        "description": "Have a new idea or project? Our Melbourne HQ team will respond within one business day.",
        "value": "hello@codeteki.com.au",
        "cta": "Send an Email",
        "icon": "Mail",
    },
    {
        "title": "Support Team",
        "description": "Active client with a question? Reach the dedicated codeteki.help desk.",
        "value": "support@codeteki.com.au",
        "cta": "Open Support Ticket",
        "icon": "LifeBuoy",
    },
    {
        "title": "Call Us",
        "description": "Prefer to talk? Book a call and speak directly with our solution engineers.",
        "value": "+61 3 7019 1234",
        "cta": "Schedule a Call",
        "icon": "Phone",
    },
]

HERO_STATS = {
    "badge": "🚀 AI-Powered Business Solutions",
    "title": "Transform Your Business with AI-Powered Solutions",
    "highlighted": "AI-Powered",
    "description": "At Codeteki, we reimagine operations with human-centred automation, measurable ROI, and production-ready AI copilots.",
    "primaryCta": {"label": "Talk to Us Today", "href": "/contact"},
    "secondaryCta": {"label": "View Our Services", "href": "/services"},
    "metrics": [
        {"label": "Avg. ROI", "value": "210%"},
        {"label": "Delivery Speed", "value": "6 Weeks"},
        {"label": "Client NPS", "value": "72"},
    ],
    "subheading": "Melbourne-based AI engineering & enablement partner",
    "image": "https://codeteki.au/assets/image_1750241082304-CG0Qm923.png",
    "logos": [
        {
            "name": "Desifirms AI",
            "logo": "https://codeteki.au/assets/logo_codeteki1_1750313736817-CyvEyPyd.png",
        },
        {
            "name": "Melbourne Partners",
            "logo": "https://codeteki.au/favicon.png",
        },
    ],
    "floatingBadge": {
        "title": "Desifirms AI Tools",
        "subtitle": "Mirror deployments from Desifirms in one click.",
        "logo": "https://codeteki.au/assets/logo_codeteki1_1750313736817-CyvEyPyd.png",
    },
}

BUSINESS_IMPACT = {
    "title": "Real Business Impact",
    "description": "Our AI-powered solutions deliver concrete business outcomes that transform how your business operates.",
    "metrics": [
        {
            "value": "10x",
            "label": "Customer Inquiries Handled",
            "caption": "Tier-one AI concierges triage, resolve, and escalate without wait times.",
            "icon": "MessageCircle",
            "theme": {"bg": "bg-blue-100", "text": "text-blue-600"},
        },
        {
            "value": "24/7",
            "label": "Operation Capability",
            "caption": "Always-on virtual teams keep sales, support, and ops humming.",
            "icon": "Timer",
            "theme": {"bg": "bg-green-100", "text": "text-green-600"},
        },
        {
            "value": "60%",
            "label": "Cost Reduction",
            "caption": "Automate repetitive workflows and reinvest savings in growth.",
            "icon": "TrendingDown",
            "theme": {"bg": "bg-yellow-100", "text": "text-yellow-600"},
        },
        {
            "value": "<2s",
            "label": "Response Time",
            "caption": "Realtime answers powered by contextual knowledge bases.",
            "icon": "Zap",
            "theme": {"bg": "bg-purple-100", "text": "text-purple-600"},
        },
    ],
    "cta": {"label": "Calculate Your ROI", "href": "/contact"},
    "logos": [
        {
            "name": "Codeteki Digital",
            "logo": "https://codeteki.au/assets/logo_codeteki1_1750313736817-CyvEyPyd.png",
        },
        {"name": "Desifirms AI", "logo": "https://codeteki.au/favicon.png"},
    ],
}
