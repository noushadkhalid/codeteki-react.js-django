"""
Management command to populate AI Tools from the frontend fallback data.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from core.models import AIToolsSection, AITool


REMOTE_URL = "https://www.desifirms.com.au/ai-tools"

AI_TOOLS_DATA = [
    {
        "title": "Australian Trip Planner",
        "description": "Discover curated itineraries, verified attractions, and travel tips for every Australian city.",
        "emoji": "compass",
        "status": "free",
        "category": "lifestyle",
        "external_url": f"{REMOTE_URL}/australian-trip-planner",
    },
    {
        "title": "Baby Growth Tracker",
        "description": "Track milestones, immunisation schedules, and growth charts aligned with Australian health data.",
        "emoji": "child_care",
        "status": "free",
        "category": "health",
        "external_url": f"{REMOTE_URL}/baby-growth-tracker",
    },
    {
        "title": "Pregnancy Due Date Calculator",
        "description": "Plan trimester visits and due dates using conception or cycle data.",
        "emoji": "pregnant_woman",
        "status": "free",
        "category": "health",
        "external_url": f"{REMOTE_URL}/pregnancy-due-date",
    },
    {
        "title": "Water Intake Calculator",
        "description": "Daily hydration goals tuned for local climate and lifestyle.",
        "emoji": "water_drop",
        "status": "free",
        "category": "health",
        "external_url": f"{REMOTE_URL}/water-intake-calculator",
    },
    {
        "title": "Body Fat Percentage Calculator",
        "description": "Estimate body fat using multiple measurement formulas and guidance.",
        "emoji": "monitoring",
        "status": "free",
        "category": "health",
        "external_url": f"{REMOTE_URL}/body-fat-percentage",
    },
    {
        "title": "Calorie Calculator",
        "description": "Get personalised calorie targets for weight gain, maintenance, or loss.",
        "emoji": "nutrition",
        "status": "free",
        "category": "health",
        "external_url": f"{REMOTE_URL}/calorie-calculator",
    },
    {
        "title": "BMI Calculator",
        "description": "BMI with imperial/metric inputs and health categories.",
        "emoji": "scale",
        "status": "free",
        "category": "health",
        "external_url": f"{REMOTE_URL}/bmi-calculator",
    },
    {
        "title": "Mid-Market Exchange Rate Tool",
        "description": "Live rates and fee guidance for sending money overseas.",
        "emoji": "currency_exchange",
        "status": "free",
        "category": "finance",
        "external_url": f"{REMOTE_URL}/exchange-rate-tool",
    },
    {
        "title": "Gift Ideas Generator",
        "description": "Culture-aware gift suggestions for every occasion and relationship.",
        "emoji": "redeem",
        "status": "credits",
        "min_credits": 15,
        "category": "lifestyle",
        "external_url": f"{REMOTE_URL}/gift-ideas-generator",
    },
    {
        "title": "Smart Invoice Builder",
        "description": "AI-powered invoices with summaries, PDF export, and compliance checks.",
        "emoji": "receipt_long",
        "status": "credits",
        "min_credits": 20,
        "category": "business",
        "external_url": f"{REMOTE_URL}/invoice-builder",
    },
    {
        "title": "Product Description Generator",
        "description": "Create bilingual descriptions for marketplaces and catalogues.",
        "emoji": "inventory",
        "status": "credits",
        "min_credits": 18,
        "category": "business",
        "external_url": f"{REMOTE_URL}/product-description-generator",
    },
    {
        "title": "Desi Party Food Planner",
        "description": "Plan perfect South Asian food quantities for weddings and parties.",
        "emoji": "restaurant",
        "status": "premium",
        "credit_cost": 75,
        "category": "lifestyle",
        "external_url": f"{REMOTE_URL}/desi-food-planner",
        "preview_url": f"{REMOTE_URL}/desi-food-planner",
    },
    {
        "title": "Desi Diet & Weight Management",
        "description": "Diet plans with Desi ingredient swaps and weekly shopping lists.",
        "emoji": "restaurant_menu",
        "status": "premium",
        "credit_cost": 65,
        "category": "health",
        "external_url": f"{REMOTE_URL}/diet-planner",
        "preview_url": f"{REMOTE_URL}/diet-planner",
    },
    {
        "title": "Visa Immigration Assistant",
        "description": "Analyse visa options and pathways with personalised scoring.",
        "emoji": "flight_takeoff",
        "status": "premium",
        "credit_cost": 40,
        "category": "immigration",
        "external_url": f"{REMOTE_URL}/visa-guidance",
        "preview_url": f"{REMOTE_URL}/visa-guidance",
    },
    {
        "title": "Property Development Planner",
        "description": "See what you can build based on zoning law, setbacks, and council data.",
        "emoji": "construction",
        "status": "premium",
        "credit_cost": 90,
        "category": "property",
        "external_url": f"{REMOTE_URL}/property-development-planner",
        "preview_url": f"{REMOTE_URL}/property-development-planner",
    },
    {
        "title": "Investment Property Analyzer",
        "description": "Detailed feasibility reports that combine council data with AI recommendations.",
        "emoji": "real_estate_agent",
        "status": "premium",
        "credit_cost": 70,
        "category": "property",
        "external_url": f"{REMOTE_URL}/investment-property-analyzer",
        "preview_url": f"{REMOTE_URL}/investment-property-analyzer",
        "is_coming_soon": True,
    },
    {
        "title": "Jet Lag Recovery Planner",
        "description": "Personalised routines that adapt to your itinerary, hydration, and sleep data.",
        "emoji": "flight",
        "status": "premium",
        "credit_cost": 50,
        "category": "lifestyle",
        "external_url": f"{REMOTE_URL}/jet-lag-recovery-planner",
        "preview_url": f"{REMOTE_URL}/jet-lag-recovery-planner",
        "is_coming_soon": True,
    },
    {
        "title": "Business Ideas Generator",
        "description": "Category-aware ideas for service businesses, retail concepts, and franchises.",
        "emoji": "lightbulb",
        "status": "credits",
        "min_credits": 25,
        "category": "business",
        "external_url": f"{REMOTE_URL}/business-ideas-generator",
        "is_coming_soon": True,
    },
    {
        "title": "Unified PDF Editor",
        "description": "Merge, annotate, translate, and sign documents with Desi-focused templates.",
        "emoji": "picture_as_pdf",
        "status": "credits",
        "min_credits": 22,
        "category": "business",
        "external_url": f"{REMOTE_URL}/unified-pdf-editor",
        "is_coming_soon": True,
    },
]


class Command(BaseCommand):
    help = "Populate AI Tools section and tools from frontend fallback data"

    def handle(self, *args, **options):
        # Create or get the AI Tools Section
        section, created = AIToolsSection.objects.get_or_create(
            pk=1,
            defaults={
                "badge": "Built by Codeteki - Hosted on DesiFirms",
                "title": "Explore the production-ready AI tools we already operate",
                "description": "All Codeteki utilities are deployed on DesiFirms.com.au for the Australian market. This page connects you directly to the live tools - no mock-ups, no future promises.",
                "is_active": True,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS("Created AI Tools Section"))
        else:
            self.stdout.write(self.style.WARNING("AI Tools Section already exists"))

        # Create tools
        tools_created = 0
        tools_updated = 0

        for idx, tool_data in enumerate(AI_TOOLS_DATA):
            slug = slugify(tool_data["title"])

            tool, created = AITool.objects.update_or_create(
                slug=slug,
                defaults={
                    "section": section,
                    "title": tool_data["title"],
                    "description": tool_data["description"],
                    "icon": tool_data.get("emoji", "smart_toy"),
                    "status": tool_data.get("status", "free"),
                    "category": tool_data.get("category", "general"),
                    "external_url": tool_data.get("external_url", ""),
                    "preview_url": tool_data.get("preview_url", ""),
                    "min_credits": tool_data.get("min_credits", 0),
                    "credit_cost": tool_data.get("credit_cost", 0),
                    "is_coming_soon": tool_data.get("is_coming_soon", False),
                    "is_active": True,
                    "order": idx,
                }
            )

            if created:
                tools_created += 1
            else:
                tools_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Created {tools_created} tools, updated {tools_updated} tools."
            )
        )
