import json

from django.contrib import admin, messages
from django.utils.html import format_html

from .models import (
    AITool,
    AIToolsSection,
    AISEORecommendation,
    BlogPost,
    BusinessImpactLogo,
    BusinessImpactMetric,
    BusinessImpactSection,
    ChatConversation,
    ChatLead,
    ChatMessage,
    ChatbotSettings,
    ContactMethod,
    ContactInquiry,
    CTASection,
    DemoImage,
    DemoShowcase,
    FAQCategory,
    FAQItem,
    FooterLink,
    FooterSection,
    HeroMetric,
    HeroPartnerLogo,
    HeroSection,
    KnowledgeArticle,
    KnowledgeCategory,
    KnowledgeFAQ,
    NavigationItem,
    NavigationMenu,
    PageSEO,
    PricingFeature,
    PricingPlan,
    ROICalculatorSection,
    ROICalculatorStat,
    ROICalculatorTool,
    SEODataUpload,
    SEOKeyword,
    SEOKeywordCluster,
    Service,
    ServiceProcessStep,
    ServiceOutcome,
    SiteSettings,
    StatMetric,
    Testimonial,
    WhyChooseReason,
    WhyChooseSection,
)


class HeroMetricInline(admin.TabularInline):
    model = HeroMetric
    extra = 0


class HeroPartnerInline(admin.TabularInline):
    model = HeroPartnerLogo
    extra = 0


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "badge", "is_active", "updated_at")
    list_filter = ("is_active",)
    inlines = [HeroMetricInline, HeroPartnerInline]


class ServiceOutcomeInline(admin.TabularInline):
    model = ServiceOutcome
    extra = 0


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "badge", "icon", "order")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ServiceOutcomeInline]
    ordering = ("order",)


@admin.register(ServiceProcessStep)
class ServiceProcessStepAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "accent", "order")
    ordering = ("order",)


class FAQItemInline(admin.TabularInline):
    model = FAQItem
    extra = 0


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    ordering = ("order",)
    inlines = [FAQItemInline]


class ImpactMetricInline(admin.TabularInline):
    model = BusinessImpactMetric
    extra = 0


class ImpactLogoInline(admin.TabularInline):
    model = BusinessImpactLogo
    extra = 0


@admin.register(BusinessImpactSection)
class BusinessImpactAdmin(admin.ModelAdmin):
    list_display = ("title", "updated_at")
    inlines = [ImpactMetricInline, ImpactLogoInline]


@admin.register(ContactMethod)
class ContactMethodAdmin(admin.ModelAdmin):
    list_display = ("title", "value", "icon", "order")
    ordering = ("order",)


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service", "status", "created_at")
    list_filter = ("status", "service")
    search_fields = ("name", "email", "message")
    ordering = ("-created_at",)


# ROI Calculator Section
class ROICalculatorStatInline(admin.TabularInline):
    model = ROICalculatorStat
    extra = 0


class ROICalculatorToolInline(admin.TabularInline):
    model = ROICalculatorTool
    extra = 0


@admin.register(ROICalculatorSection)
class ROICalculatorSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "badge", "is_active", "updated_at")
    list_filter = ("is_active",)
    inlines = [ROICalculatorStatInline, ROICalculatorToolInline]


# AI Tools Section
class AIToolInline(admin.TabularInline):
    model = AITool
    extra = 0
    prepopulated_fields = {"slug": ("title",)}


@admin.register(AIToolsSection)
class AIToolsSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "badge", "is_active", "updated_at")
    list_filter = ("is_active",)
    inlines = [AIToolInline]


@admin.register(AITool)
class AIToolAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "category", "is_coming_soon", "is_active", "order")
    list_filter = ("status", "category", "is_active", "is_coming_soon")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order",)
    fieldsets = (
        (None, {"fields": ("section", "title", "slug", "description", "is_active", "order")}),
        ("Visuals", {"fields": ("icon", "emoji", "color", "badge")}),
        ("Categorisation", {"fields": ("category", "status", "is_coming_soon")}),
        ("Credits & Pricing", {"fields": ("min_credits", "credit_cost")}),
        ("Links & CTA", {"fields": ("external_url", "preview_url", "cta_label", "cta_url", "secondary_cta_label", "secondary_cta_url")}),
    )


# Why Choose Section
class WhyChooseReasonInline(admin.TabularInline):
    model = WhyChooseReason
    extra = 0


@admin.register(WhyChooseSection)
class WhyChooseSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "badge", "is_active", "updated_at")
    list_filter = ("is_active",)
    inlines = [WhyChooseReasonInline]


# Footer Section
class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 0


@admin.register(FooterSection)
class FooterSectionAdmin(admin.ModelAdmin):
    list_display = ("company_name", "abn", "updated_at")
    inlines = [FooterLinkInline]


# Site Settings
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "site_tagline", "primary_email", "updated_at")
    fieldsets = (
        ("Site Information", {
            "fields": ("site_name", "site_tagline", "site_description")
        }),
        ("Logos & Branding", {
            "fields": ("logo", "logo_dark", "favicon")
        }),
        ("Contact Information", {
            "fields": ("primary_email", "secondary_email", "primary_phone", "secondary_phone", "address")
        }),
        ("Support & SLAs", {
            "fields": (
                "support_badge",
                "support_response_value",
                "support_response_label",
                "support_response_helper",
                "support_response_message",
                "support_response_confirmation",
            )
        }),
        ("Social Media", {
            "fields": ("facebook", "twitter", "linkedin", "instagram", "youtube", "github")
        }),
        ("Business Information", {
            "fields": ("abn", "business_hours")
        }),
        ("Analytics", {
            "fields": ("google_analytics_id", "facebook_pixel_id")
        }),
    )

    def has_add_permission(self, request):
        # Only allow one SiteSettings instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of site settings
        return False


# Page SEO
@admin.register(PageSEO)
class PageSEOAdmin(admin.ModelAdmin):
    list_display = ("page", "meta_title", "updated_at")
    list_filter = ("page",)
    fieldsets = (
        ("Page Selection", {
            "fields": ("page",)
        }),
        ("Meta Tags", {
            "fields": ("meta_title", "meta_description", "meta_keywords", "canonical_url")
        }),
        ("Open Graph", {
            "fields": ("og_title", "og_description", "og_image")
        }),
    )


# Testimonials
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "rating", "is_featured", "is_active", "order")
    list_filter = ("is_featured", "is_active", "rating")
    ordering = ("-is_featured", "order")


# CTA Sections
@admin.register(CTASection)
class CTASectionAdmin(admin.ModelAdmin):
    list_display = ("title", "placement", "is_active", "order")
    list_filter = ("placement", "is_active")
    ordering = ("placement", "order")


# Demo Showcase
class DemoImageInline(admin.TabularInline):
    model = DemoImage
    extra = 0


@admin.register(DemoShowcase)
class DemoShowcaseAdmin(admin.ModelAdmin):
    list_display = ("title", "industry", "status", "is_featured", "is_active", "order")
    list_filter = ("status", "is_featured", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-is_featured", "order")
    inlines = [DemoImageInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "industry", "status", "is_featured", "is_active", "order")}),
        ("Visuals", {"fields": ("icon", "color_class", "highlight_badge", "thumbnail", "screenshot")}),
        ("Content", {"fields": ("short_description", "full_description", "features", "feature_count")}),
        ("Links", {"fields": ("demo_url", "video_url")}),
        ("Client Details", {"fields": ("client_name", "client_logo", "technologies_used", "completion_date")}),
    )


# Pricing Plans
class PricingFeatureInline(admin.TabularInline):
    model = PricingFeature
    extra = 0


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "currency", "billing_period", "is_popular", "is_active", "order")
    list_filter = ("is_popular", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order",)
    inlines = [PricingFeatureInline]


# Statistics
@admin.register(StatMetric)
class StatMetricAdmin(admin.ModelAdmin):
    list_display = ("value", "label", "section", "is_active", "order")
    list_filter = ("section", "is_active")
    ordering = ("section", "order")


# Navigation
class NavigationItemInline(admin.TabularInline):
    model = NavigationItem
    extra = 0


@admin.register(NavigationMenu)
class NavigationMenuAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "is_active", "updated_at")
    list_filter = ("location", "is_active")
    inlines = [NavigationItemInline]


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ("title", "menu", "parent", "is_active", "order")
    list_filter = ("menu", "is_active")
    ordering = ("menu", "order")


# Blog Posts
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "is_published", "is_featured", "published_at", "views_count")
    list_filter = ("is_published", "is_featured", "category")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-published_at",)
    search_fields = ("title", "excerpt", "content")


@admin.register(SEODataUpload)
class SEODataUploadAdmin(admin.ModelAdmin):
    list_display = ("name", "source", "status", "row_count", "processed_at", "last_ai_run_at")
    list_filter = ("status", "source")
    readonly_fields = ("status", "row_count", "processed_at", "last_ai_run_at", "insights_pretty")
    search_fields = ("name",)
    actions = ["process_uploads", "generate_ai_playbooks", "generate_blog_drafts"]
    fieldsets = (
        (None, {"fields": ("name", "source", "csv_file", "notes")}),
        ("Automation", {"fields": ("status", "row_count", "processed_at", "last_ai_run_at", "insights_pretty")}),
    )

    def insights_pretty(self, obj):
        if not obj or not obj.insights:
            return "—"
        formatted = json.dumps(obj.insights, indent=2, ensure_ascii=False)
        return format_html(
            "<pre style='white-space: pre-wrap; max-height: 320px'>{}</pre>",
            formatted,
        )

    insights_pretty.short_description = "Insights"

    @admin.action(description="Process selected CSV uploads")
    def process_uploads(self, request, queryset):
        processed = 0
        for upload in queryset:
            try:
                upload.ingest_from_file()
            except Exception as exc:
                upload.mark_failed(str(exc))
                self.message_user(
                    request,
                    f"{upload.name} failed to process: {exc}",
                    level=messages.ERROR,
                )
            else:
                processed += 1
        if processed:
            self.message_user(
                request,
                f"Successfully processed {processed} upload(s).",
                level=messages.SUCCESS,
            )

    @admin.action(description="Generate AI playbooks for selected uploads")
    def generate_ai_playbooks(self, request, queryset):
        generated = 0
        for upload in queryset:
            try:
                result = upload.run_ai_automation(refresh=True)
            except Exception as exc:
                self.message_user(
                    request,
                    f"Unable to generate AI content for {upload.name}: {exc}",
                    level=messages.ERROR,
                )
                continue
            generated += result.get("recommendations", 0)
            if not result.get("ai_enabled"):
                self.message_user(
                    request,
                    f"AI is disabled for {upload.name}. Provide OPENAI_API_KEY to enable responses.",
                    level=messages.WARNING,
                )
        if generated:
            self.message_user(
                request,
                f"Created {generated} AI recommendation(s).",
                level=messages.SUCCESS,
            )

    @admin.action(description="Generate blog drafts from keyword clusters")
    def generate_blog_drafts(self, request, queryset):
        created = 0
        for upload in queryset:
            try:
                result = upload.generate_blog_posts()
            except Exception as exc:
                self.message_user(
                    request,
                    f"Unable to generate blogs for {upload.name}: {exc}",
                    level=messages.ERROR,
                )
                continue
            created += result.get("created", 0)
            if not result.get("ai_enabled"):
                self.message_user(
                    request,
                    f"AI is disabled for {upload.name}. Provide OPENAI_API_KEY to enable blogging.",
                    level=messages.WARNING,
                )
        if created:
            self.message_user(
                request,
                f"Created {created} blog draft(s).",
                level=messages.SUCCESS,
            )


@admin.register(SEOKeyword)
class SEOKeywordAdmin(admin.ModelAdmin):
    list_display = (
        "keyword",
        "upload",
        "intent",
        "search_volume",
        "seo_difficulty",
        "paid_difficulty",
        "priority_score",
    )
    list_filter = ("upload", "intent", "keyword_type")
    search_fields = ("keyword",)
    autocomplete_fields = ("upload", "cluster")
    readonly_fields = ("priority_score", "metadata", "created_at", "updated_at")
    ordering = ("-priority_score",)


@admin.register(SEOKeywordCluster)
class SEOKeywordClusterAdmin(admin.ModelAdmin):
    list_display = ("label", "upload", "intent", "keyword_count", "avg_volume", "priority_score")
    list_filter = ("upload", "intent")
    search_fields = ("label", "seed_keyword")
    autocomplete_fields = ("upload",)
    ordering = ("-priority_score",)
    readonly_fields = ("summary",)


@admin.register(AISEORecommendation)
class AISEORecommendationAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "upload", "cluster", "status", "ai_model", "created_at")
    list_filter = ("category", "status", "ai_model")
    search_fields = ("title", "response")
    autocomplete_fields = ("upload", "cluster", "keyword")
    readonly_fields = (
        "prompt",
        "response",
        "ai_model",
        "prompt_tokens",
        "completion_tokens",
        "metadata_pretty",
        "status",
        "error_message",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (None, {"fields": ("title", "upload", "cluster", "keyword", "category", "status", "ai_model")}),
        ("Prompt", {"fields": ("prompt",)}),
        ("Response", {"fields": ("response", "metadata_pretty", "error_message")}),
        ("Usage", {"fields": ("prompt_tokens", "completion_tokens", "created_at", "updated_at")}),
    )

    def metadata_pretty(self, obj):
        if not obj or not obj.metadata:
            return "—"
        formatted = json.dumps(obj.metadata, indent=2, ensure_ascii=False)
        return format_html("<pre style='white-space: pre-wrap'>{}</pre>", formatted)

    metadata_pretty.short_description = "Metadata"


@admin.register(ChatbotSettings)
class ChatbotSettingsAdmin(admin.ModelAdmin):
    list_display = ("name", "persona_title", "brand_voice", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "persona_title", "brand_voice", "accent_color", "hero_image")}),
        ("Messaging", {"fields": ("intro_message", "fallback_message", "lead_capture_prompt", "success_message", "quick_replies")}),
        ("Escalation", {"fields": ("escalation_threshold", "contact_email", "meeting_link")}),
    )


@admin.register(KnowledgeCategory)
class KnowledgeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "color", "order")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order",)


class KnowledgeFAQInline(admin.TabularInline):
    model = KnowledgeFAQ
    extra = 0


@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "persona", "is_featured", "published_at")
    list_filter = ("status", "persona", "category")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "content", "keywords", "tags")
    ordering = ("-published_at",)
    inlines = [KnowledgeFAQInline]
    fieldsets = (
        (None, {"fields": ("category", "title", "slug", "summary", "content", "status", "published_at", "is_featured")}),
        ("Audience & Meta", {"fields": ("persona", "keywords", "tags", "metadata")}),
        ("CTA", {"fields": ("call_to_action", "call_to_action_url")}),
        ("Media", {"fields": ("cover_image",)}),
    )


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("role", "content", "created_at", "metadata")
    can_delete = False


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ("conversation_id", "visitor_name", "visitor_email", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("conversation_id", "visitor_email", "visitor_name")
    readonly_fields = ("conversation_id", "metadata", "last_user_message", "created_at", "updated_at")
    inlines = [ChatMessageInline]


@admin.register(ChatLead)
class ChatLeadAdmin(admin.ModelAdmin):
    list_display = ("conversation", "name", "email", "company", "intent", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("name", "email", "company", "intent")
