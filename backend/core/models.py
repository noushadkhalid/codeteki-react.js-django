import uuid

from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField


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
    media = models.ImageField(upload_to="hero/", blank=True, null=True)
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
    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    badge = models.CharField(max_length=120, blank=True)
    description = models.TextField()
    icon = models.CharField(max_length=40, default="Sparkles")
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class ServiceOutcome(models.Model):
    service = models.ForeignKey(
        Service, related_name="outcomes", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text


class ServiceProcessStep(TimestampedModel):
    title = models.CharField(max_length=160)
    description = models.TextField()
    icon = models.CharField(max_length=40, default="Sparkles")
    accent = models.CharField(max_length=20, default="blue", help_text="Tailwind-friendly color keyword")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Service Process Step"

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
    logo = models.ImageField(upload_to='footer/', blank=True, null=True)
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
    logo = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Main logo")
    logo_dark = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Logo for dark backgrounds")
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)

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

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name


# SEO Meta for different pages
class PageSEO(TimestampedModel):
    PAGE_CHOICES = [
        ('home', 'Home Page'),
        ('services', 'Services Page'),
        ('ai-tools', 'AI Tools Page'),
        ('demos', 'Demos Page'),
        ('faq', 'FAQ Page'),
        ('contact', 'Contact Page'),
        ('about', 'About Page'),
        ('pricing', 'Pricing Page'),
    ]

    page = models.CharField(max_length=50, choices=PAGE_CHOICES, unique=True)
    meta_title = models.CharField(max_length=160)
    meta_description = models.TextField(max_length=320)
    meta_keywords = models.TextField(blank=True, help_text="Comma separated keywords")
    og_title = models.CharField(max_length=160, blank=True, verbose_name="Open Graph Title")
    og_description = models.TextField(max_length=320, blank=True)
    og_image = models.ImageField(upload_to='seo/', blank=True, null=True)
    canonical_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Page SEO"
        verbose_name_plural = "Page SEO Settings"

    def __str__(self):
        return f"SEO - {self.get_page_display()}"


# Testimonials
class Testimonial(TimestampedModel):
    name = models.CharField(max_length=160)
    position = models.CharField(max_length=160, blank=True)
    company = models.CharField(max_length=160, blank=True)
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
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
    thumbnail = models.ImageField(upload_to='demos/', help_text="Main image for the demo")
    demo_url = models.URLField(blank=True, help_text="Link to live demo")
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    client_name = models.CharField(max_length=160, blank=True)
    client_logo = models.ImageField(upload_to='demos/clients/', blank=True, null=True)
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
    screenshot = models.ImageField(upload_to='demos/screenshots/', blank=True, null=True)

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
    image = models.ImageField(upload_to='demos/gallery/')
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


# Blog/News (Optional but good to have)
class BlogPost(TimestampedModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(max_length=320)
    content = RichTextField()
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    author = models.CharField(max_length=120, default="Codeteki Team")
    category = models.CharField(max_length=80, blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma separated")
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "Blog Post"

    def __str__(self):
        return self.title


class SEODataUpload(TimestampedModel):
    SOURCE_UBERSUGGEST = "ubersuggest_keywords"
    SOURCE_CHOICES = [
        (SOURCE_UBERSUGGEST, "Ubersuggest Keyword Export"),
    ]

    STATUS_PENDING = "pending"
    STATUS_PROCESSED = "processed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSED, "Processed"),
        (STATUS_FAILED, "Failed"),
    ]

    name = models.CharField(max_length=255)
    source = models.CharField(max_length=64, choices=SOURCE_CHOICES, default=SOURCE_UBERSUGGEST)
    csv_file = models.FileField(upload_to="seo/uploads/")
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    row_count = models.PositiveIntegerField(default=0)
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
    hero_image = models.ImageField(upload_to="chatbot/", blank=True, null=True)
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
    cover_image = models.ImageField(upload_to="knowledge/", blank=True, null=True)
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
