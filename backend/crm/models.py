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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='contacts',
        null=True,
        blank=True,
        help_text="Which brand this contact belongs to"
    )
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, help_text="Leave blank to auto-extract from email/domain")
    company = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
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

    def __str__(self):
        return f"{self.name} ({self.email})"

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

    def save(self, *args, **kwargs):
        """Normalize email and auto-extract name/company if needed."""
        if self.email:
            self.email = self.normalize_email(self.email)

            # Auto-extract company from domain if not provided
            if not self.company or self.company.strip() == '':
                email_domain = self.email.split('@')[1] if '@' in self.email else ''
                if email_domain and not email_domain.endswith(('gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com')):
                    self.company = self._humanize_domain(email_domain)

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


class EmailLog(models.Model):
    """Track all sent emails."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='email_logs')
    sequence_step = models.ForeignKey(
        SequenceStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )

    # Email content
    subject = models.CharField(max_length=255)
    body = models.TextField()
    from_email = models.EmailField(default='outreach@codeteki.au')
    to_email = models.EmailField()

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
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'

    def __str__(self):
        status = "Sent" if self.sent_at else "Draft"
        return f"{status}: {self.subject} to {self.to_email}"


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


class EmailDraft(models.Model):
    """
    AI Email Composer - First contact tool.
    After sending, contacts are added to pipeline for AI autopilot follow-ups.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
            # Codeteki - Sales
            ('services_intro', 'Web/AI Services Introduction'),
            ('seo_services', 'SEO Services Pitch'),
            ('sales_followup', 'Sales Follow-up'),
            ('proposal_followup', 'Proposal Follow-up'),
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Email Draft'
        verbose_name_plural = 'AI Email Composer'

    def get_all_recipients(self):
        """Get all recipients as list of dicts with email, name, contact (if any)."""
        recipients = []

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

        # Add manual emails
        if self.manual_emails:
            for line in self.manual_emails.strip().split('\n'):
                email = line.strip()
                if email and '@' in email:
                    # Check if already in contacts list
                    if not any(r['email'] == email for r in recipients):
                        recipients.append({
                            'email': email,
                            'name': email.split('@')[0],
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

    def get_recipient_count(self):
        """Get total count of recipients."""
        return len(self.get_all_recipients())

    def update_recipient_count(self):
        """Update the total_recipients field."""
        self.total_recipients = self.get_recipient_count()
        self.save(update_fields=['total_recipients'])

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
