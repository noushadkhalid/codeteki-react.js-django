"""
Comprehensive Django Admin Configuration for Codeteki CMS
Organized by page sections for easy content management
"""

import json
from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import Count

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
    SiteSettings,
    FooterSection, FooterLink,
    NavigationMenu, NavigationItem,
    StatMetric,

    # SEO
    PageSEO,
    SEODataUpload, SEOKeyword, SEOKeywordCluster, AISEORecommendation,

    # Leads & Chat
    ChatLead, ChatConversation, ChatMessage,
    ChatbotSettings,
    KnowledgeCategory, KnowledgeArticle, KnowledgeFAQ,

    # Blog & Content
    BlogPost,

    # Pricing
    PricingPlan, PricingFeature,
)


# =============================================================================
# DASHBOARD / HOME PAGE SECTIONS
# =============================================================================

class HeroMetricInline(admin.TabularInline):
    model = HeroMetric
    extra = 1
    fields = ('label', 'value', 'order')


class HeroPartnerInline(admin.TabularInline):
    model = HeroPartnerLogo
    extra = 1
    fields = ('name', 'logo_url', 'order')


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
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


class BusinessImpactMetricInline(admin.TabularInline):
    model = BusinessImpactMetric
    extra = 1
    fields = ('value', 'label', 'caption', 'icon', 'theme_bg_class', 'theme_text_class', 'order')


class BusinessImpactLogoInline(admin.TabularInline):
    model = BusinessImpactLogo
    extra = 1
    fields = ('name', 'logo_url', 'order')


@admin.register(BusinessImpactSection)
class BusinessImpactSectionAdmin(admin.ModelAdmin):
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
class TestimonialAdmin(admin.ModelAdmin):
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


class ROICalculatorStatInline(admin.TabularInline):
    model = ROICalculatorStat
    extra = 1


class ROICalculatorToolInline(admin.TabularInline):
    model = ROICalculatorTool
    extra = 1


@admin.register(ROICalculatorSection)
class ROICalculatorSectionAdmin(admin.ModelAdmin):
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


class WhyChooseReasonInline(admin.TabularInline):
    model = WhyChooseReason
    extra = 1
    fields = ('title', 'description', 'icon', 'color', 'order')


@admin.register(WhyChooseSection)
class WhyChooseSectionAdmin(admin.ModelAdmin):
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

class ServiceOutcomeInline(admin.TabularInline):
    model = ServiceOutcome
    extra = 1
    fields = ('text', 'order')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
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
class ServiceProcessStepAdmin(admin.ModelAdmin):
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

class AIToolInline(admin.StackedInline):
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
class AIToolsSectionAdmin(admin.ModelAdmin):
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
class AIToolAdmin(admin.ModelAdmin):
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

class DemoImageInline(admin.TabularInline):
    model = DemoImage
    extra = 1
    fields = ('image', 'caption', 'order')


@admin.register(DemoShowcase)
class DemoShowcaseAdmin(admin.ModelAdmin):
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

class FAQPageStatInline(admin.TabularInline):
    model = FAQPageStat
    extra = 1
    fields = ('value', 'label', 'detail', 'order')


@admin.register(FAQPageSection)
class FAQPageSectionAdmin(admin.ModelAdmin):
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


class FAQItemInline(admin.TabularInline):
    model = FAQItem
    extra = 1
    fields = ('question', 'answer', 'order')


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
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
class ContactMethodAdmin(admin.ModelAdmin):
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
class ContactInquiryAdmin(admin.ModelAdmin):
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
class PageSEOAdmin(admin.ModelAdmin):
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
class SEODataUploadAdmin(admin.ModelAdmin):
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

    @admin.action(description="✅ Process selected CSV uploads")
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

    @admin.action(description="🤖 Generate AI playbooks")
    def generate_ai_playbooks(self, request, queryset):
        generated = 0
        for upload in queryset:
            try:
                result = upload.run_ai_automation(refresh=True)
                generated += result.get('recommendations', 0)
            except Exception as exc:
                self.message_user(request, f"❌ AI failed for {upload.name}: {exc}", messages.ERROR)
                continue

        if generated:
            self.message_user(request, f"✅ Created {generated} AI recommendation(s).", messages.SUCCESS)

    @admin.action(description="📝 Generate blog drafts from clusters")
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
class SEOKeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'upload', 'intent', 'search_volume', 'seo_difficulty', 'paid_difficulty', 'priority_score')
    list_filter = ('upload', 'intent', 'keyword_type')
    search_fields = ('keyword',)
    autocomplete_fields = ('upload', 'cluster')
    readonly_fields = ('priority_score', 'metadata', 'created_at', 'updated_at')
    ordering = ('-priority_score',)

    class Meta:
        verbose_name_plural = "🔍 SEO: Keywords"


@admin.register(SEOKeywordCluster)
class SEOKeywordClusterAdmin(admin.ModelAdmin):
    list_display = ('label', 'upload', 'intent', 'keyword_count', 'avg_volume', 'priority_score')
    list_filter = ('upload', 'intent')
    search_fields = ('label', 'seed_keyword')
    autocomplete_fields = ('upload',)
    ordering = ('-priority_score',)
    readonly_fields = ('summary',)

    class Meta:
        verbose_name_plural = "🔍 SEO: Keyword Clusters"


@admin.register(AISEORecommendation)
class AISEORecommendationAdmin(admin.ModelAdmin):
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

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('role', 'content', 'created_at', 'metadata')
    can_delete = False
    fields = ('role', 'content', 'created_at')
    max_num = 50


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
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
class ChatLeadAdmin(admin.ModelAdmin):
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
class ChatbotSettingsAdmin(admin.ModelAdmin):
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


class KnowledgeFAQInline(admin.TabularInline):
    model = KnowledgeFAQ
    extra = 1


@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin):
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
class KnowledgeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'color', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)

    class Meta:
        verbose_name_plural = "💬 Leads: Knowledge Categories"


# =============================================================================
# SITE-WIDE SETTINGS
# =============================================================================

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'site_tagline', 'primary_email', 'primary_phone', 'updated_at')

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
        ('⏰ Business Hours', {
            'fields': ('business_hours',),
            'description': 'Enter as JSON format or multi-line text'
        }),
        ('📱 Social Media', {
            'fields': (
                ('facebook', 'twitter'),
                ('linkedin', 'instagram'),
                ('youtube', 'github')
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


class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 1
    fields = ('text', 'url', 'order')


@admin.register(FooterSection)
class FooterSectionAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'abn', 'updated_at')
    inlines = [FooterLinkInline]

    fieldsets = (
        ('🏢 Company Info', {
            'fields': ('company_name', 'tagline', 'description', 'abn')
        }),
    )

    class Meta:
        verbose_name_plural = "⚙️ Settings: Footer"


class NavigationItemInline(admin.TabularInline):
    model = NavigationItem
    extra = 1
    fields = ('title', 'url', 'icon', 'parent', 'open_in_new_tab', 'is_active', 'order')


@admin.register(NavigationMenu)
class NavigationMenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active', 'item_count', 'updated_at')
    list_filter = ('location', 'is_active')
    inlines = [NavigationItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

    class Meta:
        verbose_name_plural = "⚙️ Settings: Navigation"


@admin.register(StatMetric)
class StatMetricAdmin(admin.ModelAdmin):
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
class CTASectionAdmin(admin.ModelAdmin):
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

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'is_featured', 'published_at', 'views_count')
    list_filter = ('is_published', 'is_featured', 'category', 'published_at')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-published_at',)
    search_fields = ('title', 'excerpt', 'content')
    date_hierarchy = 'published_at'

    fieldsets = (
        ('📝 Post Content', {
            'fields': ('title', 'slug', 'author', 'category', 'excerpt', 'content')
        }),
        ('🖼️ Featured Image', {
            'fields': ('featured_image',)
        }),
        ('📊 Publishing', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
        ('🔍 SEO & Tags', {
            'fields': ('tags', 'meta_title', 'meta_description')
        }),
        ('📈 Stats', {
            'fields': ('views_count', 'reading_time'),
            'classes': ('collapse',)
        }),
    )

    class Meta:
        verbose_name_plural = "📝 Blog: Posts"


# =============================================================================
# PRICING
# =============================================================================

class PricingFeatureInline(admin.TabularInline):
    model = PricingFeature
    extra = 1
    fields = ('text', 'is_included', 'order')


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
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
