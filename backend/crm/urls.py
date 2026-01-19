"""
CRM URL Configuration

API endpoints:
- /api/crm/pipelines/
- /api/crm/deals/
- /api/crm/contacts/
- /api/crm/contacts/search/      - AJAX contact search for email composer
- /api/crm/generate-email/       - AI email generation for composer
- /api/crm/email-sequences/
- /api/crm/ai-activity/
- /api/crm/stats/
- /api/crm/track/<tracking_id>/open.gif

Webhooks:
- /api/crm/webhooks/reply/       - Email reply notifications
- /api/crm/webhooks/unsubscribe/ - Unsubscribe/bounce notifications
"""

from django.urls import path
from .views import (
    PipelineListView,
    PipelineDetailView,
    DealListView,
    DealDetailView,
    DealMoveStageView,
    ContactListView,
    ContactDetailView,
    ContactSearchView,
    GenerateAIEmailView,
    EmailSequenceListView,
    AIActivityView,
    CRMStatsView,
    EmailTrackingPixelView,
    EmailReplyWebhookView,
    UnsubscribeWebhookView,
    # Dashboard views
    pipeline_dashboard,
    pipeline_board,
    move_deal_stage,
)

app_name = 'crm'

urlpatterns = [
    # Dashboard (Kanban views)
    path('dashboard/', pipeline_dashboard, name='pipeline_dashboard'),
    path('board/<int:pipeline_id>/', pipeline_board, name='pipeline_board'),
    path('board/move-deal/', move_deal_stage, name='move_deal_stage'),

    # Pipelines
    path('pipelines/', PipelineListView.as_view(), name='pipeline-list'),
    path('pipelines/<int:pipeline_id>/', PipelineDetailView.as_view(), name='pipeline-detail'),

    # Deals
    path('deals/', DealListView.as_view(), name='deal-list'),
    path('deals/<uuid:deal_id>/', DealDetailView.as_view(), name='deal-detail'),
    path('deals/<uuid:deal_id>/move-stage/', DealMoveStageView.as_view(), name='deal-move-stage'),

    # Contacts
    path('contacts/', ContactListView.as_view(), name='contact-list'),
    path('contacts/search/', ContactSearchView.as_view(), name='contact-search'),
    path('contacts/<uuid:contact_id>/', ContactDetailView.as_view(), name='contact-detail'),

    # Email Sequences
    path('email-sequences/', EmailSequenceListView.as_view(), name='email-sequence-list'),

    # AI Activity
    path('ai-activity/', AIActivityView.as_view(), name='ai-activity'),

    # AI Email Generation (for composer)
    path('generate-email/', GenerateAIEmailView.as_view(), name='generate-email'),

    # Stats
    path('stats/', CRMStatsView.as_view(), name='stats'),

    # Email Tracking
    path('track/<uuid:tracking_id>/open.gif', EmailTrackingPixelView.as_view(), name='tracking-pixel'),

    # Webhooks (for Zoho/email service callbacks)
    path('webhooks/reply/', EmailReplyWebhookView.as_view(), name='webhook-reply'),
    path('webhooks/unsubscribe/', UnsubscribeWebhookView.as_view(), name='webhook-unsubscribe'),
]
