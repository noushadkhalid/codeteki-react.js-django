from django.urls import path

from .views import (
    AIToolsContentAPIView,
    AIToolsPageAPIView,
    BlogAPIView,
    BlogDetailAPIView,
    BusinessImpactAPIView,
    ContactAPIView,
    ContactPageAPIView,
    CTASectionsAPIView,
    ChatConversationAPIView,
    ChatbotConfigAPIView,
    ChatbotMessageAPIView,
    DemosAPIView,
    DemosPageAPIView,
    FAQAPIView,
    FooterContentAPIView,
    HeroContentAPIView,
    HomePageAPIView,
    KnowledgeBaseAPIView,
    ChatbotKnowledgeAPIView,
    NavigationAPIView,
    PageSEOAPIView,
    PricingAPIView,
    ROICalculateAPIView,
    ROICalculatorContentAPIView,
    SEOAutomationInsightsAPIView,
    ServicesAPIView,
    ServiceDetailAPIView,
    ServicesPageAPIView,
    SiteSettingsAPIView,
    StatsAPIView,
    TestimonialsAPIView,
    WhyChooseContentAPIView,
)

app_name = "core"

urlpatterns = [
    # Original endpoints
    path("hero/", HeroContentAPIView.as_view(), name="hero"),
    path("services/", ServicesAPIView.as_view(), name="services"),
    path("services/<slug:slug>/", ServiceDetailAPIView.as_view(), name="service-detail"),
    path("faq/", FAQAPIView.as_view(), name="faq"),
    path("contact/", ContactAPIView.as_view(), name="contact"),
    path("impact/", BusinessImpactAPIView.as_view(), name="impact"),
    path("calculate-roi", ROICalculateAPIView.as_view(), name="calculate-roi"),

    # New section endpoints
    path("roi-calculator/", ROICalculatorContentAPIView.as_view(), name="roi-calculator"),
    path("ai-tools/", AIToolsContentAPIView.as_view(), name="ai-tools"),
    path("why-choose/", WhyChooseContentAPIView.as_view(), name="why-choose"),
    path("footer/", FooterContentAPIView.as_view(), name="footer"),

    # Global settings and SEO
    path("settings/", SiteSettingsAPIView.as_view(), name="settings"),
    path("seo/", PageSEOAPIView.as_view(), name="seo"),
    path("seo/automation/", SEOAutomationInsightsAPIView.as_view(), name="seo-automation"),
    path("knowledge-base/", KnowledgeBaseAPIView.as_view(), name="knowledge-base"),
    path("chatbot/knowledge/", ChatbotKnowledgeAPIView.as_view(), name="chatbot-knowledge"),

    # Content sections
    path("testimonials/", TestimonialsAPIView.as_view(), name="testimonials"),
    path("cta-sections/", CTASectionsAPIView.as_view(), name="cta-sections"),
    path("demos/", DemosAPIView.as_view(), name="demos"),
    path("pricing/", PricingAPIView.as_view(), name="pricing"),
    path("stats/", StatsAPIView.as_view(), name="stats"),

    # Navigation and blog
    path("navigation/", NavigationAPIView.as_view(), name="navigation"),
    path("blog/", BlogAPIView.as_view(), name="blog"),
    path("blog/<slug:slug>/", BlogDetailAPIView.as_view(), name="blog-detail"),
    # Page-level aggregated endpoints
    path("pages/home/", HomePageAPIView.as_view(), name="page-home"),
    path("pages/services/", ServicesPageAPIView.as_view(), name="page-services"),
    path("pages/ai-tools/", AIToolsPageAPIView.as_view(), name="page-ai-tools"),
    path("pages/demos/", DemosPageAPIView.as_view(), name="page-demos"),
    path("pages/contact/", ContactPageAPIView.as_view(), name="page-contact"),

    # Chatbot + conversations
    path("chatbot/config/", ChatbotConfigAPIView.as_view(), name="chatbot-config"),
    path("chatbot/conversation/", ChatConversationAPIView.as_view(), name="chatbot-conversation"),
    path("chatbot/message/", ChatbotMessageAPIView.as_view(), name="chatbot-message"),
    path("chat/", ChatbotMessageAPIView.as_view(), name="chat"),
]
