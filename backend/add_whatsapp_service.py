"""
Add WhatsApp AI Automation service to Codeteki services page.
Run with: python manage.py shell < add_whatsapp_service.py
"""
from core.models import Service, ServiceOutcome, ServiceFeature, ServiceCapability, ServiceBenefit, ServiceProcess

SLUG = 'whatsapp-ai-automation'

# Check if already exists
if Service.objects.filter(slug=SLUG).exists():
    print(f"Service '{SLUG}' already exists. Deleting and recreating...")
    Service.objects.filter(slug=SLUG).delete()

# Create the service
service = Service.objects.create(
    title="WhatsApp AI Automation",
    slug=SLUG,
    badge="AI Messaging",
    description="Turn WhatsApp into your smartest sales channel. Our AI agents qualify leads, answer questions, and hand off to your team — 24/7, fully automated.",
    icon="MessageCircle",
    is_featured=True,
    order=2,
    tagline="AI-Powered WhatsApp",
    subtitle="Turn every WhatsApp conversation into a qualified lead with intelligent AI agents that never sleep",
    full_description=(
        "Most businesses lose leads because they can't respond fast enough. "
        "Our WhatsApp AI Automation puts an intelligent agent on your business number "
        "that instantly engages every inquiry, qualifies leads through natural conversation, "
        "and seamlessly hands off hot prospects to your team.\n\n"
        "Built on Meta's official WhatsApp Business API, your AI agent understands your business, "
        "speaks your brand voice, and guides customers through your services — from first hello "
        "to booked appointment. No more missed leads. No more after-hours silence. "
        "Just smart, always-on customer engagement that converts."
    ),
    hero_image_url="https://images.unsplash.com/photo-1611746872915-64382b5c76da?w=800",
    gradient_from="green-500",
    gradient_to="emerald-600",
)
print(f"Created service: {service.title}")

# Outcomes (shown on service cards)
outcomes = [
    "24/7 instant WhatsApp response to every inquiry",
    "AI-powered lead qualification and scoring",
    "Seamless human handoff when prospects are ready",
    "Full CRM integration with conversation history",
]
for i, text in enumerate(outcomes):
    ServiceOutcome.objects.create(service=service, text=text, order=i)
print(f"  Added {len(outcomes)} outcomes")

# Features (detail page grid)
features = [
    "AI auto-responder trained on your business",
    "Smart lead qualification through conversation",
    "Automatic contact creation and CRM sync",
    "Real-time owner notifications (SMS + Email)",
    "Human handoff with full conversation context",
    "WhatsApp inbox for team replies",
    "Conversation analytics and lead scoring",
    "Multi-language support",
    "Clickable action buttons (book, register, browse)",
    "Opt-out handling and compliance built-in",
    "Deal pipeline auto-creation and tracking",
    "Custom AI personality matching your brand voice",
]
for i, text in enumerate(features):
    ServiceFeature.objects.create(service=service, text=text, order=i)
print(f"  Added {len(features)} features")

# Capabilities (cards with icons)
capabilities = [
    {
        "icon": "Bot",
        "title": "AI Conversation Agent",
        "description": "Domain-trained AI that understands your business, answers questions naturally, and guides customers to take action — register, book, or buy.",
    },
    {
        "icon": "UserCheck",
        "title": "Smart Lead Qualification",
        "description": "Automatically classifies visitors as prospects, existing customers, or browsers. Scores engagement and routes hot leads to your team instantly.",
    },
    {
        "icon": "ArrowRightLeft",
        "title": "Seamless Human Handoff",
        "description": "When a customer needs personal attention, the AI smoothly transfers to your team with full conversation context. You get notified via SMS and email.",
    },
    {
        "icon": "BarChart3",
        "title": "CRM Pipeline Integration",
        "description": "Every WhatsApp conversation automatically creates contacts, deals, and activity logs in your CRM. No manual data entry, no lost leads.",
    },
    {
        "icon": "Zap",
        "title": "Instant Response, Always On",
        "description": "Respond to customer inquiries in seconds, not hours. Your AI agent works 24/7 including weekends and holidays — never misses a lead.",
    },
    {
        "icon": "Shield",
        "title": "Meta-Compliant & Secure",
        "description": "Built on Meta's official WhatsApp Business Cloud API. Full opt-out compliance, data privacy, and transparent AI disclosure built in.",
    },
]
for i, cap in enumerate(capabilities):
    ServiceCapability.objects.create(
        service=service, icon=cap["icon"], title=cap["title"],
        description=cap["description"], order=i,
    )
print(f"  Added {len(capabilities)} capabilities")

# Benefits
benefits = [
    "Capture leads you're currently losing to slow response times",
    "Reduce customer support workload by 60-80%",
    "Qualify prospects before they reach your sales team",
    "Convert after-hours inquiries into booked appointments",
    "Build a complete customer database automatically",
    "Scale customer engagement without hiring more staff",
    "Get real-time notifications for high-intent prospects",
    "Track every conversation from first touch to conversion",
]
for i, text in enumerate(benefits):
    ServiceBenefit.objects.create(service=service, text=text, order=i)
print(f"  Added {len(benefits)} benefits")

# Process steps
process_steps = [
    {
        "step": 1,
        "title": "Discovery & Setup",
        "description": "We learn your business, services, and customer journey. Set up your WhatsApp Business account and configure the AI with your brand knowledge.",
    },
    {
        "step": 2,
        "title": "AI Training",
        "description": "Train your AI agent on your FAQs, pricing, services, and conversation style. Fine-tune responses until they match your brand voice perfectly.",
    },
    {
        "step": 3,
        "title": "CRM Integration",
        "description": "Connect to your CRM pipeline. Configure lead scoring, deal creation, owner notifications, and human handoff workflows.",
    },
    {
        "step": 4,
        "title": "Launch & Optimise",
        "description": "Go live with your AI agent. Monitor conversations, refine responses, and continuously improve lead qualification based on real data.",
    },
]
for ps in process_steps:
    ServiceProcess.objects.create(
        service=service, step=ps["step"], title=ps["title"],
        description=ps["description"],
    )
print(f"  Added {len(process_steps)} process steps")

print(f"\nDone! Service live at: https://codeteki.au/services/{SLUG}")
