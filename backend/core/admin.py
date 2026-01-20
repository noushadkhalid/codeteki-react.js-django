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
    Service, ServiceOutcome, ServiceFeature, ServiceCapability, ServiceBenefit, ServiceProcess, ServiceProcessStep,

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
    # Ubersuggest Integration
    SEOProject, SEOCompetitor, SEOCompetitorKeyword,
    SEOBacklinkOpportunity, SEOKeywordRank, SEOContentGap,

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
    """Short features shown on service cards."""
    model = ServiceOutcome
    extra = 1
    fields = ('text', 'order')
    verbose_name = "Card Feature"
    verbose_name_plural = "📋 Card Features (shown on service cards - keep to 3-4 items)"


class ServiceFeatureInline(TabularInline):
    """Detailed features for service detail page."""
    model = ServiceFeature
    extra = 1
    fields = ('text', 'order')
    verbose_name = "Detail Feature"
    verbose_name_plural = "✅ Detail Page Features (shown in 'Key Features' grid - aim for 8 items)"


class ServiceCapabilityInline(StackedInline):
    """Capability cards with icon, title, description."""
    model = ServiceCapability
    extra = 1
    fields = ('icon', 'title', 'description', 'order')
    verbose_name = "Capability"
    verbose_name_plural = "💪 Capabilities (cards with icon + description - aim for 6 items)"


class ServiceBenefitInline(TabularInline):
    """Benefits for 'Why Choose Us' section."""
    model = ServiceBenefit
    extra = 1
    fields = ('text', 'order')
    verbose_name = "Benefit"
    verbose_name_plural = "🎯 Benefits (shown in 'Why Choose Us' section - aim for 6 items)"


class ServiceProcessInline(TabularInline):
    """Process steps specific to this service."""
    model = ServiceProcess
    extra = 1
    fields = ('step_number', 'title', 'description', 'order')
    verbose_name = "Process Step"
    verbose_name_plural = "🔄 Process Steps (shown in 'Our Process' section - aim for 4 steps)"


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ('title', 'badge', 'icon', 'order', 'is_featured', 'slug')
    list_editable = ('order', 'is_featured')
    list_filter = ('badge', 'is_featured')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [
        ServiceOutcomeInline,
        ServiceFeatureInline,
        ServiceCapabilityInline,
        ServiceBenefitInline,
        ServiceProcessInline,
    ]
    ordering = ('order',)

    fieldsets = (
        ('⚙️ Basic Info (for service cards)', {
            'fields': ('title', 'slug', 'badge', 'description', 'icon', 'order', 'is_featured'),
            'description': 'This information appears on service cards in listings and home page.'
        }),
        ('📄 Detail Page Content', {
            'fields': ('tagline', 'subtitle', 'full_description'),
            'description': 'Content shown on the service detail page hero and overview sections.',
            'classes': ('collapse',),
        }),
        ('🖼️ Hero Image', {
            'fields': ('hero_image', 'hero_image_url'),
            'description': 'Upload an image or provide an external URL. Recommended: 1200x800px landscape.',
            'classes': ('collapse',),
        }),
        ('🎨 Styling', {
            'fields': ('gradient_from', 'gradient_to'),
            'description': 'Tailwind color classes for gradients, e.g. "purple-600", "indigo-600"',
            'classes': ('collapse',),
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
        verbose_name_plural = "⚙️ Services: Global Process Steps (Legacy)"


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
    list_display = ('__str__', 'target_keyword', 'meta_title', 'target_url_display', 'has_all_fields', 'updated_at')
    list_filter = ('page', 'service', 'blog_post')
    search_fields = ('meta_title', 'meta_description', 'target_keyword', 'custom_url')
    autocomplete_fields = ('service', 'blog_post', 'source_recommendation')
    actions = ['generate_ai_meta']
    readonly_fields = ('view_ai_recommendations',)

    fieldsets = (
        ('📄 Page Selection', {
            'fields': ('page', 'custom_url'),
            'description': 'Select a preset page OR enter a custom URL'
        }),
        ('🔗 Link to Content (Optional)', {
            'fields': ('service', 'blog_post'),
            'description': 'Link to a service or blog post for automatic URL'
        }),
        ('🎯 Target Keyword', {
            'fields': ('target_keyword', 'source_recommendation', 'view_ai_recommendations'),
        }),
        ('🔍 Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url')
        }),
        ('📱 Open Graph (Social Media)', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'description': 'Controls how your page appears when shared on Facebook, LinkedIn, etc.'
        }),
    )

    def target_url_display(self, obj):
        return obj.target_url
    target_url_display.short_description = "Target URL"

    def has_all_fields(self, obj):
        """Check if all important SEO fields are filled."""
        has_title = bool(obj.meta_title and len(obj.meta_title) > 10)
        has_desc = bool(obj.meta_description and len(obj.meta_description) > 20)
        has_keyword = bool(obj.target_keyword)
        has_keywords = bool(obj.meta_keywords)

        if has_title and has_desc and has_keyword and has_keywords:
            return format_html('<span style="color: #10b981;">✅ Complete</span>')
        elif has_title and has_desc:
            return format_html('<span style="color: #f59e0b;">⚠️ Missing keywords</span>')
        else:
            return format_html('<span style="color: #ef4444;">❌ Incomplete</span>')
    has_all_fields.short_description = "Status"

    def view_ai_recommendations(self, obj):
        """Show link to view AI recommendations for this page's keyword."""
        from django.urls import reverse

        links = []

        # Link to source recommendation if exists
        if obj.source_recommendation:
            url = reverse('admin:core_aiseorecommendation_change', args=[obj.source_recommendation.id])
            links.append(f'<a href="{url}" target="_blank" style="color: #3b82f6;">📄 View Source Recommendation</a>')

        # Link to all Meta Kit recommendations
        rec_url = reverse('admin:core_aiseorecommendation_changelist') + '?category=metadata'
        links.append(f'<a href="{rec_url}" target="_blank" style="color: #8b5cf6;">🔍 Browse All Meta Kits</a>')

        # Link to SEO Keywords
        kw_url = reverse('admin:core_seokeyword_changelist')
        links.append(f'<a href="{kw_url}" target="_blank" style="color: #06b6d4;">📊 View Ubersuggest Keywords</a>')

        if not links:
            return "No recommendations linked"

        return format_html('<br>'.join(links))
    view_ai_recommendations.short_description = "AI Recommendations"

    @action(description="🤖 Generate AI Meta Tags (Using Ubersuggest Keywords)")
    def generate_ai_meta(self, request, queryset):
        """Generate optimized meta tags using actual Ubersuggest keyword data."""
        from core.services.ai_client import AIContentEngine
        from core.models import SEOKeyword, AISEORecommendation
        import re

        ai = AIContentEngine()
        if not ai.enabled:
            self.message_user(request, "❌ OpenAI API key not configured.", messages.ERROR)
            return

        generated = 0
        errors = []

        # Get all keywords from Ubersuggest uploads, sorted by priority
        all_keywords = list(SEOKeyword.objects.order_by('-priority_score', '-search_volume')[:100])

        # Build keyword mapping by relevance to page types
        keyword_page_map = {
            'home': ['ai', 'business', 'automation', 'solutions', 'australia', 'melbourne'],
            'services': ['services', 'solutions', 'development', 'automation', 'consulting'],
            'ai-tools': ['ai tools', 'ai assistant', 'productivity', 'free tools'],
            'demos': ['demo', 'showcase', 'examples', 'portfolio'],
            'faq': ['faq', 'questions', 'help', 'support', 'how to'],
            'contact': ['contact', 'consultation', 'book', 'enquiry', 'get in touch'],
        }

        for page_seo in queryset:
            try:
                page_name = str(page_seo)
                page_url = page_seo.target_url

                # Find relevant keywords for this page
                relevant_keywords = []
                page_key = page_seo.page if page_seo.page != 'custom' else None

                if page_seo.service:
                    # Match keywords to service
                    service_terms = page_seo.service.title.lower().split()
                    service_desc = (page_seo.service.description or "").lower()
                    for kw in all_keywords:
                        kw_lower = kw.keyword.lower()
                        if any(term in kw_lower for term in service_terms) or any(term in service_desc for term in kw_lower.split()):
                            relevant_keywords.append(kw)
                        if len(relevant_keywords) >= 10:
                            break
                elif page_key and page_key in keyword_page_map:
                    # Match keywords to static page
                    page_terms = keyword_page_map[page_key]
                    for kw in all_keywords:
                        kw_lower = kw.keyword.lower()
                        if any(term in kw_lower for term in page_terms):
                            relevant_keywords.append(kw)
                        if len(relevant_keywords) >= 10:
                            break

                # If no specific matches, use top keywords by priority
                if not relevant_keywords:
                    relevant_keywords = all_keywords[:5]

                # Check for existing AI recommendations for these keywords
                existing_recs = []
                if relevant_keywords:
                    keyword_ids = [k.id for k in relevant_keywords]
                    existing_recs = list(AISEORecommendation.objects.filter(
                        keyword_id__in=keyword_ids,
                        category='metadata',
                        status='generated'
                    ).order_by('-created_at')[:3])

                # Build context
                keyword_context = ""
                if relevant_keywords:
                    keyword_context = "**Ubersuggest Keyword Data (use these actual keywords!):**\n"
                    for kw in relevant_keywords[:8]:
                        keyword_context += f"- {kw.keyword} (Vol: {kw.search_volume}, Diff: {kw.seo_difficulty or 'N/A'}, Intent: {kw.intent})\n"

                existing_rec_context = ""
                if existing_recs:
                    existing_rec_context = "\n**Existing AI Recommendations for these keywords:**\n"
                    for rec in existing_recs[:2]:
                        # Extract key parts from existing recommendations
                        existing_rec_context += f"- {rec.title}: {rec.response[:200]}...\n"

                page_context = ""
                if page_seo.service:
                    page_context = f"""
**Service Details:**
- Title: {page_seo.service.title}
- Description: {page_seo.service.description or 'N/A'}
- Tagline: {getattr(page_seo.service, 'tagline', 'N/A')}
"""
                elif page_seo.blog_post:
                    page_context = f"""
**Blog Post:**
- Title: {page_seo.blog_post.title}
- Excerpt: {page_seo.blog_post.excerpt or 'N/A'}
"""
                else:
                    page_descriptions = {
                        'home': 'Main landing page - AI-powered business solutions, automation, web development for Australian SMBs',
                        'services': 'Services overview - AI Workforce, Automation, Custom Tools, Web Development, SEO Engine',
                        'ai-tools': 'Free AI tools and utilities for daily business productivity',
                        'demos': 'Product demos and interactive showcases of AI solutions',
                        'faq': 'Frequently asked questions about services, pricing, AI capabilities',
                        'contact': 'Contact page with booking form, business hours, consultation requests',
                    }
                    page_context = f"**Page:** {page_descriptions.get(page_seo.page, 'Business page')}"

                prompt = f"""Generate SEO-optimized meta tags for this webpage using the ACTUAL keyword research data provided.

**Page URL:** {page_url}
**Page Name:** {page_name}

{page_context}

{keyword_context}
{existing_rec_context}

**Business Context:**
- Company: Codeteki
- Location: Melbourne, Australia
- Focus: AI-powered business solutions for Australian SMBs
- Services: AI chatbots, automation, custom tools, web development, SEO

**IMPORTANT Requirements:**
1. **USE THE ACTUAL KEYWORDS** from the Ubersuggest data above - don't invent new ones!
2. Meta Title: 50-60 chars, include the highest-volume relevant keyword naturally
3. Meta Description: 150-160 chars, compelling CTA, include 1-2 keywords naturally
4. Target Keyword: Pick the BEST keyword from the list (highest volume + relevance)
5. Meta Keywords: Use 5-8 keywords from the Ubersuggest list above

**Output Format (exactly):**
**Meta Title:** [title here]
**Meta Description:** [description here]
**Target Keyword:** [single best keyword from Ubersuggest data]
**Meta Keywords:** [comma-separated keywords from Ubersuggest data]
"""

                result = ai.generate(
                    prompt=prompt,
                    system_prompt="You are an SEO expert. Use the ACTUAL keyword research data provided - do not make up keywords. Focus on the highest-value keywords from the Ubersuggest data.",
                    temperature=0.2
                )

                if not result.get("success"):
                    errors.append(f"{page_name}: {result.get('error', 'Unknown error')}")
                    continue

                output = result.get("output", "")

                # Parse the AI response
                title_match = re.search(r'\*\*Meta Title:\*\*\s*(.+?)(?:\n|$)', output)
                desc_match = re.search(r'\*\*Meta Description:\*\*\s*(.+?)(?:\n|$)', output)
                keyword_match = re.search(r'\*\*Target Keyword:\*\*\s*(.+?)(?:\n|$)', output)
                keywords_match = re.search(r'\*\*Meta Keywords:\*\*\s*(.+?)(?:\n|$)', output)

                if title_match:
                    page_seo.meta_title = title_match.group(1).strip()[:160]
                if desc_match:
                    page_seo.meta_description = desc_match.group(1).strip()[:320]
                if keyword_match:
                    page_seo.target_keyword = keyword_match.group(1).strip()[:255]
                if keywords_match:
                    page_seo.meta_keywords = keywords_match.group(1).strip()

                # Also set OG tags
                if not page_seo.og_title:
                    page_seo.og_title = page_seo.meta_title
                if not page_seo.og_description:
                    page_seo.og_description = page_seo.meta_description

                # Set canonical URL
                from django.conf import settings
                site_url = getattr(settings, 'SITE_URL', 'https://www.codeteki.au').rstrip('/')
                page_seo.canonical_url = f"{site_url}{page_seo.target_url}"

                page_seo.save()
                generated += 1

                kw_used = page_seo.target_keyword[:30] if page_seo.target_keyword else "N/A"
                self.message_user(
                    request,
                    f"✅ {page_name}: Keyword='{kw_used}' | Title='{page_seo.meta_title[:35]}...'",
                    messages.SUCCESS
                )

            except Exception as e:
                errors.append(f"{page_seo}: {str(e)}")

        if generated:
            self.message_user(request, f"✅ Generated AI meta tags for {generated} page(s) using Ubersuggest data!", messages.SUCCESS)
        elif not all_keywords:
            self.message_user(request, "⚠️ No Ubersuggest keywords found. Upload keyword data first!", messages.WARNING)
        if errors:
            self.message_user(request, f"⚠️ Errors: {', '.join(errors[:3])}", messages.WARNING)

    @action(description="⚡ Quick AI Meta Tags (No Ubersuggest needed)")
    def generate_quick_meta(self, request, queryset):
        """Generate AI meta tags directly without requiring Ubersuggest data."""
        from core.services.ai_client import AIContentEngine
        from django.conf import settings
        import re

        ai = AIContentEngine()
        if not ai.enabled:
            self.message_user(request, "❌ OpenAI API key not configured.", messages.ERROR)
            return

        generated = 0
        errors = []

        for page_seo in queryset:
            try:
                page_name = str(page_seo)
                page_url = page_seo.target_url

                # Build context based on page type
                if page_seo.service:
                    context = f"""
Service: {page_seo.service.title}
Description: {page_seo.service.description or 'AI-powered business solution'}
Tagline: {getattr(page_seo.service, 'tagline', '')}
URL: /services/{page_seo.service.slug}
"""
                elif page_seo.blog_post:
                    context = f"""
Blog Post: {page_seo.blog_post.title}
Excerpt: {page_seo.blog_post.excerpt or ''}
URL: /blog/{page_seo.blog_post.slug}
"""
                else:
                    page_contexts = {
                        'home': 'Homepage - AI-powered business solutions for Australian SMBs. Automation, chatbots, web development.',
                        'services': 'Services overview - AI Workforce, Automation, Custom Tools, Web Development, SEO Engine.',
                        'ai-tools': 'Free AI tools and utilities for business productivity.',
                        'demos': 'Product demos and interactive showcases of AI solutions.',
                        'faq': 'Frequently asked questions about AI services and pricing.',
                        'contact': 'Contact page - book consultations, get in touch.',
                    }
                    context = f"Page: {page_contexts.get(page_seo.page, page_name)}\nURL: {page_url}"

                prompt = f"""Generate SEO-optimized meta tags for this webpage.

{context}

**Business Context:**
- Company: Codeteki
- Location: Melbourne, Australia
- Focus: AI-powered business automation for Australian SMBs
- Services: AI chatbots, workflow automation, custom tools, web development

**Requirements:**
1. Meta Title: 50-60 chars, include primary topic, end with "| Codeteki"
2. Meta Description: 150-160 chars, compelling CTA, value proposition
3. Meta Keywords: 5-8 relevant keywords, comma-separated
4. OG Title: Same as meta title or slightly shorter
5. OG Description: Same as meta description or more engaging

**Output Format (exactly):**
**Meta Title:** [title here]
**Meta Description:** [description here]
**Meta Keywords:** [keywords here]
**OG Title:** [og title here]
**OG Description:** [og description here]
"""

                result = ai.generate(
                    prompt=prompt,
                    system_prompt="You are an SEO expert. Generate compelling, accurate meta tags optimized for search and social sharing.",
                    temperature=0.3
                )

                if not result.get("success"):
                    errors.append(f"{page_name}: {result.get('error', 'Unknown error')}")
                    continue

                output = result.get("output", "")

                # Parse response
                title_match = re.search(r'\*\*Meta Title:\*\*\s*(.+?)(?:\n|$)', output)
                desc_match = re.search(r'\*\*Meta Description:\*\*\s*(.+?)(?:\n|$)', output)
                keywords_match = re.search(r'\*\*Meta Keywords:\*\*\s*(.+?)(?:\n|$)', output)
                og_title_match = re.search(r'\*\*OG Title:\*\*\s*(.+?)(?:\n|$)', output)
                og_desc_match = re.search(r'\*\*OG Description:\*\*\s*(.+?)(?:\n|$)', output)

                if title_match:
                    page_seo.meta_title = title_match.group(1).strip()[:160]
                if desc_match:
                    page_seo.meta_description = desc_match.group(1).strip()[:320]
                if keywords_match:
                    page_seo.meta_keywords = keywords_match.group(1).strip()
                if og_title_match:
                    page_seo.og_title = og_title_match.group(1).strip()[:160]
                if og_desc_match:
                    page_seo.og_description = og_desc_match.group(1).strip()[:320]

                # Set canonical URL
                site_url = getattr(settings, 'SITE_URL', 'https://www.codeteki.au').rstrip('/')
                page_seo.canonical_url = f"{site_url}{page_seo.target_url}"

                page_seo.save()
                generated += 1

                self.message_user(
                    request,
                    f"✅ {page_name}: title, desc, keywords, OG, canonical",
                    messages.SUCCESS
                )

            except Exception as e:
                errors.append(f"{page_seo}: {str(e)}")

        if generated:
            self.message_user(request, f"✅ Generated AI meta tags for {generated} page(s)!", messages.SUCCESS)
        if errors:
            self.message_user(request, f"⚠️ Errors: {', '.join(errors[:3])}", messages.WARNING)

    class Meta:
        verbose_name_plural = "🔍 SEO: Page SEO"


@admin.register(SEODataUpload)
class SEODataUploadAdmin(ModelAdmin):
    list_display = ('name', 'project', 'source', 'status', 'row_count', 'processed_at', 'last_ai_run_at')
    list_filter = ('status', 'source', 'project')
    readonly_fields = ('status', 'row_count', 'error_count', 'processed_at', 'last_ai_run_at', 'insights_pretty')
    search_fields = ('name', 'project__name')
    autocomplete_fields = ('project',)
    actions = ['process_uploads', 'process_ubersuggest', 'generate_ai_playbooks', 'generate_blog_drafts']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('📤 Upload Information', {
            'fields': ('project', 'name', 'source', 'csv_file', 'notes')
        }),
        ('🤖 Processing Results', {
            'fields': ('status', 'row_count', 'error_count', 'processed_at', 'last_ai_run_at', 'insights_pretty'),
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

    @action(description="✅ Process selected CSV uploads (Keywords)")
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

    @action(description="🔄 Process Ubersuggest Export (All Types)")
    def process_ubersuggest(self, request, queryset):
        """Process any Ubersuggest CSV export using the smart router."""
        from .services.seo_importer import UbersuggestImportRouter

        processed = 0
        for upload in queryset:
            try:
                router = UbersuggestImportRouter(upload)
                result = router.run()
                processed += 1
                self.message_user(
                    request,
                    f"✅ {upload.name}: {result.get('rows', 0)} rows imported",
                    messages.SUCCESS
                )
            except Exception as exc:
                upload.mark_failed(str(exc))
                self.message_user(request, f"❌ {upload.name} failed: {exc}", messages.ERROR)

        if processed:
            self.message_user(request, f"✅ Successfully processed {processed} Ubersuggest upload(s).", messages.SUCCESS)

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
    actions = ['apply_meta_to_page', 'apply_to_matching_service']

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

    def _parse_meta_kit_response(self, response):
        """Parse AI Meta Kit response and extract all fields."""
        import re

        data = {
            'meta_title': None,
            'meta_description': None,
            'meta_keywords': None,
            'og_title': None,
            'og_description': None,
        }

        # Try multiple patterns for title
        title_patterns = [
            r'\*\*Page Title:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Meta Title:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Title:\*\*\s*(.+?)(?:\n|$)',
            r'Page Title:\s*(.+?)(?:\n|$)',
            r'Meta Title:\s*(.+?)(?:\n|$)',
        ]
        for pattern in title_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                data['meta_title'] = match.group(1).strip().strip('"\'')
                break

        # Try multiple patterns for description
        desc_patterns = [
            r'\*\*Meta Description:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Description:\*\*\s*(.+?)(?:\n|$)',
            r'Meta Description:\s*(.+?)(?:\n|$)',
        ]
        for pattern in desc_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                data['meta_description'] = match.group(1).strip().strip('"\'')
                break

        # Try to extract keywords
        keyword_patterns = [
            r'\*\*Meta Keywords:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Keywords:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Target Keywords:\*\*\s*(.+?)(?:\n|$)',
            r'Meta Keywords:\s*(.+?)(?:\n|$)',
            r'Keywords:\s*(.+?)(?:\n|$)',
        ]
        for pattern in keyword_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                data['meta_keywords'] = match.group(1).strip().strip('"\'')
                break

        # Try to extract OG title
        og_title_patterns = [
            r'\*\*OG Title:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Open Graph Title:\*\*\s*(.+?)(?:\n|$)',
            r'OG Title:\s*(.+?)(?:\n|$)',
        ]
        for pattern in og_title_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                data['og_title'] = match.group(1).strip().strip('"\'')
                break

        # Try to extract OG description
        og_desc_patterns = [
            r'\*\*OG Description:\*\*\s*(.+?)(?:\n|$)',
            r'\*\*Open Graph Description:\*\*\s*(.+?)(?:\n|$)',
            r'OG Description:\s*(.+?)(?:\n|$)',
        ]
        for pattern in og_desc_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                data['og_description'] = match.group(1).strip().strip('"\'')
                break

        return data

    @action(description="🚀 Auto-Apply Meta Kit to Best Matching Page")
    def apply_meta_to_page(self, request, queryset):
        """Parse Meta Kit responses and apply ALL fields to best matching PageSEO entry."""

        # Keyword to service mapping
        KEYWORD_SERVICE_MAP = {
            'web development': 'web-dev',
            'website development': 'web-dev',
            'website developer': 'web-dev',
            'ecommerce': 'web-dev',
            'automation': 'automation',
            'business automation': 'automation',
            'workflow automation': 'automation',
            'task automation': 'automation',
            'crm automation': 'automation',
            'ai chatbot': 'ai-workforce',
            'ai workforce': 'ai-workforce',
            'chatbot': 'ai-workforce',
            'voice agent': 'ai-workforce',
            'ai phone': 'ai-workforce',
            'customer service': 'ai-workforce',
            'custom tool': 'custom-tools',
            'api integration': 'custom-tools',
            'software integration': 'custom-tools',
            'zapier': 'custom-tools',
            'ai tool': 'daily-ai',
            'daily ai': 'daily-ai',
            'ai assistant': 'daily-ai',
            'seo': 'seo-engine',
            'mcp': 'mcp-integration',
        }

        applied = 0
        skipped = []

        # Filter for metadata category (Meta Tags)
        meta_recs = queryset.filter(category='metadata')

        if not meta_recs.exists():
            self.message_user(request, "⚠️ Select Meta Kit (Meta Tags) recommendations only.", messages.WARNING)
            return

        for rec in meta_recs:
            try:
                response = rec.response or ""

                # Parse ALL fields from AI response
                parsed = self._parse_meta_kit_response(response)

                if not parsed['meta_title'] and not parsed['meta_description']:
                    skipped.append(f"Rec #{rec.id} (no title/desc found in response)")
                    continue

                # Get keyword from metadata or rec.keyword
                keyword = ""
                if rec.keyword:
                    keyword = rec.keyword.keyword
                elif rec.metadata and 'keywords' in rec.metadata:
                    keywords = rec.metadata['keywords']
                    if keywords and len(keywords) > 0:
                        keyword = keywords[0].get('keyword', '')

                if not keyword:
                    skipped.append(f"Rec #{rec.id} (no keyword)")
                    continue

                # Find matching service by keyword
                matched_service = None
                keyword_lower = keyword.lower()

                for kw_pattern, service_slug in KEYWORD_SERVICE_MAP.items():
                    if kw_pattern in keyword_lower:
                        matched_service = Service.objects.filter(slug=service_slug).first()
                        if matched_service:
                            break

                if matched_service:
                    # Update existing PageSEO for this service
                    page_seo = PageSEO.objects.filter(service=matched_service).first()
                    if page_seo:
                        # Apply ALL parsed fields
                        if parsed['meta_title']:
                            page_seo.meta_title = parsed['meta_title'][:160]
                        if parsed['meta_description']:
                            page_seo.meta_description = parsed['meta_description'][:320]

                        # Get keywords - from AI response OR from Ubersuggest metadata
                        meta_keywords = parsed['meta_keywords']
                        if not meta_keywords and rec.metadata and 'keywords' in rec.metadata:
                            # Extract keywords from Ubersuggest cluster data
                            kw_list = rec.metadata['keywords']
                            if kw_list:
                                meta_keywords = ', '.join([k.get('keyword', '') for k in kw_list if k.get('keyword')])
                        if meta_keywords:
                            page_seo.meta_keywords = meta_keywords

                        # Set OG tags (use parsed or fall back to meta)
                        page_seo.og_title = parsed['og_title'] or parsed['meta_title'] or page_seo.og_title
                        page_seo.og_description = parsed['og_description'] or parsed['meta_description'] or page_seo.og_description

                        # Set canonical URL from SITE_URL + target_url
                        from django.conf import settings
                        site_url = getattr(settings, 'SITE_URL', 'https://www.codeteki.au').rstrip('/')
                        page_seo.canonical_url = f"{site_url}{page_seo.target_url}"

                        # Set target keyword and link to recommendation
                        page_seo.target_keyword = keyword
                        page_seo.source_recommendation = rec
                        page_seo.save()
                        applied += 1

                        fields_applied = ['title', 'desc']
                        if meta_keywords:
                            fields_applied.append('keywords')
                        if page_seo.og_title:
                            fields_applied.append('OG')
                        fields_applied.append('canonical')

                        self.message_user(
                            request,
                            f"✅ '{keyword}' → /services/{matched_service.slug} ({', '.join(fields_applied)})",
                            messages.SUCCESS
                        )
                    else:
                        skipped.append(f"{keyword} (no PageSEO for {matched_service.slug})")
                else:
                    skipped.append(f"{keyword} (no matching service)")

            except Exception as e:
                self.message_user(request, f"❌ Error: {e}", messages.ERROR)

        if applied:
            self.message_user(request, f"✅ Applied {applied} Meta Kit(s) with ALL fields!", messages.SUCCESS)
        elif skipped:
            self.message_user(request, f"⚠️ Could not apply. Skipped: {', '.join(skipped[:5])}", messages.WARNING)
        else:
            self.message_user(request, "⚠️ No valid Meta Kit data found in selected recommendations.", messages.WARNING)

        if skipped and applied:
            self.message_user(request, f"ℹ️ Skipped {len(skipped)}: {', '.join(skipped[:3])}...", messages.INFO)

    @action(description="🔗 Apply to ALL Matching Services (Smart Match)")
    def apply_to_matching_service(self, request, queryset):
        """Smart match keywords to services using multiple strategies."""
        from difflib import SequenceMatcher

        applied = 0
        skipped = []
        services = list(Service.objects.all())
        page_seos = {ps.service_id: ps for ps in PageSEO.objects.filter(service__isnull=False)}

        # Filter for metadata category (Meta Tags)
        meta_recs = queryset.filter(category='metadata')

        if not meta_recs.exists():
            self.message_user(request, "⚠️ Select Meta Kit (Meta Tags) recommendations only.", messages.WARNING)
            return

        for rec in meta_recs:
            try:
                response = rec.response or ""

                # Parse ALL fields from AI response using shared parser
                parsed = self._parse_meta_kit_response(response)

                if not parsed['meta_title'] and not parsed['meta_description']:
                    skipped.append(f"Rec #{rec.id} (no title/desc)")
                    continue

                # Get keyword
                keyword = ""
                if rec.keyword:
                    keyword = rec.keyword.keyword
                elif rec.metadata and 'keywords' in rec.metadata:
                    keywords = rec.metadata['keywords']
                    if keywords:
                        keyword = keywords[0].get('keyword', '')

                if not keyword:
                    skipped.append(f"Rec #{rec.id} (no keyword)")
                    continue

                # Find best matching service using multiple strategies
                best_match = None
                best_score = 0
                keyword_lower = keyword.lower()
                keyword_words = set(keyword_lower.split())

                for service in services:
                    score = 0
                    service_title_lower = service.title.lower()
                    service_desc_lower = (service.description or "").lower()

                    # Strategy 1: Exact substring match (highest priority)
                    if keyword_lower in service_title_lower:
                        score = max(score, 0.9)
                    if keyword_lower in service_desc_lower:
                        score = max(score, 0.8)

                    # Strategy 2: Word overlap
                    title_words = set(service_title_lower.split())
                    desc_words = set(service_desc_lower.split())
                    title_overlap = len(keyword_words & title_words) / max(len(keyword_words), 1)
                    desc_overlap = len(keyword_words & desc_words) / max(len(keyword_words), 1)
                    score = max(score, title_overlap * 0.7, desc_overlap * 0.6)

                    # Strategy 3: Fuzzy match
                    fuzzy_title = SequenceMatcher(None, keyword_lower, service_title_lower).ratio()
                    score = max(score, fuzzy_title * 0.5)

                    if score > best_score and score > 0.3:
                        best_score = score
                        best_match = service

                if best_match and best_match.id in page_seos:
                    page_seo = page_seos[best_match.id]

                    # Apply ALL parsed fields
                    if parsed['meta_title']:
                        page_seo.meta_title = parsed['meta_title'][:160]
                    if parsed['meta_description']:
                        page_seo.meta_description = parsed['meta_description'][:320]

                    # Get keywords - from AI response OR from Ubersuggest metadata
                    meta_keywords = parsed['meta_keywords']
                    if not meta_keywords and rec.metadata and 'keywords' in rec.metadata:
                        # Extract keywords from Ubersuggest cluster data
                        kw_list = rec.metadata['keywords']
                        if kw_list:
                            meta_keywords = ', '.join([k.get('keyword', '') for k in kw_list if k.get('keyword')])
                    if meta_keywords:
                        page_seo.meta_keywords = meta_keywords

                    # Set OG tags
                    page_seo.og_title = parsed['og_title'] or parsed['meta_title'] or page_seo.og_title
                    page_seo.og_description = parsed['og_description'] or parsed['meta_description'] or page_seo.og_description

                    # Set canonical URL from SITE_URL + target_url
                    from django.conf import settings
                    site_url = getattr(settings, 'SITE_URL', 'https://www.codeteki.au').rstrip('/')
                    page_seo.canonical_url = f"{site_url}{page_seo.target_url}"

                    page_seo.target_keyword = keyword
                    page_seo.source_recommendation = rec
                    page_seo.save()
                    applied += 1

                    fields_applied = ['title', 'desc']
                    if meta_keywords:
                        fields_applied.append('keywords')
                    if page_seo.og_title:
                        fields_applied.append('OG')
                    fields_applied.append('canonical')

                    self.message_user(
                        request,
                        f"✅ '{keyword}' → {best_match.title} (score: {best_score:.0%}, {', '.join(fields_applied)})",
                        messages.SUCCESS
                    )
                elif best_match:
                    skipped.append(f"{keyword} (no PageSEO for {best_match.title})")
                else:
                    skipped.append(f"{keyword} (no matching service)")

            except Exception as e:
                self.message_user(request, f"❌ Error: {e}", messages.ERROR)
                skipped.append(f"Error: {str(e)[:30]}")

        if applied:
            self.message_user(request, f"✅ Auto-applied {applied} SEO settings with ALL fields!", messages.SUCCESS)
        elif skipped:
            self.message_user(request, f"⚠️ No matching services found. Skipped: {', '.join(skipped[:3])}", messages.WARNING)
        else:
            self.message_user(request, "⚠️ No valid Meta Kit data found in selected recommendations.", messages.WARNING)

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
            'fields': ('visitor_name', 'visitor_email', 'visitor_company', 'source')
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
            'fields': ('logo', 'logo_dark', 'favicon', 'default_og_image'),
            'description': 'Default OG Image is used for social sharing when pages don\'t have their own image.'
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
    readonly_fields = ('url', 'status', 'performance_display', 'seo_display', 'lcp_display', 'cls_display', 'tbt_display')
    fields = ('url', 'status', 'performance_display', 'seo_display', 'lcp_display', 'cls_display', 'tbt_display')
    can_delete = True
    max_num = 50

    @display(description="Performance")
    def performance_display(self, obj):
        if obj.performance_score is None:
            return "—"
        score = obj.performance_score
        color = "#0cce6b" if score >= 90 else "#ffa400" if score >= 50 else "#ff4e42"
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, score)

    @display(description="SEO")
    def seo_display(self, obj):
        if obj.seo_score is None:
            return "—"
        score = obj.seo_score
        color = "#0cce6b" if score >= 90 else "#ffa400" if score >= 50 else "#ff4e42"
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, score)

    @display(description="LCP (s)")
    def lcp_display(self, obj):
        if obj.lcp is None:
            return "—"
        lcp = obj.lcp
        color = "#0cce6b" if lcp <= 2.5 else "#ffa400" if lcp <= 4 else "#ff4e42"
        return format_html('<span style="color: {};">{:.2f}s</span>', color, lcp)

    @display(description="CLS")
    def cls_display(self, obj):
        if obj.cls is None:
            return "—"
        cls = obj.cls
        color = "#0cce6b" if cls <= 0.1 else "#ffa400" if cls <= 0.25 else "#ff4e42"
        return format_html('<span style="color: {};">{:.3f}</span>', color, cls)

    @display(description="TBT (ms)")
    def tbt_display(self, obj):
        if obj.tbt is None:
            return "—"
        tbt = obj.tbt
        color = "#0cce6b" if tbt <= 200 else "#ffa400" if tbt <= 600 else "#ff4e42"
        return format_html('<span style="color: {};">{:.0f}ms</span>', color, tbt)


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
                       'started_at', 'completed_at', 'ai_analysis', 'celery_task_id', 'created_at', 'updated_at')
    inlines = [PageAuditInline]
    date_hierarchy = 'created_at'
    actions = ['run_lighthouse_audit', 'run_pagespeed_analysis', 'generate_ai_analysis', 'generate_combined_ai_analysis', 'generate_pdf_report', 'preview_ai_data']

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
        ('⏰ Status & Timing', {
            'fields': ('status', 'celery_task_id', 'started_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @action(description="🔍 Run Lighthouse audit (Background)")
    def run_lighthouse_audit(self, request, queryset):
        """Queue Lighthouse audit to run in background via Celery."""
        from .tasks import run_lighthouse_audit_task

        for audit in queryset:
            # Update status to pending/queued
            audit.status = 'running'
            audit.save(update_fields=['status'])

            # Queue the task
            task = run_lighthouse_audit_task.delay(audit.id)

            # Store task ID for tracking
            audit.celery_task_id = task.id
            audit.save(update_fields=['celery_task_id'])

            url_count = len(audit.target_urls) if audit.target_urls else 1
            self.message_user(
                request,
                f"🚀 Lighthouse audit '{audit.name}' queued for {url_count} URLs. "
                f"Task ID: {task.id}. Refresh page to see progress.",
                messages.SUCCESS
            )

    @action(description="⚡ Run PageSpeed analysis (Background)")
    def run_pagespeed_analysis(self, request, queryset):
        """Queue PageSpeed analysis to run in background via Celery."""
        from .tasks import run_pagespeed_audit_task

        for audit in queryset:
            # Update status
            audit.status = 'running'
            audit.save(update_fields=['status'])

            # Queue the task
            task = run_pagespeed_audit_task.delay(audit.id)

            # Store task ID for tracking
            audit.celery_task_id = task.id
            audit.save(update_fields=['celery_task_id'])

            url_count = len(audit.target_urls) if audit.target_urls else 1
            self.message_user(
                request,
                f"🚀 PageSpeed analysis '{audit.name}' queued for {url_count} URLs. "
                f"Task ID: {task.id}. Refresh page to see progress.",
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

    @action(description="🔍 Preview AI Data (Debug)")
    def preview_ai_data(self, request, queryset):
        """Preview what data will be sent to AI for analysis - useful for debugging."""
        from django.http import JsonResponse
        from .services.seo_audit_ai import SEOAuditAIEngine
        import json

        audit = queryset.first()
        if not audit:
            self.message_user(request, "❌ No audit selected", messages.ERROR)
            return

        try:
            engine = SEOAuditAIEngine(audit)
            data = engine._gather_audit_data()

            # Count issues by category
            issue_counts = {cat: len(issues) for cat, issues in data.get('issues_by_category', {}).items()}

            # Summary message
            summary = (
                f"📊 Data Preview for '{audit.name}':\n"
                f"• Pages: {len(data.get('pages', []))}\n"
                f"• Performance issues: {issue_counts.get('performance', 0)}\n"
                f"• SEO issues: {issue_counts.get('seo', 0)}\n"
                f"• Accessibility issues: {issue_counts.get('accessibility', 0)}\n"
                f"• Best Practices issues: {issue_counts.get('best-practices', 0)}\n"
                f"• Total issues with details: {sum(1 for cat in data.get('issues_by_category', {}).values() for issue in cat if issue.get('details'))}"
            )

            self.message_user(request, summary, messages.INFO)

            # Return JSON response with full data for inspection
            return JsonResponse({
                'audit_name': audit.name,
                'data_summary': {
                    'pages_count': len(data.get('pages', [])),
                    'issue_counts': issue_counts,
                    'has_core_web_vitals': len(data.get('core_web_vitals', [])) > 0,
                },
                'site_audit': data.get('site_audit', {}),
                'pages': data.get('pages', []),
                'core_web_vitals': data.get('core_web_vitals', []),
                'issues_by_category': data.get('issues_by_category', {}),
            }, json_dumps_params={'indent': 2})

        except Exception as e:
            self.message_user(request, f"❌ Error gathering data: {str(e)}", messages.ERROR)

    @action(description="📄 Generate PDF Report")
    def generate_pdf_report(self, request, queryset):
        """Generate a professional PDF report for the selected audit."""
        from django.http import HttpResponse
        from .services.seo_report_pdf import generate_seo_audit_pdf
        import traceback
        import logging
        logger = logging.getLogger(__name__)

        audit = queryset.first()
        if not audit:
            self.message_user(request, "❌ No audit selected", messages.ERROR)
            return

        if not audit.total_pages or audit.total_pages == 0:
            self.message_user(
                request,
                "❌ No page audits found. Run a Lighthouse or PageSpeed audit first.",
                messages.ERROR
            )
            return

        try:
            pdf_content = generate_seo_audit_pdf(audit)

            # Create response with PDF
            filename = f"{audit.domain.replace('.', '_')}-seo-report-{audit.created_at.strftime('%Y%m%d')}.pdf"
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            self.message_user(
                request,
                f"✅ PDF report generated for '{audit.name}'",
                messages.SUCCESS
            )

            return response

        except Exception as e:
            # Log full traceback to console/logs
            tb = traceback.format_exc()
            logger.error(f"PDF generation error:\n{tb}")
            print(f"PDF generation error:\n{tb}")  # Also print to console
            self.message_user(request, f"❌ Error generating PDF: {str(e)}", messages.ERROR)

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
    actions = ['regenerate_ai_analysis', 'export_analysis_markdown', 'generate_pdf_report']
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

    @action(description="📄 Generate PDF Report")
    def generate_pdf_report(self, request, queryset):
        """Generate a professional PDF report for the selected audit."""
        from django.http import HttpResponse
        from .services.seo_report_pdf import generate_seo_audit_pdf
        import traceback
        import logging
        logger = logging.getLogger(__name__)

        audit = queryset.first()
        if not audit:
            self.message_user(request, "❌ No audit selected", messages.ERROR)
            return

        try:
            pdf_content = generate_seo_audit_pdf(audit)

            # Create response with PDF
            filename = f"{audit.domain.replace('.', '_')}-seo-report-{audit.created_at.strftime('%Y%m%d')}.pdf"
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except Exception as e:
            # Log full traceback to console/logs
            tb = traceback.format_exc()
            logger.error(f"PDF generation error:\n{tb}")
            print(f"PDF generation error:\n{tb}")  # Also print to console
            self.message_user(request, f"❌ Error generating PDF: {str(e)}", messages.ERROR)

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
    list_display = ('title', 'severity', 'category', 'page_url_display', 'display_value', 'savings_ms', 'status', 'created_at_display')
    list_filter = ('severity', 'category', 'status', 'page_audit__site_audit', 'created_at')
    search_fields = ('title', 'description', 'audit_id', 'page_audit__url')
    readonly_fields = ('audit_id', 'title', 'description', 'category', 'severity', 'score',
                       'display_value', 'savings_ms', 'savings_bytes', 'details', 'ai_fix_recommendation',
                       'created_at', 'updated_at')
    actions = ['mark_fixed', 'mark_ignored', 'generate_fix_recommendation']
    date_hierarchy = 'created_at'
    ordering = ['-created_at', 'severity', '-savings_ms']
    list_per_page = 50

    @display(description="Page URL", ordering='page_audit__url')
    def page_url_display(self, obj):
        """Display page URL with link and truncation."""
        if not obj.page_audit:
            return "—"
        url = obj.page_audit.url
        # Truncate long URLs for display
        display_url = url if len(url) <= 50 else url[:47] + '...'
        return format_html(
            '<a href="{}" target="_blank" title="{}" style="color: #6366F1;">{}</a>',
            url, url, display_url
        )

    @display(description="Found", ordering='created_at')
    def created_at_display(self, obj):
        """Display creation date in a readable format."""
        if obj.created_at:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
        return "—"

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
        ('📅 Timestamps', {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('collapse',)
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
    actions = ['run_pagespeed_analysis', 'generate_ai_recommendations']

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

    @action(description="🤖 Generate AI Recommendations")
    def generate_ai_recommendations(self, request, queryset):
        """Generate AI recommendations based on PageSpeed results."""
        from .services.ai_client import AIContentEngine
        from .models import SEORecommendation

        ai = AIContentEngine()
        if not ai.enabled:
            self.message_user(request, "❌ OpenAI API not configured. Set OPENAI_API_KEY.", messages.ERROR)
            return

        for record in queryset:
            if not record.lab_performance_score:
                self.message_user(request, f"⚠️ {record.url}: Run PageSpeed analysis first", messages.WARNING)
                continue

            try:
                # Build prompt with PageSpeed data
                prompt = f"""Analyze this PageSpeed Insights data and provide SEO/Performance recommendations:

URL: {record.url}
Strategy: {record.strategy}

SCORES:
- Performance: {record.lab_performance_score}/100

CORE WEB VITALS (Lab):
- LCP (Largest Contentful Paint): {record.lab_lcp}s (Good: <2.5s, Needs Improvement: 2.5-4s, Poor: >4s)
- CLS (Cumulative Layout Shift): {record.lab_cls} (Good: <0.1, Needs Improvement: 0.1-0.25, Poor: >0.25)
- TBT (Total Blocking Time): {record.lab_tbt}ms (Good: <200ms, Poor: >600ms)
- FCP (First Contentful Paint): {record.lab_fcp}s
- Speed Index: {record.lab_si}s

REAL USER DATA (CrUX):
- Field LCP: {record.field_lcp or 'N/A'}s
- Field CLS: {record.field_cls or 'N/A'}
- Field INP: {record.field_inp or 'N/A'}ms
- Overall Category: {record.overall_category or 'N/A'}

Provide:
1. PRIORITY ISSUES (top 3 things to fix immediately)
2. QUICK WINS (easy improvements)
3. SPECIFIC CODE RECOMMENDATIONS (what to optimize)
4. ESTIMATED IMPACT (how much scores could improve)

Be specific and actionable. Focus on the worst metrics first."""

                result = ai.generate(prompt=prompt, temperature=0.3)

                if result.get('success'):
                    # Save recommendation
                    SEORecommendation.objects.create(
                        target_url=record.url,
                        recommendation_type='technical_fix',
                        title=f"PageSpeed Analysis: {record.url}",
                        current_value=f"Performance: {record.lab_performance_score}/100",
                        recommended_value=result.get('output', ''),
                        reasoning=f"Generated from PageSpeed Insights analysis on {record.strategy}",
                        priority='high' if record.lab_performance_score < 50 else 'medium',
                        status='pending',
                        ai_model=result.get('model', 'gpt-4o-mini'),
                        ai_tokens_used=result.get('usage', {}).get('total_tokens', 0),
                    )
                    self.message_user(
                        request,
                        f"✅ AI recommendations generated for {record.url}",
                        messages.SUCCESS
                    )
                else:
                    self.message_user(request, f"❌ AI failed for {record.url}: {result.get('error')}", messages.ERROR)

            except Exception as e:
                self.message_user(request, f"❌ Error: {str(e)}", messages.ERROR)

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


# =============================================================================
# UBERSUGGEST INTEGRATION
# =============================================================================

class SEOCompetitorInline(TabularInline):
    model = SEOCompetitor
    extra = 0
    fields = ('domain', 'domain_score', 'organic_keywords', 'monthly_traffic', 'is_primary')
    readonly_fields = ('domain_score', 'organic_keywords', 'monthly_traffic')


class SEODataUploadInline(TabularInline):
    model = SEODataUpload
    extra = 0
    fields = ('name', 'source', 'status', 'row_count', 'processed_at')
    readonly_fields = ('status', 'row_count', 'processed_at')


@admin.register(SEOProject)
class SEOProjectAdmin(ModelAdmin):
    list_display = ('name', 'domain', 'status', 'domain_score', 'organic_keywords', 'monthly_traffic', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'domain')
    readonly_fields = ('domain_score', 'organic_keywords', 'monthly_traffic', 'backlinks_count', 'created_at', 'updated_at')
    inlines = [SEOCompetitorInline, SEODataUploadInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('📁 Project Info', {
            'fields': ('name', 'domain', 'status', 'target_country', 'target_language')
        }),
        ('📊 Domain Metrics (from Ubersuggest)', {
            'fields': ('domain_score', 'organic_keywords', 'monthly_traffic', 'backlinks_count'),
            'classes': ('collapse',)
        }),
        ('🎯 Goals', {
            'fields': ('target_traffic', 'target_keywords'),
            'classes': ('collapse',)
        }),
        ('📅 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    class Meta:
        verbose_name_plural = "🔍 Ubersuggest: Projects"


class SEOCompetitorKeywordInline(TabularInline):
    model = SEOCompetitorKeyword
    extra = 0
    fields = ('keyword', 'position', 'search_volume', 'is_content_gap', 'opportunity_score')
    readonly_fields = ('keyword', 'position', 'search_volume', 'is_content_gap', 'opportunity_score')
    ordering = ('-opportunity_score',)
    max_num = 20


@admin.register(SEOCompetitor)
class SEOCompetitorAdmin(ModelAdmin):
    list_display = ('domain', 'project', 'domain_score', 'organic_keywords', 'monthly_traffic', 'is_primary', 'updated_at')
    list_filter = ('project', 'is_primary')
    search_fields = ('domain', 'project__name')
    readonly_fields = ('domain_score', 'organic_keywords', 'monthly_traffic', 'backlinks_count', 'metrics_updated_at', 'created_at', 'updated_at')
    autocomplete_fields = ('project',)
    inlines = [SEOCompetitorKeywordInline]
    ordering = ('-domain_score',)

    fieldsets = (
        ('🏢 Competitor Info', {
            'fields': ('project', 'domain', 'name', 'is_primary', 'notes')
        }),
        ('📊 Metrics', {
            'fields': ('domain_score', 'organic_keywords', 'monthly_traffic', 'backlinks_count', 'metrics_updated_at')
        }),
        ('📅 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    class Meta:
        verbose_name_plural = "🔍 Ubersuggest: Competitors"


@admin.register(SEOCompetitorKeyword)
class SEOCompetitorKeywordAdmin(ModelAdmin):
    list_display = ('keyword', 'competitor', 'position', 'search_volume', 'is_content_gap', 'opportunity_score')
    list_filter = ('competitor__project', 'competitor', 'is_content_gap')
    search_fields = ('keyword', 'competitor__domain')
    readonly_fields = ('opportunity_score', 'created_at', 'updated_at')
    autocomplete_fields = ('competitor',)
    ordering = ('-opportunity_score', '-search_volume')

    class Meta:
        verbose_name_plural = "🔍 Ubersuggest: Competitor Keywords"


@admin.register(SEOBacklinkOpportunity)
class SEOBacklinkOpportunityAdmin(ModelAdmin):
    list_display = ('source_domain', 'project', 'domain_authority', 'opportunity_type', 'status', 'priority_score', 'updated_at')
    list_filter = ('project', 'opportunity_type', 'status')
    search_fields = ('source_domain', 'source_url', 'source_title')
    readonly_fields = ('priority_score', 'created_at', 'updated_at')
    autocomplete_fields = ('project',)
    ordering = ('-priority_score', '-domain_authority')

    fieldsets = (
        ('🔗 Link Info', {
            'fields': ('project', 'source_domain', 'source_url', 'source_title', 'opportunity_type')
        }),
        ('📊 Quality Metrics', {
            'fields': ('domain_authority', 'page_authority', 'priority_score')
        }),
        ('📋 Outreach', {
            'fields': ('status', 'contact_email', 'contact_name', 'outreach_date', 'follow_up_date', 'notes')
        }),
        ('📅 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_contacted', 'mark_as_acquired']

    @action(description="✉️ Mark as Contacted")
    def mark_as_contacted(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='contacted', outreach_date=timezone.now().date())
        self.message_user(request, f'{updated} opportunities marked as contacted', messages.SUCCESS)

    @action(description="✅ Mark as Acquired")
    def mark_as_acquired(self, request, queryset):
        updated = queryset.update(status='acquired')
        self.message_user(request, f'{updated} backlinks marked as acquired', messages.SUCCESS)

    class Meta:
        verbose_name_plural = "🔍 Ubersuggest: Backlink Opportunities"


@admin.register(SEOKeywordRank)
class SEOKeywordRankAdmin(ModelAdmin):
    list_display = ('keyword', 'project', 'position', 'previous_position', 'change_display', 'search_volume', 'date')
    list_filter = ('project', 'date')
    search_fields = ('keyword', 'project__name')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('project',)
    date_hierarchy = 'date'
    ordering = ('-date', 'position')

    def change_display(self, obj):
        if obj.position_change is None or obj.position_change == 0:
            return "—"
        if obj.position_change > 0:  # Positive = improved (moved up)
            return format_html('<span style="color: green;">▲ {}</span>', obj.position_change)
        return format_html('<span style="color: red;">▼ {}</span>', abs(obj.position_change))
    change_display.short_description = "Change"

    class Meta:
        verbose_name_plural = "🔍 Ubersuggest: Keyword Rankings"


@admin.register(SEOContentGap)
class SEOContentGapAdmin(ModelAdmin):
    list_display = ('keyword', 'project', 'best_competitor_position', 'search_volume', 'opportunity_score', 'priority', 'status')
    list_filter = ('project', 'priority', 'status')
    search_fields = ('keyword', 'project__name')
    readonly_fields = ('opportunity_score', 'competitors_ranking', 'created_at', 'updated_at')
    autocomplete_fields = ('project',)
    ordering = ('-opportunity_score', '-search_volume')

    fieldsets = (
        ('🎯 Gap Info', {
            'fields': ('project', 'keyword', 'search_volume', 'seo_difficulty', 'cpc')
        }),
        ('📊 Competitor Positions', {
            'fields': ('best_competitor_position', 'competitors_ranking')
        }),
        ('📝 Content Planning', {
            'fields': ('suggested_content_type', 'content_brief', 'target_url')
        }),
        ('⭐ Priority', {
            'fields': ('opportunity_score', 'priority', 'status')
        }),
        ('📅 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_in_progress', 'mark_as_published']

    @action(description="🔄 Mark as In Progress")
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} content gaps marked as in progress', messages.SUCCESS)

    @action(description="✅ Mark as Published")
    def mark_as_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} content gaps marked as published', messages.SUCCESS)

    class Meta:
        verbose_name_plural = "🔍 Ubersuggest: Content Gaps"


# =============================================================================
# CELERY ADMIN OVERRIDES (Using Unfold for consistent styling)
# =============================================================================

# Override django_celery_results admin
try:
    from django_celery_results.models import TaskResult, GroupResult
    from django_celery_results.admin import TaskResultAdmin as OriginalTaskResultAdmin

    # Unregister the default admin
    admin.site.unregister(TaskResult)
    admin.site.unregister(GroupResult)

    @admin.register(TaskResult)
    class TaskResultAdmin(ModelAdmin):
        list_display = ('task_id', 'task_name', 'status_badge', 'date_done', 'worker')
        list_filter = ('status', 'task_name', 'worker', 'date_done')
        search_fields = ('task_id', 'task_name')
        readonly_fields = ('task_id', 'task_name', 'task_args', 'task_kwargs', 'status',
                          'content_type', 'content_encoding', 'result', 'date_created',
                          'date_done', 'traceback', 'meta', 'worker')
        ordering = ['-date_done']

        fieldsets = (
            ('Task Info', {
                'fields': ('task_id', 'task_name', 'status', 'worker')
            }),
            ('Arguments', {
                'fields': ('task_args', 'task_kwargs'),
                'classes': ['collapse']
            }),
            ('Result', {
                'fields': ('result', 'traceback', 'meta'),
            }),
            ('Timestamps', {
                'fields': ('date_created', 'date_done'),
                'classes': ['collapse']
            }),
        )

        def has_add_permission(self, request):
            return False

        def has_change_permission(self, request, obj=None):
            return False

        @display(description="Status", label=True)
        def status_badge(self, obj):
            colors = {
                'SUCCESS': 'success',
                'FAILURE': 'danger',
                'PENDING': 'warning',
                'STARTED': 'info',
                'RETRY': 'warning',
                'REVOKED': 'secondary',
            }
            return obj.status, colors.get(obj.status, 'info')

    @admin.register(GroupResult)
    class GroupResultAdmin(ModelAdmin):
        list_display = ('group_id', 'date_done')
        list_filter = ('date_done',)
        search_fields = ('group_id',)
        readonly_fields = ('group_id', 'date_created', 'date_done', 'content_type',
                          'content_encoding', 'result')
        ordering = ['-date_done']

        def has_add_permission(self, request):
            return False

        def has_change_permission(self, request, obj=None):
            return False

except ImportError:
    pass  # django_celery_results not installed


# Override django_celery_beat admin
try:
    from django_celery_beat.models import (
        PeriodicTask, IntervalSchedule, CrontabSchedule,
        SolarSchedule, ClockedSchedule, PeriodicTasks
    )
    from django_celery_beat import admin as celery_beat_admin

    # Unregister all default celery beat admin classes
    admin.site.unregister(PeriodicTask)
    admin.site.unregister(IntervalSchedule)
    admin.site.unregister(CrontabSchedule)
    admin.site.unregister(SolarSchedule)
    admin.site.unregister(ClockedSchedule)

    @admin.register(PeriodicTask)
    class PeriodicTaskAdmin(ModelAdmin):
        list_display = ('name', 'task', 'enabled_badge', 'schedule_display', 'last_run_at', 'total_run_count')
        list_filter = ('enabled', 'task', 'one_off')
        search_fields = ('name', 'task')
        ordering = ['name']
        actions = ['enable_tasks', 'disable_tasks', 'run_tasks']

        fieldsets = (
            ('Task Settings', {
                'fields': ('name', 'task', 'enabled', 'one_off', 'description')
            }),
            ('Schedule', {
                'fields': ('interval', 'crontab', 'solar', 'clocked', 'start_time', 'expires'),
                'description': 'Set one type of schedule (interval, crontab, solar, or clocked)'
            }),
            ('Arguments', {
                'fields': ('args', 'kwargs'),
                'classes': ['collapse']
            }),
            ('Execution Options', {
                'fields': ('queue', 'exchange', 'routing_key', 'headers', 'priority'),
                'classes': ['collapse']
            }),
            ('Run Info', {
                'fields': ('last_run_at', 'total_run_count', 'date_changed'),
                'classes': ['collapse']
            }),
        )

        readonly_fields = ('last_run_at', 'total_run_count', 'date_changed')

        @display(description="Enabled", label=True)
        def enabled_badge(self, obj):
            if obj.enabled:
                return "Yes", "success"
            return "No", "danger"

        @display(description="Schedule")
        def schedule_display(self, obj):
            if obj.interval:
                return f"Every {obj.interval}"
            if obj.crontab:
                return f"Cron: {obj.crontab}"
            if obj.solar:
                return f"Solar: {obj.solar}"
            if obj.clocked:
                return f"Clocked: {obj.clocked}"
            return "No schedule"

        @action(description="Enable selected tasks")
        def enable_tasks(self, request, queryset):
            updated = queryset.update(enabled=True)
            self.message_user(request, f"Enabled {updated} task(s)")

        @action(description="Disable selected tasks")
        def disable_tasks(self, request, queryset):
            updated = queryset.update(enabled=False)
            self.message_user(request, f"Disabled {updated} task(s)")

        @action(description="Run selected tasks now")
        def run_tasks(self, request, queryset):
            from celery import current_app
            ran = 0
            for task in queryset:
                try:
                    args = json.loads(task.args or '[]')
                    kwargs = json.loads(task.kwargs or '{}')
                    current_app.send_task(task.task, args=args, kwargs=kwargs)
                    ran += 1
                except Exception as e:
                    self.message_user(request, f"Failed to run {task.name}: {e}", messages.ERROR)
            if ran:
                self.message_user(request, f"Triggered {ran} task(s)")

    @admin.register(IntervalSchedule)
    class IntervalScheduleAdmin(ModelAdmin):
        list_display = ('__str__', 'every', 'period')
        list_filter = ('period',)
        ordering = ['period', 'every']

    @admin.register(CrontabSchedule)
    class CrontabScheduleAdmin(ModelAdmin):
        list_display = ('__str__', 'minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year')
        ordering = ['month_of_year', 'day_of_month', 'day_of_week', 'hour', 'minute']

    @admin.register(SolarSchedule)
    class SolarScheduleAdmin(ModelAdmin):
        list_display = ('__str__', 'event', 'latitude', 'longitude')
        list_filter = ('event',)
        ordering = ['event']

    @admin.register(ClockedSchedule)
    class ClockedScheduleAdmin(ModelAdmin):
        list_display = ('__str__', 'clocked_time')
        ordering = ['-clocked_time']

except ImportError:
    pass  # django_celery_beat not installed


# =============================================================================
# AUTH ADMIN OVERRIDES (Using Unfold for consistent styling)
# =============================================================================

from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin

# Unregister default auth admin
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """User admin with Unfold styling."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    """Group admin with Unfold styling."""
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
