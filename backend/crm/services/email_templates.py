"""
CRM Email Template Service

Renders beautiful HTML email templates for CRM outreach campaigns.
"""

from django.template.loader import render_to_string
from django.utils import timezone
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


# Template mapping for different email types and stages
EMAIL_TEMPLATES = {
    # Desi Firms - Real Estate Pipeline
    'desifirms': {
        'realestate': {
            'agent_invitation': 'crm/emails/realestate_invitation.html',
            'agent_followup_1': 'crm/emails/realestate_followup1.html',
            'agent_followup_2': 'crm/emails/realestate_followup2.html',
            'agent_responded': 'crm/emails/realestate_responded.html',
            'agent_registered': 'crm/emails/realestate_registered.html',
            'agent_listing': 'crm/emails/realestate_listing.html',
        },
        'business': {
            'directory_invitation': 'crm/emails/business_invitation.html',
            'directory_followup_1': 'crm/emails/business_followup1.html',
            'directory_followup_2': 'crm/emails/business_followup2.html',
            'business_responded': 'crm/emails/business_responded.html',
            'business_signedup': 'crm/emails/business_signedup.html',
            'business_listed': 'crm/emails/business_listed.html',
        },
        'backlink': {
            'backlink_pitch': 'crm/emails/backlink_pitch.html',
            'backlink_followup': 'crm/emails/backlink_followup.html',
        },
        # Fallback template for any Desi Firms email
        '_default': 'crm/emails/desifirms_generic.html',
    },
    # Codeteki Brand
    'codeteki': {
        'sales': {
            'services_intro': 'crm/emails/codeteki_services.html',
            'sales_followup': 'crm/emails/codeteki_followup.html',
            'sales_followup_2': 'crm/emails/codeteki_followup2.html',
            'sales_responded': 'crm/emails/codeteki_responded.html',
            'discovery_scheduled': 'crm/emails/codeteki_discovery.html',
            'proposal_sent': 'crm/emails/codeteki_proposal.html',
            'welcome_client': 'crm/emails/codeteki_welcome.html',
        },
        'backlink': {
            'backlink_pitch': 'crm/emails/codeteki_backlink.html',
            'backlink_followup': 'crm/emails/codeteki_backlink.html',  # Same template for follow-up
        },
        '_default': 'crm/emails/codeteki_generic.html',
    },
}


# Maps pipeline stage names to email template types
STAGE_TO_EMAIL_TYPE = {
    # Desi Firms Real Estate Pipeline stages
    'identified': None,  # No email sent
    'invitation sent': 'agent_invitation',
    'follow-up 1': 'agent_followup_1',
    'follow-up 2': 'agent_followup_2',
    'not interested': None,  # No email sent

    # Desi Firms Business Directory Pipeline stages
    'business found': None,  # No email sent
    'invited': 'directory_invitation',
    'follow up 1': 'directory_followup_1',
    'follow up 2': 'directory_followup_2',
    'responded': 'business_responded',  # Used by both real estate and business
    'signed up': 'business_signedup',
    'registered': 'agent_registered',  # Real estate specific
    'listing': 'agent_listing',  # Real estate specific
    'listed': 'business_listed',  # Business specific

    # Backlink Pipeline stages
    'prospect identified': None,
    'initial outreach': 'backlink_pitch',
    'follow-up sent': 'backlink_followup',
    'negotiating': None,
    'backlink secured': None,

    # Codeteki Sales Pipeline
    'lead found': None,
    'intro sent': 'services_intro',
    'follow up 1': 'sales_followup',
    'follow up 2': 'sales_followup_2',
    'responded': 'sales_responded',
    'discovery call': 'discovery_scheduled',
    'proposal sent': 'proposal_sent',
    'negotiating': None,
    'client': 'welcome_client',
    'lost': None,
}


def get_email_type_for_stage(stage_name: str) -> Optional[str]:
    """
    Get the email type for a given pipeline stage.

    Args:
        stage_name: Name of the pipeline stage

    Returns:
        Email type string or None if no email should be sent
    """
    return STAGE_TO_EMAIL_TYPE.get(stage_name.lower())


def get_pipeline_type_from_name(pipeline_name: str) -> str:
    """
    Determine pipeline type from pipeline name.

    Args:
        pipeline_name: Name of the pipeline

    Returns:
        Pipeline type (realestate, business, backlink, sales)
    """
    name_lower = pipeline_name.lower()

    if 'real estate' in name_lower or 'realestate' in name_lower:
        return 'realestate'
    elif 'business' in name_lower or 'directory' in name_lower:
        return 'business'
    elif 'backlink' in name_lower or 'seo' in name_lower:
        return 'backlink'
    elif 'sales' in name_lower:
        return 'sales'
    else:
        return 'business'  # Default


def get_template_for_email(
    brand_slug: str,
    pipeline_type: str,
    email_type: str
) -> Optional[str]:
    """
    Get the template path for a specific email type.

    Args:
        brand_slug: Brand identifier (desifirms, codeteki)
        pipeline_type: Type of pipeline (realestate, business, backlink, sales)
        email_type: Type of email (agent_invitation, followup_1, etc.)

    Returns:
        Template path or None if not found
    """
    brand_templates = EMAIL_TEMPLATES.get(brand_slug, {})

    # Try specific pipeline + email type
    pipeline_templates = brand_templates.get(pipeline_type, {})
    template = pipeline_templates.get(email_type)

    if template:
        return template

    # Try brand default
    return brand_templates.get('_default')


def render_email_html(
    brand_slug: str,
    pipeline_type: str,
    email_type: str,
    context: Dict[str, Any],
    recipient_email: str,
) -> Optional[str]:
    """
    Render an HTML email using the appropriate template.

    Args:
        brand_slug: Brand identifier
        pipeline_type: Pipeline type
        email_type: Email type
        context: Template context variables
        recipient_email: Recipient email for unsubscribe link

    Returns:
        Rendered HTML string or None if template not found
    """
    from crm.views import get_unsubscribe_url

    template_path = get_template_for_email(brand_slug, pipeline_type, email_type)

    if not template_path:
        logger.warning(f"No template found for {brand_slug}/{pipeline_type}/{email_type}")
        return None

    # Generate unsubscribe URL using brand-aware function
    unsubscribe_url = get_unsubscribe_url(recipient_email, brand_slug)

    # Build full context
    full_context = {
        **context,
        'unsubscribe_url': unsubscribe_url,
        'current_year': timezone.now().year,
        'brand_slug': brand_slug,
    }

    try:
        return render_to_string(template_path, full_context)
    except Exception as e:
        logger.error(f"Error rendering template {template_path}: {e}")
        return None


def get_styled_email(
    brand_slug: str,
    pipeline_type: str,
    email_type: str,
    recipient_name: str,
    recipient_email: str,
    recipient_company: str = '',
    subject: str = '',
    body: str = '',
    **extra_context
) -> Dict[str, str]:
    """
    Get a styled HTML email, falling back to plain text if template not found.

    Args:
        brand_slug: Brand identifier
        pipeline_type: Pipeline type
        email_type: Email type
        recipient_name: Recipient's name
        recipient_email: Recipient's email
        recipient_company: Recipient's company (optional)
        subject: Email subject
        body: Plain text body (used as fallback or for template)
        **extra_context: Additional template variables

    Returns:
        Dict with 'html' and 'plain' versions of the email
    """
    context = {
        'recipient_name': recipient_name,
        'recipient_email': recipient_email,
        'recipient_company': recipient_company or 'your business',
        'subject': subject,
        'body_text': body,
        **extra_context
    }

    html_content = render_email_html(
        brand_slug=brand_slug,
        pipeline_type=pipeline_type,
        email_type=email_type,
        context=context,
        recipient_email=recipient_email,
    )

    # If no HTML template, create a simple HTML wrapper
    if not html_content:
        html_content = create_simple_html_wrapper(body, brand_slug, recipient_email)

    return {
        'html': html_content,
        'plain': body,  # Keep plain text for email clients that don't support HTML
    }


def create_simple_html_wrapper(
    body: str,
    brand_slug: str,
    recipient_email: str
) -> str:
    """
    Create a simple HTML wrapper for plain text emails.
    Used as fallback when no template exists.
    """
    from crm.views import get_unsubscribe_url

    # Generate brand-aware unsubscribe URL
    unsubscribe_url = get_unsubscribe_url(recipient_email, brand_slug)

    # Convert newlines to HTML breaks
    html_body = body.replace('\n\n', '</p><p style="margin: 0 0 15px 0;">').replace('\n', '<br>')

    # Brand-specific styling
    if 'desi' in brand_slug.lower():
        primary_color = '#0093E9'
        gradient = 'linear-gradient(135deg, #0093E9 0%, #80D0C7 100%)'
        brand_name = 'Desi Firms'
        website = 'https://www.desifirms.com.au'
        bg_color = '#f3f4f6'
        card_bg = '#ffffff'
        text_color = '#374151'
        btn_text_color = '#ffffff'
    else:
        primary_color = '#f9cd15'
        gradient = '#ffffff'
        brand_name = 'Codeteki'
        website = 'https://codeteki.au'
        bg_color = '#f8f9fa'
        card_bg = '#ffffff'
        text_color = '#4b5563'
        btn_text_color = '#1f2937'

    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: {bg_color};">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: {bg_color};">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; background: {card_bg}; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
                    <!-- Header -->
                    <tr>
                        <td style="background: {gradient}; padding: 30px; text-align: center; border-radius: 12px 12px 0 0; border-bottom: 3px solid {primary_color};">
                            <h1 style="color: #ffffff; font-size: 22px; margin: 0; font-weight: 700;">{brand_name}</h1>
                        </td>
                    </tr>
                    <!-- Body -->
                    <tr>
                        <td style="padding: 35px 30px;">
                            <p style="color: {text_color}; font-size: 16px; line-height: 1.7; margin: 0 0 15px 0;">
                                {html_body}
                            </p>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background: {bg_color}; padding: 25px 30px; border-top: 1px solid #333333; border-radius: 0 0 12px 12px; text-align: center;">
                            <p style="color: #888888; font-size: 13px; margin: 0 0 10px 0;">
                                <a href="{website}" style="color: {primary_color}; text-decoration: none;">{website}</a>
                            </p>
                            <p style="color: #666666; font-size: 12px; margin: 0;">
                                <a href="{unsubscribe_url}" style="color: #666666; text-decoration: underline;">Unsubscribe</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''
