"""
CRM Admin Configuration
Using Django Unfold for modern Tailwind-based UI
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from django import forms

from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import action, display

from .models import (
    Brand,
    Contact,
    CodetekiContact,
    DesiFirmsContact,
    Pipeline,
    PipelineStage,
    Deal,
    EmailSequence,
    SequenceStep,
    EmailLog,
    AIDecisionLog,
    BacklinkOpportunity,
    AIPromptTemplate,
    DealActivity,
    ContactImport,
    BacklinkImport,
    EmailDraft,
)


# =============================================================================
# BRAND ADMIN
# =============================================================================

@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ['name', 'website', 'from_email', 'is_active', 'contacts_count', 'pipelines_count']
    list_filter = ['is_active']
    search_fields = ['name', 'website', 'from_email']
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Brand Info', {
            'fields': ('name', 'slug', 'website', 'description', 'logo_url', 'primary_color', 'is_active')
        }),
        ('Email Configuration', {
            'fields': ('from_email', 'from_name', 'reply_to_email')
        }),
        ('Zoho Credentials (Optional - uses global if empty)', {
            'fields': ('zoho_client_id', 'zoho_client_secret', 'zoho_account_id', 'zoho_refresh_token', 'zoho_api_domain'),
            'classes': ['collapse']
        }),
        ('AI Configuration', {
            'fields': ('ai_company_description', 'ai_value_proposition', 'ai_business_updates', 'ai_target_context', 'ai_approach_style', 'backlink_content_types'),
            'description': 'These are used to personalize AI-generated emails. Business updates and target context help AI write context-aware emails.'
        }),
    )

    @display(description="Contacts")
    def contacts_count(self, obj):
        return obj.contacts.count()

    @display(description="Pipelines")
    def pipelines_count(self, obj):
        return obj.pipelines.count()

    @action(description="🔧 Test Email Configuration")
    def test_email_config(self, request, queryset):
        """Send a test email to verify Zoho configuration is working."""
        from crm.services.email_service import ZohoEmailService
        from django.contrib import messages
        from django.template.response import TemplateResponse
        from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

        if queryset.count() > 1:
            self.message_user(request, "⚠️ Please select only 1 brand to test.", messages.WARNING)
            return

        brand = queryset.first()

        # Check if form submitted with test email
        if 'send_test' in request.POST:
            test_email = request.POST.get('test_email', '').strip()
            if not test_email or '@' not in test_email:
                self.message_user(request, "❌ Please enter a valid email address.", messages.ERROR)
                return

            # Initialize email service for this brand
            email_service = ZohoEmailService(brand=brand)

            # Check configuration
            config_info = []
            config_info.append(f"Brand: {brand.name}")
            config_info.append(f"From Email: {email_service.from_email}")
            config_info.append(f"From Name: {email_service.from_name}")
            config_info.append(f"API Domain: {email_service.api_domain}")
            config_info.append(f"Account ID: {email_service.account_id[:8]}..." if email_service.account_id else "Account ID: NOT SET")
            config_info.append(f"Client ID: {email_service.client_id[:8]}..." if email_service.client_id else "Client ID: NOT SET")
            config_info.append(f"Enabled: {email_service.enabled}")

            if not email_service.enabled:
                self.message_user(
                    request,
                    f"❌ Zoho not configured for {brand.name}! Missing credentials. Config: {' | '.join(config_info)}",
                    messages.ERROR
                )
                return

            # Try to send test email
            result = email_service.send(
                to=test_email,
                subject=f"[TEST] Email Configuration Test - {brand.name}",
                body=f"""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #22c55e;">✅ Email Configuration Working!</h2>
                    <p>This is a test email from <strong>{brand.name}</strong>.</p>
                    <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">
                    <h3>Configuration Details:</h3>
                    <ul>
                        <li><strong>Brand:</strong> {brand.name}</li>
                        <li><strong>From Email:</strong> {email_service.from_email}</li>
                        <li><strong>From Name:</strong> {email_service.from_name}</li>
                        <li><strong>API Domain:</strong> {email_service.api_domain}</li>
                    </ul>
                    <p style="color: #6b7280; font-size: 12px; margin-top: 30px;">
                        This test email was sent from the CRM admin panel.
                    </p>
                </body>
                </html>
                """,
                from_name=f"{brand.name} (Test)"
            )

            if result.get('success'):
                self.message_user(
                    request,
                    f"✅ Test email sent successfully to {test_email}! Message ID: {result.get('message_id', 'N/A')}. "
                    f"Check your inbox (and spam folder). Config: {' | '.join(config_info)}",
                    messages.SUCCESS
                )
            else:
                self.message_user(
                    request,
                    f"❌ Failed to send test email: {result.get('error', 'Unknown error')}. Config: {' | '.join(config_info)}",
                    messages.ERROR
                )
            return

        # Show test email form
        email_service = ZohoEmailService(brand=brand)
        context = {
            **self.admin_site.each_context(request),
            'title': f'Test Email Configuration - {brand.name}',
            'brand': brand,
            'opts': self.model._meta,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
            'queryset': queryset,
            'email_service': email_service,
            'config': {
                'from_email': email_service.from_email,
                'from_name': email_service.from_name,
                'api_domain': email_service.api_domain,
                'account_id': f"{email_service.account_id[:8]}..." if email_service.account_id else "NOT SET",
                'client_id': f"{email_service.client_id[:8]}..." if email_service.client_id else "NOT SET",
                'client_secret': "SET" if email_service.client_secret else "NOT SET",
                'refresh_token': "SET" if email_service.refresh_token else "NOT SET",
                'enabled': email_service.enabled,
            }
        }

        return TemplateResponse(
            request,
            'admin/crm/brand/test_email_config.html',
            context
        )

    actions = ['test_email_config']

    class Media:
        js = ('admin/js/seo-loading.js',)


# =============================================================================
# INLINES
# =============================================================================

class PipelineStageInline(TabularInline):
    model = PipelineStage
    extra = 1
    fields = ('name', 'order', 'days_until_followup', 'is_terminal')
    ordering = ['order']


class SequenceStepInline(TabularInline):
    model = SequenceStep
    extra = 1
    fields = ('order', 'delay_days', 'subject_template', 'ai_personalize')
    ordering = ['order']


class DealActivityInline(TabularInline):
    model = DealActivity
    extra = 0
    fields = ('activity_type', 'description', 'created_at')
    readonly_fields = ('activity_type', 'description', 'created_at')
    ordering = ['-created_at']
    max_num = 20
    can_delete = False


class EmailLogInline(TabularInline):
    model = EmailLog
    extra = 0
    fields = ('subject', 'sent_at', 'opened', 'replied')
    readonly_fields = ('subject', 'sent_at', 'opened', 'replied')
    ordering = ['-created_at']
    max_num = 10
    can_delete = False


# =============================================================================
# CONTACT ADMIN
# =============================================================================

class ContactAdminForm(forms.ModelForm):
    """Custom form with duplicate email validation."""

    class Meta:
        model = Contact
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        brand = cleaned_data.get('brand')

        if email and brand:
            # Normalize email
            email = Contact.normalize_email(email) if hasattr(Contact, 'normalize_email') else email.lower().strip()

            # Check for existing contact with same email + brand (exclude current instance)
            qs = Contact.objects.filter(email__iexact=email, brand=brand)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                existing = qs.first()
                raise forms.ValidationError(
                    f"A contact with email '{email}' already exists for {brand.name}. "
                    f"Existing contact: {existing.name or 'No name'} (ID: {existing.pk})"
                )

        return cleaned_data


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    form = ContactAdminForm
    list_display = [
        'name',
        'email',
        'company',
        'status_badge',
        'email_count',
        'last_emailed_display',
        'is_unsubscribed_badge',
        'created_at',
    ]
    list_filter = ['status', 'is_unsubscribed', 'brand', 'contact_type', 'source', 'created_at']
    search_fields = ['name', 'email', 'company', 'website']
    readonly_fields = ['created_at', 'updated_at', 'id', 'last_emailed_at', 'email_count', 'unsubscribed_at']
    ordering = ['-created_at']

    class Media:
        js = ('admin/js/seo-loading.js',)

    fieldsets = (
        ('Contact Information', {
            'fields': ('brand', 'name', 'email', 'company', 'website')
        }),
        ('Status', {
            'fields': ('status', 'contact_type', 'source'),
            'description': 'Track outreach progress'
        }),
        ('Email History', {
            'fields': ('email_count', 'last_emailed_at'),
            'description': 'Auto-updated when emails are sent'
        }),
        ('Unsubscribe', {
            'fields': ('is_unsubscribed', 'unsubscribed_brands', 'unsubscribed_at', 'unsubscribe_reason'),
            'classes': ['collapse'],
            'description': 'Brand-specific unsubscribes. Global unsubscribe blocks all brands.'
        }),
        ('Classification', {
            'fields': ('tags', 'domain_authority', 'ai_score'),
            'classes': ['collapse']
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )

    @display(description="Status", label=True)
    def status_badge(self, obj):
        # If unsubscribed (globally or brand-specific), always show as danger with clear indicator
        if obj.is_unsubscribed:
            return "🚫 UNSUBSCRIBED", "danger"
        elif obj.unsubscribed_brands and len(obj.unsubscribed_brands) > 0:
            return "🚫 UNSUBSCRIBED", "danger"

        colors = {
            'new': 'info',
            'contacted': 'warning',
            'replied': 'success',
            'interested': 'success',
            'not_interested': 'danger',
            'unsubscribed': 'danger',
        }
        return obj.get_status_display(), colors.get(obj.status, 'info')

    @display(description="Unsubscribed", label=True)
    def is_unsubscribed_badge(self, obj):
        if obj.is_unsubscribed:
            return "🚫 ALL BRANDS", "danger"
        elif obj.unsubscribed_brands and len(obj.unsubscribed_brands) > 0:
            brands = ', '.join(obj.unsubscribed_brands).upper()
            return f"🚫 {brands}", "danger"  # Red for visibility
        return "✅ Active", "success"

    @display(description="Last Emailed")
    def last_emailed_display(self, obj):
        if obj.last_emailed_at:
            return obj.last_emailed_at.strftime('%Y-%m-%d')
        return "-"

    @action(description="Mark as Unsubscribed")
    def mark_unsubscribed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            is_unsubscribed=True,
            unsubscribed_at=timezone.now(),
            status='unsubscribed'
        )
        self.message_user(request, f"Marked {updated} contact(s) as unsubscribed.")

    @action(description="Resubscribe (remove unsubscribe)")
    def resubscribe(self, request, queryset):
        from crm.models import Deal
        updated = 0
        deals_reactivated = 0

        for contact in queryset:
            # Clear all unsubscribe flags
            contact.is_unsubscribed = False
            contact.unsubscribed_brands = []
            contact.unsubscribed_at = None
            contact.unsubscribe_reason = ''
            contact.status = 'new'
            contact.save()
            updated += 1

            # Reactivate deals that were lost due to unsubscribe
            reactivated = Deal.objects.filter(
                contact=contact,
                status='lost',
                lost_reason='unsubscribed'
            ).update(status='active', lost_reason='')
            deals_reactivated += reactivated

        msg = f"Resubscribed {updated} contact(s)."
        if deals_reactivated:
            msg += f" Reactivated {deals_reactivated} deal(s)."
        self.message_user(request, msg)

    @action(description="📊 Add to Pipeline (with selection)")
    def add_to_pipeline_followup(self, request, queryset):
        """Add contacts to a selected pipeline - shows confirmation page first."""
        from crm.models import Pipeline, Deal, PipelineStage
        from django.utils import timezone
        from django.template.response import TemplateResponse
        from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
        from django.contrib import messages

        # Get the brand from first contact
        first_contact = queryset.first()
        if not first_contact or not first_contact.brand:
            self.message_user(request, "❌ No brand found for selected contacts.", messages.ERROR)
            return

        brand = first_contact.brand

        # Get available pipelines for this brand
        pipelines = Pipeline.objects.filter(brand=brand, is_active=True)

        if not pipelines.exists():
            self.message_user(request, f"❌ No active pipelines for {brand.name}.", messages.ERROR)
            return

        # Check if form was submitted with pipeline selection
        if 'apply' in request.POST:
            pipeline_id = request.POST.get('pipeline')
            stage_id = request.POST.get('stage')

            if not pipeline_id:
                self.message_user(request, "❌ Please select a pipeline.", messages.ERROR)
                return

            pipeline = Pipeline.objects.get(id=pipeline_id)

            # Get stage
            if stage_id:
                stage = PipelineStage.objects.get(id=stage_id)
            else:
                # Default to first stage
                stage = pipeline.stages.order_by('order').first()

            if not stage:
                self.message_user(request, "❌ Pipeline has no stages.", messages.ERROR)
                return

            # Now create deals
            created = 0
            skipped = 0

            for contact in queryset:
                if contact.is_unsubscribed:
                    skipped += 1
                    continue

                # Check if already in this pipeline
                existing = Deal.objects.filter(contact=contact, pipeline=pipeline, status='active').exists()
                if existing:
                    skipped += 1
                    continue

                Deal.objects.create(
                    contact=contact,
                    pipeline=pipeline,
                    current_stage=stage,
                    status='active',
                    emails_sent=0,  # No emails sent yet
                    next_action_date=timezone.now() + timezone.timedelta(days=stage.days_until_followup or 3),
                    ai_notes=f"Added manually to '{pipeline.name}' at '{stage.name}' stage"
                )
                created += 1

            self.message_user(
                request,
                f"✅ Created {created} deals in '{pipeline.name}' → '{stage.name}'. Skipped {skipped}.",
                messages.SUCCESS
            )
            return

        # Show confirmation page with pipeline/stage selection
        context = {
            **self.admin_site.each_context(request),
            'title': 'Select Pipeline and Stage',
            'queryset': queryset,
            'opts': self.model._meta,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
            'pipelines': pipelines,
            'brand': brand,
            'contact_count': queryset.count(),
            'contacts_preview': queryset[:10],  # Show first 10
        }

        return TemplateResponse(
            request,
            'admin/crm/contact/add_to_pipeline_confirmation.html',
            context
        )

    actions = ['mark_unsubscribed', 'resubscribe', 'add_to_pipeline_followup']


# =============================================================================
# BRAND-SPECIFIC CONTACT ADMINS (Separate Views)
# =============================================================================

class CodetekiContactAdminForm(forms.ModelForm):
    """Custom form for Codeteki contacts with duplicate email validation."""

    class Meta:
        model = Contact
        fields = '__all__'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = Contact.normalize_email(email) if hasattr(Contact, 'normalize_email') else email.lower().strip()

            # Get Codeteki brand
            try:
                brand = Brand.objects.get(slug='codeteki')
            except Brand.DoesNotExist:
                return email

            # Check for existing contact
            qs = Contact.objects.filter(email__iexact=email, brand=brand)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                existing = qs.first()
                raise forms.ValidationError(
                    f"A contact with email '{email}' already exists for Codeteki. "
                    f"Existing contact: {existing.name or 'No name'} (ID: {existing.pk})"
                )
        return email


@admin.register(CodetekiContact)
class CodetekiContactAdmin(ContactAdmin):
    """Codeteki-only contacts view - brand auto-selected."""
    form = CodetekiContactAdminForm

    # Remove brand from fieldsets - it's auto-set
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'company', 'website')
        }),
        ('Status', {
            'fields': ('status', 'contact_type', 'source'),
            'description': 'Track outreach progress'
        }),
        ('Email History', {
            'fields': ('email_count', 'last_emailed_at'),
            'description': 'Auto-updated when emails are sent'
        }),
        ('Unsubscribe', {
            'fields': ('is_unsubscribed', 'unsubscribed_brands', 'unsubscribed_at', 'unsubscribe_reason'),
            'classes': ['collapse'],
            'description': 'Brand-specific unsubscribes. Global unsubscribe blocks all brands.'
        }),
        ('Classification', {
            'fields': ('tags', 'domain_authority', 'ai_score'),
            'classes': ['collapse']
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(brand__slug='codeteki')

    def save_model(self, request, obj, form, change):
        """Auto-set brand to Codeteki for new contacts."""
        if not change:  # New object
            try:
                obj.brand = Brand.objects.get(slug='codeteki')
            except Brand.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)


class DesiFirmsContactAdminForm(forms.ModelForm):
    """Custom form for Desi Firms contacts with duplicate email validation."""

    class Meta:
        model = Contact
        fields = '__all__'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = Contact.normalize_email(email) if hasattr(Contact, 'normalize_email') else email.lower().strip()

            # Get Desi Firms brand
            try:
                brand = Brand.objects.get(slug='desifirms')
            except Brand.DoesNotExist:
                return email

            # Check for existing contact
            qs = Contact.objects.filter(email__iexact=email, brand=brand)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                existing = qs.first()
                raise forms.ValidationError(
                    f"A contact with email '{email}' already exists for Desi Firms. "
                    f"Existing contact: {existing.name or 'No name'} (ID: {existing.pk})"
                )
        return email


@admin.register(DesiFirmsContact)
class DesiFirmsContactAdmin(ContactAdmin):
    """Desi Firms-only contacts view - brand auto-selected."""
    form = DesiFirmsContactAdminForm

    # Remove brand from fieldsets - it's auto-set
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'company', 'website')
        }),
        ('Status', {
            'fields': ('status', 'contact_type', 'source'),
            'description': 'Track outreach progress'
        }),
        ('Email History', {
            'fields': ('email_count', 'last_emailed_at'),
            'description': 'Auto-updated when emails are sent'
        }),
        ('Unsubscribe', {
            'fields': ('is_unsubscribed', 'unsubscribed_brands', 'unsubscribed_at', 'unsubscribe_reason'),
            'classes': ['collapse'],
            'description': 'Brand-specific unsubscribes. Global unsubscribe blocks all brands.'
        }),
        ('Classification', {
            'fields': ('tags', 'domain_authority', 'ai_score'),
            'classes': ['collapse']
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(brand__slug='desifirms')

    def save_model(self, request, obj, form, change):
        """Auto-set brand to Desi Firms for new contacts."""
        if not change:  # New object
            try:
                obj.brand = Brand.objects.get(slug='desifirms')
            except Brand.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)


# =============================================================================
# PIPELINE ADMIN
# =============================================================================

@admin.register(Pipeline)
class PipelineAdmin(ModelAdmin):
    list_display = ['name', 'pipeline_type_badge', 'stages_count', 'deals_count', 'is_active']
    list_filter = ['pipeline_type', 'is_active']
    search_fields = ['name', 'description']
    inlines = [PipelineStageInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'pipeline_type', 'description', 'is_active')
        }),
    )

    @display(description="Type", label=True)
    def pipeline_type_badge(self, obj):
        colors = {
            'sales': 'success',
            'backlink': 'warning',
            'partnership': 'info',
        }
        return obj.get_pipeline_type_display(), colors.get(obj.pipeline_type, 'info')

    @display(description="Stages")
    def stages_count(self, obj):
        return obj.stages.count()

    @display(description="Deals")
    def deals_count(self, obj):
        return obj.deals.count()


@admin.register(PipelineStage)
class PipelineStageAdmin(ModelAdmin):
    list_display = ['name', 'pipeline', 'order', 'days_until_followup', 'is_terminal']
    list_filter = ['pipeline', 'is_terminal']
    ordering = ['pipeline', 'order']


# =============================================================================
# DEAL ADMIN
# =============================================================================

@admin.register(Deal)
class DealAdmin(ModelAdmin):
    list_display = [
        'contact_name',
        'pipeline',
        'current_stage_display',
        'status_badge',
        'lost_reason_display',
        'next_action_date',
        'emails_sent',
        'value_display',
        'created_at',
    ]
    list_filter = ['pipeline', 'current_stage', 'status', 'lost_reason', 'created_at']
    search_fields = ['contact__name', 'contact__email', 'contact__company']
    readonly_fields = ['id', 'created_at', 'updated_at', 'stage_entered_at', 'emails_sent']
    inlines = [DealActivityInline, EmailLogInline]
    ordering = ['-created_at']

    class Media:
        js = ('admin/js/seo-loading.js',)

    fieldsets = (
        ('Deal Information', {
            'fields': ('contact', 'pipeline', 'current_stage', 'status', 'lost_reason', 'value')
        }),
        ('AI & Automation', {
            'fields': ('ai_notes', 'next_action_date')
        }),
        ('Tracking', {
            'fields': ('emails_sent', 'last_contact_date', 'stage_entered_at'),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )

    @display(description="Contact")
    def contact_name(self, obj):
        return obj.contact.name

    @display(description="Stage")
    def current_stage_display(self, obj):
        if obj.current_stage:
            return obj.current_stage.name
        return "-"

    @display(description="Status", label=True)
    def status_badge(self, obj):
        colors = {
            'active': 'info',
            'won': 'success',
            'lost': 'danger',
            'paused': 'warning',
        }
        return obj.get_status_display(), colors.get(obj.status, 'info')

    @display(description="Lost Reason", label=True)
    def lost_reason_display(self, obj):
        if obj.status != 'lost' or not obj.lost_reason:
            return "-", "default"
        reason_colors = {
            'unsubscribed': 'danger',
            'no_response': 'warning',
            'not_interested': 'warning',
            'competitor': 'info',
            'budget': 'info',
            'timing': 'info',
            'invalid_email': 'danger',
            'other': 'default',
        }
        return obj.get_lost_reason_display(), reason_colors.get(obj.lost_reason, 'default')

    @display(description="Value")
    def value_display(self, obj):
        if obj.value:
            return f"${obj.value:,.2f}"
        return "-"

    @action(description="Move to next stage")
    def move_to_next_stage(self, request, queryset):
        for deal in queryset:
            if deal.current_stage:
                next_stage = PipelineStage.objects.filter(
                    pipeline=deal.pipeline,
                    order__gt=deal.current_stage.order
                ).order_by('order').first()
                if next_stage:
                    deal.move_to_stage(next_stage)
        self.message_user(request, f"Moved {queryset.count()} deals to next stage.")

    @action(description="🏆 Mark as Won (stops all automation)")
    def mark_as_won(self, request, queryset):
        """Mark deals as won - for contacts who registered/converted. Stops all automation."""
        from django.contrib import messages
        from django.utils import timezone

        # Pipeline type to Registered Users pipeline mapping
        pipeline_mapping = {
            'realestate': 'Registered Users - Real Estate',
            'business': 'Registered Users - Business',
            'events': 'Registered Users - Events',
        }

        won_count = 0
        moved_count = 0

        for deal in queryset:
            if deal.status != 'won':
                deal.status = 'won'
                deal.save(update_fields=['status', 'updated_at'])

                # Log the activity
                DealActivity.objects.create(
                    deal=deal,
                    activity_type='status_change',
                    description=f"Marked as Won - contact converted/registered"
                )
                won_count += 1

                # Move to Registered Users pipeline
                source_type = deal.pipeline.pipeline_type if deal.pipeline else None
                pipeline_name_lower = deal.pipeline.name.lower() if deal.pipeline else ''

                # Skip if already in registered users pipeline
                if 'registered users' in pipeline_name_lower or 'nudge' in pipeline_name_lower:
                    continue

                target_pipeline_name = pipeline_mapping.get(source_type)
                if not target_pipeline_name:
                    continue

                try:
                    # Find target pipeline
                    target_pipeline = Pipeline.objects.filter(
                        name__iexact=target_pipeline_name,
                        is_active=True
                    ).first()

                    if not target_pipeline:
                        continue

                    # Check if already exists
                    if Deal.objects.filter(
                        contact=deal.contact,
                        pipeline=target_pipeline,
                        status='active'
                    ).exists():
                        continue

                    # Get first stage
                    first_stage = target_pipeline.stages.order_by('order').first()
                    if not first_stage:
                        continue

                    # Create new deal in registered users pipeline
                    new_deal = Deal.objects.create(
                        contact=deal.contact,
                        pipeline=target_pipeline,
                        current_stage=first_stage,
                        status='active',
                        next_action_date=timezone.now(),
                        ai_notes=f"Auto-created from won deal in {deal.pipeline.name}",
                    )

                    DealActivity.objects.create(
                        deal=new_deal,
                        activity_type='stage_change',
                        description=f"Deal created from won deal in {deal.pipeline.name}",
                    )
                    moved_count += 1

                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(f"Failed to move won deal: {e}")

        if won_count > 0:
            msg = f"🏆 Marked {won_count} deal(s) as Won!"
            if moved_count > 0:
                msg += f" Moved {moved_count} to Registered Users pipeline for nurturing."
            self.message_user(request, msg, messages.SUCCESS)
        else:
            self.message_user(request, "No deals were updated (they may already be won).", messages.WARNING)

    @action(description="❌ Mark as Lost")
    def mark_as_lost(self, request, queryset):
        """Mark deals as lost - for contacts who declined or are not interested."""
        from django.contrib import messages

        lost_count = 0
        for deal in queryset:
            if deal.status not in ['won', 'lost']:
                deal.status = 'lost'
                deal.lost_reason = 'not_interested'
                deal.save(update_fields=['status', 'lost_reason', 'updated_at'])

                # Log the activity
                DealActivity.objects.create(
                    deal=deal,
                    activity_type='status_change',
                    description=f"Marked as Lost - not interested"
                )
                lost_count += 1

        if lost_count > 0:
            self.message_user(request, f"❌ Marked {lost_count} deal(s) as Lost. They won't receive further emails.", messages.SUCCESS)
        else:
            self.message_user(request, "No deals were updated (they may already be won/lost).", messages.WARNING)

    @action(description="📧 Preview AI Email (select 1 deal)")
    def preview_email(self, request, queryset):
        """Generate and show AI email draft without sending. Select only 1 deal for full preview."""
        from crm.services.ai_agent import CRMAIAgent
        from django.contrib import messages

        if queryset.count() > 1:
            self.message_user(
                request,
                f"⚠️ Please select only 1 deal for preview. You selected {queryset.count()}. Use 'Generate Draft Emails' for bulk.",
                messages.WARNING
            )
            return

        deal = queryset.first()
        ai_agent = CRMAIAgent()

        try:
            email_result = ai_agent.compose_email(deal, context={'email_type': 'outreach'})
            if email_result.get('success'):
                # Store preview in deal's ai_notes for reference
                preview_text = f"[DRAFT {deal.contact.email}]\nSubject: {email_result['subject']}\n\n{email_result['body']}"
                deal.ai_notes = preview_text
                deal.save(update_fields=['ai_notes'])

                self.message_user(request, f"✅ Preview generated for {deal.contact.name}!", messages.SUCCESS)
                self.message_user(request, f"📧 SUBJECT: {email_result['subject']}", messages.INFO)
                self.message_user(request, f"📝 BODY: {email_result['body'][:500]}{'...' if len(email_result['body']) > 500 else ''}", messages.INFO)
                self.message_user(request, f"💡 Full preview saved to deal's AI Notes. Edit deal to view/modify.", messages.INFO)
            else:
                self.message_user(request, f"❌ Failed to generate email: {email_result.get('error', 'Unknown')}", messages.ERROR)
        except Exception as e:
            self.message_user(request, f"❌ Error: {str(e)}", messages.ERROR)

    @action(description="📝 Generate Draft Emails (bulk - saves to AI Notes)")
    def generate_drafts(self, request, queryset):
        """Generate email drafts for multiple deals and save to AI Notes field."""
        from crm.tasks import generate_email_draft
        from django.contrib import messages

        count = queryset.count()
        for deal in queryset:
            generate_email_draft.delay(str(deal.id))

        self.message_user(
            request,
            f"📝 Queued {count} draft(s) for generation. Check each deal's 'AI Notes' field in ~30 seconds.",
            messages.SUCCESS
        )

    @action(description="📤 Send Follow-up Email (with preview)")
    def send_email_now(self, request, queryset):
        """Send follow-up email to selected deals - shows preview first."""
        from crm.services.ai_agent import CRMAIAgent
        from crm.services.email_service import ZohoEmailService
        from crm.services.email_templates import (
            get_styled_email, get_email_type_for_stage,
            get_template_for_email
        )
        from crm.views import get_unsubscribe_url
        from django.template.loader import render_to_string
        from django.contrib import messages
        from django.template.response import TemplateResponse
        from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
        from crm.models import EmailLog, DealActivity
        from django.utils import timezone
        from datetime import timedelta

        # Check for confirmation - SEND EMAILS DIRECTLY (not via Celery)
        if 'confirm_send' in request.POST:
            sent_count = 0
            failed_count = 0
            skipped = 0

            for deal in queryset:
                # Get brand first for unsubscribe check
                brand = deal.pipeline.brand if deal.pipeline else None
                brand_slug = brand.slug if brand else None
                contact = deal.contact

                # Check if contact is unsubscribed (global OR brand-specific)
                if contact.is_unsubscribed or (brand_slug and contact.is_unsubscribed_from_brand(brand_slug)):
                    self.message_user(request, f"⚠️ Skipped {contact.email} - unsubscribed", messages.WARNING)
                    skipped += 1
                    continue

                # Check if email was sent recently (within 24 hours)
                recent_email = EmailLog.objects.filter(
                    deal=deal,
                    sent_at__gte=timezone.now() - timedelta(hours=24)
                ).exists()

                if recent_email:
                    skipped += 1
                    continue

                # Validate brand
                if not brand:
                    self.message_user(request, f"❌ Deal {deal.contact.email} has no brand configured", messages.ERROR)
                    failed_count += 1
                    continue

                email_service = ZohoEmailService(brand=brand)
                if not email_service.enabled:
                    self.message_user(request, f"❌ Zoho not configured for {brand.name}", messages.ERROR)
                    failed_count += 1
                    continue

                # Determine email type based on stage
                pipeline_type = deal.pipeline.pipeline_type if deal.pipeline else 'sales'
                pipeline_name = deal.pipeline.name if deal.pipeline else ''
                stage_name = deal.current_stage.name if deal.current_stage else 'follow_up'
                email_type = get_email_type_for_stage(stage_name, pipeline_type, pipeline_name) or 'agent_followup_1'

                # Get recipient info
                recipient_name = contact.name.split()[0] if contact.name else 'there'
                recipient_email = contact.email
                recipient_company = contact.company or 'your business'

                # Check for pre-designed template
                template_path = get_template_for_email(brand_slug, pipeline_type, email_type)

                if template_path and 'generic' not in template_path:
                    # Use pre-designed template
                    context = {
                        'recipient_name': recipient_name,
                        'recipient_email': recipient_email,
                        'recipient_company': recipient_company,
                        'unsubscribe_url': get_unsubscribe_url(recipient_email, brand_slug),
                        'current_year': timezone.now().year,
                        'brand_slug': brand_slug,
                    }
                    html_body = render_to_string(template_path, context)

                    # Get subject based on email type
                    subject_map = {
                        # Real Estate
                        'agent_invitation': f"Join {brand.name} as a Founding Member",
                        'agent_followup_1': f"Just checking in - free listing opportunity",
                        'agent_followup_2': f"Final reminder - free real estate listing",
                        # Business Directory
                        'directory_invitation': f"List {recipient_company} on {brand.name} - FREE",
                        'directory_followup_1': f"Quick follow-up - free business listing",
                        'directory_followup_2': f"Final reminder - free listing opportunity",
                        # Events
                        'events_invitation': f"List your events on {brand.name} - FREE",
                        'events_followup_1': f"Quick follow-up - free event listing",
                        'events_followup_2': f"Final reminder - free event listing",
                        'events_responded': f"Thank you for your interest - {brand.name}",
                        # Nudge - Registered but inactive users
                        'business_nudge': f"Your business listing is almost ready!",
                        'business_nudge_2': f"Still thinking about it? Here's why you should list",
                        'realestate_nudge': f"Your agent profile awaits!",
                        'realestate_nudge_2': f"Quick check-in from {brand.name}",
                        'events_nudge': f"Ready to promote your events?",
                        'events_nudge_2': f"Got any events coming up?",
                    }
                    subject = subject_map.get(email_type, f"Following up - {brand.name}")
                else:
                    # Use AI to generate email
                    ai_agent = CRMAIAgent()
                    email_result = ai_agent.compose_email(deal, context={'email_type': 'followup'})

                    if not email_result.get('success'):
                        self.message_user(request, f"❌ Failed to generate email for {recipient_email}", messages.ERROR)
                        failed_count += 1
                        continue

                    styled_email = get_styled_email(
                        brand_slug=brand_slug,
                        pipeline_type=pipeline_type,
                        email_type='followup',
                        recipient_name=recipient_name,
                        recipient_email=recipient_email,
                        recipient_company=recipient_company,
                        subject=email_result['subject'],
                        body=email_result['body'],
                    )
                    html_body = styled_email['html']
                    subject = email_result['subject']

                # Create email log BEFORE sending
                email_log = EmailLog.objects.create(
                    deal=deal,
                    subject=subject,
                    body=html_body[:5000],  # Truncate for storage
                    to_email=recipient_email,
                    from_email=email_service.from_email,
                    ai_generated=not bool(template_path and 'generic' not in template_path)
                )

                # SEND EMAIL DIRECTLY
                result = email_service.send(
                    to=recipient_email,
                    subject=subject,
                    body=html_body,
                    from_name=brand.from_name
                )

                if result.get('success'):
                    # Update email log
                    email_log.sent_at = timezone.now()
                    email_log.zoho_message_id = result.get('message_id', '')
                    email_log.save()

                    # Update deal
                    deal.emails_sent = (deal.emails_sent or 0) + 1
                    deal.last_contact_date = timezone.now()

                    # Move to next stage
                    if deal.current_stage:
                        next_stage = PipelineStage.objects.filter(
                            pipeline=deal.pipeline,
                            order__gt=deal.current_stage.order
                        ).order_by('order').first()
                        if next_stage:
                            deal.current_stage = next_stage
                            deal.next_action_date = timezone.now() + timedelta(days=next_stage.days_until_followup or 5)

                    deal.save()

                    # Log activity
                    DealActivity.objects.create(
                        deal=deal,
                        activity_type='email_sent',
                        description=f"Follow-up email sent: {subject}",
                        metadata={'email_log_id': str(email_log.id), 'message_id': result.get('message_id')}
                    )

                    # Update contact
                    contact.last_emailed_at = timezone.now()
                    contact.email_count = (contact.email_count or 0) + 1
                    contact.status = 'contacted'
                    contact.save(update_fields=['last_emailed_at', 'email_count', 'status'])

                    sent_count += 1

                    # Show first success details
                    if sent_count == 1:
                        self.message_user(
                            request,
                            f"📧 First email: From {result.get('from_email')} to {recipient_email}, ID: {result.get('message_id', 'N/A')}",
                            messages.INFO
                        )
                else:
                    # Delete the email log since send failed
                    email_log.delete()
                    failed_count += 1
                    self.message_user(
                        request,
                        f"❌ Failed to send to {recipient_email}: {result.get('error', 'Unknown error')}",
                        messages.ERROR
                    )

            # Summary message
            if sent_count:
                self.message_user(request, f"✅ Successfully sent {sent_count} email(s) & moved to next stage!", messages.SUCCESS)
            if skipped:
                self.message_user(request, f"⏭️ Skipped {skipped} - recently emailed (within 24h)", messages.WARNING)
            if failed_count and not sent_count:
                self.message_user(request, f"❌ All {failed_count} emails failed to send", messages.ERROR)
            return

        # Generate styled preview for first deal
        from crm.services.email_templates import (
            get_styled_email, get_email_type_for_stage, get_pipeline_type_from_name,
            get_template_for_email, render_email_html
        )
        from crm.views import get_unsubscribe_url
        preview_deal = queryset.first()
        preview_email = None

        if preview_deal:
            try:
                # Determine brand and pipeline info
                brand_slug = preview_deal.pipeline.brand.slug if preview_deal.pipeline and preview_deal.pipeline.brand else 'desifirms'
                pipeline_type = preview_deal.pipeline.pipeline_type if preview_deal.pipeline else 'realestate'
                pipeline_name = preview_deal.pipeline.name if preview_deal.pipeline else ''
                stage_name = preview_deal.current_stage.name if preview_deal.current_stage else 'follow_up'
                email_type = get_email_type_for_stage(stage_name, pipeline_type, pipeline_name) or 'agent_followup_1'

                # Get recipient info
                recipient_name = preview_deal.contact.name.split()[0] if preview_deal.contact.name else 'there'
                recipient_email = preview_deal.contact.email
                recipient_company = preview_deal.contact.company or 'your business'

                # Check if we have a pre-designed template for this email type
                template_path = get_template_for_email(brand_slug, pipeline_type, email_type)

                if template_path and 'generic' not in template_path:
                    # USE PRE-DESIGNED TEMPLATE - no AI needed!
                    # These templates have hardcoded beautiful content
                    from django.template.loader import render_to_string
                    from django.utils import timezone

                    context = {
                        'recipient_name': recipient_name,
                        'recipient_email': recipient_email,
                        'recipient_company': recipient_company,
                        'unsubscribe_url': get_unsubscribe_url(recipient_email, brand_slug),
                        'current_year': timezone.now().year,
                        'brand_slug': brand_slug,
                    }

                    html_content = render_to_string(template_path, context)

                    # Get subject from template name
                    subject_map = {
                        'agent_invitation': f"Join Desi Firms Real Estate as a Founding Member",
                        'agent_followup_1': f"Just checking in - free listing opportunity",
                        'agent_followup_2': f"Final reminder - free real estate listing",
                        'directory_invitation': f"List {recipient_company} on Desi Firms - FREE",
                        'directory_followup_1': f"Quick follow-up - free business listing",
                        'directory_followup_2': f"Final reminder - free listing opportunity",
                        # Nudge - Registered but inactive users
                        'business_nudge': f"Your business listing is almost ready!",
                        'business_nudge_2': f"Still thinking about it? Here's why you should list",
                        'realestate_nudge': f"Your agent profile awaits!",
                        'realestate_nudge_2': f"Quick check-in from Desi Firms",
                        'events_nudge': f"Ready to promote your events?",
                        'events_nudge_2': f"Got any events coming up?",
                    }
                    subject = subject_map.get(email_type, 'Following up')

                    preview_email = {
                        'subject': subject,
                        'body': '(Using pre-designed template - see preview below)',
                        'html': html_content,
                        'contact': preview_deal.contact.name,
                        'email': preview_deal.contact.email,
                        'using_template': True,
                    }
                else:
                    # No pre-designed template - use AI generation
                    ai_agent = CRMAIAgent()
                    email_result = ai_agent.compose_email(preview_deal, context={'email_type': 'followup'})
                    if email_result.get('success'):
                        styled = get_styled_email(
                            brand_slug=brand_slug,
                            pipeline_type=pipeline_type,
                            email_type=email_type,
                            recipient_name=recipient_name,
                            recipient_email=recipient_email,
                            recipient_company=recipient_company,
                            subject=email_result['subject'],
                            body=email_result['body'],
                        )

                        preview_email = {
                            'subject': email_result['subject'],
                            'body': email_result['body'],
                            'html': styled.get('html', ''),
                            'contact': preview_deal.contact.name,
                            'email': preview_deal.contact.email,
                        }
            except Exception as e:
                preview_email = {'error': str(e)}

        # Get stage info
        stages = {}
        for deal in queryset:
            stage_name = deal.current_stage.name if deal.current_stage else 'No Stage'
            if stage_name not in stages:
                stages[stage_name] = 0
            stages[stage_name] += 1

        context = {
            **self.admin_site.each_context(request),
            'title': 'Confirm Send Follow-up Emails',
            'queryset': queryset,
            'opts': self.model._meta,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
            'deal_count': queryset.count(),
            'deals_preview': queryset[:10],
            'preview_email': preview_email,
            'stages': stages,
        }

        return TemplateResponse(
            request,
            'admin/crm/deal/send_email_confirmation.html',
            context
        )

    @action(description="⏸️ Pause automation")
    def pause_deals(self, request, queryset):
        """Pause selected deals to stop automated emails."""
        updated = queryset.update(status='paused')
        self.message_user(request, f"⏸️ Paused {updated} deal(s). They won't receive automated emails.")

    @action(description="▶️ Resume automation")
    def resume_deals(self, request, queryset):
        """Resume paused deals."""
        from django.utils import timezone
        updated = queryset.filter(status='paused').update(status='active', next_action_date=timezone.now())
        self.message_user(request, f"▶️ Resumed {updated} deal(s). They will be processed in next cycle.")

    actions = ['mark_as_won', 'mark_as_lost', 'move_to_next_stage', 'preview_email', 'generate_drafts', 'send_email_now', 'pause_deals', 'resume_deals']


# =============================================================================
# EMAIL SEQUENCE ADMIN
# =============================================================================

@admin.register(EmailSequence)
class EmailSequenceAdmin(ModelAdmin):
    list_display = ['name', 'pipeline', 'steps_count', 'is_active']
    list_filter = ['pipeline', 'is_active']
    search_fields = ['name', 'description']
    inlines = [SequenceStepInline]

    @display(description="Steps")
    def steps_count(self, obj):
        return obj.steps.count()


@admin.register(SequenceStep)
class SequenceStepAdmin(ModelAdmin):
    list_display = ['sequence', 'order', 'subject_template', 'delay_days', 'ai_personalize']
    list_filter = ['sequence', 'ai_personalize']
    ordering = ['sequence', 'order']


# =============================================================================
# EMAIL LOG ADMIN (Read-only)
# =============================================================================

@admin.register(EmailLog)
class EmailLogAdmin(ModelAdmin):
    list_display = [
        'subject_truncated',
        'to_email',
        'sent_at',
        'opened_badge',
        'replied_badge',
        'ai_generated',
    ]
    list_filter = ['opened', 'replied', 'ai_generated', 'sent_at']
    search_fields = ['subject', 'to_email', 'deal__contact__name']
    readonly_fields = [
        'id', 'deal', 'sequence_step', 'subject', 'body', 'from_email', 'to_email',
        'sent_at', 'opened', 'opened_at', 'clicked', 'clicked_at',
        'replied', 'replied_at', 'reply_content', 'ai_generated',
        'zoho_message_id', 'tracking_id', 'created_at'
    ]
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @display(description="Subject")
    def subject_truncated(self, obj):
        if len(obj.subject) > 50:
            return obj.subject[:50] + "..."
        return obj.subject

    @display(description="Opened", label=True)
    def opened_badge(self, obj):
        if obj.opened:
            return "Yes", "success"
        return "No", "danger"

    @display(description="Replied", label=True)
    def replied_badge(self, obj):
        if obj.replied:
            return "Yes", "success"
        return "No", "danger"


# =============================================================================
# AI DECISION LOG ADMIN (Read-only audit)
# =============================================================================

@admin.register(AIDecisionLog)
class AIDecisionLogAdmin(ModelAdmin):
    list_display = [
        'decision_type_badge',
        'deal_or_contact',
        'action_taken',
        'tokens_used',
        'created_at',
    ]
    list_filter = ['decision_type', 'model_used', 'created_at']
    search_fields = ['action_taken', 'reasoning']
    readonly_fields = [
        'id', 'deal', 'contact', 'decision_type', 'reasoning',
        'action_taken', 'metadata', 'tokens_used', 'model_used', 'created_at'
    ]
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @display(description="Type", label=True)
    def decision_type_badge(self, obj):
        colors = {
            'compose_email': 'info',
            'move_stage': 'warning',
            'classify_reply': 'success',
            'score_lead': 'primary',
            'deal_analyze': 'secondary',
            'send_email': 'info',
            'pause_deal': 'danger',
        }
        return obj.get_decision_type_display(), colors.get(obj.decision_type, 'info')

    @display(description="Target")
    def deal_or_contact(self, obj):
        if obj.deal:
            return f"Deal: {obj.deal.contact.name}"
        if obj.contact:
            return f"Contact: {obj.contact.name}"
        return "-"


# =============================================================================
# BACKLINK OPPORTUNITY ADMIN
# =============================================================================

@admin.register(BacklinkOpportunity)
class BacklinkOpportunityAdmin(ModelAdmin):
    list_display = [
        'target_domain',
        'domain_authority_display',
        'relevance_score_display',
        'status_badge',
        'contact',
        'link_verified',
    ]
    list_filter = ['status', 'link_verified', 'created_at']
    search_fields = ['target_domain', 'target_url', 'our_content_url']
    readonly_fields = ['id', 'created_at', 'updated_at', 'link_verified_at']
    ordering = ['-domain_authority', '-relevance_score']

    fieldsets = (
        ('Target Information', {
            'fields': ('target_url', 'target_domain', 'domain_authority', 'relevance_score')
        }),
        ('Our Content', {
            'fields': ('our_content_url', 'anchor_text_suggestion', 'outreach_angle')
        }),
        ('Status & Contact', {
            'fields': ('status', 'contact', 'notes')
        }),
        ('Verification', {
            'fields': ('link_verified', 'link_verified_at', 'actual_link_url'),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )

    @display(description="DA")
    def domain_authority_display(self, obj):
        if obj.domain_authority >= 50:
            color = '#22c55e'
        elif obj.domain_authority >= 30:
            color = '#f59e0b'
        else:
            color = '#ef4444'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.domain_authority
        )

    @display(description="Relevance")
    def relevance_score_display(self, obj):
        return f"{obj.relevance_score}%"

    @display(description="Status", label=True)
    def status_badge(self, obj):
        colors = {
            'new': 'info',
            'researching': 'warning',
            'outreaching': 'primary',
            'placed': 'success',
            'rejected': 'danger',
        }
        return obj.get_status_display(), colors.get(obj.status, 'info')


# =============================================================================
# AI PROMPT TEMPLATE ADMIN
# =============================================================================

@admin.register(AIPromptTemplate)
class AIPromptTemplateAdmin(ModelAdmin):
    list_display = ['name', 'prompt_type_badge', 'variables_preview', 'is_active']
    list_filter = ['prompt_type', 'is_active']
    search_fields = ['name', 'prompt_text']

    fieldsets = (
        (None, {
            'fields': ('name', 'prompt_type', 'is_active')
        }),
        ('Prompt Configuration', {
            'fields': ('prompt_text', 'system_prompt', 'variables')
        }),
    )

    @display(description="Type", label=True)
    def prompt_type_badge(self, obj):
        return obj.get_prompt_type_display(), "info"

    @display(description="Variables")
    def variables_preview(self, obj):
        if obj.variables:
            return ", ".join(obj.variables[:3])
        return "-"


# =============================================================================
# DEAL ACTIVITY ADMIN (Read-only)
# =============================================================================

@admin.register(DealActivity)
class DealActivityAdmin(ModelAdmin):
    list_display = ['deal', 'activity_type_badge', 'description_truncated', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['description', 'deal__contact__name']
    readonly_fields = ['id', 'deal', 'activity_type', 'description', 'metadata', 'created_at']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    @display(description="Type", label=True)
    def activity_type_badge(self, obj):
        colors = {
            'stage_change': 'warning',
            'email_sent': 'info',
            'email_opened': 'success',
            'email_replied': 'success',
            'note_added': 'secondary',
            'ai_action': 'primary',
            'status_change': 'warning',
        }
        return obj.get_activity_type_display(), colors.get(obj.activity_type, 'info')

    @display(description="Description")
    def description_truncated(self, obj):
        if len(obj.description) > 80:
            return obj.description[:80] + "..."
        return obj.description


# =============================================================================
# CONTACT IMPORT ADMIN
# =============================================================================

@admin.register(ContactImport)
class ContactImportAdmin(ModelAdmin):
    list_display = ['file_name', 'brand', 'contact_type', 'status_badge', 'imported_count', 'error_count', 'created_at']
    list_filter = ['brand', 'contact_type', 'status', 'created_at']
    search_fields = ['file_name']
    readonly_fields = ['id', 'status', 'total_rows', 'imported_count', 'skipped_count', 'error_count', 'errors', 'completed_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Import Settings', {
            'fields': ('brand', 'file', 'contact_type', 'source')
        }),
        ('Deal Creation (Optional)', {
            'fields': ('create_deals', 'pipeline'),
            'description': 'Optionally create deals for each imported contact'
        }),
        ('Results', {
            'fields': ('status', 'total_rows', 'imported_count', 'skipped_count', 'error_count', 'completed_at'),
            'classes': ['collapse']
        }),
        ('Errors', {
            'fields': ('errors',),
            'classes': ['collapse']
        }),
    )

    actions = ['process_import']

    class Media:
        js = ('admin/js/seo-loading.js',)

    @display(description="Status", label=True)
    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'failed': 'danger',
        }
        return obj.get_status_display(), colors.get(obj.status, 'info')

    @action(description="Process selected imports")
    def process_import(self, request, queryset):
        from crm.tasks import process_contact_import

        processed = 0
        for contact_import in queryset.filter(status='pending'):
            process_contact_import.delay(str(contact_import.id))
            processed += 1

        self.message_user(request, f"Queued {processed} imports for processing.")

    def save_model(self, request, obj, form, change):
        if not change:  # New import
            obj.file_name = obj.file.name if obj.file else 'Unknown'
        super().save_model(request, obj, form, change)

        # Auto-process on save if pending
        if obj.status == 'pending':
            from crm.tasks import process_contact_import
            process_contact_import.delay(str(obj.id))


# =============================================================================
# BACKLINK IMPORT ADMIN
# =============================================================================

@admin.register(BacklinkImport)
class BacklinkImportAdmin(ModelAdmin):
    list_display = ['file_name', 'brand', 'source', 'status_badge', 'imported_count', 'error_count', 'created_at']
    list_filter = ['brand', 'source', 'status', 'created_at']
    search_fields = ['file_name']
    readonly_fields = ['id', 'status', 'total_rows', 'imported_count', 'skipped_count', 'error_count', 'errors', 'completed_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Import Settings', {
            'fields': ('brand', 'file', 'source'),
            'description': 'Upload CSV or Excel file from Ubersuggest, Ahrefs, SEMrush, or Moz'
        }),
        ('Content Settings', {
            'fields': ('our_content_url',),
            'description': 'Your content URL to promote for all imported backlink opportunities'
        }),
        ('Filter Settings', {
            'fields': ('min_domain_authority', 'create_contacts'),
            'description': 'Optional: Filter low DA domains, create contacts from emails'
        }),
        ('Results', {
            'fields': ('status', 'total_rows', 'imported_count', 'skipped_count', 'error_count', 'completed_at'),
            'classes': ['collapse']
        }),
        ('Errors', {
            'fields': ('errors',),
            'classes': ['collapse']
        }),
    )

    actions = ['process_import']

    class Media:
        js = ('admin/js/seo-loading.js',)

    @display(description="Status", label=True)
    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'failed': 'danger',
        }
        return obj.get_status_display(), colors.get(obj.status, 'info')

    @action(description="Process selected imports")
    def process_import(self, request, queryset):
        from crm.tasks import process_backlink_import

        processed = 0
        for backlink_import in queryset.filter(status='pending'):
            process_backlink_import.delay(str(backlink_import.id))
            processed += 1

        self.message_user(request, f"Queued {processed} imports for processing.")

    def save_model(self, request, obj, form, change):
        if not change:  # New import
            obj.file_name = obj.file.name if obj.file else 'Unknown'
        super().save_model(request, obj, form, change)

        # Auto-process on save if pending
        if obj.status == 'pending':
            from crm.tasks import process_backlink_import
            process_backlink_import.delay(str(obj.id))


# =============================================================================
# AI EMAIL COMPOSER - FIRST CONTACT TOOL
# =============================================================================

@admin.register(EmailDraft)
class EmailDraftAdmin(ModelAdmin):
    """
    First Contact Email Tool - Modern Zoho-style Composer.
    After sending, contacts are added to pipeline for AI autopilot follow-ups.
    Contacts already in a pipeline are SKIPPED (managed by autopilot).
    """
    change_form_template = 'admin/crm/emaildraft/change_form.html'

    list_display = [
        'draft_title',
        'brand',
        'pipeline_display',
        'recipient_count_display',
        'deals_created_display',
        'sent_status_display',
        'schedule_status_display',
        'updated_at',
    ]
    list_filter = ['brand', 'pipeline', 'is_sent', 'schedule_status', 'email_type', 'created_at']
    search_fields = ['contacts__name', 'contacts__email', 'manual_emails', 'template_name', 'generated_subject']
    ordering = ['-updated_at']
    filter_horizontal = ['contacts']  # Nice dual-list selector for multiple contacts
    autocomplete_fields = []  # Using custom chip UI instead

    fieldsets = (
        ('1. Brand & Pipeline', {
            'fields': ('brand', 'pipeline'),
            'description': 'Select brand and pipeline. After sending, contacts will be added to this pipeline for automated follow-ups.'
        }),
        ('2. Add Recipients', {
            'fields': ('contacts', 'manual_emails', 'send_to_pipeline_contacts'),
            'description': 'Select contacts AND/OR add emails manually. By default, contacts already in a pipeline are skipped. Check the box below to include them.'
        }),
        ('3. Email Settings', {
            'fields': ('email_type', 'tone', 'your_suggestions'),
            'description': 'Choose type, tone, and add your key points for AI'
        }),
        ('4. AI Generated Email', {
            'fields': ('generated_subject', 'generated_body'),
            'description': 'Click "Generate AI Email" action to fill these'
        }),
        ('5. Final Email (First Contact)', {
            'fields': ('final_subject', 'final_body'),
            'description': 'This is the first email. After sending, pipeline autopilot handles follow-ups.'
        }),
        ('Scheduling', {
            'fields': ('scheduled_for', 'schedule_status', 'schedule_error'),
            'classes': ['collapse'],
            'description': 'Schedule email to send at peak business hours (Australia/Sydney timezone)'
        }),
        ('Status', {
            'fields': ('sent_count', 'deals_created', 'total_recipients', 'is_sent', 'sent_at'),
            'classes': ['collapse'],
        }),
        ('Template', {
            'fields': ('is_template', 'template_name'),
            'classes': ['collapse'],
        }),
    )
    readonly_fields = ['is_sent', 'sent_at', 'sent_count', 'total_recipients', 'deals_created', 'schedule_status', 'schedule_error']

    class Media:
        css = {
            'all': []
        }
        js = ('admin/js/seo-loading.js',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Update recipient count after save
        obj.total_recipients = obj.get_recipient_count()
        obj.save(update_fields=['total_recipients'])

    @display(description="Pipeline")
    def pipeline_display(self, obj):
        if obj.pipeline:
            return obj.pipeline.name
        return format_html('<span style="color: #ef4444;">No Pipeline!</span>')

    @display(description="Deals Created")
    def deals_created_display(self, obj):
        if obj.deals_created > 0:
            return format_html('<span style="color: #22c55e; font-weight: bold;">{}</span>', obj.deals_created)
        return "-"

    @display(description="Draft")
    def draft_title(self, obj):
        if obj.is_template and obj.template_name:
            return f"📋 {obj.template_name}"
        if obj.is_sent:
            return f"✅ Sent ({obj.sent_count})"
        return f"📝 Draft"

    @display(description="Recipients")
    def recipient_count_display(self, obj):
        count = obj.total_recipients or obj.get_recipient_count()
        if count == 0:
            return format_html('<span style="color: #9ca3af;">No recipients</span>')
        return format_html('<span style="font-weight: bold; color: #3b82f6;">{} recipient(s)</span>', count)

    @display(description="Type", label=True)
    def email_type_badge(self, obj):
        colors = {
            'sales_intro': 'info',
            'sales_followup': 'warning',
            'backlink_outreach': 'success',
            'partnership': 'primary',
            'custom': 'secondary',
        }
        return obj.get_email_type_display(), colors.get(obj.email_type, 'info')

    @display(description="Status", label=True)
    def sent_status_display(self, obj):
        if obj.is_sent:
            return f"Sent ({obj.sent_count})", "success"
        if obj.sent_count > 0:
            return f"Partial ({obj.sent_count})", "warning"
        if obj.final_body:
            return "Ready", "warning"
        if obj.generated_body:
            return "AI Draft", "info"
        return "Pending", "secondary"

    @display(description="Schedule", label=True)
    def schedule_status_display(self, obj):
        if obj.schedule_status == 'scheduled' and obj.scheduled_for:
            return f"📅 {obj.get_scheduled_time_display()}", "info"
        elif obj.schedule_status == 'sending':
            return "Sending...", "warning"
        elif obj.schedule_status == 'completed':
            return "Sent", "success"
        elif obj.schedule_status == 'cancelled':
            return "Cancelled", "secondary"
        elif obj.schedule_status == 'failed':
            return f"Failed", "danger"
        return "-", "secondary"

    @action(description="🤖 Generate AI Email")
    def generate_ai_email(self, request, queryset):
        """Generate AI email content based on user suggestions."""
        from crm.services.ai_agent import CRMAIAgent
        from django.contrib import messages

        ai_agent = CRMAIAgent()
        generated = 0

        for draft in queryset:
            if draft.is_sent:
                self.message_user(request, f"⚠️ {draft}: Already sent, skipping", messages.WARNING)
                continue

            try:
                # Get recipient info from contact or manual fields
                recipient_name = draft.get_recipient_name()
                recipient_company = draft.contact.company if draft.contact else draft.recipient_company
                recipient_website = draft.contact.website if draft.contact else draft.recipient_website

                context = {
                    'email_type': draft.email_type,
                    'tone': draft.tone,
                    'suggestions': draft.your_suggestions,
                    'recipient_name': recipient_name,
                    'recipient_company': recipient_company or '',
                    'recipient_website': recipient_website or '',
                    'recipient_email': draft.contact.email if draft.contact else draft.recipient_email or '',
                    'brand_name': draft.brand.name,
                    'brand_website': draft.brand.website,
                    'brand_description': draft.brand.ai_company_description or '',
                    'value_proposition': draft.brand.ai_value_proposition or '',
                    'pipeline_type': draft.pipeline.pipeline_type if draft.pipeline else '',
                    'pipeline_name': draft.pipeline.name if draft.pipeline else '',
                    # New context fields for smarter AI
                    'business_updates': draft.brand.ai_business_updates or '',
                    'target_context': draft.brand.ai_target_context or '',
                    'approach_style': draft.brand.ai_approach_style or 'problem_solving',
                }

                result = ai_agent.compose_email_from_context(context)

                if result.get('success'):
                    draft.generated_subject = result['subject']
                    draft.generated_body = result['body']
                    draft.save(update_fields=['generated_subject', 'generated_body', 'updated_at'])
                    generated += 1
                else:
                    self.message_user(request, f"❌ {draft}: {result.get('error')}", messages.ERROR)
            except Exception as e:
                self.message_user(request, f"❌ {draft}: {str(e)}", messages.ERROR)

        if generated:
            self.message_user(request, f"🤖 Generated {generated} email(s)!", messages.SUCCESS)

    @action(description="📋 Copy AI to Final")
    def copy_to_final(self, request, queryset):
        """Copy AI generated content to final fields."""
        from django.contrib import messages

        copied = 0
        for draft in queryset:
            if draft.generated_subject and draft.generated_body:
                draft.final_subject = draft.generated_subject
                draft.final_body = draft.generated_body
                draft.save(update_fields=['final_subject', 'final_body', 'updated_at'])
                copied += 1

        self.message_user(request, f"📋 Copied {copied} draft(s) to final.", messages.SUCCESS)

    @action(description="📤 Send & Add to Pipeline (with preview)")
    def send_email_now(self, request, queryset):
        """
        Send first contact email with preview. Shows all recipients before sending.
        Contacts already in ANY pipeline are SKIPPED (managed by autopilot).
        """
        from crm.services.email_service import ZohoEmailService
        from crm.models import Contact, Deal, PipelineStage
        from crm.services.email_templates import get_styled_email
        from django.contrib import messages
        from django.utils import timezone
        from django.template.response import TemplateResponse
        from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

        # Only process one draft at a time for preview
        if queryset.count() > 1:
            self.message_user(request, "⚠️ Please select only 1 draft at a time for sending.", messages.WARNING)
            return

        draft = queryset.first()

        # Validate basics
        if not draft.pipeline:
            self.message_user(request, f"❌ {draft}: No pipeline selected!", messages.ERROR)
            return

        subject = draft.final_subject or draft.generated_subject
        body_text = draft.final_body or draft.generated_body

        if not subject or not body_text:
            self.message_user(request, f"⚠️ {draft}: No content - generate first", messages.WARNING)
            return

        # Get all recipients and categorize them
        all_recipients = draft.get_all_recipients()
        if not all_recipients:
            self.message_user(request, f"⚠️ {draft}: No recipients", messages.WARNING)
            return

        # Categorize recipients for preview
        recipients_preview = []
        valid_recipients = []
        in_pipeline_count = 0
        blocked_count = 0

        for recipient in all_recipients:
            recipient_email = Contact.normalize_email(recipient['email'])
            if not recipient_email:
                continue

            contact = recipient.get('contact')
            if not contact:
                contact = Contact.objects.filter(email__iexact=recipient_email, brand=draft.brand).first()

            brand_slug = draft.brand.slug if draft.brand else None
            status = 'ok'

            # Check unsubscribed
            if contact and (contact.is_unsubscribed or contact.is_unsubscribed_from_brand(brand_slug)):
                status = 'blocked'
                blocked_count += 1
            # Check in pipeline
            elif contact and not draft.send_to_pipeline_contacts:
                if Deal.objects.filter(contact=contact, status='active').exists():
                    status = 'pipeline'
                    in_pipeline_count += 1

            if status == 'ok':
                valid_recipients.append({
                    'email': recipient_email,
                    'name': recipient.get('name', ''),
                    'company': recipient.get('company', ''),
                    'website': recipient.get('website', ''),
                    'contact': contact,
                })

            recipients_preview.append({
                'email': recipient_email,
                'name': recipient.get('name', ''),
                'company': recipient.get('company', ''),
                'status': status,
            })

        # If confirmation received, send emails
        if 'confirm_send' in request.POST:
            try:
                return self._execute_send(request, draft, valid_recipients, subject, body_text)
            except Exception as e:
                self.message_user(request, f"❌ Error sending emails: {str(e)}", messages.ERROR)
                from django.http import HttpResponseRedirect
                from django.urls import reverse
                return HttpResponseRedirect(reverse('admin:crm_emaildraft_changelist'))

        # If schedule requested, schedule for later
        if 'confirm_schedule' in request.POST:
            try:
                return self._schedule_send(request, draft, len(valid_recipients))
            except Exception as e:
                self.message_user(request, f"❌ Error scheduling: {str(e)}", messages.ERROR)
                from django.http import HttpResponseRedirect
                from django.urls import reverse
                return HttpResponseRedirect(reverse('admin:crm_emaildraft_changelist'))

        # Generate preview HTML for first recipient (use any recipient for preview, even if in pipeline)
        preview_html = None
        preview_recipients = valid_recipients if valid_recipients else all_recipients
        if preview_recipients:
            first = preview_recipients[0]
            from crm.services.ai_agent import CRMAIAgent
            ai_agent = CRMAIAgent()
            salutation = ai_agent.get_smart_salutation(
                email=first['email'],
                name=first.get('name', ''),
                company=first.get('company', '')
            )
            personalized_body = body_text.replace('{{SALUTATION}}', salutation)
            extracted_name = salutation.replace('Hi ', '').replace(',', '').strip() if salutation.startswith('Hi ') else 'there'

            styled = get_styled_email(
                brand_slug=draft.brand.slug if draft.brand else 'desifirms',
                pipeline_type=draft.pipeline.pipeline_type if draft.pipeline else 'business',
                email_type=draft.email_type or 'directory_invitation',
                recipient_name=extracted_name,
                recipient_email=first['email'],
                recipient_company=first.get('company', ''),
                subject=subject,
                body=personalized_body,
            )
            preview_html = styled.get('html', '')

        # Show preview page
        draft_title = draft.final_subject or draft.generated_subject or draft.get_email_type_display()
        context = {
            **self.admin_site.each_context(request),
            'title': f'Preview: {draft_title}',
            'draft': draft,
            'subject': subject,
            'preview_html': preview_html,
            'recipients_preview': recipients_preview[:20],  # First 20
            'valid_count': len(valid_recipients),
            'in_pipeline_count': in_pipeline_count,
            'blocked_count': blocked_count,
            'total_count': len(all_recipients),
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
            'opts': self.model._meta,
            # Schedule context (empty for list action, can be pre-filled from form)
            'schedule_preset': '',
            'schedule_datetime': '',
        }

        return TemplateResponse(request, 'admin/crm/emaildraft/send_preview.html', context)

    def _execute_send(self, request, draft, valid_recipients, subject, body_text):
        """Actually send emails after confirmation."""
        from crm.services.email_service import ZohoEmailService
        from crm.services.email_templates import get_styled_email
        from crm.services.ai_agent import CRMAIAgent
        from crm.models import Contact, Deal, PipelineStage
        from django.contrib import messages
        from django.utils import timezone

        # Get invited stage
        invited_stage = PipelineStage.objects.filter(
            pipeline=draft.pipeline,
            name__icontains='invited'
        ).first() or PipelineStage.objects.filter(
            pipeline=draft.pipeline
        ).order_by('order')[1:2].first() or PipelineStage.objects.filter(
            pipeline=draft.pipeline
        ).order_by('order').first()

        if not invited_stage:
            self.message_user(request, f"❌ {draft}: Pipeline has no stages!", messages.ERROR)
            return

        email_service = ZohoEmailService(brand=draft.brand)
        if not email_service.enabled:
            self.message_user(request, f"❌ Zoho not configured for {draft.brand.name}! Check Brand settings for Zoho credentials.", messages.ERROR)
            return

        ai_agent = CRMAIAgent()
        sent_count = 0
        failed_count = 0
        total_deals = 0
        first_error = None

        for recipient in valid_recipients:
            contact = recipient.get('contact')
            recipient_email = recipient['email']
            recipient_name = recipient.get('name', '')
            recipient_company = recipient.get('company', '')

            # Generate smart salutation
            salutation = ai_agent.get_smart_salutation(
                email=recipient_email,
                name=recipient_name,
                company=recipient_company
            )

            # Replace {{SALUTATION}} placeholder in body
            personalized_body = body_text.replace('{{SALUTATION}}', salutation)

            # Extract first name for template
            extracted_name = salutation.replace('Hi ', '').replace(',', '').strip() if salutation.startswith('Hi ') else 'there'
            if ' Team' in extracted_name:
                extracted_name = 'there'

            # Generate styled HTML with correct recipient email for unsubscribe link
            styled_email = get_styled_email(
                brand_slug=draft.brand.slug if draft.brand else 'desifirms',
                pipeline_type=draft.pipeline.pipeline_type if draft.pipeline else 'business',
                email_type=draft.email_type or 'directory_invitation',
                recipient_name=extracted_name,
                recipient_email=recipient_email,
                recipient_company=recipient_company,
                subject=subject,
                body=personalized_body,
            )
            html_body = styled_email['html']

            # Send email
            result = email_service.send(
                to=recipient_email,
                subject=subject,
                body=html_body,
                from_name=draft.brand.from_name
            )

            if result.get('success'):
                sent_count += 1

                # Get or create contact
                if not contact:
                    contact = Contact.objects.filter(email__iexact=recipient_email, brand=draft.brand).first()

                if not contact:
                    from django.db import transaction
                    try:
                        with transaction.atomic():
                            contact = Contact.objects.create(
                                email=recipient_email,
                                brand=draft.brand,
                                name=recipient_name or extracted_name,
                                company=recipient_company,
                                website=recipient.get('website', ''),
                                status='contacted',
                                last_emailed_at=timezone.now(),
                                email_count=1,
                                source='email_composer'
                            )
                    except Exception:
                        contact = Contact.objects.filter(email__iexact=recipient_email, brand=draft.brand).first()
                        if contact:
                            contact.last_emailed_at = timezone.now()
                            contact.email_count = (contact.email_count or 0) + 1
                            contact.status = 'contacted'
                            contact.save(update_fields=['last_emailed_at', 'email_count', 'status'])
                else:
                    contact.last_emailed_at = timezone.now()
                    contact.email_count = (contact.email_count or 0) + 1
                    contact.status = 'contacted'
                    contact.save(update_fields=['last_emailed_at', 'email_count', 'status'])

                # Create or update deal in pipeline
                if contact:
                    existing_deal = Deal.objects.filter(
                        contact=contact,
                        pipeline=draft.pipeline,
                        status='active'
                    ).first()

                    if existing_deal:
                        existing_deal.emails_sent = (existing_deal.emails_sent or 0) + 1
                        existing_deal.last_contact_date = timezone.now()
                        existing_deal.next_action_date = timezone.now() + timezone.timedelta(days=existing_deal.current_stage.days_until_followup if existing_deal.current_stage else 3)
                        existing_deal.ai_notes = (existing_deal.ai_notes or '') + f"\n[{timezone.now().strftime('%Y-%m-%d')}] Email sent via Composer: {subject}"
                        existing_deal.save()
                    else:
                        Deal.objects.create(
                            contact=contact,
                            pipeline=draft.pipeline,
                            current_stage=invited_stage,
                            status='active',
                            emails_sent=1,
                            last_contact_date=timezone.now(),
                            next_action_date=timezone.now() + timezone.timedelta(days=invited_stage.days_until_followup or 3),
                            ai_notes=f"First contact via Email Composer\nSubject: {subject}"
                        )
                        total_deals += 1
            else:
                failed_count += 1
                error_msg = result.get('error', 'Unknown error')
                # Store first error for user feedback
                if failed_count == 1:
                    first_error = error_msg

        # Update draft tracking
        draft.sent_count = (draft.sent_count or 0) + sent_count
        draft.deals_created = (draft.deals_created or 0) + total_deals
        draft.is_sent = True
        draft.sent_at = timezone.now()
        draft.save(update_fields=['sent_count', 'deals_created', 'is_sent', 'sent_at'])

        # Return with summary message
        from django.http import HttpResponseRedirect
        from django.urls import reverse

        msg = f"📤 Sent {sent_count} email(s)"
        if sent_count > 0:
            msg += f" from {email_service.from_email}"
        if total_deals > 0:
            msg += f", created {total_deals} new deal(s)"
        if failed_count > 0:
            msg += f" ({failed_count} failed)"
            if first_error:
                msg += f" - Error: {first_error}"

        self.message_user(request, msg, messages.SUCCESS if sent_count > 0 else messages.WARNING)
        return HttpResponseRedirect(reverse('admin:crm_emaildraft_changelist'))

    def _schedule_send(self, request, draft, valid_count):
        """Schedule email to be sent at a future time."""
        from django.contrib import messages
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        from django.utils import timezone
        from datetime import datetime, timedelta
        import pytz

        sydney = pytz.timezone('Australia/Sydney')

        # Get schedule time from form
        schedule_preset = request.POST.get('schedule_preset', '')
        schedule_datetime = request.POST.get('schedule_datetime', '')

        scheduled_time = None

        if schedule_preset:
            # Calculate time from preset
            now = timezone.now().astimezone(sydney)

            if schedule_preset == 'tomorrow_9':
                target = now + timedelta(days=1)
                target = target.replace(hour=9, minute=0, second=0, microsecond=0)
            elif schedule_preset == 'tomorrow_10':
                target = now + timedelta(days=1)
                target = target.replace(hour=10, minute=0, second=0, microsecond=0)
            elif schedule_preset == 'tomorrow_14':
                target = now + timedelta(days=1)
                target = target.replace(hour=14, minute=0, second=0, microsecond=0)
            elif schedule_preset == 'tomorrow_15':
                target = now + timedelta(days=1)
                target = target.replace(hour=15, minute=0, second=0, microsecond=0)
            elif schedule_preset == 'monday_9':
                days_until_monday = (7 - now.weekday()) % 7
                if days_until_monday == 0:
                    days_until_monday = 7
                target = now + timedelta(days=days_until_monday)
                target = target.replace(hour=9, minute=0, second=0, microsecond=0)
            elif schedule_preset == 'monday_10':
                days_until_monday = (7 - now.weekday()) % 7
                if days_until_monday == 0:
                    days_until_monday = 7
                target = now + timedelta(days=days_until_monday)
                target = target.replace(hour=10, minute=0, second=0, microsecond=0)
            else:
                raise ValueError(f"Unknown schedule preset: {schedule_preset}")

            scheduled_time = target.astimezone(pytz.UTC)

        elif schedule_datetime:
            # Parse custom datetime (input is in AEST)
            naive_dt = datetime.strptime(schedule_datetime, '%Y-%m-%dT%H:%M')
            local_dt = sydney.localize(naive_dt)
            scheduled_time = local_dt.astimezone(pytz.UTC)

            # Validate it's in the future
            if scheduled_time <= timezone.now():
                raise ValueError("Scheduled time must be in the future")
        else:
            raise ValueError("No schedule time selected")

        # Update draft with schedule
        draft.scheduled_for = scheduled_time
        draft.schedule_status = 'scheduled'
        draft.schedule_error = ''
        draft.save(update_fields=['scheduled_for', 'schedule_status', 'schedule_error'])

        # Format display time
        display_time = draft.get_scheduled_time_display()

        self.message_user(
            request,
            f"📅 Scheduled {valid_count} email(s) for {display_time}",
            messages.SUCCESS
        )
        return HttpResponseRedirect(reverse('admin:crm_emaildraft_changelist'))

    @action(description="📋 Save as Template")
    def save_as_template(self, request, queryset):
        """Mark selected drafts as reusable templates."""
        from django.contrib import messages

        for draft in queryset:
            if not draft.template_name:
                draft.template_name = f"{draft.brand.name} - {draft.get_email_type_display()}"
            draft.is_template = True
            draft.save(update_fields=['is_template', 'template_name', 'updated_at'])

        self.message_user(
            request,
            f"📋 Saved {queryset.count()} draft(s) as templates. They'll appear in the Templates filter.",
            messages.SUCCESS
        )

    actions = ['generate_ai_email', 'copy_to_final', 'send_email_now', 'save_as_template']

    def response_add(self, request, obj):
        """Handle custom buttons when adding a new draft (Send directly from add form)."""
        from django.contrib import messages
        from django.http import HttpResponseRedirect
        from django.urls import reverse

        # Handle "Send & Add to Pipeline" button on new draft
        if '_send_and_pipeline' in request.POST:
            return self._send_single_draft(request, obj)

        # Handle "Save as Template" button
        if '_save_as_template' in request.POST:
            if not obj.template_name:
                obj.template_name = f"{obj.brand.name} - {obj.get_email_type_display()}"
            obj.is_template = True
            obj.save(update_fields=['is_template', 'template_name', 'updated_at'])
            self.message_user(request, f"📋 Saved as template: {obj.template_name}", messages.SUCCESS)
            return HttpResponseRedirect(
                reverse('admin:crm_emaildraft_change', args=[obj.pk])
            )

        return super().response_add(request, obj)

    def response_change(self, request, obj):
        """Handle custom buttons from the change form template."""
        from django.contrib import messages
        from django.http import HttpResponseRedirect
        from django.urls import reverse

        # Handle "Send & Add to Pipeline" button
        if '_send_and_pipeline' in request.POST:
            return self._send_single_draft(request, obj)

        # Handle "Save as Template" button
        if '_save_as_template' in request.POST:
            if not obj.template_name:
                obj.template_name = f"{obj.brand.name} - {obj.get_email_type_display()}"
            obj.is_template = True
            obj.save(update_fields=['is_template', 'template_name', 'updated_at'])
            self.message_user(request, f"📋 Saved as template: {obj.template_name}", messages.SUCCESS)
            return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)

    def _send_single_draft(self, request, draft):
        """
        Show preview before sending. Called from custom change form button.
        Reuses the same preview logic as send_email_now action.
        """
        from crm.models import Contact, Deal
        from crm.services.email_templates import get_styled_email
        from django.contrib import messages
        from django.http import HttpResponseRedirect
        from django.template.response import TemplateResponse
        from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

        # Validate pipeline
        if not draft.pipeline:
            self.message_user(request, f"❌ No pipeline selected!", messages.ERROR)
            return HttpResponseRedirect(request.path)

        # Get email content
        subject = draft.final_subject or draft.generated_subject
        body_text = draft.final_body or draft.generated_body

        if not subject or not body_text:
            self.message_user(request, f"⚠️ No content - generate or write email first", messages.WARNING)
            return HttpResponseRedirect(request.path)

        # Get all recipients
        all_recipients = draft.get_all_recipients()
        if not all_recipients:
            self.message_user(request, f"⚠️ No recipients", messages.WARNING)
            return HttpResponseRedirect(request.path)

        # Categorize recipients for preview
        recipients_preview = []
        valid_recipients = []
        in_pipeline_count = 0
        blocked_count = 0

        for recipient in all_recipients:
            recipient_email = Contact.normalize_email(recipient['email'])
            if not recipient_email:
                continue

            contact = recipient.get('contact')
            if not contact:
                contact = Contact.objects.filter(email__iexact=recipient_email, brand=draft.brand).first()

            brand_slug = draft.brand.slug if draft.brand else None
            status = 'ok'

            # Check unsubscribed
            if contact and (contact.is_unsubscribed or contact.is_unsubscribed_from_brand(brand_slug)):
                status = 'blocked'
                blocked_count += 1
            # Check in pipeline
            elif contact and not draft.send_to_pipeline_contacts:
                if Deal.objects.filter(contact=contact, status='active').exists():
                    status = 'pipeline'
                    in_pipeline_count += 1

            if status == 'ok':
                valid_recipients.append({
                    'email': recipient_email,
                    'name': recipient.get('name', ''),
                    'company': recipient.get('company', ''),
                    'website': recipient.get('website', ''),
                    'contact': contact,
                })

            recipients_preview.append({
                'email': recipient_email,
                'name': recipient.get('name', ''),
                'company': recipient.get('company', ''),
                'status': status,
            })

        # If confirmation received, send emails
        if 'confirm_send' in request.POST:
            try:
                return self._execute_send(request, draft, valid_recipients, subject, body_text)
            except Exception as e:
                self.message_user(request, f"❌ Error sending emails: {str(e)}", messages.ERROR)
                from django.http import HttpResponseRedirect
                from django.urls import reverse
                return HttpResponseRedirect(reverse('admin:crm_emaildraft_changelist'))

        # If schedule requested, schedule for later
        if 'confirm_schedule' in request.POST:
            try:
                return self._schedule_send(request, draft, len(valid_recipients))
            except Exception as e:
                self.message_user(request, f"❌ Error scheduling: {str(e)}", messages.ERROR)
                from django.http import HttpResponseRedirect
                from django.urls import reverse
                return HttpResponseRedirect(reverse('admin:crm_emaildraft_changelist'))

        # Generate preview HTML for first recipient (use any recipient for preview, even if in pipeline)
        preview_html = None
        preview_recipients = valid_recipients if valid_recipients else all_recipients
        if preview_recipients:
            first = preview_recipients[0]
            from crm.services.ai_agent import CRMAIAgent
            ai_agent = CRMAIAgent()
            salutation = ai_agent.get_smart_salutation(
                email=first['email'],
                name=first.get('name', ''),
                company=first.get('company', '')
            )
            personalized_body = body_text.replace('{{SALUTATION}}', salutation)
            extracted_name = salutation.replace('Hi ', '').replace(',', '').strip() if salutation.startswith('Hi ') else 'there'

            styled = get_styled_email(
                brand_slug=draft.brand.slug if draft.brand else 'desifirms',
                pipeline_type=draft.pipeline.pipeline_type if draft.pipeline else 'business',
                email_type=draft.email_type or 'directory_invitation',
                recipient_name=extracted_name,
                recipient_email=first['email'],
                recipient_company=first.get('company', ''),
                subject=subject,
                body=personalized_body,
            )
            preview_html = styled.get('html', '')

        # Show preview page
        draft_title = draft.final_subject or draft.generated_subject or draft.get_email_type_display()

        # Check if schedule data was passed from composer
        schedule_preset = request.POST.get('schedule_preset', '')
        schedule_datetime = request.POST.get('schedule_datetime', '')

        context = {
            **self.admin_site.each_context(request),
            'title': f'Preview: {draft_title}',
            'draft': draft,
            'subject': subject,
            'preview_html': preview_html,
            'recipients_preview': recipients_preview[:20],
            'valid_count': len(valid_recipients),
            'in_pipeline_count': in_pipeline_count,
            'blocked_count': blocked_count,
            'total_count': len(all_recipients),
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
            'opts': self.model._meta,
            # Pre-fill schedule if passed from composer
            'schedule_preset': schedule_preset,
            'schedule_datetime': schedule_datetime,
        }

        return TemplateResponse(request, 'admin/crm/emaildraft/send_preview.html', context)


