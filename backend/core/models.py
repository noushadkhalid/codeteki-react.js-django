import uuid

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from ckeditor.fields import RichTextField

from .fields import WebPImageField, OptimizedImageField, ThumbnailImageField


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class HeroSection(TimestampedModel):
    PAGE_CHOICES = [
        ("home", "Home Page"),
        ("services", "Services Page"),
        ("ai-tools", "AI Tools Page"),
        ("demos", "Demos Page"),
        ("faq", "FAQ Page"),
        ("contact", "Contact Page"),
    ]

    page = models.CharField(
        max_length=30,
        choices=PAGE_CHOICES,
        default="home",
        help_text="Landing page this hero should be displayed on.",
    )

    badge = models.CharField(max_length=120)
    badge_emoji = models.CharField(max_length=12, default="🚀")
    title = models.CharField(max_length=255)
    highlighted_text = models.CharField(max_length=120)
    highlight_gradient_from = models.CharField(max_length=12, default="#f9cb07")
    highlight_gradient_to = models.CharField(max_length=12, default="#ff6b35")
    subheading = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    primary_cta_label = models.CharField(max_length=80)
    primary_cta_href = models.CharField(max_length=200)
    secondary_cta_label = models.CharField(max_length=80)
    secondary_cta_href = models.CharField(max_length=200)
    image_url = models.URLField(blank=True)
    media = OptimizedImageField(upload_to="hero/", blank=True, null=True)
    background_pattern = models.CharField(max_length=60, default="sunrise-glow")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Hero Section"
        ordering = ["page", "-updated_at"]

    def __str__(self):
        return f"{self.title} ({self.page})"

    @property
    def media_url(self):
        if self.media:
            return self.media.url
        return self.image_url


class HeroMetric(models.Model):
    hero = models.ForeignKey(
        HeroSection, related_name="metrics", on_delete=models.CASCADE
    )
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=60)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.value} {self.label}"


class HeroPartnerLogo(models.Model):
    hero = models.ForeignKey(
        HeroSection, related_name="partner_logos", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=120)
    logo_url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class BusinessImpactSection(TimestampedModel):
    title = models.CharField(max_length=160)
    description = models.TextField()
    cta_label = models.CharField(max_length=80)
    cta_href = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Business Impact Section"

    def __str__(self):
        return self.title


class BusinessImpactMetric(models.Model):
    section = models.ForeignKey(
        BusinessImpactSection, related_name="metrics", on_delete=models.CASCADE
    )
    value = models.CharField(max_length=40)
    label = models.CharField(max_length=120)
    caption = models.CharField(max_length=255)
    icon = models.CharField(max_length=40, default="MessageCircle")
    theme_bg_class = models.CharField(max_length=40, default="bg-blue-100")
    theme_text_class = models.CharField(max_length=40, default="text-blue-600")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.value} {self.label}"


class BusinessImpactLogo(models.Model):
    section = models.ForeignKey(
        BusinessImpactSection, related_name="logos", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=120)
    logo_url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Service(TimestampedModel):
    # Basic info (for cards/listing)
    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    badge = models.CharField(max_length=120, blank=True, help_text="Short badge text e.g. 'Enterprise Ready'")
    description = models.TextField(help_text="Short description for service cards")
    icon = models.CharField(max_length=40, default="Sparkles", help_text="Lucide icon name")
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    # Detail page content
    tagline = models.CharField(max_length=160, blank=True, help_text="Short tagline shown in hero badge")
    subtitle = models.CharField(max_length=255, blank=True, help_text="Longer subtitle for hero section")
    full_description = models.TextField(blank=True, help_text="Full description for the Overview section")
    hero_image = WebPImageField(upload_to='services/', blank=True, null=True, help_text="Hero image for detail page")
    hero_image_url = models.URLField(blank=True, help_text="Or use external image URL")

    # Styling
    gradient_from = models.CharField(max_length=30, default="purple-600", help_text="Tailwind gradient start e.g. 'purple-600'")
    gradient_to = models.CharField(max_length=30, default="indigo-600", help_text="Tailwind gradient end e.g. 'indigo-600'")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title

    @property
    def hero_image_src(self):
        """Return hero image URL from either upload or external URL."""
        if self.hero_image:
            return self.hero_image.url
        return self.hero_image_url or ""


class ServiceOutcome(models.Model):
    """Features/outcomes shown on service cards (short list)."""
    service = models.ForeignKey(
        Service, related_name="outcomes", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Service Feature (Card)"
        verbose_name_plural = "Service Features (Card)"

    def __str__(self):
        return self.text


class ServiceFeature(models.Model):
    """Detailed features for the service detail page (8 items grid)."""
    service = models.ForeignKey(
        Service, related_name="features", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Service Feature (Detail Page)"
        verbose_name_plural = "Service Features (Detail Page)"

    def __str__(self):
        return self.text


class ServiceCapability(models.Model):
    """Capability cards with icon, title, and description."""
    service = models.ForeignKey(
        Service, related_name="capabilities", on_delete=models.CASCADE
    )
    icon = models.CharField(max_length=40, default="Sparkles", help_text="Lucide icon name")
    title = models.CharField(max_length=120)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Service Capability"
        verbose_name_plural = "Service Capabilities"

    def __str__(self):
        return self.title


class ServiceBenefit(models.Model):
    """Benefits list for the 'Why Choose Us' section."""
    service = models.ForeignKey(
        Service, related_name="benefits", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Service Benefit"
        verbose_name_plural = "Service Benefits"

    def __str__(self):
        return self.text


class ServiceProcess(models.Model):
    """Process steps specific to each service."""
    service = models.ForeignKey(
        Service, related_name="process_steps", on_delete=models.CASCADE
    )
    step_number = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=120)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "step_number"]
        verbose_name = "Service Process Step"
        verbose_name_plural = "Service Process Steps"

    def __str__(self):
        return f"{self.step_number}. {self.title}"


# Legacy: Global process steps (kept for backwards compatibility)
class ServiceProcessStep(TimestampedModel):
    title = models.CharField(max_length=160)
    description = models.TextField()
    icon = models.CharField(max_length=40, default="Sparkles")
    accent = models.CharField(max_length=20, default="blue", help_text="Tailwind-friendly color keyword")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Global Process Step (Legacy)"

    def __str__(self):
        return self.title


# FAQ Page Section (Hero/Header)
class FAQPageSection(TimestampedModel):
    badge = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200, default='FAQ Hub')
    description = models.TextField(default='Answers for every stage of your AI journey')
    search_placeholder = models.CharField(max_length=100, default='Search FAQs...')
    cta_text = models.CharField(max_length=100, default='Book strategy call')
    cta_url = models.CharField(max_length=255, default='/contact')
    secondary_cta_text = models.CharField(max_length=100, blank=True, default='Still stuck? Message the team')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "FAQ Page Section"
        verbose_name_plural = "FAQ Page Sections"

    def __str__(self):
        return self.title


class FAQPageStat(models.Model):
    section = models.ForeignKey(FAQPageSection, related_name='stats', on_delete=models.CASCADE)
    value = models.CharField(max_length=60, help_text='e.g., < 24 hrs, 80+, 14')
    label = models.CharField(max_length=120, help_text='e.g., Average response time')
    detail = models.CharField(max_length=200, blank=True, help_text='Additional detail text')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'FAQ Page Stat'

    def __str__(self):
        return f"{self.value} - {self.label}"


class FAQCategory(TimestampedModel):
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True, help_text='Category description')
    icon = models.CharField(max_length=40, blank=True, help_text='Icon name for the category')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "FAQ Category"

    def __str__(self):
        return self.title


class FAQItem(models.Model):
    category = models.ForeignKey(
        FAQCategory, related_name="items", on_delete=models.CASCADE
    )
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.question


class ContactMethod(TimestampedModel):
    title = models.CharField(max_length=160)
    description = models.CharField(max_length=255)
    value = models.CharField(max_length=120)
    cta_label = models.CharField(max_length=80)
    icon = models.CharField(max_length=40, default="Mail")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Contact Method"

    def __str__(self):
        return self.title


class ContactInquiry(TimestampedModel):
    STATUS_NEW = "new"
    STATUS_REVIEWED = "reviewed"
    STATUS_CONTACTED = "contacted"
    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_REVIEWED, "Reviewed"),
        (STATUS_CONTACTED, "Contacted"),
    ]

    name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    service = models.CharField(max_length=120, blank=True)
    message = models.TextField()
    source = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Inquiry"

    def __str__(self):
        return f"{self.name} - {self.email}"


# ROI Calculator Section
class ROICalculatorSection(TimestampedModel):
    badge = models.CharField(max_length=120, default="Smart Business Calculator")
    title = models.CharField(max_length=255)
    highlighted_text = models.CharField(max_length=120)
    description = RichTextField()
    subtitle = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "ROI Calculator Section"

    def __str__(self):
        return self.title


class ROICalculatorStat(models.Model):
    section = models.ForeignKey(
        ROICalculatorSection, related_name="stats", on_delete=models.CASCADE
    )
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=60)
    detail = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.value} - {self.label}"


class ROICalculatorTool(models.Model):
    section = models.ForeignKey(
        ROICalculatorSection, related_name="tools", on_delete=models.CASCADE
    )
    tool_id = models.CharField(max_length=40, unique=True)
    label = models.CharField(max_length=120)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "ROI Calculator Tool"

    def __str__(self):
        return self.label


# AI Tools Section
class AIToolsSection(TimestampedModel):
    badge = models.CharField(max_length=120, default="Free AI Tools")
    title = models.CharField(max_length=255)
    description = RichTextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "AI Tools Section"

    def __str__(self):
        return self.title


class AITool(TimestampedModel):
    section = models.ForeignKey(
        AIToolsSection, related_name="tools", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=40, default="Zap")
    color = models.CharField(max_length=40, default="blue", help_text="Color theme for the tool card")
    emoji = models.CharField(max_length=8, blank=True, help_text="Optional emoji badge")
    category = models.CharField(max_length=40, default="general")
    status = models.CharField(
        max_length=20,
        choices=[("free", "Free"), ("credits", "Credits"), ("premium", "Premium")],
        default="free",
    )
    badge = models.CharField(max_length=80, blank=True)
    external_url = models.URLField(blank=True)
    preview_url = models.URLField(blank=True)
    cta_label = models.CharField(max_length=80, blank=True)
    cta_url = models.URLField(blank=True)
    secondary_cta_label = models.CharField(max_length=80, blank=True)
    secondary_cta_url = models.URLField(blank=True)
    min_credits = models.PositiveIntegerField(default=0)
    credit_cost = models.PositiveIntegerField(default=0)
    is_coming_soon = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "AI Tool"

    def __str__(self):
        return self.title


# Why Choose Us Section
class WhyChooseSection(TimestampedModel):
    badge = models.CharField(max_length=120, default="Why Choose Codeteki")
    title = models.CharField(max_length=255)
    description = RichTextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Why Choose Us Section"

    def __str__(self):
        return self.title


class WhyChooseReason(models.Model):
    section = models.ForeignKey(
        WhyChooseSection, related_name="reasons", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=160)
    description = models.TextField()
    icon = models.CharField(max_length=40, default="CheckCircle")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


# Footer Section
class FooterSection(TimestampedModel):
    company_name = models.CharField(max_length=160, default="Codeteki Digital Services")
    company_description = models.TextField()
    logo = WebPImageField(upload_to='footer/', blank=True, null=True)
    abn = models.CharField(max_length=100, blank=True)

    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)

    # Copyright
    copyright_text = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Footer Section"

    def __str__(self):
        return self.company_name


class FooterLink(models.Model):
    COLUMN_CHOICES = [
        ('services', 'Services Column'),
        ('company', 'Company Column'),
        ('contact', 'Contact Column'),
    ]

    section = models.ForeignKey(
        FooterSection, related_name="links", on_delete=models.CASCADE
    )
    column = models.CharField(max_length=20, choices=COLUMN_CHOICES)
    title = models.CharField(max_length=120)
    url = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["column", "order"]

    def __str__(self):
        return f"{self.column} - {self.title}"


# Site Settings (Global Settings)
class SiteSettings(TimestampedModel):
    # Site Info
    site_name = models.CharField(max_length=160, default="Codeteki")
    site_tagline = models.CharField(max_length=255, blank=True)
    site_description = models.TextField(blank=True)

    # Logos
    logo = WebPImageField(upload_to='site/', blank=True, null=True, help_text="Main logo")
    logo_dark = WebPImageField(upload_to='site/', blank=True, null=True, help_text="Logo for dark backgrounds")
    favicon = WebPImageField(upload_to='site/', blank=True, null=True, convert_to_webp=False)

    # Contact Information
    primary_email = models.EmailField(blank=True)
    secondary_email = models.EmailField(blank=True)
    primary_phone = models.CharField(max_length=20, blank=True)
    secondary_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    support_badge = models.CharField(max_length=160, default="We respond within 24 hours")
    support_response_value = models.CharField(max_length=60, default="< 24 hrs")
    support_response_label = models.CharField(max_length=120, default="Average response time")
    support_response_helper = models.CharField(max_length=160, default="Based on care plan")
    support_response_message = models.CharField(max_length=180, default="Get a response within 24 hours")
    support_response_confirmation = models.CharField(
        max_length=200, default="We'll contact you within 24 hours to confirm your consultation."
    )

    # Social Media
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    github = models.URLField(blank=True)

    # Business Info
    abn = models.CharField(max_length=100, blank=True, verbose_name="ABN")
    business_hours = models.TextField(blank=True)

    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True)
    facebook_pixel_id = models.CharField(max_length=50, blank=True)

    # Default SEO / Social Sharing
    default_og_image = OptimizedImageField(
        upload_to='site/',
        blank=True,
        null=True,
        webp_max_size=(1200, 630),
        help_text="Default image for social sharing (1200x630). Used when pages don't have their own OG image."
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name


class SocialLink(models.Model):
    """Dynamic social links - add any social platform."""
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter / X'),
        ('linkedin', 'LinkedIn'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('github', 'GitHub'),
        ('tiktok', 'TikTok'),
        ('pinterest', 'Pinterest'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('discord', 'Discord'),
        ('snapchat', 'Snapchat'),
        ('threads', 'Threads'),
        ('other', 'Other'),
    ]

    footer_section = models.ForeignKey(
        FooterSection,
        on_delete=models.CASCADE,
        related_name='social_links'
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField()
    custom_label = models.CharField(max_length=50, blank=True, help_text="Custom label for 'Other' platform")
    icon = models.CharField(max_length=50, blank=True, help_text="Custom icon name (Lucide icon)")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"

    def __str__(self):
        return f"{self.get_platform_display()}: {self.url}"


class BusinessHours(models.Model):
    """Business hours with proper form fields instead of JSON."""
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
        ('monday_friday', 'Monday - Friday'),
        ('weekends', 'Weekends'),
    ]

    site_settings = models.ForeignKey(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name='hours'
    )
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    hours = models.CharField(
        max_length=100,
        help_text="e.g., '9:00 AM - 6:00 PM AEDT' or 'Closed' or 'By appointment'"
    )
    is_closed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Business Hours"
        verbose_name_plural = "Business Hours"

    def __str__(self):
        return f"{self.get_day_display()}: {self.hours}"


# SEO Meta for different pages
class PageSEO(TimestampedModel):
    """
    SEO settings for any page - static pages or dynamic (service details, blog posts).
    """
    PAGE_CHOICES = [
        ('home', 'Home Page'),
        ('services', 'Services Page'),
        ('ai-tools', 'AI Tools Page'),
        ('demos', 'Demos Page'),
        ('faq', 'FAQ Page'),
        ('contact', 'Contact Page'),
        ('custom', 'Custom URL'),
    ]

    # Page identification - either preset or custom URL
    page = models.CharField(max_length=50, choices=PAGE_CHOICES, default='custom')
    custom_url = models.CharField(
        max_length=255, blank=True,
        help_text="For dynamic pages like /services/ai-chatbots or /blog/my-post"
    )

    # Link to specific content (optional)
    service = models.OneToOneField(
        'Service', on_delete=models.CASCADE, null=True, blank=True,
        related_name='seo_settings',
        help_text="Link to a service for auto-URL"
    )
    blog_post = models.OneToOneField(
        'BlogPost', on_delete=models.CASCADE, null=True, blank=True,
        related_name='seo_settings',
        help_text="Link to a blog post for auto-URL"
    )

    # Core SEO fields
    meta_title = models.CharField(max_length=160)
    meta_description = models.TextField(max_length=320)
    meta_keywords = models.TextField(blank=True, help_text="Comma separated keywords")
    canonical_url = models.URLField(blank=True)

    # Open Graph
    og_title = models.CharField(max_length=160, blank=True, verbose_name="Open Graph Title")
    og_description = models.TextField(max_length=320, blank=True)
    og_image = OptimizedImageField(upload_to='seo/', blank=True, null=True, webp_max_size=(1200, 630))

    # Track which AI recommendation this came from
    source_recommendation = models.ForeignKey(
        'AISEORecommendation', on_delete=models.SET_NULL, null=True, blank=True,
        help_text="AI recommendation that generated this SEO"
    )
    target_keyword = models.CharField(max_length=255, blank=True, help_text="Primary keyword being targeted")

    class Meta:
        verbose_name = "Page SEO"
        verbose_name_plural = "Page SEO Settings"

    def __str__(self):
        if self.service:
            return f"SEO - Service: {self.service.title}"
        if self.blog_post:
            return f"SEO - Blog: {self.blog_post.title}"
        if self.custom_url:
            return f"SEO - {self.custom_url}"
        return f"SEO - {self.get_page_display()}"

    @property
    def target_url(self):
        """Get the URL this SEO applies to."""
        if self.service:
            return f"/services/{self.service.slug}"
        if self.blog_post:
            return f"/blog/{self.blog_post.slug}"
        if self.custom_url:
            return self.custom_url
        return f"/{self.page}" if self.page != 'home' else "/"

    @property
    def effective_og_image(self):
        """Get OG image - falls back to site default if not set."""
        if self.og_image:
            return self.og_image
        # Fall back to site default
        try:
            site_settings = SiteSettings.objects.first()
            if site_settings and site_settings.default_og_image:
                return site_settings.default_og_image
        except Exception:
            pass
        return None

    @property
    def effective_og_title(self):
        """Get OG title - falls back to meta title if not set."""
        return self.og_title or self.meta_title

    @property
    def effective_og_description(self):
        """Get OG description - falls back to meta description if not set."""
        return self.og_description or self.meta_description


# Testimonials
class Testimonial(TimestampedModel):
    name = models.CharField(max_length=160)
    position = models.CharField(max_length=160, blank=True)
    company = models.CharField(max_length=160, blank=True)
    image = ThumbnailImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=5, help_text="Rating out of 5")
    content = models.TextField()
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-is_featured", "order"]

    def __str__(self):
        return f"{self.name} - {self.company}"


# Call-to-Action Sections
class CTASection(TimestampedModel):
    PLACEMENT_CHOICES = [
        ('home', 'Home Page'),
        ('services', 'Services Page'),
        ('ai-tools', 'AI Tools Page'),
        ('demos', 'Demos Page'),
        ('global', 'All Pages'),
    ]

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    primary_button_text = models.CharField(max_length=80)
    primary_button_url = models.CharField(max_length=255)
    secondary_button_text = models.CharField(max_length=80, blank=True)
    secondary_button_url = models.CharField(max_length=255, blank=True)
    background_color = models.CharField(max_length=40, default="#f9cb07")
    text_color = models.CharField(max_length=40, default="#000000")
    placement = models.CharField(max_length=20, choices=PLACEMENT_CHOICES)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["placement", "order"]
        verbose_name = "Call-to-Action Section"

    def __str__(self):
        return f"{self.title} ({self.get_placement_display()})"


# Demos/Showcase
class DemoShowcase(TimestampedModel):
    STATUS_LIVE = "live"
    STATUS_COMING_SOON = "coming_soon"
    STATUS_IN_DEVELOPMENT = "in_development"
    STATUS_PLANNING = "planning"
    STATUS_CHOICES = [
        (STATUS_LIVE, "Live Demo"),
        (STATUS_COMING_SOON, "Coming Soon"),
        (STATUS_IN_DEVELOPMENT, "In Development"),
        (STATUS_PLANNING, "Planning"),
    ]

    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    full_description = RichTextField()
    thumbnail = ThumbnailImageField(upload_to='demos/', help_text="Main image for the demo")
    demo_url = models.URLField(blank=True, help_text="Link to live demo")
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    client_name = models.CharField(max_length=160, blank=True)
    client_logo = ThumbnailImageField(upload_to='demos/clients/', blank=True, null=True)
    technologies_used = models.TextField(blank=True, help_text="Comma separated list")
    completion_date = models.DateField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    industry = models.CharField(max_length=120, blank=True)
    icon = models.CharField(max_length=40, default="Sparkles", help_text="Lucide icon name")
    color_class = models.CharField(max_length=60, default="bg-blue-500", help_text="Tailwind class for icon background")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_COMING_SOON)
    features = models.TextField(blank=True, help_text="One feature per line")
    feature_count = models.PositiveIntegerField(default=0, help_text="Optional count for additional features")
    highlight_badge = models.CharField(max_length=80, blank=True)
    screenshot = OptimizedImageField(upload_to='demos/screenshots/', blank=True, null=True)

    class Meta:
        ordering = ["-is_featured", "order"]
        verbose_name = "Demo Showcase"
        verbose_name_plural = "Demo Showcases"

    def __str__(self):
        return self.title

    def feature_list(self):
        lines = [line.strip() for line in (self.features or "").splitlines() if line.strip()]
        return lines


class DemoImage(models.Model):
    demo = models.ForeignKey(DemoShowcase, related_name="images", on_delete=models.CASCADE)
    image = OptimizedImageField(upload_to='demos/gallery/')
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.demo.title} - Image {self.order}"


# Pricing Plans
class PricingPlan(TimestampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="AUD")
    billing_period = models.CharField(max_length=50, default="month", help_text="e.g., month, year, one-time")
    description = models.TextField(blank=True)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    button_text = models.CharField(max_length=80, default="Get Started")
    button_url = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Pricing Plan"

    def __str__(self):
        return f"{self.name} - ${self.price}/{self.billing_period}"


class PricingFeature(models.Model):
    plan = models.ForeignKey(PricingPlan, related_name="features", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_included = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.plan.name} - {self.text}"


# Stats/Metrics for different sections
class StatMetric(TimestampedModel):
    SECTION_CHOICES = [
        ('home', 'Home Page'),
        ('about', 'About Page'),
        ('services', 'Services Page'),
    ]

    section = models.CharField(max_length=20, choices=SECTION_CHOICES)
    value = models.CharField(max_length=60, help_text="e.g., 100+, $2M, 95%")
    label = models.CharField(max_length=120)
    icon = models.CharField(max_length=40, default="TrendingUp")
    color = models.CharField(max_length=40, default="blue")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["section", "order"]
        verbose_name = "Statistics Metric"

    def __str__(self):
        return f"{self.value} - {self.label}"


# Navigation Menu
class NavigationMenu(TimestampedModel):
    LOCATION_CHOICES = [
        ('header', 'Header Navigation'),
        ('footer', 'Footer Navigation'),
        ('sidebar', 'Sidebar Navigation'),
    ]

    name = models.CharField(max_length=120)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Navigation Menu"

    def __str__(self):
        return f"{self.name} ({self.get_location_display()})"


class NavigationItem(models.Model):
    menu = models.ForeignKey(NavigationMenu, related_name="items", on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    url = models.CharField(max_length=255)
    icon = models.CharField(max_length=40, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    open_in_new_tab = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Navigation Item"

    def __str__(self):
        return self.title


# Blog/News - Enhanced for SEO and Content Marketing
class BlogCategory(TimestampedModel):
    """Blog categories for organizing content."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=40, default="article", help_text="Material icon name")
    color = models.CharField(max_length=20, default="blue", help_text="Theme color")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/blog/category/{self.slug}/"


class BlogPost(TimestampedModel):
    """Blog posts with enhanced SEO fields for content marketing."""
    STATUS_DRAFT = "draft"
    STATUS_REVIEW = "review"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_REVIEW, "In Review"),
        (STATUS_PUBLISHED, "Published"),
    ]

    # Basic fields
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(max_length=320, help_text="Brief summary for previews (max 320 chars)")
    content = RichTextField()
    featured_image = OptimizedImageField(upload_to='blog/', blank=True, null=True)
    author = models.CharField(max_length=120, default="Codeteki Team")

    # Category - now a foreign key
    blog_category = models.ForeignKey(
        BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )
    category = models.CharField(max_length=80, blank=True, help_text="Legacy field - use blog_category instead")
    tags = models.CharField(max_length=255, blank=True, help_text="Comma separated tags")

    # SEO Fields
    meta_title = models.CharField(max_length=70, blank=True, help_text="SEO title (max 70 chars). Leave blank to use post title.")
    meta_description = models.TextField(max_length=160, blank=True, help_text="SEO description (max 160 chars). Leave blank to use excerpt.")
    focus_keyword = models.CharField(max_length=100, blank=True, help_text="Primary keyword to optimize for")
    secondary_keywords = models.CharField(max_length=255, blank=True, help_text="Comma separated secondary keywords")
    canonical_url = models.URLField(blank=True, help_text="Canonical URL if different from default")

    # Open Graph
    og_title = models.CharField(max_length=100, blank=True, help_text="Open Graph title for social sharing")
    og_description = models.TextField(max_length=300, blank=True, help_text="Open Graph description for social sharing")
    og_image = OptimizedImageField(upload_to='blog/og/', blank=True, null=True, webp_max_size=(1200, 630), help_text="Image for social sharing (1200x630 recommended)")

    # Publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)  # Legacy field
    published_at = models.DateTimeField(blank=True, null=True)

    # Reading & engagement
    reading_time_minutes = models.PositiveIntegerField(default=5, help_text="Estimated reading time in minutes")
    views_count = models.PositiveIntegerField(default=0)

    # Content source (for Ubersuggest integration)
    source_cluster = models.ForeignKey(
        'SEOKeywordCluster', on_delete=models.SET_NULL, null=True, blank=True,
        related_name="blog_posts", help_text="SEO keyword cluster this post targets"
    )
    ai_generated = models.BooleanField(default=False, help_text="Was this content AI-generated?")

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Blog Post"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/blog/{self.slug}/"

    def get_meta_title(self):
        """Return meta title or fallback to post title."""
        return self.meta_title or self.title

    def get_meta_description(self):
        """Return meta description or fallback to excerpt."""
        return self.meta_description or self.excerpt[:160]

    def tag_list(self):
        """Return list of tags."""
        return [tag.strip() for tag in (self.tags or "").split(",") if tag.strip()]

    def keyword_list(self):
        """Return list of secondary keywords."""
        return [kw.strip() for kw in (self.secondary_keywords or "").split(",") if kw.strip()]


class BlogGenerationJob(TimestampedModel):
    """
    AI Blog Generation Jobs.

    Handles CSV uploads from Ubersuggest, competitor analysis, backlink opportunities,
    or manual topic entry. Smart scans data and generates human-like blog posts.
    """

    SOURCE_CSV_KEYWORDS = 'csv_keywords'
    SOURCE_CSV_PROMPTS = 'csv_prompts'
    SOURCE_CSV_COMPETITORS = 'csv_competitors'
    SOURCE_CSV_BACKLINKS = 'csv_backlinks'
    SOURCE_MANUAL_TOPICS = 'manual_topics'
    SOURCE_AUTO_DETECT = 'auto_detect'

    SOURCE_CHOICES = [
        (SOURCE_AUTO_DETECT, '🔍 Auto-Detect CSV Type'),
        (SOURCE_CSV_PROMPTS, '💡 Prompt Ideas CSV'),
        (SOURCE_CSV_KEYWORDS, '🔑 Keywords CSV'),
        (SOURCE_CSV_COMPETITORS, '🏆 Competitor Keywords'),
        (SOURCE_CSV_BACKLINKS, '🔗 Backlink Opportunities'),
        (SOURCE_MANUAL_TOPICS, '✏️ Manual Topics'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_SCANNING = 'scanning'
    STATUS_GENERATING = 'generating'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SCANNING, 'Scanning Data'),
        (STATUS_GENERATING, 'Generating Content'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    STYLE_CONVERSATIONAL = 'conversational'
    STYLE_PROFESSIONAL = 'professional'
    STYLE_TECHNICAL = 'technical'
    STYLE_CASUAL = 'casual'

    STYLE_CHOICES = [
        (STYLE_CONVERSATIONAL, 'Conversational (Recommended)'),
        (STYLE_PROFESSIONAL, 'Professional'),
        (STYLE_TECHNICAL, 'Technical/Expert'),
        (STYLE_CASUAL, 'Casual/Friendly'),
    ]

    # Job identification
    name = models.CharField(
        max_length=255,
        help_text="Descriptive name for this job (e.g., 'AI Website Builders - Jan 2025')"
    )

    # Source configuration
    source_type = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES,
        default=SOURCE_AUTO_DETECT,
        help_text="Type of data source. 'Auto-Detect' will analyze the CSV structure."
    )
    csv_file = models.FileField(
        upload_to='blog/generation/',
        blank=True,
        null=True,
        help_text="Upload CSV file from Ubersuggest, competitor analysis, or any keyword data"
    )
    manual_topics = models.TextField(
        blank=True,
        help_text="Enter topics manually, one per line. Used when source is 'Manual Topics'"
    )

    # Generation settings
    target_word_count = models.PositiveIntegerField(
        default=1500,
        help_text="Target word count for each blog post (1000-2500 recommended)"
    )
    writing_style = models.CharField(
        max_length=50,
        choices=STYLE_CHOICES,
        default=STYLE_CONVERSATIONAL,
        help_text="Writing style affects tone and structure"
    )
    include_services = models.BooleanField(
        default=True,
        help_text="Naturally mention relevant Codeteki services in the content"
    )
    auto_publish = models.BooleanField(
        default=False,
        help_text="Automatically publish generated posts (otherwise saved as drafts)"
    )
    target_category = models.ForeignKey(
        'BlogCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Category for generated blog posts"
    )
    max_posts = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of posts to generate from this job"
    )

    # Scan results
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    detected_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Auto-detected CSV type after scanning"
    )
    scan_results = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detected columns, sample data, and extracted topics"
    )
    selected_topics = models.JSONField(
        default=list,
        blank=True,
        help_text="Topics selected for blog generation"
    )

    # Results
    generated_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog Generation Job'
        verbose_name_plural = 'Blog Generation Jobs'

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def get_generated_posts(self):
        """Return BlogPosts generated by this job."""
        return BlogPost.objects.filter(
            ai_generated=True,
            source_cluster__isnull=True,  # Not from SEO clusters
            created_at__gte=self.created_at
        ).filter(
            slug__startswith=slugify(self.name)[:20] if self.name else ''
        )


class SEODataUpload(TimestampedModel):
    """Handles CSV uploads from Ubersuggest and other SEO tools."""

    # Ubersuggest Export Types
    SOURCE_UBERSUGGEST_KEYWORDS = "ubersuggest_keywords"
    SOURCE_UBERSUGGEST_COMPETITORS = "ubersuggest_competitors"
    SOURCE_UBERSUGGEST_COMPETITOR_KEYWORDS = "ubersuggest_competitor_keywords"
    SOURCE_UBERSUGGEST_BACKLINKS = "ubersuggest_backlinks"
    SOURCE_UBERSUGGEST_TOP_PAGES = "ubersuggest_top_pages"
    SOURCE_UBERSUGGEST_CONTENT_IDEAS = "ubersuggest_content_ideas"
    SOURCE_UBERSUGGEST_SITE_AUDIT = "ubersuggest_site_audit"
    SOURCE_UBERSUGGEST_KEYWORD_GAPS = "ubersuggest_keyword_gaps"
    SOURCE_UBERSUGGEST_RANKINGS = "ubersuggest_rankings"

    SOURCE_CHOICES = [
        ("Ubersuggest Exports", (
            (SOURCE_UBERSUGGEST_KEYWORDS, "Keywords Research"),
            (SOURCE_UBERSUGGEST_COMPETITORS, "Competitors List"),
            (SOURCE_UBERSUGGEST_COMPETITOR_KEYWORDS, "Competitor Keywords"),
            (SOURCE_UBERSUGGEST_BACKLINKS, "Backlinks Export"),
            (SOURCE_UBERSUGGEST_TOP_PAGES, "Top Pages by Traffic"),
            (SOURCE_UBERSUGGEST_CONTENT_IDEAS, "Content Ideas"),
            (SOURCE_UBERSUGGEST_SITE_AUDIT, "Site Audit Issues"),
            (SOURCE_UBERSUGGEST_KEYWORD_GAPS, "Keyword Gap Analysis"),
            (SOURCE_UBERSUGGEST_RANKINGS, "Rank Tracking Export"),
        )),
    ]

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_PROCESSED = "processed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_PROCESSED, "Processed"),
        (STATUS_FAILED, "Failed"),
    ]

    project = models.ForeignKey(
        "SEOProject",
        related_name="data_uploads",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Optional: Link to a project (e.g., 'Desifirms' or 'Client ABC'). Leave blank if just testing."
    )
    name = models.CharField(
        max_length=255,
        help_text="Descriptive name. Example: 'Desifirms Keywords Dec 2025' or 'Codeteki Competitor Analysis'"
    )
    source = models.CharField(
        max_length=64,
        choices=SOURCE_CHOICES,
        default=SOURCE_UBERSUGGEST_KEYWORDS,
        help_text="What type of Ubersuggest export is this? 'Keywords Research' is most common."
    )
    csv_file = models.FileField(
        upload_to="seo/uploads/",
        help_text="Upload the CSV file exported from Ubersuggest → Keywords → Export"
    )
    notes = models.TextField(
        blank=True,
        help_text="Optional notes. Example: 'Focus on accounting keywords' or 'Competitor: XYZ Accounting'"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    row_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0, help_text="Rows that failed to import")
    processed_at = models.DateTimeField(blank=True, null=True)
    last_ai_run_at = models.DateTimeField(blank=True, null=True)
    insights = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "SEO Data Upload"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name} ({self.get_source_display()})"

    def ingest_from_file(self):
        """Parse the CSV file and hydrate keyword + cluster records."""
        from .services.seo_importer import SEOIngestService

        service = SEOIngestService(self)
        result = service.run()
        self.status = self.STATUS_PROCESSED
        self.processed_at = timezone.now()
        self.row_count = result.get("rows", 0)
        self.insights = result.get("insights", {})
        self.save(update_fields=["status", "processed_at", "row_count", "insights", "updated_at"])
        return result

    def mark_failed(self, message: str):
        self.status = self.STATUS_FAILED
        self.insights = {"error": message}
        self.save(update_fields=["status", "insights", "updated_at"])

    def run_ai_automation(self, *, cluster_limit: int = 5, ai_engine=None, refresh: bool = False):
        """Generate AI-powered recommendations for this upload."""
        from .services.seo_ai import SEOAutomationEngine

        if refresh:
            self.recommendations.all().delete()
        engine = SEOAutomationEngine(self, ai_engine=ai_engine)
        result = engine.generate(cluster_limit=cluster_limit)
        self.last_ai_run_at = timezone.now()
        self.save(update_fields=["last_ai_run_at", "updated_at"])
        return result

    def generate_blog_posts(self, *, cluster_limit: int = 3, ai_engine=None, category: str = "Insights"):
        """Create BlogPost drafts powered by AI using high-priority clusters."""
        from .services.blog_generator import BlogContentGenerator

        generator = BlogContentGenerator(self, ai_engine=ai_engine)
        return generator.generate(cluster_limit=cluster_limit, category=category)


class SEOKeyword(TimestampedModel):
    INTENT_INFORMATIONAL = "informational"
    INTENT_TRANSACTIONAL = "transactional"
    INTENT_COMMERCIAL = "commercial"
    INTENT_NAVIGATIONAL = "navigational"
    INTENT_CHOICES = [
        (INTENT_INFORMATIONAL, "Informational"),
        (INTENT_TRANSACTIONAL, "Transactional"),
        (INTENT_COMMERCIAL, "Commercial"),
        (INTENT_NAVIGATIONAL, "Navigational"),
    ]

    KEYWORD_TYPE_CHOICES = [
        ("short_tail", "Short Tail"),
        ("mid_tail", "Mid Tail"),
        ("long_tail", "Long Tail"),
    ]

    upload = models.ForeignKey(SEODataUpload, related_name="keywords", on_delete=models.CASCADE)
    cluster = models.ForeignKey("SEOKeywordCluster", related_name="keywords", blank=True, null=True, on_delete=models.SET_NULL)
    keyword = models.CharField(max_length=255)
    search_volume = models.PositiveIntegerField(default=0)
    seo_difficulty = models.PositiveSmallIntegerField(blank=True, null=True)
    paid_difficulty = models.PositiveSmallIntegerField(blank=True, null=True)
    cpc = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    keyword_type = models.CharField(max_length=20, choices=KEYWORD_TYPE_CHOICES, default="mid_tail")
    intent = models.CharField(max_length=32, choices=INTENT_CHOICES, default=INTENT_INFORMATIONAL)
    ranking_url = models.CharField(max_length=255, blank=True)
    trend = models.CharField(max_length=120, blank=True)
    priority_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-priority_score", "keyword"]
        verbose_name = "SEO Keyword"

    def __str__(self):
        return self.keyword


class SEOKeywordCluster(TimestampedModel):
    upload = models.ForeignKey(SEODataUpload, related_name="clusters", on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    seed_keyword = models.CharField(max_length=255, blank=True)
    intent = models.CharField(max_length=32, choices=SEOKeyword.INTENT_CHOICES, default=SEOKeyword.INTENT_INFORMATIONAL)
    avg_volume = models.PositiveIntegerField(default=0)
    avg_difficulty = models.PositiveSmallIntegerField(default=0)
    keyword_count = models.PositiveIntegerField(default=0)
    priority_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    summary = models.TextField(blank=True)

    class Meta:
        ordering = ["-priority_score", "label"]
        verbose_name = "SEO Keyword Cluster"

    def __str__(self):
        return f"{self.label} ({self.keyword_count} kws)"


class AISEORecommendation(TimestampedModel):
    CATEGORY_OPPORTUNITY = "opportunity"
    CATEGORY_CLUSTER_BRIEF = "content_brief"
    CATEGORY_METADATA = "metadata"
    CATEGORY_FAQ = "faq"

    CATEGORY_CHOICES = [
        (CATEGORY_OPPORTUNITY, "Opportunity Overview"),
        (CATEGORY_CLUSTER_BRIEF, "Content Brief"),
        (CATEGORY_METADATA, "Meta Tags"),
        (CATEGORY_FAQ, "FAQ Suggestions"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_GENERATED = "generated"
    STATUS_ERROR = "error"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_GENERATED, "Generated"),
        (STATUS_ERROR, "Error"),
    ]

    upload = models.ForeignKey(SEODataUpload, related_name="recommendations", on_delete=models.CASCADE)
    cluster = models.ForeignKey(SEOKeywordCluster, related_name="recommendations", blank=True, null=True, on_delete=models.CASCADE)
    keyword = models.ForeignKey(SEOKeyword, related_name="recommendations", blank=True, null=True, on_delete=models.CASCADE)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    prompt = models.TextField()
    response = models.TextField(blank=True)
    ai_model = models.CharField(max_length=80, blank=True)
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "AI SEO Recommendation"

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"


class ChatbotSettings(TimestampedModel):
    name = models.CharField(max_length=120, default="Codeteki AI Consultant")
    persona_title = models.CharField(max_length=160, default="AI Success Partner")
    intro_message = models.TextField(default="Hi! I'm Codeteki's AI consultant. How can I help you today?")
    fallback_message = models.TextField(
        default="Thanks for the context. I'll loop in a specialist ASAP so you get a detailed reply."
    )
    lead_capture_prompt = models.TextField(
        default="Can I grab your name + email so we can send a tailored plan?"
    )
    success_message = models.TextField(
        default="Thanks! Our team will reach out with next steps shortly."
    )
    brand_voice = models.CharField(max_length=80, default="Confident & helpful")
    contact_email = models.EmailField(blank=True)
    meeting_link = models.URLField(blank=True)
    accent_color = models.CharField(max_length=12, default="#f9cb07")
    hero_image = OptimizedImageField(upload_to="chatbot/", blank=True, null=True)
    quick_replies = models.JSONField(default=list, blank=True)
    escalation_threshold = models.PositiveSmallIntegerField(default=3, help_text="How many exchanges before suggesting human hand-off.")

    class Meta:
        verbose_name = "Chatbot Settings"

    def __str__(self):
        return self.name


class KnowledgeCategory(TimestampedModel):
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=40, default="Sparkles")
    color = models.CharField(max_length=20, default="yellow")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Knowledge Category"

    def __str__(self):
        return self.name


class KnowledgeArticle(TimestampedModel):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
    ]

    AUDIENCE_CHOICES = [
        ("prospect", "Prospective Customer"),
        ("customer", "Existing Customer"),
        ("technical", "Technical Stakeholder"),
    ]

    category = models.ForeignKey(
        KnowledgeCategory, related_name="articles", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    summary = models.TextField()
    content = RichTextField()
    keywords = models.TextField(
        blank=True, help_text="Comma separated terms to assist chat retrieval."
    )
    persona = models.CharField(
        max_length=40, choices=AUDIENCE_CHOICES, default="prospect"
    )
    call_to_action = models.CharField(max_length=160, blank=True)
    call_to_action_url = models.URLField(blank=True)
    cover_image = OptimizedImageField(upload_to="knowledge/", blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    published_at = models.DateTimeField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-published_at", "-updated_at"]
        verbose_name = "Knowledge Article"

    def __str__(self):
        return self.title

    def tag_list(self):
        return [tag.strip() for tag in (self.tags or "").split(",") if tag.strip()]


class KnowledgeFAQ(TimestampedModel):
    article = models.ForeignKey(
        KnowledgeArticle, related_name="faqs", on_delete=models.CASCADE
    )
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Knowledge Article FAQ"

    def __str__(self):
        return self.question


class ChatConversation(TimestampedModel):
    STATUS_OPEN = "open"
    STATUS_ESCALATED = "escalated"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_ESCALATED, "Escalated"),
        (STATUS_CLOSED, "Closed"),
    ]

    conversation_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    visitor_name = models.CharField(max_length=120, blank=True)
    visitor_email = models.EmailField(blank=True)
    visitor_company = models.CharField(max_length=160, blank=True)
    source = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    metadata = models.JSONField(default=dict, blank=True)
    last_user_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Chat Conversation"

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class ChatMessage(TimestampedModel):
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_SYSTEM = "system"
    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_ASSISTANT, "Assistant"),
        (ROLE_SYSTEM, "System"),
    ]

    conversation = models.ForeignKey(
        ChatConversation, related_name="messages", on_delete=models.CASCADE
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    token_count = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Chat Message"

    def __str__(self):
        return f"{self.role} message in {self.conversation.conversation_id}"


class ChatLead(TimestampedModel):
    STATUS_NEW = "new"
    STATUS_CONTACTED = "contacted"
    STATUS_QUALIFIED = "qualified"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_CONTACTED, "Contacted"),
        (STATUS_QUALIFIED, "Qualified"),
    ]

    conversation = models.OneToOneField(
        ChatConversation, related_name="lead", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=160, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=160, blank=True)
    intent = models.CharField(max_length=160, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)

    class Meta:
        verbose_name = "Chat Lead"

    def __str__(self):
        return self.name or f"Lead {self.pk}"


# =============================================================================
# SEO ENGINE MODELS - Site Audits, PageSpeed, Search Console
# =============================================================================

class SiteAudit(TimestampedModel):
    """Container for a site-wide SEO audit."""
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    STRATEGY_MOBILE = "mobile"
    STRATEGY_DESKTOP = "desktop"
    STRATEGY_CHOICES = [
        (STRATEGY_MOBILE, "Mobile"),
        (STRATEGY_DESKTOP, "Desktop"),
    ]

    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=255, default="codeteki.au")
    strategy = models.CharField(max_length=10, choices=STRATEGY_CHOICES, default=STRATEGY_MOBILE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Target URLs to audit (JSON list)
    target_urls = models.JSONField(default=list, blank=True, help_text="List of URLs to audit")

    # Aggregate scores (calculated from page audits)
    avg_performance = models.FloatField(null=True, blank=True)
    avg_seo = models.FloatField(null=True, blank=True)
    avg_accessibility = models.FloatField(null=True, blank=True)
    avg_best_practices = models.FloatField(null=True, blank=True)

    # Issue counts
    total_pages = models.IntegerField(default=0)
    total_issues = models.IntegerField(default=0)
    critical_issues = models.IntegerField(default=0)
    warning_issues = models.IntegerField(default=0)

    # AI Analysis
    ai_analysis = models.TextField(blank=True, help_text="ChatGPT analysis of audit results")
    ai_recommendations = models.JSONField(default=list, blank=True)

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Celery task tracking
    celery_task_id = models.CharField(max_length=255, blank=True, null=True,
                                       help_text="Celery task ID for background audit")

    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Site Audit"

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def run_audit(self):
        """Execute the site audit using Lighthouse."""
        from .services.lighthouse import LighthouseService
        service = LighthouseService(self)
        return service.run_audit()

    def generate_ai_analysis(self):
        """Generate ChatGPT analysis of audit results."""
        from .services.seo_audit_ai import SEOAuditAIEngine
        engine = SEOAuditAIEngine(self)
        return engine.analyze()


class AIAnalysisReport(SiteAudit):
    """Proxy model for viewing AI Analysis reports separately."""
    class Meta:
        proxy = True
        verbose_name = "AI Analysis Report"
        verbose_name_plural = "AI Analysis Reports"


class PageAudit(TimestampedModel):
    """Individual page audit results (from Lighthouse)."""
    site_audit = models.ForeignKey(
        SiteAudit, related_name="page_audits", on_delete=models.CASCADE, null=True, blank=True
    )
    url = models.URLField(max_length=500, db_index=True)
    strategy = models.CharField(max_length=10, default="mobile")

    # Lighthouse Scores (0-100)
    performance_score = models.IntegerField(null=True, blank=True)
    accessibility_score = models.IntegerField(null=True, blank=True)
    best_practices_score = models.IntegerField(null=True, blank=True)
    seo_score = models.IntegerField(null=True, blank=True)

    # Core Web Vitals
    lcp = models.FloatField(null=True, blank=True, help_text="Largest Contentful Paint (seconds)")
    fid = models.FloatField(null=True, blank=True, help_text="First Input Delay (milliseconds)")
    inp = models.FloatField(null=True, blank=True, help_text="Interaction to Next Paint (milliseconds)")
    cls = models.FloatField(null=True, blank=True, help_text="Cumulative Layout Shift")
    fcp = models.FloatField(null=True, blank=True, help_text="First Contentful Paint (seconds)")
    ttfb = models.FloatField(null=True, blank=True, help_text="Time to First Byte (milliseconds)")
    si = models.FloatField(null=True, blank=True, help_text="Speed Index (seconds)")
    tbt = models.FloatField(null=True, blank=True, help_text="Total Blocking Time (milliseconds)")

    # Raw data storage
    raw_data = models.JSONField(default=dict, blank=True)

    # Status
    status = models.CharField(max_length=20, default="pending")
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Page Audit"

    def __str__(self):
        return f"{self.url} - P:{self.performance_score} SEO:{self.seo_score}"


class AuditIssue(TimestampedModel):
    """Individual issues found during audits."""
    SEVERITY_ERROR = "error"
    SEVERITY_WARNING = "warning"
    SEVERITY_INFO = "info"
    SEVERITY_PASSED = "passed"
    SEVERITY_CHOICES = [
        (SEVERITY_ERROR, "Error"),
        (SEVERITY_WARNING, "Warning"),
        (SEVERITY_INFO, "Info"),
        (SEVERITY_PASSED, "Passed"),
    ]

    CATEGORY_PERFORMANCE = "performance"
    CATEGORY_SEO = "seo"
    CATEGORY_ACCESSIBILITY = "accessibility"
    CATEGORY_BEST_PRACTICES = "best-practices"
    CATEGORY_CHOICES = [
        (CATEGORY_PERFORMANCE, "Performance"),
        (CATEGORY_SEO, "SEO"),
        (CATEGORY_ACCESSIBILITY, "Accessibility"),
        (CATEGORY_BEST_PRACTICES, "Best Practices"),
    ]

    STATUS_OPEN = "open"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_FIXED = "fixed"
    STATUS_IGNORED = "ignored"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_FIXED, "Fixed"),
        (STATUS_IGNORED, "Ignored"),
    ]

    page_audit = models.ForeignKey(
        PageAudit, related_name="issues", on_delete=models.CASCADE
    )

    # Issue identification
    audit_id = models.CharField(max_length=100, help_text="Lighthouse audit ID")
    title = models.CharField(max_length=300)
    description = models.TextField()

    # Classification
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)

    # Metrics
    score = models.FloatField(null=True, blank=True, help_text="Audit score (0-1)")
    display_value = models.CharField(max_length=200, blank=True, help_text="Human-readable value")
    savings_ms = models.FloatField(default=0, help_text="Potential time savings in ms")
    savings_bytes = models.IntegerField(default=0, help_text="Potential size savings in bytes")

    # Fix tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    ai_fix_recommendation = models.TextField(blank=True, help_text="ChatGPT fix recommendation")
    fixed_at = models.DateTimeField(null=True, blank=True)

    # Raw details
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["severity", "-savings_ms"]
        verbose_name = "Audit Issue"

    def __str__(self):
        return f"{self.severity.upper()}: {self.title}"


class PageSpeedResult(TimestampedModel):
    """PageSpeed Insights API results with field data (CrUX)."""
    page_audit = models.ForeignKey(
        PageAudit, related_name="pagespeed_results", on_delete=models.CASCADE, null=True, blank=True
    )
    url = models.URLField(max_length=500, db_index=True)
    strategy = models.CharField(max_length=10, default="mobile")

    # Lab Data (same as Lighthouse)
    lab_performance_score = models.IntegerField(null=True, blank=True)
    lab_lcp = models.FloatField(null=True, blank=True)
    lab_fcp = models.FloatField(null=True, blank=True)
    lab_cls = models.FloatField(null=True, blank=True)
    lab_tbt = models.FloatField(null=True, blank=True)
    lab_si = models.FloatField(null=True, blank=True)

    # Field Data (Real User Metrics from CrUX)
    field_lcp = models.FloatField(null=True, blank=True, help_text="75th percentile LCP from real users")
    field_fid = models.FloatField(null=True, blank=True, help_text="75th percentile FID from real users")
    field_inp = models.FloatField(null=True, blank=True, help_text="75th percentile INP from real users")
    field_cls = models.FloatField(null=True, blank=True, help_text="75th percentile CLS from real users")
    field_fcp = models.FloatField(null=True, blank=True, help_text="75th percentile FCP from real users")
    field_ttfb = models.FloatField(null=True, blank=True, help_text="75th percentile TTFB from real users")

    # Origin-level metrics
    origin_lcp = models.FloatField(null=True, blank=True)
    origin_inp = models.FloatField(null=True, blank=True)
    origin_cls = models.FloatField(null=True, blank=True)

    # Overall assessment
    overall_category = models.CharField(max_length=20, blank=True, help_text="FAST, AVERAGE, or SLOW")

    # Raw data
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "PageSpeed Result"

    def __str__(self):
        return f"PageSpeed: {self.url} ({self.overall_category})"


class SearchConsoleData(TimestampedModel):
    """Google Search Console performance data."""
    upload = models.ForeignKey(
        SEODataUpload, related_name="search_console_data", on_delete=models.CASCADE, null=True, blank=True
    )

    # Query data
    date = models.DateField(db_index=True)
    query = models.CharField(max_length=500, db_index=True)
    page = models.URLField(max_length=500)

    # Metrics
    clicks = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    ctr = models.FloatField(default=0, help_text="Click-through rate (0-1)")
    position = models.FloatField(default=0, help_text="Average position in search results")

    # Dimensions
    country = models.CharField(max_length=10, blank=True)
    device = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["-date", "-impressions"]
        verbose_name = "Search Console Data"
        verbose_name_plural = "Search Console Data"
        indexes = [
            models.Index(fields=["date", "query"]),
            models.Index(fields=["page", "date"]),
        ]

    def __str__(self):
        return f"{self.query} - {self.date} (pos: {self.position:.1f})"


class SearchConsoleSync(TimestampedModel):
    """Track Search Console sync operations."""
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    property_url = models.URLField(max_length=255, help_text="Search Console property URL")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Results
    rows_imported = models.IntegerField(default=0)
    queries_imported = models.IntegerField(default=0)
    pages_imported = models.IntegerField(default=0)

    # Metadata
    error_message = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Search Console Sync"

    def __str__(self):
        return f"Sync {self.start_date} to {self.end_date} ({self.get_status_display()})"

    def run_sync(self):
        """Execute the Search Console sync."""
        from .services.search_console import SearchConsoleService
        service = SearchConsoleService()
        return service.sync_data(self)


class KeywordRanking(TimestampedModel):
    """Track keyword rankings over time."""
    keyword = models.ForeignKey(
        SEOKeyword, related_name="rankings", on_delete=models.CASCADE
    )
    date = models.DateField(db_index=True)

    # Position data
    position = models.FloatField()
    previous_position = models.FloatField(null=True, blank=True)
    position_change = models.FloatField(default=0)

    # Traffic data (from Search Console)
    clicks = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    ctr = models.FloatField(default=0)

    # URL ranking
    ranking_url = models.URLField(max_length=500, blank=True)

    # SERP features
    has_featured_snippet = models.BooleanField(default=False)
    has_local_pack = models.BooleanField(default=False)
    has_video = models.BooleanField(default=False)
    has_image = models.BooleanField(default=False)
    serp_features = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-date", "position"]
        verbose_name = "Keyword Ranking"
        indexes = [
            models.Index(fields=["keyword", "date"]),
        ]

    def __str__(self):
        change = f"+{self.position_change}" if self.position_change > 0 else str(self.position_change)
        return f"{self.keyword.keyword} - Pos {self.position:.1f} ({change})"


class CompetitorProfile(TimestampedModel):
    """Track competitor domains for SEO analysis."""
    domain = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    # Domain metrics (updated periodically)
    domain_authority = models.IntegerField(default=0)
    organic_traffic_est = models.IntegerField(default=0)
    total_keywords = models.IntegerField(default=0)
    total_backlinks = models.IntegerField(default=0)

    # Analysis
    last_analysis = models.DateTimeField(null=True, blank=True)
    analysis_data = models.JSONField(default=dict, blank=True)
    ai_insights = models.TextField(blank=True)

    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Competitor Profile"

    def __str__(self):
        return f"{self.name} ({self.domain})"


class SEORecommendation(TimestampedModel):
    """AI-generated SEO recommendations with status tracking."""
    TYPE_META_TITLE = "meta_title"
    TYPE_META_DESCRIPTION = "meta_description"
    TYPE_CONTENT_BRIEF = "content_brief"
    TYPE_TECHNICAL_FIX = "technical_fix"
    TYPE_NEW_CONTENT = "new_content"
    TYPE_INTERNAL_LINK = "internal_link"
    TYPE_CHOICES = [
        (TYPE_META_TITLE, "Meta Title"),
        (TYPE_META_DESCRIPTION, "Meta Description"),
        (TYPE_CONTENT_BRIEF, "Content Brief"),
        (TYPE_TECHNICAL_FIX, "Technical Fix"),
        (TYPE_NEW_CONTENT, "New Content"),
        (TYPE_INTERNAL_LINK, "Internal Link"),
    ]

    STATUS_GENERATED = "generated"
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_APPLIED = "applied"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_GENERATED, "Generated"),
        (STATUS_PENDING, "Pending Review"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_APPLIED, "Applied"),
        (STATUS_REJECTED, "Rejected"),
    ]

    PRIORITY_CRITICAL = "critical"
    PRIORITY_HIGH = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW = "low"
    PRIORITY_CHOICES = [
        (PRIORITY_CRITICAL, "Critical"),
        (PRIORITY_HIGH, "High"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_LOW, "Low"),
    ]

    # Source links
    upload = models.ForeignKey(
        SEODataUpload, on_delete=models.CASCADE, null=True, blank=True, related_name="seo_recommendations"
    )
    keyword = models.ForeignKey(
        SEOKeyword, on_delete=models.SET_NULL, null=True, blank=True, related_name="seo_recommendations"
    )
    cluster = models.ForeignKey(
        SEOKeywordCluster, on_delete=models.SET_NULL, null=True, blank=True, related_name="seo_recommendations"
    )
    audit_issue = models.ForeignKey(
        AuditIssue, on_delete=models.SET_NULL, null=True, blank=True, related_name="recommendations"
    )

    # Target
    target_url = models.URLField(max_length=500, blank=True)
    target_field = models.CharField(max_length=100, blank=True, help_text="Field to update (e.g., meta_title)")

    # Recommendation
    recommendation_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    current_value = models.TextField(blank=True)
    recommended_value = models.TextField()
    reasoning = models.TextField(blank=True)

    # Status
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_GENERATED)
    applied_at = models.DateTimeField(null=True, blank=True)

    # AI metadata
    ai_model = models.CharField(max_length=50, blank=True)
    ai_tokens_used = models.IntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "SEO Recommendation"

    def __str__(self):
        return f"{self.get_recommendation_type_display()}: {self.title}"


class SEOChangeLog(TimestampedModel):
    """Audit trail for applied SEO changes."""
    recommendation = models.ForeignKey(
        SEORecommendation, on_delete=models.CASCADE, related_name="change_logs"
    )
    target_url = models.URLField(max_length=500)
    target_field = models.CharField(max_length=100)
    old_value = models.TextField()
    new_value = models.TextField()
    applied_by = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    reverted = models.BooleanField(default=False)
    reverted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-applied_at"]
        verbose_name = "SEO Change Log"

    def __str__(self):
        return f"Changed {self.target_field} on {self.target_url}"


class ScheduledAudit(TimestampedModel):
    """Automated recurring site audits."""
    FREQUENCY_DAILY = "daily"
    FREQUENCY_WEEKLY = "weekly"
    FREQUENCY_MONTHLY = "monthly"
    FREQUENCY_CHOICES = [
        (FREQUENCY_DAILY, "Daily"),
        (FREQUENCY_WEEKLY, "Weekly"),
        (FREQUENCY_MONTHLY, "Monthly"),
    ]

    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    target_urls = models.JSONField(default=list, help_text="List of URLs to audit")
    strategy = models.CharField(max_length=10, default="mobile")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default=FREQUENCY_WEEKLY)

    # Scheduling
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)

    # Notifications
    notify_emails = models.JSONField(default=list, blank=True, help_text="Email addresses for notifications")
    notify_on_score_drop = models.BooleanField(default=True)
    score_drop_threshold = models.IntegerField(default=5, help_text="Alert if score drops by this many points")

    # Related audit
    last_audit = models.ForeignKey(
        SiteAudit, on_delete=models.SET_NULL, null=True, blank=True, related_name="scheduled_for"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Scheduled Audit"

    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"


class SEOChatSession(TimestampedModel):
    """SEO assistant chat sessions."""
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, null=True, blank=True
    )
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Context linking
    upload = models.ForeignKey(
        SEODataUpload, on_delete=models.SET_NULL, null=True, blank=True
    )
    audit = models.ForeignKey(
        SiteAudit, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Session data
    context = models.JSONField(default=dict, blank=True)
    title = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "SEO Chat Session"

    def __str__(self):
        return f"SEO Chat {self.session_id}"


class SEOChatMessage(TimestampedModel):
    """Messages in SEO chat sessions."""
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_SYSTEM = "system"
    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_ASSISTANT, "Assistant"),
        (ROLE_SYSTEM, "System"),
    ]

    session = models.ForeignKey(
        SEOChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()

    # Data references
    data_references = models.JSONField(default=list, blank=True)

    # Token usage
    tokens_used = models.IntegerField(default=0)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "SEO Chat Message"

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


# =============================================================================
# UBERSUGGEST INTEGRATION & COMPETITOR TRACKING
# =============================================================================

class SEOProject(TimestampedModel):
    """
    Client/Project container for SEO tracking.
    Each project tracks one domain with its competitors, keywords, and rankings.

    Example Projects:
    - "Codeteki" → codeteki.au (your own site)
    - "Desifirms" → desifirms.com.au (your other site)
    - "Client ABC Accounting" → abcaccounting.com.au (client site)
    """
    STATUS_ACTIVE = "active"
    STATUS_PAUSED = "paused"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_PAUSED, "Paused"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    name = models.CharField(
        max_length=200,
        help_text="Client or project name. Examples: 'Codeteki', 'Desifirms', 'Client ABC'"
    )
    domain = models.CharField(
        max_length=255,
        help_text="Website domain WITHOUT https://. Examples: 'codeteki.au', 'desifirms.com.au'"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    # Tracking settings
    target_country = models.CharField(
        max_length=10,
        default="AU",
        help_text="2-letter country code. AU=Australia, US=USA, UK=United Kingdom"
    )
    target_language = models.CharField(
        max_length=10,
        default="en",
        help_text="2-letter language code. en=English, es=Spanish"
    )

    # Ubersuggest metrics (updated from imports)
    domain_score = models.IntegerField(
        null=True, blank=True,
        help_text="Domain Authority from Ubersuggest (0-100). Higher = stronger domain."
    )
    organic_keywords = models.IntegerField(
        null=True, blank=True,
        help_text="Total keywords this domain ranks for in Google"
    )
    monthly_traffic = models.IntegerField(
        null=True, blank=True,
        help_text="Estimated monthly visitors from organic search"
    )
    backlinks_count = models.IntegerField(
        null=True, blank=True,
        help_text="Total links from other websites pointing to this domain"
    )

    # Goals
    target_traffic = models.IntegerField(
        null=True, blank=True,
        help_text="Your goal for monthly traffic. Example: 10000"
    )
    target_keywords = models.IntegerField(
        null=True, blank=True,
        help_text="Target number of keywords to rank for. Example: 500"
    )

    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Any notes about this project. Example: 'Focus on accounting services keywords'"
    )

    # Link to site audits
    latest_audit = models.ForeignKey(
        SiteAudit, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "SEO Project"

    def __str__(self):
        return f"{self.name} ({self.domain})"


class SEOCompetitor(TimestampedModel):
    """
    Competitor tracking for a project.
    Stores competitor domains and their metrics from Ubersuggest.

    Example: If your project is "Desifirms", competitors might be:
    - hrblock.com.au (H&R Block)
    - taxreturn.com.au
    - itp.com.au
    """
    project = models.ForeignKey(
        SEOProject, on_delete=models.CASCADE, related_name="competitors"
    )
    domain = models.CharField(
        max_length=255,
        help_text="Competitor's domain WITHOUT https://. Example: 'hrblock.com.au'"
    )
    name = models.CharField(
        max_length=200, blank=True,
        help_text="Competitor's business name. Example: 'H&R Block Australia'"
    )

    # Ubersuggest metrics
    domain_score = models.IntegerField(
        null=True, blank=True,
        help_text="Their Domain Authority (0-100)"
    )
    organic_keywords = models.IntegerField(
        null=True, blank=True,
        help_text="How many keywords they rank for"
    )
    monthly_traffic = models.IntegerField(
        null=True, blank=True,
        help_text="Their estimated monthly traffic"
    )
    backlinks_count = models.IntegerField(
        null=True, blank=True,
        help_text="How many backlinks they have"
    )

    # Tracking
    is_primary = models.BooleanField(
        default=False,
        help_text="Check this for your main competitor. You'll see them highlighted in reports."
    )
    notes = models.TextField(
        blank=True,
        help_text="Notes about this competitor. Example: 'They rank #1 for accounting melbourne'"
    )

    # Last updated from Ubersuggest
    metrics_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-is_primary", "domain"]
        verbose_name = "SEO Competitor"
        unique_together = ["project", "domain"]

    def __str__(self):
        return f"{self.domain} (vs {self.project.domain})"


class SEOCompetitorKeyword(TimestampedModel):
    """
    Keywords that competitors rank for.
    Used to find content gaps and opportunities.
    """
    competitor = models.ForeignKey(
        SEOCompetitor, on_delete=models.CASCADE, related_name="keywords"
    )
    keyword = models.CharField(max_length=255)

    # Competitor's ranking
    position = models.IntegerField(null=True, blank=True, help_text="Competitor's ranking position")
    traffic = models.IntegerField(null=True, blank=True, help_text="Traffic this keyword brings to competitor")

    # Keyword metrics
    search_volume = models.IntegerField(default=0)
    seo_difficulty = models.IntegerField(null=True, blank=True)
    cpc = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Our ranking (if any)
    our_position = models.IntegerField(null=True, blank=True, help_text="Our ranking for this keyword")
    is_content_gap = models.BooleanField(default=False, help_text="We don't rank but competitor does")

    # Opportunity score (calculated)
    opportunity_score = models.DecimalField(
        max_digits=6, decimal_places=2, default=0,
        help_text="Higher = better opportunity (volume/difficulty ratio)"
    )

    class Meta:
        ordering = ["-opportunity_score", "-search_volume"]
        verbose_name = "Competitor Keyword"
        unique_together = ["competitor", "keyword"]

    def __str__(self):
        return f"{self.keyword} (pos: {self.position})"

    def save(self, *args, **kwargs):
        # Calculate opportunity score
        if self.search_volume and self.seo_difficulty:
            self.opportunity_score = (self.search_volume / max(self.seo_difficulty, 1)) * (
                1.5 if self.is_content_gap else 1.0
            )
        super().save(*args, **kwargs)


class SEOBacklinkOpportunity(TimestampedModel):
    """
    Potential backlink sources discovered from competitor analysis.
    """
    STATUS_NEW = "new"
    STATUS_CONTACTED = "contacted"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_ACQUIRED = "acquired"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_CONTACTED, "Contacted"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_ACQUIRED, "Acquired"),
        (STATUS_REJECTED, "Rejected"),
    ]

    TYPE_GUEST_POST = "guest_post"
    TYPE_RESOURCE = "resource"
    TYPE_DIRECTORY = "directory"
    TYPE_MENTION = "mention"
    TYPE_BROKEN = "broken_link"
    TYPE_COMPETITOR = "competitor_link"
    TYPE_CHOICES = [
        (TYPE_GUEST_POST, "Guest Post"),
        (TYPE_RESOURCE, "Resource Page"),
        (TYPE_DIRECTORY, "Directory"),
        (TYPE_MENTION, "Brand Mention"),
        (TYPE_BROKEN, "Broken Link"),
        (TYPE_COMPETITOR, "Competitor Backlink"),
    ]

    project = models.ForeignKey(
        SEOProject, on_delete=models.CASCADE, related_name="backlink_opportunities"
    )

    # Source info
    source_domain = models.CharField(max_length=255)
    source_url = models.URLField(max_length=500, blank=True)
    source_title = models.CharField(max_length=300, blank=True)

    # Metrics
    domain_authority = models.IntegerField(null=True, blank=True)
    page_authority = models.IntegerField(null=True, blank=True)

    # Classification
    opportunity_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=TYPE_COMPETITOR)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)

    # Which competitors have this link
    competitors_with_link = models.ManyToManyField(
        SEOCompetitor, blank=True, related_name="backlink_sources"
    )

    # Outreach tracking
    contact_email = models.EmailField(blank=True)
    contact_name = models.CharField(max_length=200, blank=True)
    outreach_date = models.DateField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)

    # Notes
    notes = models.TextField(blank=True)

    # Priority score
    priority_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        ordering = ["-priority_score", "-domain_authority"]
        verbose_name = "Backlink Opportunity"
        verbose_name_plural = "Backlink Opportunities"

    def __str__(self):
        return f"{self.source_domain} (DA: {self.domain_authority})"


class SEOKeywordRank(TimestampedModel):
    """
    Historical keyword ranking data.
    Track how rankings change over time.
    """
    project = models.ForeignKey(
        SEOProject, on_delete=models.CASCADE, related_name="rank_history"
    )
    keyword = models.CharField(max_length=255)

    # Ranking data
    date = models.DateField(db_index=True)
    position = models.IntegerField(null=True, blank=True, help_text="Ranking position (1-100+)")
    previous_position = models.IntegerField(null=True, blank=True)

    # URL ranking
    ranking_url = models.URLField(max_length=500, blank=True)

    # Keyword metrics (snapshot)
    search_volume = models.IntegerField(default=0)

    # Change tracking
    position_change = models.IntegerField(default=0, help_text="Positive = improved")

    class Meta:
        ordering = ["-date", "position"]
        verbose_name = "Keyword Rank History"
        verbose_name_plural = "Keyword Rank History"
        unique_together = ["project", "keyword", "date"]
        indexes = [
            models.Index(fields=["project", "keyword", "date"]),
        ]

    def __str__(self):
        return f"{self.keyword}: #{self.position} on {self.date}"

    def save(self, *args, **kwargs):
        if self.position and self.previous_position:
            self.position_change = self.previous_position - self.position
        super().save(*args, **kwargs)


class SEOContentGap(TimestampedModel):
    """
    Content gaps - keywords competitors rank for but we don't.
    Prioritized opportunities for new content.
    """
    PRIORITY_HIGH = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW = "low"
    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, "High Priority"),
        (PRIORITY_MEDIUM, "Medium Priority"),
        (PRIORITY_LOW, "Low Priority"),
    ]

    STATUS_NEW = "new"
    STATUS_PLANNED = "planned"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_PUBLISHED = "published"
    STATUS_IGNORED = "ignored"
    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_PLANNED, "Planned"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_IGNORED, "Ignored"),
    ]

    project = models.ForeignKey(
        SEOProject, on_delete=models.CASCADE, related_name="content_gaps"
    )
    keyword = models.CharField(max_length=255)

    # Keyword metrics
    search_volume = models.IntegerField(default=0)
    seo_difficulty = models.IntegerField(null=True, blank=True)
    cpc = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Competitor info
    competitors_ranking = models.JSONField(
        default=list, blank=True,
        help_text='List of {"competitor": "domain", "position": 5}'
    )
    best_competitor_position = models.IntegerField(null=True, blank=True)

    # Classification
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)

    # Content planning
    suggested_content_type = models.CharField(
        max_length=50, blank=True,
        help_text="blog_post, service_page, landing_page, guide, etc."
    )
    content_brief = models.TextField(blank=True)
    target_url = models.URLField(max_length=500, blank=True, help_text="URL once content is published")

    # Opportunity score
    opportunity_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        ordering = ["-opportunity_score", "-search_volume"]
        verbose_name = "Content Gap"
        unique_together = ["project", "keyword"]

    def __str__(self):
        return f"Gap: {self.keyword} (vol: {self.search_volume})"

    def save(self, *args, **kwargs):
        # Calculate opportunity score
        if self.search_volume:
            difficulty_factor = (100 - (self.seo_difficulty or 50)) / 100
            self.opportunity_score = self.search_volume * difficulty_factor

            # Adjust priority based on score
            if self.opportunity_score > 500:
                self.priority = self.PRIORITY_HIGH
            elif self.opportunity_score > 100:
                self.priority = self.PRIORITY_MEDIUM
            else:
                self.priority = self.PRIORITY_LOW
        super().save(*args, **kwargs)
