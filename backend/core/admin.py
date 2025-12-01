"""
Comprehensive Django Admin Configuration for Codeteki CMS
Organized by page sections for easy content management
Using Django Unfold for modern Tailwind-based UI
"""

import json
from django import forms
from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import Count

from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import action, display


# =============================================================================
# HIDE DEFAULT APP LIST FROM DASHBOARD
# Override the default admin site to hide the messy app list
# All navigation is done through the organized sidebar
# =============================================================================
def _get_empty_app_list(self, request, app_label=None):
    """Return empty app list to hide 'Site administration' section."""
    return []

# Patch the default admin site to hide app list
admin.site.get_app_list = lambda request, app_label=None: []

from .models import (
    # Home Page
    HeroSection, HeroMetric, HeroPartnerLogo,
    BusinessImpactSection, BusinessImpactMetric, BusinessImpactLogo,
    Testimonial,

    # Services
    Service, ServiceOutcome, ServiceProcessStep,

    # AI Tools
    AIToolsSection, AITool,

    # Demos
    DemoShowcase, DemoImage,

    # FAQ
    FAQPageSection, FAQPageStat, FAQCategory, FAQItem,

    # Contact
    ContactMethod, ContactInquiry,

    # Other Sections
    ROICalculatorSection, ROICalculatorStat, ROICalculatorTool,
    WhyChooseSection, WhyChooseReason,
    CTASection,

    # Site-wide
    SiteSettings, BusinessHours, SocialLink,
    FooterSection, FooterLink,
    NavigationMenu, NavigationItem,
    StatMetric,

    # SEO
    PageSEO,
    SEODataUpload, SEOKeyword, SEOKeywordCluster, AISEORecommendation,

    # SEO Engine
    SiteAudit, PageAudit, AuditIssue, AIAnalysisReport,
    PageSpeedResult, SearchConsoleData, SearchConsoleSync,
    KeywordRanking, CompetitorProfile, SEORecommendation,
    SEOChangeLog, ScheduledAudit, SEOChatSession, SEOChatMessage,

    # Leads & Chat
    ChatLead, ChatConversation, ChatMessage,
    ChatbotSettings,
    KnowledgeCategory, KnowledgeArticle, KnowledgeFAQ,

    # Blog & Content
    BlogCategory, BlogPost,

    # Pricing
    PricingPlan, PricingFeature,
)


# =============================================================================
# DASHBOARD / HOME PAGE SECTIONS
# =============================================================================

class HeroMetricInline(TabularInline):
    model = HeroMetric
    extra = 1
    fields = ('label', 'value', 'order')


class HeroPartnerInline(TabularInline):
    model = HeroPartnerLogo
    extra = 1
    fields = ('name', 'logo_url', 'order')


@admin.register(HeroSection)
class HeroSectionAdmin(ModelAdmin):
    list_display = ('title', 'badge', 'is_active', 'updated_at')
    list_filter = ('is_active', 'updated_at')
    search_fields = ('title', 'description')
    inlines = [HeroMetricInline, HeroPartnerInline]

    fieldsets = (
        ('🎯 Main Content', {
            'fields': ('page', 'badge', 'badge_emoji', 'title', 'highlighted_text', 'subheading', 'description')
        }),
        ('🎨 Styling', {
            'fields': ('highlight_gradient_from', 'highlight_gradient_to', 'background_pattern')
        }),
        ('🖼️ Media', {
            'fields': ('media', 'image_url')
        }),
        ('🔗 Call to Actions', {
            'fields': (
                ('primary_cta_label', 'primary_cta_href'),
                ('secondary_cta_label', 'secondary_cta_href')
            )
        }),
        ('⚙️ Settings', {
            'fields': ('is_active',)
        }),
    )

    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "🏠 Home: Hero Section"


class BusinessImpactMetricInline(TabularInline):
    model = BusinessImpactMetric
    extra = 1
    fields = ('value', 'label', 'caption', 'icon', 'theme_bg_class', 'theme_text_class', 'order')


class BusinessImpactLogoInline(TabularInline):
    model = BusinessImpactLogo
    extra = 1
    fields = ('name', 'logo_url', 'order')


@admin.register(BusinessImpactSection)
class BusinessImpactSectionAdmin(ModelAdmin):
    list_display = ('title', 'updated_at')
    inlines = [BusinessImpactMetricInline, BusinessImpactLogoInline]

    fieldsets = (
        ('📊 Business Impact Content', {
            'fields': ('title', 'description', 'cta_label', 'cta_href')
        }),
    )

    class Meta:
        verbose_name_plural = "🏠 Home: Business Impact"


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ('name', 'company', 'rating', 'is_featured', 'is_active', 'order')
    list_filter = ('is_featured', 'is_active', 'rating')
    list_editable = ('is_featured', 'is_active', 'order')
    search_fields = ('name', 'company', 'text')
    ordering = ('-is_featured', 'order')

    fieldsets = (
        ('👤 Person Details', {
            'fields': ('name', 'title', 'company', 'avatar')
        }),
        ('💬 Testimonial', {
            'fields': ('text', 'rating')
        }),
        ('🎯 Visibility', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )

    class Meta:
        verbose_name_plural = "🏠 Home: Testimonials"


class ROICalculatorStatInline(TabularInline):
    model = ROICalculatorStat
    extra = 1


class ROICalculatorToolInline(TabularInline):
    model = ROICalculatorTool
    extra = 1


@admin.register(ROICalculatorSection)
class ROICalculatorSectionAdmin(ModelAdmin):
    list_display = ('title', 'badge', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    inlines = [ROICalculatorStatInline, ROICalculatorToolInline]

    fieldsets = (
        ('🧮 ROI Calculator Content', {
            'fields': ('badge', 'title', 'highlighted_text', 'description', 'is_active')
        }),
    )

    class Meta:
        verbose_name_plural = "🏠 Home: ROI Calculator"


class WhyChooseReasonInline(TabularInline):
    model = WhyChooseReason
    extra = 1
    fields = ('title', 'description', 'icon', 'color', 'order')


@admin.register(WhyChooseSection)
class WhyChooseSectionAdmin(ModelAdmin):
    list_display = ('title', 'badge', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    inlines = [WhyChooseReasonInline]

    fieldsets = (
        ('⭐ Why Choose Us Content', {
            'fields': ('badge', 'title', 'description', 'is_active')
        }),
    )

    class Meta:
        verbose_name_plural = "🏠 Home: Why Choose Us"


# =============================================================================
# SERVICES SECTION
# =============================================================================

class ServiceOutcomeInline(TabularInline):
    model = ServiceOutcome
    extra = 1
    fields = ('text', 'order')


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ('title', 'badge', 'icon', 'order', 'is_featured', 'slug')
    list_editable = ('order', 'is_featured')
    list_filter = ('badge', 'is_featured')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ServiceOutcomeInline]
    ordering = ('order',)

    fieldsets = (
        ('⚙️ Service Information', {
            'fields': ('title', 'slug', 'badge', 'description')
        }),
        ('🎨 Display', {
            'fields': ('icon', 'order')
        }),
        ('🔥 Featured', {
            'fields': ('is_featured',),
            'description': 'Highlight services that should appear in the home page featured list.'
        }),
    )

    class Meta:
        verbose_name_plural = "⚙️ Services: All Services"


@admin.register(ServiceProcessStep)
class ServiceProcessStepAdmin(ModelAdmin):
    list_display = ('title', 'icon', 'accent', 'order')
    list_editable = ('order',)
    ordering = ('order',)

    fieldsets = (
        ('📋 Process Step', {
            'fields': ('title', 'description', 'icon', 'accent', 'order')
        }),
    )

    class Meta:
        verbose_name_plural = "⚙️ Services: Process Steps"


# =============================================================================
# AI TOOLS SECTION
# =============================================================================

class AIToolInline(StackedInline):
    model = AITool
    extra = 0
    prepopulated_fields = {'slug': ('title',)}
    fields = (
        ('title', 'slug'),
        'description',
        ('icon', 'emoji', 'color', 'badge'),
        ('category', 'status', 'is_coming_soon'),
        ('min_credits', 'credit_cost'),
        ('is_active', 'order')
    )


@admin.register(AIToolsSection)
class AIToolsSectionAdmin(ModelAdmin):
    list_display = ('title', 'badge', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    inlines = [AIToolInline]

    fieldsets = (
        ('🤖 AI Tools Section', {
            'fields': ('badge', 'title', 'description', 'is_active')
        }),
    )

    class Meta:
        verbose_name_plural = "🤖 AI Tools: Section"


@admin.register(AITool)
class AIToolAdmin(ModelAdmin):
    list_display = ('title', 'status', 'category', 'is_coming_soon', 'is_active', 'order')
    list_filter = ('status', 'category', 'is_active', 'is_coming_soon')
    list_editable = ('is_active', 'order')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order',)

    fieldsets = (
        ('📝 Basic Information', {
            'fields': ('section', 'title', 'slug', 'description')
        }),
        ('🎨 Visuals', {
            'fields': (('icon', 'emoji', 'color'), 'badge')
        }),
        ('📊 Categorization', {
            'fields': (('category', 'status'), 'is_coming_soon')
        }),
        ('💳 Credits & Pricing', {
            'fields': ('min_credits', 'credit_cost')
        }),
        ('🔗 Links & CTAs', {
            'fields': (
                ('external_url', 'preview_url'),
                ('cta_label', 'cta_url'),
                ('secondary_cta_label', 'secondary_cta_url')
            )
        }),
        ('⚙️ Settings', {
            'fields': ('is_active', 'order')
        }),
    )

    class Meta:
        verbose_name_plural = "🤖 AI Tools: Individual Tools"


# =============================================================================
# DEMOS SECTION
# =============================================================================

class DemoImageInline(TabularInline):
    model = DemoImage
    extra = 1
    fields = ('image', 'caption', 'order')


@admin.register(DemoShowcase)
class DemoShowcaseAdmin(ModelAdmin):
    list_display = ('title', 'industry', 'status', 'is_featured', 'is_active', 'order')
    list_filter = ('status', 'is_featured', 'is_active', 'industry')
    list_editable = ('is_featured', 'is_active', 'order')
    search_fields = ('title', 'short_description', 'client_name')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-is_featured', 'order')
    inlines = [DemoImageInline]

    fieldsets = (
        ('📱 Demo Information', {
            'fields': ('title', 'slug', 'industry', 'short_description', 'full_description')
        }),
        ('🎨 Visuals', {
            'fields': (('icon', 'color_class'), 'highlight_badge', ('thumbnail', 'screenshot'))
        }),
        ('✨ Features', {
            'fields': ('features', 'feature_count'),
            'description': 'Enter features as JSON array or comma-separated text'
        }),
        ('🔗 Links', {
            'fields': ('demo_url', 'video_url')
        }),
        ('👔 Client Details', {
            'fields': ('client_name', 'client_logo', 'technologies_used', 'completion_date')
        }),
        ('📊 Status & Visibility', {
            'fields': (('status', 'is_featured'), 'is_active', 'order')
        }),
    )

    class Meta:
        verbose_name_plural = "🎬 Demos: Showcase"


# =============================================================================
# FAQ SECTION
# =============================================================================

class FAQPageStatInline(TabularInline):
    model = FAQPageStat
    extra = 1
    fields = ('value', 'label', 'detail', 'order')


@admin.register(FAQPageSection)
class FAQPageSectionAdmin(ModelAdmin):
    list_display = ('title', 'badge', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    inlines = [FAQPageStatInline]

    fieldsets = (
        ('❓ FAQ Page Hero', {
            'fields': ('badge', 'title', 'description')
        }),
        ('🔍 Search', {
            'fields': ('search_placeholder',)
        }),
        ('🔗 Call to Actions', {
            'fields': (('cta_text', 'cta_url'), 'secondary_cta_text')
        }),
        ('⚙️ Settings', {
            'fields': ('is_active',)
        }),
    )

    class Meta:
        verbose_name_plural = "❓ FAQ: Page Section"


class FAQItemInline(TabularInline):
    model = FAQItem
    extra = 1
    fields = ('question', 'answer', 'order')


@admin.register(FAQCategory)
class FAQCategoryAdmin(ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)
    search_fields = ('title',)
    ordering = ('order',)
    inlines = [FAQItemInline]

    fieldsets = (
        ('❓ FAQ Category', {
            'fields': ('title', 'description', 'icon', 'order')
        }),
    )

    class Meta:
        verbose_name_plural = "❓ FAQ: Categories"


# =============================================================================
# CONTACT SECTION
# =============================================================================

@admin.register(ContactMethod)
class ContactMethodAdmin(ModelAdmin):
    list_display = ('title', 'value', 'icon', 'order')
    list_editable = ('order',)
    ordering = ('order',)

    fieldsets = (
        ('📞 Contact Method', {
            'fields': (
                ('title', 'icon'),
                'value',
                'description',
                'cta_label',
                'order',
            )
        }),
    )

    class Meta:
        verbose_name_plural = "📞 Contact: Methods"


@admin.register(ContactInquiry)
class ContactInquiryAdmin(ModelAdmin):
    list_display = ('name', 'email', 'service', 'status', 'created_at')
    list_filter = ('status', 'service', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('👤 Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('💬 Inquiry Details', {
            'fields': ('service', 'message', 'status')
        }),
        ('⏰ Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_contacted', 'mark_as_converted']

    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(status='contacted')
        self.message_user(request, f'{updated} inquiries marked as contacted', messages.SUCCESS)

    def mark_as_converted(self, request, queryset):
        updated = queryset.update(status='converted')
        self.message_user(request, f'{updated} inquiries marked as converted', messages.SUCCESS)

    mark_as_contacted.short_description = "Mark as Contacted"
    mark_as_converted.short_description = "Mark as Converted"

    class Meta:
        verbose_name_plural = "📞 Contact: Inquiries"


# =============================================================================
# SEO MANAGEMENT
# =============================================================================

@admin.register(PageSEO)
class PageSEOAdmin(ModelAdmin):
    list_display = ('page', 'meta_title', 'canonical_url', 'updated_at')
    list_filter = ('page',)
    search_fields = ('meta_title', 'meta_description', 'meta_keywords')

    fieldsets = (
        ('📄 Page Selection', {
            'fields': ('page',)
        }),
        ('🔍 Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url')
        }),
        ('📱 Open Graph (Social Media)', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'description': 'Controls how your page appears when shared on Facebook, LinkedIn, etc.'
        }),
    )

    class Meta:
        verbose_name_plural = "🔍 SEO: Page SEO"


@admin.register(SEODataUpload)
class SEODataUploadAdmin(ModelAdmin):
    list_display = ('name', 'source', 'status', 'row_count', 'processed_at', 'last_ai_run_at')
    list_filter = ('status', 'source')
    readonly_fields = ('status', 'row_count', 'processed_at', 'last_ai_run_at', 'insights_pretty')
    search_fields = ('name',)
    actions = ['process_uploads', 'generate_ai_playbooks', 'generate_blog_drafts']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('📤 Upload Information', {
            'fields': ('name', 'source', 'csv_file', 'notes')
        }),
        ('🤖 AI Automation', {
            'fields': ('status', 'row_count', 'processed_at', 'last_ai_run_at', 'insights_pretty'),
            'classes': ('collapse',)
        }),
    )

    def insights_pretty(self, obj):
        if not obj or not obj.insights:
            return "—"
        formatted = json.dumps(obj.insights, indent=2, ensure_ascii=False)
        return format_html(
            "<pre style='white-space: pre-wrap; max-height: 320px; overflow-y: auto; background: #f5f5f5; padding: 10px; border-radius: 4px;'>{}</pre>",
            formatted,
        )
    insights_pretty.short_description = "Insights JSON"

    @action(description="✅ Process selected CSV uploads")
    def process_uploads(self, request, queryset):
        processed = 0
        for upload in queryset:
            try:
                upload.ingest_from_file()
                processed += 1
            except Exception as exc:
                upload.mark_failed(str(exc))
                self.message_user(request, f"❌ {upload.name} failed: {exc}", messages.ERROR)

        if processed:
            self.message_user(request, f"✅ Successfully processed {processed} upload(s).", messages.SUCCESS)

    @action(description="🤖 Generate AI playbooks (Top 3 clusters)")
    def generate_ai_playbooks(self, request, queryset):
        """Generate AI recommendations for top 3 priority clusters only to avoid timeout."""
        generated = 0
        for upload in queryset:
            try:
                # Process only top 3 clusters to avoid nginx timeout
                result = upload.run_ai_automation(cluster_limit=3, refresh=True)
                count = result.get('recommendations', 0)
                generated += count
                self.message_user(
                    request,
                    f"✅ {upload.name}: {count} recommendations from top 3 clusters",
                    messages.SUCCESS
                )
            except Exception as exc:
                self.message_user(request, f"❌ AI failed for {upload.name}: {exc}", messages.ERROR)
                continue

        if not generated:
            self.message_user(request, "⚠️ No recommendations generated. Check if clusters exist.", messages.WARNING)

    @action(description="📝 Generate blog drafts from clusters")
    def generate_blog_drafts(self, request, queryset):
        created = 0
        for upload in queryset:
            try:
                result = upload.generate_blog_posts()
                created += result.get('created', 0)
            except Exception as exc:
                self.message_user(request, f"❌ Blog generation failed: {exc}", messages.ERROR)
                continue

        if created:
            self.message_user(request, f"✅ Created {created} blog draft(s).", messages.SUCCESS)

    class Meta:
        verbose_name_plural = "🔍 SEO: Data Uploads"


@admin.register(SEOKeyword)
class SEOKeywordAdmin(ModelAdmin):
    list_display = ('keyword', 'upload', 'intent', 'search_volume', 'seo_difficulty', 'paid_difficulty', 'priority_score')
    list_filter = ('upload', 'intent', 'keyword_type')
    search_fields = ('keyword',)
    autocomplete_fields = ('upload', 'cluster')
    readonly_fields = ('priority_score', 'metadata', 'created_at', 'updated_at')
    ordering = ('-priority_score',)

    class Meta:
        verbose_name_plural = "🔍 SEO: Keywords"


@admin.register(SEOKeywordCluster)
class SEOKeywordClusterAdmin(ModelAdmin):
    list_display = ('label', 'upload', 'intent', 'keyword_count', 'avg_volume', 'priority_score')
    list_filter = ('upload', 'intent')
    search_fields = ('label', 'seed_keyword')
    autocomplete_fields = ('upload',)
    ordering = ('-priority_score',)
    readonly_fields = ('summary',)

    class Meta:
        verbose_name_plural = "🔍 SEO: Keyword Clusters"


@admin.register(AISEORecommendation)
class AISEORecommendationAdmin(ModelAdmin):
    list_display = ('title', 'category', 'upload', 'status', 'ai_model', 'created_at')
    list_filter = ('category', 'status', 'ai_model')
    search_fields = ('title', 'response')
    autocomplete_fields = ('upload', 'cluster', 'keyword')
    readonly_fields = ('prompt', 'response', 'ai_model', 'prompt_tokens', 'completion_tokens', 'metadata_pretty', 'status', 'error_message', 'created_at', 'updated_at')

    fieldsets = (
        ('📋 Recommendation Info', {
            'fields': ('title', 'upload', 'cluster', 'keyword', 'category', 'status', 'ai_model')
        }),
        ('💭 AI Prompt', {
            'fields': ('prompt',),
            'classes': ('collapse',)
        }),
        ('🤖 AI Response', {
            'fields': ('response', 'metadata_pretty', 'error_message')
        }),
        ('📊 Usage Stats', {
            'fields': ('prompt_tokens', 'completion_tokens', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def metadata_pretty(self, obj):
        if not obj or not obj.metadata:
            return "—"
        formatted = json.dumps(obj.metadata, indent=2, ensure_ascii=False)
        return format_html("<pre style='white-space: pre-wrap; background: #f5f5f5; padding: 10px; border-radius: 4px;'>{}</pre>", formatted)
    metadata_pretty.short_description = "Metadata"

    class Meta:
        verbose_name_plural = "🔍 SEO: AI Recommendations"


# =============================================================================
# LEADS & CHATBOT
# =============================================================================

class ChatMessageInline(TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('role', 'content', 'created_at', 'metadata')
    can_delete = False
    fields = ('role', 'content', 'created_at')
    max_num = 50


@admin.register(ChatConversation)
class ChatConversationAdmin(ModelAdmin):
    list_display = ('conversation_id', 'visitor_name', 'visitor_email', 'status', 'message_count', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('conversation_id', 'visitor_email', 'visitor_name')
    readonly_fields = ('conversation_id', 'metadata', 'last_user_message', 'created_at', 'updated_at', 'message_count')
    inlines = [ChatMessageInline]
    date_hierarchy = 'created_at'

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

    fieldsets = (
        ('💬 Conversation Info', {
            'fields': ('conversation_id', 'status', 'message_count')
        }),
        ('👤 Visitor Info', {
            'fields': ('visitor_name', 'visitor_email', 'visitor_phone', 'visitor_company')
        }),
        ('📊 Metadata', {
            'fields': ('last_user_message', 'metadata', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    class Meta:
        verbose_name_plural = "💬 Leads: Chat Conversations"


@admin.register(ChatLead)
class ChatLeadAdmin(ModelAdmin):
    list_display = ('name', 'email', 'company', 'intent', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'company', 'intent')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('👤 Lead Information', {
            'fields': ('conversation', 'name', 'email', 'phone', 'company')
        }),
        ('💡 Interest & Intent', {
            'fields': ('intent', 'budget', 'timeline', 'notes')
        }),
        ('📊 Lead Status', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )

    actions = ['mark_as_contacted', 'mark_as_qualified']

    def mark_as_contacted(self, request, queryset):
        updated = queryset.update(status='contacted')
        self.message_user(request, f'{updated} leads marked as contacted', messages.SUCCESS)

    def mark_as_qualified(self, request, queryset):
        updated = queryset.update(status='qualified')
        self.message_user(request, f'{updated} leads marked as qualified', messages.SUCCESS)

    mark_as_contacted.short_description = "Mark as Contacted"
    mark_as_qualified.short_description = "Mark as Qualified"

    class Meta:
        verbose_name_plural = "💬 Leads: Chat Leads"


@admin.register(ChatbotSettings)
class ChatbotSettingsAdmin(ModelAdmin):
    list_display = ('name', 'persona_title', 'brand_voice', 'updated_at')

    fieldsets = (
        ('🤖 Bot Identity', {
            'fields': ('name', 'persona_title', 'brand_voice', 'accent_color', 'hero_image')
        }),
        ('💬 Messaging', {
            'fields': ('intro_message', 'fallback_message', 'lead_capture_prompt', 'success_message', 'quick_replies')
        }),
        ('📞 Escalation', {
            'fields': ('escalation_threshold', 'contact_email', 'meeting_link')
        }),
    )

    class Meta:
        verbose_name_plural = "💬 Leads: Chatbot Settings"


class KnowledgeFAQInline(TabularInline):
    model = KnowledgeFAQ
    extra = 1


@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(ModelAdmin):
    list_display = ('title', 'category', 'status', 'persona', 'is_featured', 'published_at')
    list_filter = ('status', 'persona', 'category', 'is_featured')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'summary', 'content', 'keywords', 'tags')
    ordering = ('-published_at',)
    inlines = [KnowledgeFAQInline]

    fieldsets = (
        ('📝 Article Content', {
            'fields': ('category', 'title', 'slug', 'summary', 'content', 'cover_image')
        }),
        ('📊 Publishing', {
            'fields': ('status', 'published_at', 'is_featured')
        }),
        ('🎯 Audience & SEO', {
            'fields': ('persona', 'keywords', 'tags', 'metadata')
        }),
        ('🔗 Call to Action', {
            'fields': ('call_to_action', 'call_to_action_url')
        }),
    )

    class Meta:
        verbose_name_plural = "💬 Leads: Knowledge Base"


@admin.register(KnowledgeCategory)
class KnowledgeCategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'color', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)

    class Meta:
        verbose_name_plural = "💬 Leads: Knowledge Categories"


# =============================================================================
# SITE-WIDE SETTINGS
# =============================================================================

class BusinessHoursInline(TabularInline):
    model = BusinessHours
    extra = 1
    fields = ('day', 'hours', 'is_closed', 'order')


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    list_display = ('site_name', 'site_tagline', 'primary_email', 'primary_phone', 'updated_at')
    inlines = [BusinessHoursInline]

    fieldsets = (
        ('🏢 Site Information', {
            'fields': ('site_name', 'site_tagline', 'site_description')
        }),
        ('🎨 Logos & Branding', {
            'fields': ('logo', 'logo_dark', 'favicon')
        }),
        ('📞 Contact Information', {
            'fields': (
                ('primary_email', 'secondary_email'),
                ('primary_phone', 'secondary_phone'),
                'address'
            )
        }),
        ('🎯 Support & SLA', {
            'fields': (
                'support_badge',
                ('support_response_value', 'support_response_label'),
                'support_response_helper',
                'support_response_message',
                'support_response_confirmation'
            )
        }),
        ('🏢 Business Details', {
            'fields': ('abn',)
        }),
        ('📊 Analytics & Tracking', {
            'fields': ('google_analytics_id', 'facebook_pixel_id')
        }),
    )

    def has_add_permission(self, request):
        # Only allow one SiteSettings instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    class Meta:
        verbose_name_plural = "⚙️ Settings: Site Settings"


class FooterLinkInline(TabularInline):
    model = FooterLink
    extra = 1
    fields = ('column', 'title', 'url', 'order')


class SocialLinkInline(TabularInline):
    model = SocialLink
    extra = 1
    fields = ('platform', 'url', 'custom_label', 'is_active', 'order')
    verbose_name = "Social Link"
    verbose_name_plural = "📱 Social Media Links (Add as many as you need)"


@admin.register(FooterSection)
class FooterSectionAdmin(ModelAdmin):
    list_display = ('company_name', 'abn', 'updated_at')
    inlines = [FooterLinkInline, SocialLinkInline]

    fieldsets = (
        ('🏢 Company Info', {
            'fields': ('company_name', 'company_description', 'logo', 'abn')
        }),
        ('©️ Copyright', {
            'fields': ('copyright_text',)
        }),
    )

    class Meta:
        verbose_name_plural = "⚙️ Settings: Footer"


class NavigationItemInline(TabularInline):
    model = NavigationItem
    extra = 1
    fields = ('title', 'url', 'icon', 'parent', 'open_in_new_tab', 'is_active', 'order')


@admin.register(NavigationMenu)
class NavigationMenuAdmin(ModelAdmin):
    list_display = ('name', 'location', 'is_active', 'item_count', 'updated_at')
    list_filter = ('location', 'is_active')
    inlines = [NavigationItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

    class Meta:
        verbose_name_plural = "⚙️ Settings: Navigation"


@admin.register(StatMetric)
class StatMetricAdmin(ModelAdmin):
    list_display = ('value', 'label', 'section', 'is_active', 'order')
    list_filter = ('section', 'is_active')
    list_editable = ('is_active', 'order')
    ordering = ('section', 'order')

    fieldsets = (
        ('📊 Metric', {
            'fields': (('value', 'label'), ('icon', 'color'), 'section')
        }),
        ('⚙️ Settings', {
            'fields': ('is_active', 'order')
        }),
    )

    class Meta:
        verbose_name_plural = "⚙️ Settings: Statistics"


@admin.register(CTASection)
class CTASectionAdmin(ModelAdmin):
    list_display = ('title', 'placement', 'is_active', 'order')
    list_filter = ('placement', 'is_active')
    list_editable = ('is_active', 'order')
    ordering = ('placement', 'order')

    fieldsets = (
        ('📣 CTA Content', {
            'fields': ('title', 'subtitle', 'description', 'placement')
        }),
        ('🔗 Buttons', {
            'fields': (
                ('primary_button_text', 'primary_button_url'),
                ('secondary_button_text', 'secondary_button_url')
            )
        }),
        ('⚙️ Settings', {
            'fields': ('is_active', 'order')
        }),
    )

    class Meta:
        verbose_name_plural = "⚙️ Settings: CTA Sections"


# =============================================================================
# BLOG & CONTENT
# =============================================================================

@admin.register(BlogCategory)
class BlogCategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'order')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    ordering = ('order', 'name')


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ('title', 'author', 'blog_category', 'status', 'is_featured', 'published_at', 'views_count')
    list_filter = ('status', 'is_featured', 'blog_category', 'ai_generated', 'published_at')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-published_at', '-created_at')
    search_fields = ('title', 'excerpt', 'content', 'focus_keyword')
    date_hierarchy = 'published_at'
    autocomplete_fields = ('blog_category', 'source_cluster')

    fieldsets = (
        ('Post Content', {
            'fields': ('title', 'slug', 'author', 'blog_category', 'excerpt', 'content'),
            'description': 'Main content for the blog post'
        }),
        ('Images', {
            'fields': ('featured_image', 'og_image'),
            'description': 'Featured image and social sharing image'
        }),
        ('Publishing', {
            'fields': ('status', 'is_featured', 'published_at', 'reading_time_minutes'),
            'description': 'Control publishing status'
        }),
        ('SEO - Basic', {
            'fields': ('meta_title', 'meta_description', 'canonical_url'),
            'description': 'Search engine optimization settings'
        }),
        ('SEO - Keywords', {
            'fields': ('focus_keyword', 'secondary_keywords', 'tags'),
            'description': 'Keywords to optimize for'
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description'),
            'classes': ('collapse',),
            'description': 'Social media sharing settings'
        }),
        ('Content Source', {
            'fields': ('source_cluster', 'ai_generated'),
            'classes': ('collapse',),
            'description': 'SEO cluster this post targets'
        }),
        ('Stats', {
            'fields': ('views_count',),
            'classes': ('collapse',),
            'description': 'Engagement statistics'
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('blog_category', 'source_cluster')


# =============================================================================
# PRICING
# =============================================================================

class PricingFeatureInline(TabularInline):
    model = PricingFeature
    extra = 1
    fields = ('text', 'is_included', 'order')


@admin.register(PricingPlan)
class PricingPlanAdmin(ModelAdmin):
    list_display = ('name', 'price', 'currency', 'billing_period', 'is_popular', 'is_active', 'order')
    list_filter = ('is_popular', 'is_active', 'billing_period')
    list_editable = ('is_popular', 'is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)
    inlines = [PricingFeatureInline]

    fieldsets = (
        ('💰 Plan Details', {
            'fields': ('name', 'slug', 'tagline', 'description')
        }),
        ('💵 Pricing', {
            'fields': (('price', 'currency', 'billing_period'),)
        }),
        ('🔗 Call to Action', {
            'fields': ('button_text', 'button_url')
        }),
        ('⚙️ Settings', {
            'fields': ('is_popular', 'is_active', 'order')
        }),
    )

    class Meta:
        verbose_name_plural = "💰 Pricing: Plans"


# =============================================================================
# SEO ENGINE - Site Audits, PageSpeed, Search Console
# =============================================================================

class PageAuditInline(TabularInline):
    model = PageAudit
    extra = 0
    readonly_fields = ('url', 'performance_score', 'seo_score', 'accessibility_score', 'lcp', 'cls')
    fields = ('url', 'performance_score', 'seo_score', 'accessibility_score', 'lcp', 'cls')
    can_delete = False
    max_num = 20


class SiteAuditForm(forms.ModelForm):
    """Custom form for SiteAudit with user-friendly URL input."""
    urls_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'https://example.com/\nhttps://example.com/about\nhttps://example.com/contact'}),
        required=False,
        label="URLs to Audit",
        help_text="Enter one URL per line. Leave empty to audit the domain homepage."
    )

    class Meta:
        model = SiteAudit
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert JSON list to text for display
        if self.instance and self.instance.pk and self.instance.target_urls:
            self.fields['urls_text'].initial = '\n'.join(self.instance.target_urls)

    def clean_urls_text(self):
        """Convert text URLs to list."""
        text = self.cleaned_data.get('urls_text', '')
        if not text.strip():
            return []
        urls = [url.strip() for url in text.strip().split('\n') if url.strip()]
        # Validate URLs
        for url in urls:
            if not url.startswith(('http://', 'https://')):
                raise forms.ValidationError(f"Invalid URL: {url}. URLs must start with http:// or https://")
        return urls

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.target_urls = self.cleaned_data.get('urls_text', [])
        if commit:
            instance.save()
        return instance


@admin.register(SiteAudit)
class SiteAuditAdmin(ModelAdmin):
    form = SiteAuditForm
    list_display = ('name', 'domain', 'strategy', 'status', 'avg_performance', 'avg_seo', 'total_issues', 'created_at')
    list_filter = ('status', 'strategy', 'created_at')
    search_fields = ('name', 'domain')
    readonly_fields = ('status', 'avg_performance', 'avg_seo', 'avg_accessibility', 'avg_best_practices',
                       'total_pages', 'total_issues', 'critical_issues', 'warning_issues',
                       'started_at', 'completed_at', 'ai_analysis', 'created_at', 'updated_at')
    inlines = [PageAuditInline]
    date_hierarchy = 'created_at'
    actions = ['run_lighthouse_audit', 'run_pagespeed_analysis', 'generate_ai_analysis', 'generate_combined_ai_analysis']

    class Media:
        js = ('admin/js/seo-loading.js',)

    fieldsets = (
        ('Audit Configuration', {
            'fields': ('name', 'domain', 'strategy', 'urls_text', 'notes'),
            'description': 'Configure the audit settings. Enter URLs one per line.'
        }),
        ('📊 Scores', {
            'fields': (
                ('avg_performance', 'avg_seo'),
                ('avg_accessibility', 'avg_best_practices'),
            )
        }),
        ('⚠️ Issues', {
            'fields': (('total_pages', 'total_issues'), ('critical_issues', 'warning_issues'))
        }),
        ('AI Analysis (ChatGPT)', {
            'fields': ('ai_analysis',),
            'description': 'Run "Generate AI analysis" action to get ChatGPT recommendations.'
        }),
        ('⏰ Timing', {
            'fields': ('status', 'started_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @action(description="🔍 Run Lighthouse audit")
    def run_lighthouse_audit(self, request, queryset):
        for audit in queryset:
            try:
                result = audit.run_audit()
                if result.get('success'):
                    self.message_user(
                        request,
                        f"✅ Lighthouse '{audit.name}': {result.get('pages_audited')} pages, {result.get('total_issues')} issues. "
                        f"View in Page Audits & Audit Issues tabs",
                        messages.SUCCESS
                    )
                else:
                    self.message_user(request, f"❌ Audit failed: {result.get('error')}", messages.ERROR)
            except Exception as e:
                self.message_user(request, f"❌ Error: {str(e)}", messages.ERROR)

    @action(description="⚡ Run PageSpeed analysis")
    def run_pagespeed_analysis(self, request, queryset):
        from .services.pagespeed import PageSpeedService
        service = PageSpeedService()
        analyzed_count = 0

        for audit in queryset:
            urls = audit.target_urls or [f"https://{audit.domain}/"]
            for url in urls[:5]:  # Limit to 5 URLs
                try:
                    result = service.analyze_and_save(url, audit.strategy)
                    if result:
                        analyzed_count += 1
                except Exception as e:
                    self.message_user(request, f"❌ PageSpeed failed for {url}: {str(e)}", messages.ERROR)

        if analyzed_count > 0:
            self.message_user(
                request,
                f"✅ PageSpeed: {analyzed_count} URLs analyzed. View results in SEO Engine → PageSpeed Results",
                messages.SUCCESS
            )

    @action(description="🤖 Generate AI analysis")
    def generate_ai_analysis(self, request, queryset):
        for audit in queryset:
            try:
                result = audit.generate_ai_analysis()
                if result.get('success'):
                    self.message_user(
                        request,
                        f"✅ AI analysis for '{audit.name}': View in SEO Engine → AI Analysis tab, or click audit → AI Analysis section",
                        messages.SUCCESS
                    )
                else:
                    self.message_user(request, f"❌ AI failed: {result.get('error')}", messages.ERROR)
            except Exception as e:
                self.message_user(request, f"❌ Error: {str(e)}", messages.ERROR)

    @action(description="🧠 Generate COMBINED AI analysis (multi-source)")
    def generate_combined_ai_analysis(self, request, queryset):
        """Generate AI analysis combining all selected audits + PageSpeed + Search Console data."""
        from .services.seo_audit_ai import SEOAuditAIEngine
        try:
            # Use the first selected audit to save the combined analysis
            save_to = queryset.first()
            result = SEOAuditAIEngine.generate_combined_analysis(
                site_audits=queryset,
                save_to=save_to
            )
            if result.get('success'):
                sources = result.get('data_sources', {})
                self.message_user(
                    request,
                    f"✅ Combined AI analysis generated! Sources: {sources.get('audits', 0)} audits, "
                    f"{sources.get('pagespeed_results', 0)} PageSpeed, {sources.get('search_console_entries', 0)} Search Console. "
                    f"Saved to '{save_to.name}'",
                    messages.SUCCESS
                )
            else:
                self.message_user(request, f"❌ Combined analysis failed: {result.get('error')}", messages.ERROR)
        except Exception as e:
            self.message_user(request, f"❌ Error: {str(e)}", messages.ERROR)

    class Meta:
        verbose_name_plural = "🔍 SEO Engine: Site Audits"


@admin.register(AIAnalysisReport)
class AIAnalysisReportAdmin(ModelAdmin):
    """Admin view for AI Analysis Reports - shows only audits with AI analysis."""
    list_display = ('name', 'domain', 'status', 'analysis_preview', 'avg_performance', 'avg_seo', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'domain', 'ai_analysis')
    readonly_fields = ('name', 'domain', 'strategy', 'status', 'ai_analysis_display',
                       'avg_performance', 'avg_seo', 'avg_accessibility', 'avg_best_practices',
                       'total_issues', 'critical_issues', 'created_at')
    actions = ['regenerate_ai_analysis', 'export_analysis_markdown']
    date_hierarchy = 'created_at'

    class Media:
        js = ('admin/js/seo-loading.js',)

    def get_queryset(self, request):
        """Only show audits that have AI analysis."""
        qs = super().get_queryset(request)
        return qs.exclude(ai_analysis__isnull=True).exclude(ai_analysis='')

    @display(description="Analysis Preview")
    def analysis_preview(self, obj):
        if obj.ai_analysis:
            preview = obj.ai_analysis[:150] + '...' if len(obj.ai_analysis) > 150 else obj.ai_analysis
            return preview
        return "No analysis"

    @display(description="AI Analysis")
    def ai_analysis_display(self, obj):
        if obj.ai_analysis:
            # Format as HTML with proper styling
            return format_html(
                '<div style="white-space: pre-wrap; font-family: monospace; '
                'background: #f8f9fa; padding: 15px; border-radius: 8px; '
                'max-height: 600px; overflow-y: auto; line-height: 1.6;">{}</div>',
                obj.ai_analysis
            )
        return "No AI analysis generated yet. Run 'Generate AI Analysis' on Site Audits."

    fieldsets = (
        ('📊 Audit Summary', {
            'fields': ('name', 'domain', 'strategy', 'status'),
        }),
        ('🤖 AI Analysis', {
            'fields': ('ai_analysis_display',),
            'description': 'ChatGPT-powered SEO recommendations based on audit results.'
        }),
        ('📈 Scores', {
            'fields': (
                ('avg_performance', 'avg_seo'),
                ('avg_accessibility', 'avg_best_practices'),
            ),
        }),
        ('⚠️ Issues Found', {
            'fields': (('total_issues', 'critical_issues'),),
        }),
        ('📅 Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    @action(description="🔄 Regenerate AI Analysis")
    def regenerate_ai_analysis(self, request, queryset):
        for audit in queryset:
            try:
                result = audit.generate_ai_analysis()
                if result.get('success'):
                    self.message_user(request, f"✅ AI analysis regenerated for '{audit.name}'", messages.SUCCESS)
                else:
                    self.message_user(request, f"❌ AI failed: {result.get('error')}", messages.ERROR)
            except Exception as e:
                self.message_user(request, f"❌ Error: {str(e)}", messages.ERROR)

    @action(description="📄 Export as Markdown")
    def export_analysis_markdown(self, request, queryset):
        from django.http import HttpResponse
        audit = queryset.first()
        if not audit or not audit.ai_analysis:
            self.message_user(request, "❌ No analysis to export", messages.ERROR)
            return

        content = f"""# SEO Analysis Report: {audit.name}
**Domain:** {audit.domain}
**Date:** {audit.created_at.strftime('%Y-%m-%d')}
**Strategy:** {audit.strategy}

## Performance Scores
- Performance: {audit.avg_performance or 'N/A'}
- SEO: {audit.avg_seo or 'N/A'}
- Accessibility: {audit.avg_accessibility or 'N/A'}
- Best Practices: {audit.avg_best_practices or 'N/A'}

## Issues Summary
- Total Issues: {audit.total_issues}
- Critical Issues: {audit.critical_issues}

---

## AI Analysis

{audit.ai_analysis}

---
*Generated by Codeteki SEO Engine*
"""
        response = HttpResponse(content, content_type='text/markdown')
        response['Content-Disposition'] = f'attachment; filename="{audit.domain}-seo-analysis.md"'
        return response

    class Meta:
        verbose_name = "AI Analysis Report"
        verbose_name_plural = "🤖 SEO Engine: AI Analysis"


class AuditIssueInline(TabularInline):
    model = AuditIssue
    extra = 0
    readonly_fields = ('audit_id', 'title', 'severity', 'category', 'display_value', 'savings_ms')
    fields = ('severity', 'category', 'title', 'display_value', 'savings_ms', 'status')
    can_delete = False
    max_num = 30


@admin.register(PageAudit)
class PageAuditAdmin(ModelAdmin):
    list_display = ('url', 'site_audit', 'strategy', 'performance_score', 'seo_score', 'lcp', 'cls', 'created_at')
    list_filter = ('strategy', 'site_audit', 'created_at')
    search_fields = ('url',)
    readonly_fields = ('performance_score', 'accessibility_score', 'best_practices_score', 'seo_score',
                       'lcp', 'fid', 'inp', 'cls', 'fcp', 'ttfb', 'si', 'tbt',
                       'raw_data', 'status', 'error_message', 'created_at')
    inlines = [AuditIssueInline]

    fieldsets = (
        ('🌐 Page Info', {
            'fields': ('site_audit', 'url', 'strategy', 'status')
        }),
        ('📊 Scores', {
            'fields': (
                ('performance_score', 'seo_score'),
                ('accessibility_score', 'best_practices_score'),
            )
        }),
        ('⚡ Core Web Vitals', {
            'fields': (
                ('lcp', 'fcp', 'ttfb'),
                ('cls', 'tbt', 'si'),
                ('fid', 'inp'),
            )
        }),
        ('📄 Raw Data', {
            'fields': ('raw_data', 'error_message'),
            'classes': ('collapse',)
        }),
    )

    class Meta:
        verbose_name_plural = "🔍 SEO Engine: Page Audits"


@admin.register(AuditIssue)
class AuditIssueAdmin(ModelAdmin):
    list_display = ('title', 'severity', 'category', 'page_url', 'display_value', 'savings_ms', 'status')
    list_filter = ('severity', 'category', 'status')
    search_fields = ('title', 'description', 'audit_id')
    readonly_fields = ('audit_id', 'title', 'description', 'category', 'severity', 'score',
                       'display_value', 'savings_ms', 'savings_bytes', 'details', 'ai_fix_recommendation')
    actions = ['mark_fixed', 'mark_ignored', 'generate_fix_recommendation']

    def page_url(self, obj):
        return obj.page_audit.url if obj.page_audit else "—"
    page_url.short_description = "Page URL"

    fieldsets = (
        ('⚠️ Issue Details', {
            'fields': ('page_audit', 'audit_id', 'title', 'description')
        }),
        ('📊 Classification', {
            'fields': (('severity', 'category'), ('score', 'display_value'))
        }),
        ('💡 Savings', {
            'fields': (('savings_ms', 'savings_bytes'),)
        }),
        ('🔧 Fix Status', {
            'fields': ('status', 'fixed_at', 'ai_fix_recommendation')
        }),
        ('📄 Details', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
    )

    @action(description="✅ Mark as Fixed")
    def mark_fixed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='fixed', fixed_at=timezone.now())
        self.message_user(request, f"✅ {updated} issues marked as fixed", messages.SUCCESS)

    @action(description="🚫 Mark as Ignored")
    def mark_ignored(self, request, queryset):
        updated = queryset.update(status='ignored')
        self.message_user(request, f"🚫 {updated} issues marked as ignored", messages.SUCCESS)

    @action(description="🤖 Generate AI fix recommendation")
    def generate_fix_recommendation(self, request, queryset):
        from .services.seo_audit_ai import SEOAuditAIEngine
        from .services.ai_client import AIContentEngine

        ai = AIContentEngine()
        generated_count = 0
        for issue in queryset[:10]:  # Limit to 10
            try:
                engine = SEOAuditAIEngine(issue.page_audit.site_audit, ai)
                result = engine._generate_issue_recommendation(issue)
                if result.get('success'):
                    generated_count += 1
            except Exception as e:
                self.message_user(request, f"❌ Failed: {str(e)}", messages.ERROR)

        if generated_count > 0:
            self.message_user(
                request,
                f"✅ {generated_count} fix recommendations generated. View by clicking each issue → AI Fix Recommendation section, or in SEO Recommendations",
                messages.SUCCESS
            )

    class Meta:
        verbose_name_plural = "🔍 SEO Engine: Audit Issues"


class PageSpeedResultForm(forms.ModelForm):
    """Custom form for PageSpeedResult with user-friendly URL input."""
    class Meta:
        model = PageSpeedResult
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make URL editable for new records
        if not self.instance.pk:
            self.fields['url'].widget.attrs['placeholder'] = 'https://example.com/'


@admin.register(PageSpeedResult)
class PageSpeedResultAdmin(ModelAdmin):
    form = PageSpeedResultForm
    list_display = ('url', 'strategy', 'lab_performance_score', 'overall_category', 'field_lcp', 'field_cls', 'created_at')
    list_filter = ('strategy', 'overall_category', 'created_at')
    search_fields = ('url',)
    actions = ['run_pagespeed_analysis']

    class Media:
        js = ('admin/js/seo-loading.js',)

    def get_readonly_fields(self, request, obj=None):
        """Make result fields readonly only for existing records."""
        if obj:  # Editing existing record
            return ('lab_performance_score', 'lab_lcp', 'lab_fcp', 'lab_cls', 'lab_tbt', 'lab_si',
                   'field_lcp', 'field_fid', 'field_inp', 'field_cls', 'field_fcp', 'field_ttfb',
                   'origin_lcp', 'origin_inp', 'origin_cls', 'overall_category', 'raw_data')
        return ()

    fieldsets = (
        ('Page Info', {
            'fields': ('url', 'strategy'),
            'description': 'Enter a URL and select strategy, then save and run the analysis.'
        }),
        ('Lab Data (Lighthouse)', {
            'fields': (
                'lab_performance_score',
                ('lab_lcp', 'lab_fcp'),
                ('lab_cls', 'lab_tbt', 'lab_si'),
            )
        }),
        ('Field Data (Real Users - CrUX)', {
            'fields': (
                'overall_category',
                ('field_lcp', 'field_fcp', 'field_ttfb'),
                ('field_cls', 'field_fid', 'field_inp'),
            )
        }),
        ('Origin Data (Site-wide)', {
            'fields': (('origin_lcp', 'origin_inp', 'origin_cls'),),
            'classes': ('collapse',)
        }),
    )

    @action(description="⚡ Run PageSpeed Analysis")
    def run_pagespeed_analysis(self, request, queryset):
        from .services.pagespeed import PageSpeedService
        service = PageSpeedService()

        if not service.enabled:
            self.message_user(request, "❌ PageSpeed API not configured. Set GOOGLE_API_KEY.", messages.ERROR)
            return

        for record in queryset:
            try:
                result = service.analyze_url(record.url, record.strategy)
                if result.get('success'):
                    # Update the record with results
                    record.lab_performance_score = result.get('lab_performance_score')
                    record.lab_lcp = result.get('lab_lcp')
                    record.lab_fcp = result.get('lab_fcp')
                    record.lab_cls = result.get('lab_cls')
                    record.lab_tbt = result.get('lab_tbt')
                    record.lab_si = result.get('lab_si')
                    record.field_lcp = result.get('field_lcp')
                    record.field_fid = result.get('field_fid')
                    record.field_inp = result.get('field_inp')
                    record.field_cls = result.get('field_cls')
                    record.field_fcp = result.get('field_fcp')
                    record.field_ttfb = result.get('field_ttfb')
                    record.origin_lcp = result.get('origin_lcp')
                    record.origin_inp = result.get('origin_inp')
                    record.origin_cls = result.get('origin_cls')
                    record.overall_category = result.get('overall_category', '')
                    record.raw_data = result.get('raw_data', {})
                    record.save()
                    self.message_user(
                        request,
                        f"✅ {record.url}: Performance {record.lab_performance_score}/100",
                        messages.SUCCESS
                    )
                else:
                    self.message_user(request, f"❌ {record.url}: {result.get('error')}", messages.ERROR)
            except Exception as e:
                self.message_user(request, f"❌ Error analyzing {record.url}: {str(e)}", messages.ERROR)

    class Meta:
        verbose_name_plural = "🔍 SEO Engine: PageSpeed Results"


@admin.register(SearchConsoleSync)
class SearchConsoleSyncAdmin(ModelAdmin):
    list_display = ('property_url', 'start_date', 'end_date', 'status', 'rows_imported', 'queries_imported', 'created_at')
    list_filter = ('status', 'created_at')
    readonly_fields = ('status', 'rows_imported', 'queries_imported', 'pages_imported', 'error_message', 'completed_at')
    actions = ['run_sync']

    class Media:
        js = ('admin/js/seo-loading.js',)

    fieldsets = (
        ('📊 Sync Configuration', {
            'fields': ('property_url', ('start_date', 'end_date'))
        }),
        ('📈 Results', {
            'fields': ('status', ('rows_imported', 'queries_imported', 'pages_imported'), 'error_message', 'completed_at')
        }),
    )

    @action(description="🔄 Run Search Console sync")
    def run_sync(self, request, queryset):
        for sync in queryset:
            try:
                result = sync.run_sync()
                if result.get('success'):
                    self.message_user(
                        request,
                        f"✅ Synced {result.get('rows_imported')} rows, {result.get('queries_imported')} queries",
                        messages.SUCCESS
                    )
                else:
                    self.message_user(request, f"❌ Sync failed: {result.get('error')}", messages.ERROR)
            except Exception as e:
                self.message_user(request, f"❌ Error: {str(e)}", messages.ERROR)

    class Meta:
        verbose_name_plural = "🔍 SEO Engine: Search Console Sync"


@admin.register(SearchConsoleData)
class SearchConsoleDataAdmin(ModelAdmin):
    list_display = ('query', 'page', 'date', 'clicks', 'impressions', 'ctr_percent', 'position')
    list_filter = ('date', 'device', 'country')
    search_fields = ('query', 'page')
    date_hierarchy = 'date'
    ordering = ('-date', '-impressions')

    def ctr_percent(self, obj):
        return f"{obj.ctr * 100:.1f}%"
    ctr_percent.short_description = "CTR"

    class Meta:
        verbose_name_plural = "🔍 SEO Engine: Search Console Data"


@admin.register(KeywordRanking)
class KeywordRankingAdmin(ModelAdmin):
    list_display = ('keyword', 'date', 'position', 'position_change_display', 'clicks', 'impressions')
    list_filter = ('date', 'has_featured_snippet')
    search_fields = ('keyword__keyword', 'ranking_url')
    date_hierarchy = 'date'

    def position_change_display(self, obj):
        change = obj.position_change
        if change > 0:
            return format_html('<span style="color: green;">+{:.1f}</span>', change)
        elif change < 0:
            return format_html('<span style="color: red;">{:.1f}</span>', change)
        return "—"
    position_change_display.short_description = "Change"

    class Meta:
        verbose_name_plural = "🔍 SEO Engine: Keyword Rankings"


@admin.register(CompetitorProfile)
class CompetitorProfileAdmin(ModelAdmin):
    list_display = ('name', 'domain', 'domain_authority', 'organic_traffic_est', 'total_keywords', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'domain')

    fieldsets = (
        ('🏢 Competitor Info', {
            'fields': ('name', 'domain', 'is_active', 'notes')
        }),
        ('📊 Metrics', {
            'fields': (
                ('domain_authority', 'organic_traffic_est'),
                ('total_keywords', 'total_backlinks'),
            )
        }),
        ('🤖 AI Analysis', {
            'fields': ('last_analysis', 'analysis_data', 'ai_insights'),
            'classes': ('collapse',)
        }),
    )

    class Meta:
        verbose_name_plural = "🔍 SEO Engine: Competitors"


@admin.register(SEORecommendation)
class SEORecommendationAdmin(ModelAdmin):
    list_display = ('title', 'recommendation_type', 'priority', 'status', 'target_url', 'created_at')
    list_filter = ('recommendation_type', 'priority', 'status')
    search_fields = ('title', 'target_url', 'recommended_value')
    readonly_fields = ('current_value', 'recommended_value', 'reasoning', 'ai_model', 'ai_tokens_used', 'applied_at')
    actions = ['approve_recommendations', 'apply_recommendations']

    fieldsets = (
        ('📋 Recommendation', {
            'fields': ('title', 'recommendation_type', ('priority', 'status'))
        }),
        ('🎯 Target', {
            'fields': ('target_url', 'target_field')
        }),
        ('📝 Values', {
            'fields': ('current_value', 'recommended_value', 'reasoning')
        }),
        ('🔗 Sources', {
            'fields': ('upload', 'keyword', 'cluster', 'audit_issue'),
            'classes': ('collapse',)
        }),
        ('🤖 AI Metadata', {
            'fields': ('ai_model', 'ai_tokens_used', 'applied_at'),
            'classes': ('collapse',)
        }),
    )

    @action(description="✅ Approve selected recommendations")
    def approve_recommendations(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"✅ {updated} recommendations approved", messages.SUCCESS)

    @action(description="🚀 Apply selected recommendations")
    def apply_recommendations(self, request, queryset):
        # This would need custom implementation based on recommendation type
        self.message_user(request, "⚠️ Auto-apply not yet implemented. Please apply manually.", messages.WARNING)

    class Meta:
        verbose_name_plural = "🔍 SEO Engine: Recommendations"


@admin.register(ScheduledAudit)
class ScheduledAuditAdmin(ModelAdmin):
    list_display = ('name', 'frequency', 'is_active', 'last_run', 'next_run')
    list_filter = ('frequency', 'is_active')
    search_fields = ('name',)

    fieldsets = (
        ('📅 Schedule', {
            'fields': ('name', 'is_active', 'frequency', 'strategy')
        }),
        ('🎯 Target', {
            'fields': ('target_urls',)
        }),
        ('🔔 Notifications', {
            'fields': ('notify_emails', 'notify_on_score_drop', 'score_drop_threshold')
        }),
        ('📊 History', {
            'fields': ('last_run', 'next_run', 'last_audit'),
            'classes': ('collapse',)
        }),
    )

    class Meta:
        verbose_name_plural = "🔍 SEO Engine: Scheduled Audits"


class SEOChatMessageInline(TabularInline):
    model = SEOChatMessage
    extra = 0
    readonly_fields = ('role', 'content', 'tokens_used', 'created_at')
    fields = ('role', 'content', 'tokens_used', 'created_at')
    can_delete = False


@admin.register(SEOChatSession)
class SEOChatSessionAdmin(ModelAdmin):
    list_display = ('session_id', 'user', 'title', 'message_count', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('session_id', 'title')
    readonly_fields = ('session_id', 'context')
    inlines = [SEOChatMessageInline]

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = "Messages"

    class Meta:
        verbose_name_plural = "🔍 SEO Engine: Chat Sessions"


@admin.register(SEOChangeLog)
class SEOChangeLogAdmin(ModelAdmin):
    list_display = ('target_field', 'target_url', 'applied_by', 'applied_at', 'reverted')
    list_filter = ('reverted', 'applied_at')
    readonly_fields = ('recommendation', 'target_url', 'target_field', 'old_value', 'new_value',
                       'applied_by', 'applied_at', 'reverted', 'reverted_at')

    class Meta:
        verbose_name_plural = "🔍 SEO Engine: Change Log"
