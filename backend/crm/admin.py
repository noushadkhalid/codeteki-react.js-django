"""
CRM Admin Configuration
Using Django Unfold for modern Tailwind-based UI
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum

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
            'fields': ('ai_company_description', 'ai_value_proposition', 'backlink_content_types'),
            'description': 'These are used to personalize AI-generated emails and pitches'
        }),
    )

    @display(description="Contacts")
    def contacts_count(self, obj):
        return obj.contacts.count()

    @display(description="Pipelines")
    def pipelines_count(self, obj):
        return obj.pipelines.count()


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

@admin.register(Contact)
class ContactAdmin(ModelAdmin):
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
        updated = queryset.update(
            is_unsubscribed=False,
            unsubscribed_at=None,
            status='new'
        )
        self.message_user(request, f"Resubscribed {updated} contact(s).")

    actions = ['mark_unsubscribed', 'resubscribe']


# =============================================================================
# BRAND-SPECIFIC CONTACT ADMINS (Separate Views)
# =============================================================================

@admin.register(CodetekiContact)
class CodetekiContactAdmin(ContactAdmin):
    """Codeteki-only contacts view."""

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


@admin.register(DesiFirmsContact)
class DesiFirmsContactAdmin(ContactAdmin):
    """Desi Firms-only contacts view."""

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
        'next_action_date',
        'emails_sent',
        'value_display',
        'created_at',
    ]
    list_filter = ['pipeline', 'current_stage', 'status', 'created_at']
    search_fields = ['contact__name', 'contact__email', 'contact__company']
    readonly_fields = ['id', 'created_at', 'updated_at', 'stage_entered_at', 'emails_sent']
    inlines = [DealActivityInline, EmailLogInline]
    ordering = ['-created_at']

    fieldsets = (
        ('Deal Information', {
            'fields': ('contact', 'pipeline', 'current_stage', 'status', 'value')
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

    @action(description="📤 Send Email NOW (1 per deal)")
    def send_email_now(self, request, queryset):
        """Send AI-generated email immediately to selected deals."""
        from crm.tasks import queue_deal_email
        from django.contrib import messages

        queued = 0
        skipped = 0

        for deal in queryset:
            # Check if email was sent recently (within 24 hours)
            from crm.models import EmailLog
            from django.utils import timezone
            from datetime import timedelta

            recent_email = EmailLog.objects.filter(
                deal=deal,
                sent_at__gte=timezone.now() - timedelta(hours=24)
            ).exists()

            if recent_email:
                skipped += 1
                self.message_user(
                    request,
                    f"⏭️ {deal.contact.name}: Skipped - email sent within 24hrs",
                    messages.WARNING
                )
                continue

            # Queue email for sending
            queue_deal_email.delay(str(deal.id), 'outreach')
            queued += 1

        if queued:
            self.message_user(request, f"✅ Queued {queued} email(s) for sending!", messages.SUCCESS)
        if skipped:
            self.message_user(request, f"⏭️ Skipped {skipped} deal(s) - recently emailed", messages.WARNING)

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

    actions = ['move_to_next_stage', 'preview_email', 'generate_drafts', 'send_email_now', 'pause_deals', 'resume_deals']


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
        'updated_at',
    ]
    list_filter = ['brand', 'pipeline', 'is_sent', 'email_type', 'created_at']
    search_fields = ['contacts__name', 'contacts__email', 'manual_emails', 'template_name', 'generated_subject']
    ordering = ['-updated_at']
    filter_horizontal = ['contacts']  # Nice dual-list selector for multiple contacts
    autocomplete_fields = []  # Using custom chip UI instead

    fieldsets = (
        ('1. Brand & Pipeline', {
            'fields': ('brand', 'pipeline'),
            'description': 'Select brand and pipeline. After sending, contacts will be added to this pipeline for automated follow-ups.'
        }),
        ('2. Add Recipients (First Contact Only)', {
            'fields': ('contacts', 'manual_emails'),
            'description': 'Select contacts AND/OR add emails manually. Contacts already in ANY pipeline will be SKIPPED.'
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
        ('Status', {
            'fields': ('sent_count', 'deals_created', 'total_recipients', 'is_sent', 'sent_at'),
            'classes': ['collapse'],
        }),
        ('Template', {
            'fields': ('is_template', 'template_name'),
            'classes': ['collapse'],
        }),
    )
    readonly_fields = ['is_sent', 'sent_at', 'sent_count', 'total_recipients', 'deals_created']

    class Media:
        css = {
            'all': []
        }
        js = []

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

    @action(description="📤 Send & Add to Pipeline")
    def send_email_now(self, request, queryset):
        """
        Send first contact email using BCC (single API call) and add contacts to pipeline.
        Contacts already in ANY pipeline are SKIPPED (managed by autopilot).
        """
        from crm.services.email_service import ZohoEmailService
        from crm.models import Contact, Deal, PipelineStage
        from django.contrib import messages
        from django.utils import timezone

        total_sent = 0
        total_in_pipeline = 0
        total_blocked = 0
        total_deals = 0

        for draft in queryset:
            # Validate pipeline
            if not draft.pipeline:
                self.message_user(request, f"❌ {draft}: No pipeline selected!", messages.ERROR)
                continue

            # Get "Invited" stage (second stage) for first contact emails
            # First stage is for leads not yet contacted
            invited_stage = PipelineStage.objects.filter(
                pipeline=draft.pipeline,
                name__icontains='invited'
            ).first()

            if not invited_stage:
                # Fallback to second stage
                invited_stage = PipelineStage.objects.filter(
                    pipeline=draft.pipeline
                ).order_by('order')[1:2].first()

            if not invited_stage:
                # Last resort: first stage
                invited_stage = PipelineStage.objects.filter(
                    pipeline=draft.pipeline
                ).order_by('order').first()

            if not invited_stage:
                self.message_user(request, f"❌ {draft}: Pipeline has no stages!", messages.ERROR)
                continue

            # Get email content
            subject = draft.final_subject or draft.generated_subject
            body_text = draft.final_body or draft.generated_body

            if not subject or not body_text:
                self.message_user(request, f"⚠️ {draft}: No content - generate first", messages.WARNING)
                continue

            # Get all recipients and filter
            all_recipients = draft.get_all_recipients()
            if not all_recipients:
                self.message_user(request, f"⚠️ {draft}: No recipients", messages.WARNING)
                continue

            # Filter recipients - remove unsubscribed and already in pipeline
            valid_recipients = []
            contacts_to_update = []

            for recipient in all_recipients:
                recipient_email = recipient['email']
                contact = recipient.get('contact')

                # Get or find contact (case-insensitive email lookup)
                if not contact:
                    contact = Contact.objects.filter(email__iexact=recipient_email).first()

                # Check unsubscribed (global OR brand-specific)
                brand_slug = draft.brand.slug if draft.brand else None
                if contact:
                    if contact.is_unsubscribed or contact.is_unsubscribed_from_brand(brand_slug):
                        total_blocked += 1
                        continue

                # Check if already in active pipeline
                if contact:
                    existing_deal = Deal.objects.filter(
                        contact=contact,
                        status='active'
                    ).exists()
                    if existing_deal:
                        total_in_pipeline += 1
                        continue

                # Valid recipient
                valid_recipients.append({
                    'email': recipient_email,
                    'name': recipient.get('name', ''),
                    'company': recipient.get('company', ''),
                    'website': recipient.get('website', ''),
                    'contact': contact,
                    'brand_slug': brand_slug,  # Pass brand for later use
                })

            if not valid_recipients:
                self.message_user(
                    request,
                    f"⚠️ {draft}: No valid recipients (all filtered out)",
                    messages.WARNING
                )
                continue

            # Send individually with per-recipient styled HTML
            email_service = ZohoEmailService(brand=draft.brand)
            from crm.services.email_templates import get_styled_email

            # Check if Zoho is configured
            if not email_service.enabled:
                self.message_user(
                    request,
                    f"❌ {draft}: Zoho Mail not configured for {draft.brand.name}! "
                    f"Please configure Zoho credentials in Brand settings.",
                    messages.ERROR
                )
                continue

            sent_count = 0
            failed_count = 0

            try:
                # Send to each recipient individually with personalized unsubscribe link
                from crm.services.ai_agent import CRMAIAgent
                ai_agent = CRMAIAgent()

                for recipient in valid_recipients:
                    contact = recipient.get('contact')
                    recipient_email = recipient['email']
                    recipient_name = recipient.get('name', '')
                    recipient_company = recipient.get('company', '')

                    # Generate smart salutation (extracts name from email like john.smith@company.com → "Hi John,")
                    salutation = ai_agent.get_smart_salutation(
                        email=recipient_email,
                        name=recipient_name,
                        company=recipient_company
                    )

                    # Replace {{SALUTATION}} placeholder in body
                    personalized_body = body_text.replace('{{SALUTATION}}', salutation)

                    # Extract first name for template (from salutation like "Hi John," → "John")
                    extracted_name = salutation.replace('Hi ', '').replace(',', '').strip() if salutation.startswith('Hi ') else 'there'
                    if ' Team' in extracted_name:
                        extracted_name = 'there'  # Don't use "Company Team" as name

                    # Generate styled HTML with correct recipient email for unsubscribe link
                    styled_email = get_styled_email(
                        brand_slug=draft.brand.slug if draft.brand else 'desifirms',
                        pipeline_type=draft.pipeline.pipeline_type if draft.pipeline else 'business',
                        email_type=draft.email_type or 'directory_invitation',
                        recipient_name=extracted_name,
                        recipient_email=recipient_email,  # Correct email for unsubscribe!
                        recipient_company=recipient_company,
                        subject=subject,
                        body=personalized_body,  # Use personalized body with salutation
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

                        # Get or create contact (case-insensitive lookup)
                        contact = Contact.objects.filter(email__iexact=recipient_email).first()
                        if not contact:
                            try:
                                contact = Contact.objects.create(
                                    email=recipient_email.lower(),  # Normalize to lowercase
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
                                # If creation fails, try to get existing contact
                                contact = Contact.objects.filter(email__iexact=recipient_email).first()
                                if contact:
                                    contact.last_emailed_at = timezone.now()
                                    contact.email_count = (contact.email_count or 0) + 1
                                    contact.save(update_fields=['last_emailed_at', 'email_count'])
                        else:
                            # Update existing contact
                            contact.last_emailed_at = timezone.now()
                            contact.email_count = (contact.email_count or 0) + 1
                            contact.status = 'contacted'
                            contact.save(update_fields=['last_emailed_at', 'email_count', 'status'])

                        # Create deal in pipeline at "Invited" stage
                        if contact:
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

                total_sent += sent_count

                # Update draft tracking
                draft.sent_count = (draft.sent_count or 0) + sent_count
                draft.deals_created = (draft.deals_created or 0) + total_deals
                draft.is_sent = True
                draft.sent_at = timezone.now()
                draft.save(update_fields=['sent_count', 'deals_created', 'is_sent', 'sent_at'])

                msg = f"✅ {draft}: Sent {sent_count} emails"
                if failed_count > 0:
                    msg += f" ({failed_count} failed)"
                self.message_user(request, msg, messages.SUCCESS)

            except Exception as e:
                self.message_user(request, f"❌ {draft}: {str(e)}", messages.ERROR)

        # Summary
        self.message_user(
            request,
            f"📤 DONE: {total_sent} sent, {total_deals} deals created, {total_in_pipeline} skipped (in pipeline), {total_blocked} blocked (unsubscribed)",
            messages.SUCCESS if total_sent > 0 else messages.WARNING
        )

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
        Send a single draft via BCC and create deals.
        Called from custom change form button.
        """
        from crm.services.email_service import ZohoEmailService
        from crm.models import Contact, Deal, PipelineStage
        from django.contrib import messages
        from django.http import HttpResponseRedirect
        from django.utils import timezone

        # Validate pipeline
        if not draft.pipeline:
            self.message_user(request, f"❌ No pipeline selected!", messages.ERROR)
            return HttpResponseRedirect(request.path)

        # Get "Invited" stage for first contact emails
        invited_stage = PipelineStage.objects.filter(
            pipeline=draft.pipeline,
            name__icontains='invited'
        ).first()

        if not invited_stage:
            # Fallback to second stage
            invited_stage = PipelineStage.objects.filter(
                pipeline=draft.pipeline
            ).order_by('order')[1:2].first()

        if not invited_stage:
            # Last resort: first stage
            invited_stage = PipelineStage.objects.filter(
                pipeline=draft.pipeline
            ).order_by('order').first()

        if not invited_stage:
            self.message_user(request, f"❌ Pipeline has no stages!", messages.ERROR)
            return HttpResponseRedirect(request.path)

        # Get email content
        subject = draft.final_subject or draft.generated_subject
        body_text = draft.final_body or draft.generated_body

        if not subject or not body_text:
            self.message_user(request, f"⚠️ No content - generate or write email first", messages.WARNING)
            return HttpResponseRedirect(request.path)

        # Get all recipients and filter
        all_recipients = draft.get_all_recipients()
        if not all_recipients:
            self.message_user(request, f"⚠️ No recipients", messages.WARNING)
            return HttpResponseRedirect(request.path)

        # Filter recipients - remove unsubscribed and already in pipeline
        valid_recipients = []
        total_blocked = 0
        total_in_pipeline = 0

        for recipient in all_recipients:
            recipient_email = recipient['email']
            contact = recipient.get('contact')

            # Get or find contact (case-insensitive lookup)
            if not contact:
                contact = Contact.objects.filter(email__iexact=recipient_email).first()

            # Check unsubscribed (global OR brand-specific)
            if contact:
                brand_slug = draft.brand.slug if draft.brand else None
                if contact.is_unsubscribed or contact.is_unsubscribed_from_brand(brand_slug):
                    total_blocked += 1
                    continue

            # Check if already in active pipeline
            if contact:
                existing_deal = Deal.objects.filter(
                    contact=contact,
                    status='active'
                ).exists()
                if existing_deal:
                    total_in_pipeline += 1
                    continue

            # Valid recipient
            valid_recipients.append({
                'email': recipient_email,
                'name': recipient.get('name', ''),
                'company': recipient.get('company', ''),
                'website': recipient.get('website', ''),
                'contact': contact
            })

        if not valid_recipients:
            self.message_user(
                request,
                f"⚠️ No valid recipients (all filtered: {total_blocked} unsubscribed, {total_in_pipeline} in pipeline)",
                messages.WARNING
            )
            return HttpResponseRedirect(request.path)

        # Send individually with per-recipient styled HTML
        email_service = ZohoEmailService(brand=draft.brand)
        from crm.services.email_templates import get_styled_email

        # Check if Zoho is configured
        if not email_service.enabled:
            self.message_user(
                request,
                f"❌ Zoho Mail not configured for {draft.brand.name}! "
                f"Please configure DESIFIRMS_ZOHO_* env vars or Brand Zoho settings.",
                messages.ERROR
            )
            return HttpResponseRedirect(request.path)

        sent_count = 0
        failed_count = 0
        total_deals = 0

        try:
            # Send to each recipient individually with personalized unsubscribe link
            from crm.services.ai_agent import CRMAIAgent
            ai_agent = CRMAIAgent()

            for recipient in valid_recipients:
                contact = recipient.get('contact')
                recipient_email = recipient['email']
                recipient_name = recipient.get('name', '')
                recipient_company = recipient.get('company', '')

                # Generate smart salutation (extracts name from email like john.smith@company.com → "Hi John,")
                salutation = ai_agent.get_smart_salutation(
                    email=recipient_email,
                    name=recipient_name,
                    company=recipient_company
                )

                # Replace {{SALUTATION}} placeholder in body
                personalized_body = body_text.replace('{{SALUTATION}}', salutation)

                # Extract first name for template (from salutation like "Hi John," → "John")
                extracted_name = salutation.replace('Hi ', '').replace(',', '').strip() if salutation.startswith('Hi ') else 'there'
                if ' Team' in extracted_name:
                    extracted_name = 'there'  # Don't use "Company Team" as name

                # Generate styled HTML with correct recipient email for unsubscribe link
                styled_email = get_styled_email(
                    brand_slug=draft.brand.slug if draft.brand else 'desifirms',
                    pipeline_type=draft.pipeline.pipeline_type if draft.pipeline else 'business',
                    email_type=draft.email_type or 'directory_invitation',
                    recipient_name=extracted_name,
                    recipient_email=recipient_email,  # Correct email for unsubscribe!
                    recipient_company=recipient_company,
                    subject=subject,
                    body=personalized_body,  # Use personalized body with salutation
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

                    # Create contact if doesn't exist
                    if not contact:
                        try:
                            contact = Contact.objects.create(
                                brand=draft.brand,
                                email=recipient_email,
                                name=recipient_name or extracted_name,  # Use extracted name if no name provided
                                company=recipient_company,
                                website=recipient.get('website', ''),
                                status='contacted',
                                last_emailed_at=timezone.now(),
                                email_count=1,
                                source='email_composer'
                            )
                        except Exception:
                            # Contact may exist with different case - fetch it
                            contact = Contact.objects.filter(email__iexact=recipient_email).first()
                            if contact:
                                contact.last_emailed_at = timezone.now()
                                contact.email_count = (contact.email_count or 0) + 1
                                contact.status = 'contacted'
                                contact.save(update_fields=['last_emailed_at', 'email_count', 'status'])
                    else:
                        # Update existing contact
                        contact.last_emailed_at = timezone.now()
                        contact.email_count = (contact.email_count or 0) + 1
                        contact.status = 'contacted'
                        contact.save(update_fields=['last_emailed_at', 'email_count', 'status'])

                    # Create deal in pipeline at "Invited" stage
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

            # Update draft tracking
            draft.sent_count = (draft.sent_count or 0) + sent_count
            draft.deals_created = (draft.deals_created or 0) + total_deals
            draft.is_sent = True
            draft.sent_at = timezone.now()
            draft.save(update_fields=['sent_count', 'deals_created', 'is_sent', 'sent_at'])

            msg = f"✅ Sent {sent_count} emails! {total_deals} deals created in {draft.pipeline.name}"
            if failed_count > 0:
                msg += f" ({failed_count} failed)"
            self.message_user(request, msg, messages.SUCCESS)

        except Exception as e:
            self.message_user(request, f"❌ Error: {str(e)}", messages.ERROR)

        return HttpResponseRedirect(request.path)


