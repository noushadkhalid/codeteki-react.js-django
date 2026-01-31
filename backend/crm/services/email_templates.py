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
            # For registered but inactive users (both names work)
            'agent_nudge': 'crm/emails/realestate_nudge.html',
            'agent_nudge_2': 'crm/emails/realestate_nudge2.html',
            'realestate_nudge': 'crm/emails/realestate_nudge.html',  # Email Composer option
            'realestate_nudge_2': 'crm/emails/realestate_nudge2.html',
        },
        'business': {
            'directory_invitation': 'crm/emails/business_invitation.html',
            'listing_benefits': 'crm/emails/business_invitation.html',  # Uses same styled template
            'directory_followup_1': 'crm/emails/business_followup1.html',
            'directory_followup_2': 'crm/emails/business_followup2.html',
            'business_responded': 'crm/emails/business_responded.html',
            'business_signedup': 'crm/emails/business_signedup.html',
            'business_listed': 'crm/emails/business_listed.html',
            # For registered but inactive users
            'business_nudge': 'crm/emails/business_nudge.html',
            'business_nudge_2': 'crm/emails/business_nudge2.html',
        },
        'backlink': {
            'backlink_pitch': 'crm/emails/backlink_pitch.html',
            'backlink_followup': 'crm/emails/backlink_followup.html',
        },
        'events': {
            'events_invitation': 'crm/emails/events_invitation.html',
            'events_followup_1': 'crm/emails/events_followup1.html',
            'events_followup_2': 'crm/emails/events_followup2.html',
            'events_responded': 'crm/emails/events_responded.html',
            'events_signedup': 'crm/emails/events_signedup.html',
            'events_listed': 'crm/emails/events_listed.html',
            # For registered but inactive users
            'events_nudge': 'crm/emails/events_nudge.html',
            'events_nudge_2': 'crm/emails/events_nudge2.html',
        },
        # For registered but inactive users (general - detects user type)
        'registered_users': {
            'business_nudge': 'crm/emails/business_nudge.html',
            'business_nudge_2': 'crm/emails/business_nudge2.html',
            'realestate_nudge': 'crm/emails/realestate_nudge.html',
            'realestate_nudge_2': 'crm/emails/realestate_nudge2.html',
            'events_nudge': 'crm/emails/events_nudge.html',
            'events_nudge_2': 'crm/emails/events_nudge2.html',
            # Aliases - 'invitation' maps to the appropriate nudge template
            'invitation': 'crm/emails/business_nudge.html',
            'directory_invitation': 'crm/emails/business_nudge.html',
            'agent_invitation': 'crm/emails/realestate_nudge.html',
            'events_invitation': 'crm/emails/events_nudge.html',
        },
        # Fallback template for any Desi Firms email
        '_default': 'crm/emails/desifirms_generic.html',
    },
    # Codeteki Brand
    'codeteki': {
        'sales': {
            'services_intro': 'crm/emails/codeteki_services.html',
            'seo_services': 'crm/emails/codeteki_seo.html',
            'sales_followup': 'crm/emails/codeteki_followup.html',
            'sales_followup_2': 'crm/emails/codeteki_followup2.html',
            'sales_responded': 'crm/emails/codeteki_responded.html',
            'discovery_scheduled': 'crm/emails/codeteki_discovery.html',
            'proposal_sent': 'crm/emails/codeteki_proposal.html',
            'proposal_followup': 'crm/emails/codeteki_proposal_followup.html',
            'welcome_client': 'crm/emails/codeteki_welcome.html',
        },
        'backlink': {
            'backlink_pitch': 'crm/emails/codeteki_backlink.html',
            'backlink_followup': 'crm/emails/codeteki_backlink.html',
            'guest_post': 'crm/emails/codeteki_backlink.html',  # Reuse backlink template
        },
        'partnership': {
            'partnership_intro': 'crm/emails/codeteki_partnership.html',
            'collaboration': 'crm/emails/codeteki_collaboration.html',
            'partnership_followup': 'crm/emails/codeteki_followup.html',  # Reuse followup template
        },
        '_default': 'crm/emails/codeteki_generic.html',
    },
}


# Maps pipeline stage names to email template types
# NOTE: Stage names are lowercased before lookup, so use lowercase keys
STAGE_TO_EMAIL_TYPE = {
    # Desi Firms Real Estate Pipeline stages (from seed_crm_pipelines.py)
    'agent found': None,  # No email sent - just queue
    'invited': 'agent_invitation',  # Initial invitation email
    'follow up 1': 'agent_followup_1',  # First follow-up
    'follow up 2': 'agent_followup_2',  # Second follow-up
    'responded': 'agent_responded',  # They replied
    'registered': 'agent_registered',  # They signed up
    'listing properties': 'agent_listing',  # They're listing!
    'not interested': None,  # Archive

    # Desi Firms Business Directory Pipeline stages
    'business found': None,  # No email sent
    'follow up 1': 'directory_followup_1',  # Note: same key, context determines template
    'follow up 2': 'directory_followup_2',
    'signed up': 'business_signedup',
    'listed': 'business_listed',

    # Backlink Pipeline stages
    'target found': None,
    'pitch sent': 'backlink_pitch',
    'link placed': None,
    'rejected': None,

    # Codeteki Sales Pipeline
    'prospect found': None,
    'intro sent': 'services_intro',
    'discovery call': 'discovery_scheduled',
    'proposal sent': 'proposal_sent',
    'client': 'welcome_client',
    'lost': None,

    # Legacy/Alternative stage names (for backwards compatibility)
    'invitation sent': 'agent_invitation',
    'follow-up 1': 'agent_followup_1',
    'follow-up 2': 'agent_followup_2',
}


def get_email_type_for_stage(stage_name: str, pipeline_type: str = None) -> Optional[str]:
    """
    Get the email type for a given pipeline stage.

    Args:
        stage_name: Name of the pipeline stage
        pipeline_type: Type of pipeline (realestate, business, etc.) for context

    Returns:
        Email type string or None if no email should be sent
    """
    stage_lower = stage_name.lower()

    # Context-aware mapping for stages shared across pipelines
    if pipeline_type == 'realestate':
        real_estate_map = {
            'invited': 'agent_invitation',
            'follow up 1': 'agent_followup_1',
            'follow up 2': 'agent_followup_2',
            'responded': 'agent_responded',
            'registered': 'agent_registered',
            'listing properties': 'agent_listing',
        }
        if stage_lower in real_estate_map:
            return real_estate_map[stage_lower]

    elif pipeline_type == 'business':
        business_map = {
            'invited': 'directory_invitation',
            'follow up 1': 'directory_followup_1',
            'follow up 2': 'directory_followup_2',
            'responded': 'business_responded',
            'signed up': 'business_signedup',
            'listed': 'business_listed',
        }
        if stage_lower in business_map:
            return business_map[stage_lower]

    elif pipeline_type == 'events':
        events_map = {
            'invited': 'events_invitation',
            'follow up 1': 'events_followup_1',
            'follow up 2': 'events_followup_2',
            'responded': 'events_responded',
            'signed up': 'events_signedup',
            'listed': 'events_listed',
            'nudge 1': 'events_nudge',
            'nudge 2': 'events_nudge_2',
        }
        if stage_lower in events_map:
            return events_map[stage_lower]

    elif pipeline_type == 'registered_users':
        # For registered but inactive users - generic pipeline
        registered_map = {
            'business nudge 1': 'business_nudge',
            'business nudge 2': 'business_nudge_2',
            'realestate nudge 1': 'realestate_nudge',
            'realestate nudge 2': 'realestate_nudge_2',
            'events nudge 1': 'events_nudge',
            'events nudge 2': 'events_nudge_2',
            # Simple stage names
            'nudge 1': 'business_nudge',  # Default to business
            'nudge 2': 'business_nudge_2',
        }
        if stage_lower in registered_map:
            return registered_map[stage_lower]

    # Fall back to generic mapping
    return STAGE_TO_EMAIL_TYPE.get(stage_lower)


def get_pipeline_type_from_name(pipeline_name: str) -> str:
    """
    Determine pipeline type from pipeline name.

    Args:
        pipeline_name: Name of the pipeline

    Returns:
        Pipeline type (realestate, business, backlink, sales, events, registered_users)
    """
    name_lower = pipeline_name.lower()

    if 'real estate' in name_lower or 'realestate' in name_lower:
        return 'realestate'
    elif 'event' in name_lower:
        return 'events'
    elif 'registered' in name_lower or 'inactive' in name_lower or 'nudge' in name_lower:
        return 'registered_users'
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
    # Normalize brand_slug to handle variations
    brand_slug_normalized = brand_slug.lower().replace('-', '').replace('_', '') if brand_slug else 'desifirms'
    if 'desi' in brand_slug_normalized:
        brand_slug_normalized = 'desifirms'
    elif 'codeteki' in brand_slug_normalized:
        brand_slug_normalized = 'codeteki'

    logger.info(f"Template lookup: brand={brand_slug} (normalized={brand_slug_normalized}), pipeline={pipeline_type}, email_type={email_type}")

    brand_templates = EMAIL_TEMPLATES.get(brand_slug_normalized, {})

    # Try specific pipeline + email type
    pipeline_templates = brand_templates.get(pipeline_type, {})
    template = pipeline_templates.get(email_type)

    if template:
        logger.info(f"Found template (direct): {template}")
        return template

    logger.info(f"No direct match. Available pipeline types: {list(brand_templates.keys())}")

    # Smart fallback: determine pipeline type from email_type prefix
    email_type_lower = email_type.lower()
    fallback_types = []

    if email_type_lower.startswith('business') or email_type_lower.startswith('directory'):
        fallback_types = ['business', 'registered_users']
    elif email_type_lower.startswith('realestate') or email_type_lower.startswith('agent'):
        fallback_types = ['realestate', 'registered_users']
    elif email_type_lower.startswith('events'):
        fallback_types = ['events', 'registered_users']
    elif email_type_lower.startswith('backlink') or email_type_lower.startswith('guest'):
        fallback_types = ['backlink']
    elif email_type_lower.startswith('partnership') or email_type_lower.startswith('collaboration'):
        fallback_types = ['partnership', 'sales']
    elif email_type_lower.startswith('sales') or email_type_lower.startswith('services') or email_type_lower.startswith('seo') or email_type_lower.startswith('proposal'):
        fallback_types = ['sales']

    # Try fallback pipeline types
    for fallback_type in fallback_types:
        if fallback_type != pipeline_type:  # Don't retry the same type
            fallback_templates = brand_templates.get(fallback_type, {})
            template = fallback_templates.get(email_type)
            if template:
                logger.info(f"Found template via fallback: {brand_slug_normalized}/{fallback_type}/{email_type}")
                return template

    # If still not found and it's a generic email_type like 'invitation', try mapping to specific type
    if email_type_lower in ['invitation', 'followup', 'followup_1', 'followup_2']:
        logger.info(f"Generic email_type '{email_type}' - trying to map to specific template")
        # Map based on pipeline_type
        type_mapping = {
            'business': 'directory_invitation',
            'realestate': 'agent_invitation',
            'events': 'events_invitation',
            'registered_users': 'invitation',  # Already handled above
        }
        mapped_type = type_mapping.get(pipeline_type)
        if mapped_type:
            pipeline_templates = brand_templates.get(pipeline_type, {})
            template = pipeline_templates.get(mapped_type)
            if template:
                logger.info(f"Found template via type mapping: {brand_slug_normalized}/{pipeline_type}/{mapped_type}")
                return template

    logger.warning(f"No template found, using brand default for {brand_slug_normalized}/{pipeline_type}/{email_type}")
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


def strip_signature_from_body(body: str) -> str:
    """
    Remove common email signatures from AI-generated body content.
    This prevents duplicate signatures when templates add their own.
    """
    import re

    # Common signature patterns to remove
    signature_patterns = [
        # "Warm regards," followed by name and contact info
        r'\n\n*(?:Warm regards|Best regards|Kind regards|Regards|Cheers|Best|Thanks|Thank you),?\s*\n+.*?(?:Noushad|Desi Firms|📱|🌐|desifirms).*$',
        # Just the closing with name
        r'\n\n*(?:Warm regards|Best regards|Kind regards|Regards|Cheers|Best),?\s*\n+\s*Noushad\s*(?:\n.*)?$',
        # Phone/website line at the end
        r'\n+📱.*?(?:desifirms|codeteki).*$',
    ]

    cleaned = body
    for pattern in signature_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)

    return cleaned.strip()


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
    # Strip signature from body if template will add one
    # Keep original for plain text version
    import re
    body_for_template = strip_signature_from_body(body)

    # Also remove the greeting if it starts with "Hi Name," since template adds it
    body_for_template = re.sub(r'^Hi\s+[^,]+,?\s*\n+', '', body_for_template, flags=re.IGNORECASE)

    # Safety check: if stripping left us with empty content, use original body
    # This can happen if AI only generated greeting + signature
    body_for_template = body_for_template.strip()
    if not body_for_template:
        # Try using body without signature but keep greeting
        body_for_template = strip_signature_from_body(body).strip()
    if not body_for_template:
        # Last resort: use original body
        body_for_template = body.strip() if body else ''

    # Convert plain text body to HTML (preserve paragraphs and line breaks)
    body_html = body_for_template.replace('\n\n', '</p><p style="margin: 0 0 15px 0;">').replace('\n', '<br>')
    if body_html and not body_html.startswith('<p'):
        body_html = f'<p style="margin: 0 0 15px 0;">{body_html}</p>'

    context = {
        'recipient_name': recipient_name,
        'recipient_email': recipient_email,
        'recipient_company': recipient_company or 'your business',
        'subject': subject,
        'body_text': body,
        'body_html': body_html,  # HTML-formatted version for templates
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
                        <td style="background: {bg_color}; padding: 25px 30px; border-top: 1px solid #e5e7eb; border-radius: 0 0 12px 12px; text-align: center;">
                            <p style="color: #888888; font-size: 13px; margin: 0 0 10px 0;">
                                <a href="{website}" style="color: {primary_color}; text-decoration: none;">{website}</a>
                            </p>
                            <p style="color: #666666; font-size: 12px; margin: 0 0 15px 0;">
                                <a href="{unsubscribe_url}" style="color: #666666; text-decoration: underline;">Unsubscribe</a>
                            </p>
                            <p style="color: #9ca3af; font-size: 11px; margin: 0; padding-top: 15px; border-top: 1px solid #e5e7eb;">
                                Powered by <a href="https://codeteki.au/?utm_source=crm_email&utm_medium=email&utm_campaign=powered_by" style="color: #f9cd15; text-decoration: none; font-weight: 600;">Codeteki Digital Services</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''
