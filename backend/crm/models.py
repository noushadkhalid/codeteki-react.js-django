from django.db import models
from django.utils import timezone
import uuid


class Brand(models.Model):
    """
    Multi-brand support for CRM.
    Allows running CRM for multiple projects (Codeteki, Desi Firms, etc.)
    with different email configs, templates, and outreach strategies.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    website = models.URLField(help_text="Main website URL")
    description = models.TextField(blank=True)

    # Email Configuration
    from_email = models.EmailField(help_text="Sender email address")
    from_name = models.CharField(max_length=100, help_text="Sender display name")
    reply_to_email = models.EmailField(blank=True)

    # Zoho credentials (per brand - allows different Zoho accounts/regions)
    zoho_client_id = models.CharField(max_length=255, blank=True)
    zoho_client_secret = models.CharField(max_length=255, blank=True)
    zoho_account_id = models.CharField(max_length=255, blank=True)
    zoho_refresh_token = models.CharField(max_length=1000, blank=True)
    zoho_api_domain = models.CharField(
        max_length=50,
        blank=True,
        default='zoho.com',
        help_text="Zoho region: zoho.com (US), zoho.com.au (AU), zoho.eu (EU)"
    )

    # ZeptoMail credentials (alternative to Zoho Mail for higher volume)
    zeptomail_api_key = models.CharField(
        max_length=500,
        blank=True,
        help_text="ZeptoMail API key (e.g., Zoho-enczapikey ...). If set, uses ZeptoMail instead of Zoho Mail."
    )
    zeptomail_host = models.CharField(
        max_length=100,
        blank=True,
        default='api.zeptomail.com',
        help_text="ZeptoMail API host: api.zeptomail.com (US) or api.zeptomail.com.au (AU)"
    )

    # Twilio SMS/WhatsApp credentials
    twilio_account_sid = models.CharField(max_length=255, blank=True)
    twilio_auth_token = models.CharField(max_length=255, blank=True)
    twilio_phone_number = models.CharField(max_length=20, blank=True, help_text="E.164 format, e.g. +61400000000")
    twilio_whatsapp_number = models.CharField(max_length=20, blank=True, help_text="E.164 format for WhatsApp sender")

    # AI Configuration
    ai_company_description = models.TextField(
        blank=True,
        help_text="Description used in AI prompts (e.g., 'Codeteki is a digital agency...')"
    )
    ai_value_proposition = models.TextField(
        blank=True,
        help_text="Value proposition for outreach emails"
    )
    ai_business_updates = models.TextField(
        blank=True,
        help_text="Recent updates AI should mention (e.g., 'NEW: Image search, real estate section. Pricing: Free plan, Standard $9.99, Premium $14.99, yearly savings')"
    )
    ai_target_context = models.TextField(
        blank=True,
        help_text="Target audience context (e.g., '20+ existing customers need to know about revamp, new features, better pricing')"
    )
    ai_approach_style = models.CharField(
        max_length=50,
        blank=True,
        default='problem_solving',
        choices=[
            ('problem_solving', 'Problem-Solving (focus on solving their problems)'),
            ('value_driven', 'Value-Driven (highlight benefits and value)'),
            ('relationship', 'Relationship-First (build connection before pitching)'),
            ('direct', 'Direct (clear and to the point)'),
        ],
        help_text="AI email writing approach style"
    )
    backlink_content_types = models.JSONField(
        default=list,
        blank=True,
        help_text="Types of content for backlink outreach: ['AI tools', 'SEO guides', 'Business directory']"
    )

    # Branding
    logo_url = models.URLField(blank=True)
    primary_color = models.CharField(max_length=7, default='#f9cb07')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return self.name


class Contact(models.Model):
    """Leads and backlink targets for CRM outreach."""

    CONTACT_TYPE_CHOICES = [
        ('lead', 'Lead'),
        ('backlink_target', 'Backlink Target'),
        ('partner', 'Partner'),
    ]

    INDUSTRY_CHOICES = [
        ('restaurant', 'Restaurant / Cafe / Food'),
        ('trades', 'Trades & Home Services'),
        ('health_beauty', 'Health & Beauty'),
        ('retail', 'Retail / Shopping'),
        ('professional', 'Professional Services'),
        ('fitness', 'Fitness / Sports'),
        ('automotive', 'Automotive'),
        ('education', 'Education / Training'),
        ('real_estate', 'Real Estate'),
        ('accommodation', 'Accommodation / Hotels'),
        ('medical', 'Medical / Healthcare'),
        ('legal', 'Legal Services'),
        ('accounting', 'Accounting / Finance'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='contacts',
        null=True,
        blank=True,
        help_text="Which brand this contact belongs to"
    )
    email = models.EmailField(blank=True, default='')  # Optional for phone-only leads
    name = models.CharField(max_length=255, blank=True, help_text="Leave blank to auto-extract from email/domain")
    company = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=30, blank=True, help_text="Phone number")
    industry = models.CharField(max_length=50, blank=True, choices=INDUSTRY_CHOICES)
    address = models.TextField(blank=True, help_text="Business address")
    google_place_id = models.CharField(max_length=300, blank=True, help_text="Google Places ID for dedup")
    google_rating = models.FloatField(null=True, blank=True, help_text="Google rating 1-5")
    domain_authority = models.IntegerField(null=True, blank=True, help_text="Domain Authority score 0-100")
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES, default='lead')
    source = models.CharField(max_length=100, blank=True, help_text="Where this contact came from")
    tags = models.JSONField(default=list, blank=True, help_text="Flexible tagging")
    ai_score = models.IntegerField(default=0, help_text="AI lead scoring 0-100")
    notes = models.TextField(blank=True)

    # Email tracking & unsubscribe
    last_emailed_at = models.DateTimeField(null=True, blank=True, help_text="Last time we emailed this contact")
    email_count = models.IntegerField(default=0, help_text="Total emails sent to this contact")
    is_unsubscribed = models.BooleanField(default=False, help_text="Contact has unsubscribed from ALL brands")
    unsubscribed_brands = models.JSONField(
        default=list,
        blank=True,
        help_text="List of brand slugs they've unsubscribed from (e.g., ['codeteki', 'desifirms'])"
    )
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    unsubscribe_reason = models.TextField(blank=True, help_text="Why they unsubscribed")

    # Send optimization
    preferred_send_hour = models.IntegerField(
        null=True, blank=True,
        help_text="Preferred hour to send emails (0-23), computed from open history"
    )

    # Bounce tracking
    email_bounced = models.BooleanField(default=False, help_text="Email address hard-bounced (invalid/non-existent)")
    bounced_at = models.DateTimeField(null=True, blank=True)
    soft_bounce_count = models.IntegerField(default=0, help_text="Number of soft bounces (auto-converts to hard bounce at 3)")
    spam_reported = models.BooleanField(default=False, help_text="Recipient reported email as spam (feedback loop)")
    spam_reported_at = models.DateTimeField(null=True, blank=True)

    # SMS opt-out tracking
    sms_opted_out = models.BooleanField(default=False, help_text="Contact opted out of SMS messages")
    sms_opted_out_at = models.DateTimeField(null=True, blank=True)
    last_sms_at = models.DateTimeField(null=True, blank=True)
    sms_count = models.IntegerField(default=0, help_text="Total SMS/WhatsApp messages sent")

    # Status tracking (simplified pipeline)
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('replied', 'Replied'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('unsubscribed', 'Unsubscribed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    # Link to existing models
    chat_lead = models.ForeignKey(
        'core.ChatLead',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crm_contact'
    )
    contact_inquiry = models.ForeignKey(
        'core.ContactInquiry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crm_contact'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        constraints = [
            models.UniqueConstraint(
                fields=['brand', 'email'],
                condition=models.Q(email__gt=''),
                name='unique_brand_email_when_set',
            ),
        ]

    def __str__(self):
        if self.email:
            return f"{self.name} ({self.email})"
        return f"{self.name} ({self.phone or 'no email'})"

    def is_unsubscribed_from_brand(self, brand_slug: str) -> bool:
        """Check if contact has unsubscribed from a specific brand."""
        if self.is_unsubscribed:
            return True  # Globally unsubscribed
        return brand_slug.lower() in [b.lower() for b in (self.unsubscribed_brands or [])]

    def unsubscribe_from_brand(self, brand_slug: str, reason: str = ''):
        """Unsubscribe contact from a specific brand."""
        from django.utils import timezone
        brand_slug = brand_slug.lower()
        brands = self.unsubscribed_brands or []
        if brand_slug not in [b.lower() for b in brands]:
            brands.append(brand_slug)
            self.unsubscribed_brands = brands
        self.unsubscribed_at = timezone.now()
        if reason:
            self.unsubscribe_reason = reason
        self.save()

    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Extract and normalize email from various formats.
        Handles: "Name <email@example.com>", "email@example.com", etc.
        """
        import re
        if not email:
            return ''
        email = email.strip()
        # Extract email from "Name <email>" format
        match = re.search(r'<([^>]+)>', email)
        if match:
            email = match.group(1)
        # Remove any remaining whitespace and lowercase
        return email.strip().lower()

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """
        Normalize phone to E.164 format using phonenumbers library.
        Assumes Australian numbers by default.
        Returns empty string if invalid.
        """
        import phonenumbers
        if not phone:
            return ''
        phone = phone.strip()
        try:
            parsed = phonenumbers.parse(phone, 'AU')
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            pass
        return ''

    # Generic email prefixes that need name extraction from domain/company
    GENERIC_EMAIL_PREFIXES = {
        'info', 'admin', 'sales', 'contact', 'hello', 'support', 'team',
        'enquiry', 'enquiries', 'mail', 'office', 'help', 'service',
        'marketing', 'hq', 'head', 'reception', 'general', 'inbox',
        'noreply', 'no-reply', 'accounts', 'billing', 'hr', 'careers',
    }

    def _extract_smart_name(self) -> str:
        """
        Extract a smart name from email/company/domain.

        Logic:
        1. If email prefix is personal (rajesh@, nithya.patel@) → "Rajesh" or "Nithya"
        2. If email is generic (info@, admin@, hq@) → Use company name or domain
           - bombayre.com.au → "Bombay RE"
           - skadre.com.au → "Skad RE"
           - amberre.com.au → "Amber RE"
        """
        if not self.email or '@' not in self.email:
            return self.company or 'Contact'

        email_prefix = self.email.split('@')[0].lower()
        email_domain = self.email.split('@')[1].lower()

        # Clean prefix for comparison
        clean_prefix = email_prefix.replace('.', '').replace('_', '').replace('-', '')

        # Check if generic email
        is_generic = (
            email_prefix in self.GENERIC_EMAIL_PREFIXES or
            clean_prefix in self.GENERIC_EMAIL_PREFIXES
        )

        if not is_generic:
            # Personal email - extract name from prefix
            # Handle formats: rajesh, r.kumar, nithya.patel, bob_smith
            name_parts = email_prefix.replace('.', ' ').replace('_', ' ').replace('-', ' ').split()
            if name_parts:
                # Filter out single letters and numbers
                valid_parts = [p.title() for p in name_parts if len(p) > 1 and not p.isdigit()]
                if valid_parts:
                    return ' '.join(valid_parts[:2])  # Max 2 parts (first + last)

        # Generic email - use company or extract from domain
        if self.company:
            return self.company

        # Extract from domain: bombayre.com.au → "Bombay RE"
        return self._humanize_domain(email_domain)

    def _humanize_domain(self, domain: str) -> str:
        """
        Convert domain to human-readable company name.

        Examples:
        - bombayre.com.au → "Bombay RE"
        - skadre.com.au → "Skad RE"
        - amberre.com.au → "Amber RE"
        - reliancere.com.au → "Reliance RE"
        - a-onerealestate.com.au → "A One Real Estate"
        """
        import re

        # Get the main part (before first .)
        main_part = domain.split('.')[0]

        # Common suffixes to expand
        suffixes = {
            're': ' RE',
            'realestate': ' Real Estate',
            'property': ' Property',
            'properties': ' Properties',
            'group': ' Group',
            'au': '',
            'com': '',
        }

        # Check for known suffixes
        result = main_part
        for suffix, expansion in suffixes.items():
            if result.lower().endswith(suffix) and len(result) > len(suffix):
                result = result[:-len(suffix)] + expansion
                break

        # Clean up: replace hyphens/underscores with spaces, title case
        result = result.replace('-', ' ').replace('_', ' ')

        # Add spaces before capital letters (camelCase handling)
        result = re.sub(r'([a-z])([A-Z])', r'\1 \2', result)

        # Title case and clean up multiple spaces
        result = ' '.join(word.title() for word in result.split())

        return result.strip() or 'Contact'

    # Personal email domains to skip for company/website extraction
    PERSONAL_EMAIL_DOMAINS = (
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'live.com',
        'icloud.com', 'me.com', 'aol.com', 'mail.com', 'protonmail.com',
        'zoho.com', 'ymail.com', 'msn.com', 'bigpond.com', 'optusnet.com.au',
    )

    def save(self, *args, **kwargs):
        """Normalize email and auto-extract name/company/website if needed."""
        if self.email:
            self.email = self.normalize_email(self.email)
            email_domain = self.email.split('@')[1] if '@' in self.email else ''
            is_business_email = email_domain and not email_domain.endswith(self.PERSONAL_EMAIL_DOMAINS)

            # Auto-extract company from domain if not provided
            if is_business_email and (not self.company or self.company.strip() == ''):
                self.company = self._humanize_domain(email_domain)

            # Auto-extract website from domain if not provided
            if is_business_email and (not self.website or self.website.strip() == ''):
                self.website = f"https://{email_domain}"

            # Auto-extract name if empty, looks generic, or matches company exactly
            needs_name_extraction = (
                not self.name or
                self.name.strip() == '' or
                self.name.lower() in self.GENERIC_EMAIL_PREFIXES or
                (self.company and self.name.strip().lower() == self.company.strip().lower())
            )

            if needs_name_extraction:
                self.name = self._extract_smart_name()

        super().save(*args, **kwargs)


class CodetekiContactManager(models.Manager):
    """Manager that filters to Codeteki brand only."""
    def get_queryset(self):
        return super().get_queryset().filter(brand__slug='codeteki')


class DesiFirmsContactManager(models.Manager):
    """Manager that filters to Desi Firms brand only."""
    def get_queryset(self):
        return super().get_queryset().filter(brand__slug='desifirms')


class CodetekiContact(Contact):
    """Proxy model for Codeteki contacts - separate admin view."""
    objects = CodetekiContactManager()

    class Meta:
        proxy = True
        verbose_name = 'Codeteki Contact'
        verbose_name_plural = 'Codeteki Contacts'


class DesiFirmsContact(Contact):
    """Proxy model for Desi Firms contacts - separate admin view."""
    objects = DesiFirmsContactManager()

    class Meta:
        proxy = True
        verbose_name = 'Desi Firms Contact'
        verbose_name_plural = 'Desi Firms Contacts'


class Pipeline(models.Model):
    """Different workflows for lead acquisition and outreach."""

    PIPELINE_TYPE_CHOICES = [
        # Codeteki pipelines
        ('sales', 'Sales'),
        ('backlink', 'Backlink Outreach'),
        ('partnership', 'Partnership'),
        # Desi Firms listing acquisition pipelines
        ('business', 'Business Listings'),
        ('deals', 'Deals & Promotions'),
        ('events', 'Events'),
        ('realestate', 'Real Estate'),
        ('classifieds', 'Classifieds'),
        ('registered_users', 'Registered Users (Nudge)'),
        # SMS/WhatsApp campaigns
        ('sms_campaign', 'SMS Campaign'),
        ('whatsapp_campaign', 'WhatsApp Campaign'),
    ]

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='pipelines',
        null=True,
        blank=True,
        help_text="Which brand this pipeline belongs to"
    )
    name = models.CharField(max_length=100)
    pipeline_type = models.CharField(max_length=20, choices=PIPELINE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Pipeline'
        verbose_name_plural = 'Pipelines'

    def __str__(self):
        return f"{self.name} ({self.get_pipeline_type_display()})"


class PipelineStage(models.Model):
    """Stages within a pipeline with auto-actions."""

    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    auto_actions = models.JSONField(
        default=dict,
        blank=True,
        help_text="AI triggers: {action: 'send_email', template: 'initial_outreach'}"
    )
    days_until_followup = models.IntegerField(
        default=3,
        help_text="Days to wait before follow-up action"
    )
    subject_variant_b = models.CharField(
        max_length=255,
        blank=True,
        help_text="A/B test subject line. Leave blank to disable."
    )
    is_terminal = models.BooleanField(default=False, help_text="Marks end states like Won/Lost")

    class Meta:
        ordering = ['pipeline', 'order']
        unique_together = ['pipeline', 'order']
        verbose_name = 'Pipeline Stage'
        verbose_name_plural = 'Pipeline Stages'

    def __str__(self):
        return f"{self.pipeline.name} - {self.name}"


class Deal(models.Model):
    """Contact moving through a pipeline."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('paused', 'Paused'),
    ]

    ENGAGEMENT_TIER_CHOICES = [
        ('', 'Unknown'),
        ('engaged', 'Engaged'),
        ('hot', 'Hot'),
        ('warm', 'Warm'),
        ('lurker', 'Lurker'),
        ('cold', 'Cold'),
        ('ghost', 'Ghost'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='deals')
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='deals')
    current_stage = models.ForeignKey(
        PipelineStage,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deals'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    engagement_tier = models.CharField(
        max_length=20,
        blank=True,
        choices=ENGAGEMENT_TIER_CHOICES,
        default='',
        help_text="Auto-computed engagement tier from email activity"
    )
    autopilot_paused = models.BooleanField(
        default=False,
        help_text="Pause autopilot for this deal (manual override)"
    )
    re_engagement_attempted = models.BooleanField(
        default=False,
        help_text="Whether this deal has been through automated re-engagement"
    )
    lost_reason = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('', 'N/A'),
            ('unsubscribed', 'Unsubscribed'),
            ('no_response', 'No Response'),
            ('not_interested', 'Not Interested'),
            ('competitor', 'Chose Competitor'),
            ('budget', 'Budget Issues'),
            ('timing', 'Bad Timing'),
            ('invalid_email', 'Invalid Email'),
            ('other', 'Other'),
        ],
        help_text="Reason for losing the deal"
    )
    ai_notes = models.TextField(blank=True, help_text="AI observations and analysis")
    next_action_date = models.DateTimeField(null=True, blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stage_entered_at = models.DateTimeField(default=timezone.now)

    # Tracking
    emails_sent = models.IntegerField(default=0)
    last_contact_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Deal'
        verbose_name_plural = 'Deals'

    def __str__(self):
        stage_name = self.current_stage.name if self.current_stage else 'No Stage'
        return f"{self.contact.name} - {self.pipeline.name} ({stage_name})"

    def move_to_stage(self, stage):
        """Move deal to a new stage and update timestamps."""
        self.current_stage = stage
        self.stage_entered_at = timezone.now()

        # Calculate next action date based on stage settings
        if stage.days_until_followup:
            self.next_action_date = timezone.now() + timezone.timedelta(days=stage.days_until_followup)

        self.save()


class EmailSequence(models.Model):
    """Template sequences for automated outreach."""

    name = models.CharField(max_length=100)
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='email_sequences'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pipeline', 'name']
        verbose_name = 'Email Sequence'
        verbose_name_plural = 'Email Sequences'

    def __str__(self):
        return f"{self.name} ({self.pipeline.name})"


class SequenceStep(models.Model):
    """Individual email template in a sequence."""

    sequence = models.ForeignKey(
        EmailSequence,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    order = models.IntegerField(default=0)
    delay_days = models.IntegerField(default=0, help_text="Days after previous step")
    subject_template = models.CharField(max_length=255)
    body_template = models.TextField()
    ai_personalize = models.BooleanField(
        default=True,
        help_text="AI should personalize this email"
    )

    class Meta:
        ordering = ['sequence', 'order']
        unique_together = ['sequence', 'order']
        verbose_name = 'Sequence Step'
        verbose_name_plural = 'Sequence Steps'

    def __str__(self):
        return f"{self.sequence.name} - Step {self.order}"


CHANNEL_CHOICES = [
    ('email', 'Email'),
    ('sms', 'SMS'),
    ('whatsapp', 'WhatsApp'),
]


class EmailLog(models.Model):
    """Track all sent emails, SMS, and WhatsApp messages."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='email_logs', null=True, blank=True)
    sequence_step = models.ForeignKey(
        SequenceStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )

    # Channel
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='email')

    # A/B testing
    ab_variant = models.CharField(max_length=1, blank=True, help_text="A/B test variant: A or B")

    # Email content
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    from_email = models.EmailField(default='sales@codeteki.au')
    to_email = models.EmailField(blank=True, default='')
    to_phone = models.CharField(max_length=30, blank=True, help_text="E.164 phone for SMS/WhatsApp")

    # Twilio tracking
    message_sid = models.CharField(max_length=100, blank=True, help_text="Twilio message SID")
    delivery_status = models.CharField(max_length=20, blank=True, help_text="Twilio delivery status")

    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    opened = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    replied = models.BooleanField(default=False)
    replied_at = models.DateTimeField(null=True, blank=True)
    reply_content = models.TextField(blank=True)

    # Metadata
    ai_generated = models.BooleanField(default=False)
    zoho_message_id = models.CharField(max_length=255, blank=True)
    tracking_id = models.UUIDField(default=uuid.uuid4, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Message Log'
        verbose_name_plural = 'Message Logs'

    def __str__(self):
        status = "Sent" if self.sent_at else "Draft"
        target = self.to_email or self.to_phone or 'unknown'
        if self.channel in ('sms', 'whatsapp'):
            return f"{status} {self.channel.upper()}: to {target}"
        return f"{status}: {self.subject} to {target}"


class AIDecisionLog(models.Model):
    """Audit trail for AI decisions."""

    DECISION_TYPE_CHOICES = [
        ('compose_email', 'Compose Email'),
        ('move_stage', 'Move Stage'),
        ('classify_reply', 'Classify Reply'),
        ('score_lead', 'Score Lead'),
        ('deal_analyze', 'Analyze Deal'),
        ('send_email', 'Send Email'),
        ('pause_deal', 'Pause Deal'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='ai_decisions',
        null=True,
        blank=True
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='ai_decisions',
        null=True,
        blank=True
    )
    decision_type = models.CharField(max_length=30, choices=DECISION_TYPE_CHOICES)
    reasoning = models.TextField(help_text="AI explanation for the decision")
    action_taken = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)

    # Token usage tracking
    tokens_used = models.IntegerField(default=0)
    model_used = models.CharField(max_length=50, default='gpt-4o-mini')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Decision Log'
        verbose_name_plural = 'AI Decision Logs'

    def __str__(self):
        target = self.deal or self.contact
        return f"{self.get_decision_type_display()} - {target}"


class BacklinkOpportunity(models.Model):
    """Backlink targets for outreach pipeline."""

    STATUS_CHOICES = [
        ('new', 'New'),
        ('researching', 'Researching'),
        ('outreaching', 'Outreaching'),
        ('placed', 'Link Placed'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='backlink_opportunities',
        null=True,
        blank=True,
        help_text="Which brand this opportunity belongs to"
    )
    target_url = models.URLField(help_text="Target page URL for backlink")
    target_domain = models.CharField(max_length=255)
    domain_authority = models.IntegerField(default=0, help_text="DA score 0-100")
    relevance_score = models.IntegerField(default=0, help_text="Relevance to our content 0-100")

    # Our content to promote
    our_content_url = models.URLField(help_text="Our content URL to promote")
    anchor_text_suggestion = models.CharField(max_length=255, blank=True)
    outreach_angle = models.TextField(blank=True, help_text="AI-generated pitch angle")

    # Link to contact if found
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='backlink_opportunities'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    notes = models.TextField(blank=True)

    # Verification
    link_verified = models.BooleanField(default=False)
    link_verified_at = models.DateTimeField(null=True, blank=True)
    actual_link_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-domain_authority', '-relevance_score']
        verbose_name = 'Backlink Opportunity'
        verbose_name_plural = 'Backlink Opportunities'

    def __str__(self):
        return f"{self.target_domain} (DA: {self.domain_authority})"


class AIPromptTemplate(models.Model):
    """Store AI prompts for different CRM actions."""

    PROMPT_TYPE_CHOICES = [
        ('email_compose', 'Email Compose'),
        ('email_followup', 'Email Follow-up'),
        ('reply_classify', 'Reply Classify'),
        ('lead_score', 'Lead Score'),
        ('deal_analyze', 'Deal Analyze'),
        ('backlink_pitch', 'Backlink Pitch'),
    ]

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='prompt_templates',
        null=True,
        blank=True,
        help_text="Brand-specific template (null = shared across all brands)"
    )
    name = models.CharField(max_length=100)
    prompt_type = models.CharField(max_length=30, choices=PROMPT_TYPE_CHOICES)
    prompt_text = models.TextField()
    system_prompt = models.TextField(
        blank=True,
        help_text="Optional system prompt override"
    )
    variables = models.JSONField(
        default=list,
        blank=True,
        help_text="Expected variables: ['contact_name', 'company', 'website']"
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['prompt_type', 'name']
        verbose_name = 'AI Prompt Template'
        verbose_name_plural = 'AI Prompt Templates'

    def __str__(self):
        return f"{self.name} ({self.get_prompt_type_display()})"

    def render(self, context: dict) -> str:
        """Render prompt with context variables."""
        prompt = self.prompt_text
        for key, value in context.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        return prompt


class DealActivity(models.Model):
    """Track all activities on a deal for timeline view."""

    ACTIVITY_TYPE_CHOICES = [
        ('stage_change', 'Stage Changed'),
        ('email_sent', 'Email Sent'),
        ('email_opened', 'Email Opened'),
        ('email_replied', 'Email Replied'),
        ('note_added', 'Note Added'),
        ('ai_action', 'AI Action'),
        ('status_change', 'Status Changed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPE_CHOICES)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Deal Activity'
        verbose_name_plural = 'Deal Activities'

    def __str__(self):
        return f"{self.deal} - {self.get_activity_type_display()}"


class ContactImport(models.Model):
    """Track contact imports from CSV or Excel files."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='contact_imports'
    )
    file = models.FileField(upload_to='crm/imports/')
    file_name = models.CharField(max_length=255)
    contact_type = models.CharField(
        max_length=20,
        choices=Contact.CONTACT_TYPE_CHOICES,
        default='lead'
    )
    source = models.CharField(max_length=100, default='csv_import')
    create_deals = models.BooleanField(
        default=False,
        help_text="Automatically create deals for imported contacts"
    )
    pipeline = models.ForeignKey(
        'Pipeline',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Pipeline for auto-created deals"
    )

    # Results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_rows = models.IntegerField(default=0)
    imported_count = models.IntegerField(default=0)
    skipped_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    errors = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Import'
        verbose_name_plural = 'Contact Imports'

    def __str__(self):
        return f"{self.file_name} - {self.brand.name} ({self.status})"


class BacklinkImport(models.Model):
    """Track backlink opportunity imports from Ubersuggest/Ahrefs CSV exports."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='backlink_imports'
    )
    file = models.FileField(upload_to='crm/backlink_imports/')
    file_name = models.CharField(max_length=255)
    source = models.CharField(
        max_length=50,
        default='ubersuggest',
        help_text="Data source: ubersuggest, ahrefs, semrush, moz"
    )

    # Our content URL to promote (applied to all imported opportunities)
    our_content_url = models.URLField(
        blank=True,
        help_text="Your content URL to promote for backlinks"
    )

    # Import settings
    min_domain_authority = models.IntegerField(
        default=0,
        help_text="Skip domains with DA below this value"
    )
    create_contacts = models.BooleanField(
        default=False,
        help_text="Try to create contacts from email columns if available"
    )

    # Results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_rows = models.IntegerField(default=0)
    imported_count = models.IntegerField(default=0)
    skipped_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    errors = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Backlink Import'
        verbose_name_plural = 'Backlink Imports'

    def __str__(self):
        return f"{self.file_name} - {self.brand.name} ({self.status})"


class ProspectScan(models.Model):
    """Stores website scan results for a Codeteki prospect."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE, related_name='prospect_scans')
    url = models.URLField()

    # Raw scan data
    crawl_data = models.JSONField(default=dict)
    pagespeed_data = models.JSONField(default=dict)

    # Processed results
    grade = models.CharField(max_length=2, blank=True)
    opportunities = models.JSONField(default=list)
    subscription_trap = models.JSONField(default=dict)
    roadmap = models.JSONField(default=dict)
    tech_stack = models.CharField(max_length=200, blank=True)
    platform = models.CharField(max_length=50, blank=True)

    # Scores
    performance_score = models.IntegerField(null=True, blank=True)
    mobile_score = models.IntegerField(null=True, blank=True)
    seo_score = models.IntegerField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, default='pending',
        choices=[('pending', 'Pending'), ('scanning', 'Scanning'),
                 ('completed', 'Completed'), ('failed', 'Failed')])
    error_message = models.TextField(blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scanned_at']
        verbose_name = 'Prospect Scan'
        verbose_name_plural = 'Prospect Scans'

    def __str__(self):
        return f"{self.contact.name} - {self.url} ({self.grade or self.status})"


class EmailDraft(models.Model):
    """
    AI Message Composer - First contact tool.
    Supports Email, SMS, and WhatsApp channels.
    After sending, contacts are added to pipeline for AI autopilot follow-ups.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='email')
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='email_drafts'
    )

    # PIPELINE - contacts will be added to this pipeline after first email
    pipeline = models.ForeignKey(
        'Pipeline',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Select pipeline - contacts will be added here after first email is sent"
    )

    # BULK RECIPIENTS
    # Select multiple contacts from database
    contacts = models.ManyToManyField(
        Contact,
        blank=True,
        related_name='email_drafts',
        help_text="Select contacts from list (can select multiple)"
    )

    # Add manual emails (one per line)
    manual_emails = models.TextField(
        blank=True,
        help_text="Add emails manually - one per line. Example:\njohn@example.com\njane@company.com"
    )

    # Add manual phones (one per line, for SMS/WhatsApp)
    manual_phones = models.TextField(
        blank=True,
        help_text="Add phones manually - one per line. Example:\n+61412345678\nJohn <+61412345678>"
    )

    # Tracking
    sent_count = models.IntegerField(default=0, help_text="How many emails sent from this draft")
    total_recipients = models.IntegerField(default=0, help_text="Total recipients (contacts + manual)")
    deals_created = models.IntegerField(default=0, help_text="Deals created in pipeline")

    # Legacy fields (for backward compatibility)
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_drafts_legacy',
        help_text="Legacy - use 'contacts' instead"
    )
    recipient_name = models.CharField(max_length=255, blank=True)
    recipient_email = models.EmailField(blank=True)
    recipient_company = models.CharField(max_length=255, blank=True)
    recipient_website = models.URLField(blank=True)

    # Your input/suggestions for AI
    email_type = models.CharField(
        max_length=50,
        choices=[
            # Desi Firms - Business Listings
            ('directory_invitation', 'Directory Invitation'),
            ('listing_benefits', 'Free Listing Benefits'),
            ('invitation_followup', 'Invitation Follow-up'),
            ('onboarding_help', 'Onboarding Help'),
            # Desi Firms - Events
            ('event_invitation', 'Event Organizer Invitation'),
            ('event_benefits', 'Event Platform Benefits'),
            # Desi Firms - Real Estate
            ('agent_invitation', 'Agent/Agency Invitation'),
            ('free_listing', 'Free Property Listing'),
            # Desi Firms - Classifieds
            ('classifieds_invitation', 'Classifieds Invitation'),
            # Desi Firms - Nudge (Registered but inactive users)
            ('business_nudge', '🔔 Nudge: List Your Business'),
            ('business_nudge_2', '🔔 Nudge 2: Business Reminder'),
            ('realestate_nudge', '🔔 Nudge: Become an Agent'),
            ('realestate_nudge_2', '🔔 Nudge 2: Agent Reminder'),
            ('events_nudge', '🔔 Nudge: Post Your Events'),
            ('events_nudge_2', '🔔 Nudge 2: Events Reminder'),
            # Codeteki - Sales
            ('services_intro', 'Web/AI Services Introduction'),
            ('seo_services', 'SEO Services Pitch'),
            ('sales_followup', 'Sales Follow-up'),
            ('proposal_followup', 'Proposal Follow-up'),
            # Codeteki - Prospect Audit
            ('prospect_audit_outreach', 'Prospect Audit Outreach'),
            ('sector_outreach', 'Sector-Specific Outreach'),
            # Codeteki - Backlink
            ('backlink_pitch', 'Backlink Pitch'),
            ('guest_post', 'Guest Post Offer'),
            ('backlink_followup', 'Backlink Follow-up'),
            # Codeteki - Partnership
            ('partnership_intro', 'Partnership Introduction'),
            ('collaboration', 'Collaboration Proposal'),
            ('partnership_followup', 'Partnership Follow-up'),
            # Re-engagement / Existing Customers
            ('existing_customer_update', 'Existing Customer Update'),
            ('win_back', 'Win-back Email'),
            ('feature_announcement', 'New Feature Announcement'),
            ('pricing_update', 'Pricing Update'),
            # Generic
            ('invitation', 'General Invitation'),
            ('followup', 'General Follow-up'),
            ('custom', 'Custom'),
        ],
        default='invitation'
    )
    your_suggestions = models.TextField(
        blank=True,
        help_text="Your ideas, key points, or specific things to mention. AI will incorporate these."
    )
    tone = models.CharField(
        max_length=30,
        choices=[
            ('professional', 'Professional'),
            ('friendly', 'Friendly & Casual'),
            ('formal', 'Formal'),
            ('persuasive', 'Persuasive'),
        ],
        default='professional'
    )

    # AI Generated content
    generated_subject = models.CharField(max_length=255, blank=True)
    generated_body = models.TextField(blank=True)

    # Edited/final version
    final_subject = models.CharField(max_length=255, blank=True)
    final_body = models.TextField(blank=True)

    # Sent tracking
    is_sent = models.BooleanField(default=False, help_text="Was this email sent?")
    sent_at = models.DateTimeField(null=True, blank=True)

    # Template features
    is_template = models.BooleanField(default=False, help_text="Save as reusable template")
    template_name = models.CharField(max_length=100, blank=True, help_text="Name for template")

    # Override skip behavior
    send_to_pipeline_contacts = models.BooleanField(
        default=False,
        help_text="Also send to contacts already in a pipeline (normally skipped)"
    )

    # Scheduling fields
    SCHEDULE_STATUS_CHOICES = [
        ('not_scheduled', 'Not Scheduled'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    scheduled_for = models.DateTimeField(
        null=True, blank=True,
        help_text="Schedule email to be sent at this time (Australia/Sydney timezone)"
    )
    schedule_status = models.CharField(
        max_length=20,
        choices=SCHEDULE_STATUS_CHOICES,
        default='not_scheduled'
    )
    schedule_error = models.TextField(blank=True, help_text="Error message if scheduled send failed")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Message Draft'
        verbose_name_plural = 'AI Message Composer'

    def get_all_recipients(self):
        """Get all recipients as list of dicts. For email: email, name, contact. For SMS/WhatsApp: phone, name, contact."""
        recipients = []

        if self.channel in ('sms', 'whatsapp'):
            return self._get_phone_recipients()

        # Email channel - existing behavior
        # Add contacts from ManyToMany
        for contact in self.contacts.all():
            if not contact.is_unsubscribed:
                recipients.append({
                    'email': contact.email,
                    'name': contact.name,
                    'company': contact.company,
                    'website': contact.website,
                    'contact': contact
                })

        # Add manual emails (supports both "email" and "Name <email>" formats)
        if self.manual_emails:
            import re
            for line in self.manual_emails.strip().split('\n'):
                line = line.strip()
                if not line or '@' not in line:
                    continue
                # Parse "Name <email>" format
                match = re.match(r'^(.+?)\s*<(.+?)>$', line)
                if match:
                    name = match.group(1).strip()
                    email = match.group(2).strip()
                else:
                    email = line
                    name = email.split('@')[0]
                # Check if already in contacts list
                if not any(r['email'] == email for r in recipients):
                    recipients.append({
                        'email': email,
                        'name': name,
                        'company': '',
                        'website': '',
                        'contact': None
                    })

        # Legacy support
        if self.contact and not self.contact.is_unsubscribed:
            if not any(r['email'] == self.contact.email for r in recipients):
                recipients.append({
                    'email': self.contact.email,
                    'name': self.contact.name,
                    'company': self.contact.company,
                    'website': self.contact.website,
                    'contact': self.contact
                })

        if self.recipient_email and not any(r['email'] == self.recipient_email for r in recipients):
            recipients.append({
                'email': self.recipient_email,
                'name': self.recipient_name or self.recipient_email.split('@')[0],
                'company': self.recipient_company,
                'website': self.recipient_website,
                'contact': None
            })

        return recipients

    def _get_phone_recipients(self):
        """Get phone recipients for SMS/WhatsApp channels."""
        import re
        recipients = []

        # Add contacts from ManyToMany that have phone and aren't opted out
        for contact in self.contacts.all():
            if contact.phone and not contact.sms_opted_out:
                normalized = Contact.normalize_phone(contact.phone)
                if normalized and not any(r.get('phone') == normalized for r in recipients):
                    recipients.append({
                        'phone': normalized,
                        'name': contact.name,
                        'company': contact.company,
                        'website': contact.website,
                        'contact': contact,
                    })

        # Add manual phones
        if self.manual_phones:
            for line in self.manual_phones.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                # Parse "Name <+61...>" format
                match = re.match(r'^(.+?)\s*<(.+?)>$', line)
                if match:
                    name = match.group(1).strip()
                    phone = match.group(2).strip()
                else:
                    phone = line
                    name = ''
                normalized = Contact.normalize_phone(phone)
                if normalized and not any(r.get('phone') == normalized for r in recipients):
                    recipients.append({
                        'phone': normalized,
                        'name': name,
                        'company': '',
                        'website': '',
                        'contact': None,
                    })

        return recipients

    def get_recipient_count(self):
        """Get total count of recipients."""
        return len(self.get_all_recipients())

    def update_recipient_count(self):
        """Update the total_recipients field."""
        self.total_recipients = self.get_recipient_count()
        self.save(update_fields=['total_recipients'])

    def get_scheduled_time_display(self):
        """Get formatted scheduled time in Australia/Sydney timezone."""
        if not self.scheduled_for:
            return None
        import pytz
        sydney = pytz.timezone('Australia/Sydney')
        local_time = self.scheduled_for.astimezone(sydney)
        return local_time.strftime('%a %d %b %Y at %I:%M %p AEST')

    def cancel_schedule(self):
        """Cancel a scheduled email send."""
        self.schedule_status = 'cancelled'
        self.scheduled_for = None
        self.save(update_fields=['schedule_status', 'scheduled_for'])

    # Legacy methods for backward compatibility
    def get_recipient_email(self):
        """Legacy: Get first recipient email."""
        recipients = self.get_all_recipients()
        return recipients[0]['email'] if recipients else ''

    def get_recipient_name(self):
        """Legacy: Get first recipient name."""
        recipients = self.get_all_recipients()
        return recipients[0]['name'] if recipients else 'there'

    def __str__(self):
        if self.is_template and self.template_name:
            return f"[Template] {self.template_name}"
        count = self.total_recipients or self.get_recipient_count()
        if count > 0:
            return f"Draft - {count} recipient(s)"
        return f"Draft - {self.brand.name} ({self.email_type})"


class LeadSearch(models.Model):
    """Stores Google Places search results for lead discovery."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, related_name='lead_searches')
    query = models.CharField(max_length=200, help_text="Search query used")
    industry = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=200, help_text="Location searched")
    radius_km = models.IntegerField(default=5)
    results = models.JSONField(default=list, help_text="Raw API results")
    results_count = models.IntegerField(default=0)
    imported_count = models.IntegerField(default=0)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']
        verbose_name = 'Lead Search'
        verbose_name_plural = 'Lead Searches'

    def __str__(self):
        return f"{self.query} - {self.location} ({self.results_count} results)"
