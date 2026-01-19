"""
CRM AI Agent Service

Handles all AI-powered decision making for the CRM:
- Deal analysis and next action recommendations
- Email composition and personalization
- Reply classification
- Lead scoring
"""

import json
import logging
from typing import Optional
from django.utils import timezone

from core.services.ai_client import AIContentEngine

logger = logging.getLogger(__name__)


class CRMAIAgent:
    """
    AI agent for CRM automation.
    Uses OpenAI to analyze deals, compose emails, classify replies, and score leads.
    """

    # Generic email prefixes that indicate team/department rather than personal email
    GENERIC_EMAIL_PREFIXES = {
        'info', 'admin', 'sales', 'contact', 'hello', 'support', 'enquiry', 'enquiries',
        'team', 'office', 'marketing', 'hr', 'careers', 'jobs', 'accounts', 'billing',
        'help', 'service', 'services', 'general', 'mail', 'webmaster', 'noreply', 'no-reply',
        'reception', 'customerservice', 'customer-service', 'feedback', 'orders', 'booking',
        'bookings', 'reservations', 'press', 'media', 'partner', 'partners', 'enquire'
    }

    SYSTEM_PROMPT = """You are an expert sales and outreach AI assistant for Codeteki, a digital agency specializing in AI-powered web solutions and SEO services.

Your role is to help automate and optimize sales and backlink outreach campaigns by:
- Analyzing deals and recommending next actions
- Writing personalized, professional outreach emails
- Classifying incoming email replies
- Scoring leads based on available information

Always maintain a professional yet friendly tone. Focus on providing value to prospects.
Never be pushy or spammy. Build genuine relationships."""

    def __init__(self):
        self.ai_engine = AIContentEngine()

    def _humanize_domain_name(self, domain: str) -> str:
        """
        Convert a domain name into a human-readable company name.

        Examples:
            villagere.com.au → Village RE
            pioneerrealestate.com.au → Pioneer Real Estate
            aimestateagents.com.au → AIM Estate Agents
            sanapatel.com.au → Sana Patel
        """
        if not domain:
            return ''

        # Extract just the company part (before .com, .com.au, etc.)
        parts = domain.lower().split('.')
        company_part = parts[0] if parts else domain

        # Common business word patterns to split on (order matters - longer patterns first)
        word_patterns = [
            ('realestate', 'Real Estate'),
            ('estateagents', 'Estate Agents'),
            ('estateagent', 'Estate Agent'),
            ('properties', 'Properties'),
            ('property', 'Property'),
            ('homes', 'Homes'),
            ('group', 'Group'),
            ('agency', 'Agency'),
            ('agents', 'Agents'),
            ('australia', 'Australia'),
        ]

        # Check for common abbreviations at the end (e.g., "villagere" = "Village RE")
        re_abbreviations = [
            ('re', ' RE'),  # Real Estate
            ('pm', ' PM'),  # Property Management
        ]
        for abbrev, replacement in re_abbreviations:
            if company_part.endswith(abbrev) and len(company_part) > len(abbrev) + 2:
                base = company_part[:-len(abbrev)]
                return f"{base.title()}{replacement}"

        # Try to match and split known patterns
        result = company_part
        for pattern, replacement in word_patterns:
            if pattern in result:
                # Split at the pattern and capitalize parts
                before = result.split(pattern)[0]
                after_parts = result.split(pattern)[1:]
                after = ''.join(after_parts)

                # Capitalize the before part
                if before:
                    before = before.title()

                # Handle acronyms (all caps if 2-4 chars before pattern)
                if len(before) <= 4 and before.isalpha():
                    before = before.upper()

                result = f"{before} {replacement}".strip()
                if after:
                    result = f"{result} {after.title()}"
                break
        else:
            # No known pattern found - try to intelligently split
            # Look for camelCase or just title case it
            result = company_part.title()

        return result.strip()

    def get_smart_salutation(self, email: str, name: str = None, company: str = None) -> str:
        """
        Generate a smart salutation based on email address and available info.

        - If email starts with a personal name (rajesh@, bob@, nithya.patel@) → "Hi Rajesh,"
        - If email starts with generic prefix (info@, admin@, sales@) → "Hi [Company] Team," (extracts from domain)
        - If name is provided and looks like a real name → "Hi [FirstName],"

        Returns:
            Appropriate salutation string
        """
        if not email or '@' not in email:
            if company:
                return f"Hi {company} Team,"
            return "Hi there,"

        # Get the part before @ in email
        email_prefix = email.split('@')[0].lower()
        email_domain = email.split('@')[1].lower() if '@' in email else ''

        # Remove common separators to check the base prefix
        clean_prefix = email_prefix.replace('.', '').replace('_', '').replace('-', '')

        # Check if it's a generic prefix
        is_generic = (
            email_prefix in self.GENERIC_EMAIL_PREFIXES or
            clean_prefix in self.GENERIC_EMAIL_PREFIXES
        )

        # If we have a name that looks like a real person's name, use it
        if name and name.strip():
            name_clean = name.strip()
            # Check if name looks generic (like "Admin Team", "Info", "Sales Department")
            name_lower = name_clean.lower()
            generic_name_indicators = ['team', 'department', 'dept', 'info', 'admin', 'support', 'sales']
            is_generic_name = any(indicator in name_lower for indicator in generic_name_indicators)

            if not is_generic_name:
                # Extract first name
                first_name = name_clean.split()[0].title()
                # Make sure first name is actually a name (not a title)
                if first_name.lower() not in ['mr', 'ms', 'mrs', 'dr', 'prof', 'sir', 'madam']:
                    return f"Hi {first_name},"

        # If email is generic, extract company name from domain
        if is_generic:
            # Try to get company name from domain if not provided
            if not company and email_domain:
                company = self._humanize_domain_name(email_domain)

            if company:
                return f"Hi {company} Team,"
            return "Hi Team,"

        # Email looks like a personal name - extract and capitalize
        # Handle formats like: rajesh, r.kumar, nithya.patel, bob_smith, anshu.goel
        name_from_email = email_prefix.replace('.', ' ').replace('_', ' ').replace('-', ' ')
        # Get first part as first name
        first_name = name_from_email.split()[0].title() if name_from_email else 'there'

        # Basic validation - should look like a name (2+ letters, not all numbers)
        if len(first_name) >= 2 and not first_name.isdigit():
            return f"Hi {first_name},"

        # Fallback - try domain
        if email_domain:
            company_from_domain = self._humanize_domain_name(email_domain)
            if company_from_domain:
                return f"Hi {company_from_domain} Team,"

        if company:
            return f"Hi {company} Team,"
        return "Hi there,"

    def analyze_deal(self, deal) -> dict:
        """
        Analyze a deal and decide the next action.

        Returns:
            {
                'action': str,  # 'send_email', 'move_stage', 'wait', 'flag_for_review', 'pause'
                'reasoning': str,
                'metadata': dict
            }
        """
        from crm.models import AIDecisionLog

        # Build context about the deal
        context = self._build_deal_context(deal)

        prompt = f"""Analyze this deal and recommend the next action.

DEAL CONTEXT:
{context}

Based on the deal's current state, what should we do next?

Consider:
1. How long has it been since last contact?
2. What stage is the deal in?
3. Have we sent emails? Were they opened/replied?
4. What is the contact's engagement level?

Respond in JSON format:
{{
    "action": "send_email" | "move_stage" | "wait" | "flag_for_review" | "pause",
    "reasoning": "Brief explanation of why this action",
    "suggested_stage": "If action is move_stage, which stage name",
    "email_type": "If action is send_email, what type: initial, followup_1, followup_2, custom",
    "wait_days": "If action is wait, how many days to wait"
}}"""

        result = self.ai_engine.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3
        )

        if not result['success']:
            return {
                'action': 'flag_for_review',
                'reasoning': f"AI analysis failed: {result.get('error', 'Unknown error')}",
                'metadata': {}
            }

        try:
            parsed = json.loads(result['output'])
        except json.JSONDecodeError:
            # Try to extract action from text
            output = result['output'].lower()
            if 'send_email' in output:
                parsed = {'action': 'send_email', 'reasoning': result['output']}
            elif 'wait' in output:
                parsed = {'action': 'wait', 'reasoning': result['output']}
            else:
                parsed = {'action': 'flag_for_review', 'reasoning': result['output']}

        # Log the decision
        AIDecisionLog.objects.create(
            deal=deal,
            decision_type='deal_analyze',
            reasoning=parsed.get('reasoning', ''),
            action_taken=parsed.get('action', 'unknown'),
            metadata=parsed,
            tokens_used=result['usage'].get('prompt_tokens', 0) + result['usage'].get('completion_tokens', 0),
            model_used=result['model']
        )

        return {
            'action': parsed.get('action', 'flag_for_review'),
            'reasoning': parsed.get('reasoning', ''),
            'metadata': parsed
        }

    def compose_email(self, deal, template: Optional[str] = None, context: dict = None) -> dict:
        """
        Compose a personalized email for a deal.

        Args:
            deal: Deal object
            template: Optional template text with placeholders
            context: Additional context for personalization

        Returns:
            {'subject': str, 'body': str, 'success': bool}
        """
        from crm.models import AIDecisionLog, AIPromptTemplate

        contact = deal.contact
        context = context or {}

        # Get template if specified
        if template is None:
            # Try to find an appropriate template
            prompt_template = AIPromptTemplate.objects.filter(
                prompt_type='email_compose',
                is_active=True
            ).first()
            template = prompt_template.prompt_text if prompt_template else None

        # Get brand info for sender details
        brand = deal.pipeline.brand if deal.pipeline else None
        sender_name = brand.from_name if brand else 'The Team'
        sender_company = brand.name if brand else 'Codeteki'
        company_description = brand.ai_company_description if brand else 'a digital agency specializing in AI-powered web solutions and SEO services'
        value_proposition = brand.ai_value_proposition if brand else 'helping businesses grow their online presence through cutting-edge technology'

        # Build email context
        email_context = {
            'contact_name': contact.name,
            'contact_company': contact.company or 'your company',
            'contact_website': contact.website or '',
            'pipeline_type': deal.pipeline.pipeline_type,
            'current_stage': deal.current_stage.name if deal.current_stage else '',
            'emails_sent': deal.emails_sent,
            'our_company': sender_company,
            'sender_name': sender_name,
            **context
        }

        # Determine email type based on stage and emails sent
        if deal.emails_sent == 0:
            email_type = "initial outreach"
        elif deal.emails_sent == 1:
            email_type = "first follow-up"
        elif deal.emails_sent == 2:
            email_type = "second follow-up"
        else:
            email_type = f"follow-up #{deal.emails_sent}"

        prompt = f"""Write a professional {email_type} email for this {deal.pipeline.pipeline_type} campaign.

SENDER INFORMATION (this is who is sending the email):
- Sender Name: {sender_name}
- Company: {sender_company}
- About Us: {company_description}
- Value Proposition: {value_proposition}

RECIPIENT INFORMATION:
- Name: {contact.name}
- Company: {contact.company or 'Unknown'}
- Website: {contact.website or 'Not available'}
- Domain Authority: {contact.domain_authority or 'Unknown'}
- Contact Type: {contact.get_contact_type_display()}

CAMPAIGN CONTEXT:
- Pipeline: {deal.pipeline.name}
- Current Stage: {deal.current_stage.name if deal.current_stage else 'Initial'}
- Emails Already Sent: {deal.emails_sent}
- AI Notes: {deal.ai_notes or 'None'}

{f'TEMPLATE TO PERSONALIZE:{chr(10)}{template}' if template else ''}

Requirements:
1. Keep it concise (under 150 words for initial, under 100 for follow-ups)
2. Be professional but friendly
3. Provide clear value proposition
4. Include a soft call-to-action
5. Don't be pushy or salesy
6. If this is for backlink outreach, focus on mutual benefit
7. Sign off with "{sender_name}" - DO NOT use placeholders like [Your Name]

Respond in JSON format:
{{
    "subject": "Email subject line",
    "body": "Email body text (sign off with Best regards, {sender_name})"
}}"""

        result = self.ai_engine.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.5  # Slightly higher for more creative emails
        )

        if not result['success']:
            return {
                'subject': '',
                'body': '',
                'success': False,
                'error': result.get('error', 'AI generation failed')
            }

        try:
            parsed = json.loads(result['output'])
        except json.JSONDecodeError:
            # Try to extract from text
            lines = result['output'].strip().split('\n')
            subject = lines[0] if lines else 'Following up'
            body = '\n'.join(lines[1:]) if len(lines) > 1 else result['output']
            parsed = {'subject': subject, 'body': body}

        # Log the decision
        AIDecisionLog.objects.create(
            deal=deal,
            decision_type='compose_email',
            reasoning=f"Composed {email_type} email",
            action_taken='email_composed',
            metadata={'email_type': email_type, 'subject': parsed.get('subject', '')},
            tokens_used=result['usage'].get('prompt_tokens', 0) + result['usage'].get('completion_tokens', 0),
            model_used=result['model']
        )

        return {
            'subject': parsed.get('subject', 'Following up'),
            'body': parsed.get('body', ''),
            'success': True
        }

    def classify_reply(self, email_content: str, deal=None) -> dict:
        """
        Classify an incoming email reply.

        Returns:
            {
                'sentiment': 'positive' | 'negative' | 'neutral',
                'intent': 'interested' | 'not_interested' | 'question' | 'out_of_office' | 'unsubscribe',
                'suggested_action': str,
                'summary': str
            }
        """
        from crm.models import AIDecisionLog

        deal_context = ""
        if deal:
            deal_context = f"""
DEAL CONTEXT:
- Contact: {deal.contact.name} ({deal.contact.company or 'Unknown company'})
- Pipeline: {deal.pipeline.name}
- Stage: {deal.current_stage.name if deal.current_stage else 'Unknown'}
- Emails Sent: {deal.emails_sent}
"""

        prompt = f"""Classify this email reply and determine the appropriate next action.
{deal_context}
EMAIL CONTENT:
---
{email_content}
---

Analyze the email and respond in JSON format:
{{
    "sentiment": "positive" | "negative" | "neutral",
    "intent": "interested" | "not_interested" | "question" | "out_of_office" | "unsubscribe" | "other",
    "suggested_action": "What should we do next (e.g., 'schedule_call', 'send_info', 'remove_from_sequence', 'wait', 'move_to_interested')",
    "summary": "One-sentence summary of the reply",
    "confidence": 0.0 to 1.0
}}"""

        result = self.ai_engine.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.2  # Lower for more consistent classification
        )

        default_response = {
            'sentiment': 'neutral',
            'intent': 'other',
            'suggested_action': 'flag_for_review',
            'summary': 'Could not classify reply',
            'confidence': 0.0
        }

        if not result['success']:
            return default_response

        try:
            parsed = json.loads(result['output'])
        except json.JSONDecodeError:
            return default_response

        # Log the decision
        if deal:
            AIDecisionLog.objects.create(
                deal=deal,
                decision_type='classify_reply',
                reasoning=parsed.get('summary', ''),
                action_taken=f"Classified as {parsed.get('intent', 'unknown')}",
                metadata=parsed,
                tokens_used=result['usage'].get('prompt_tokens', 0) + result['usage'].get('completion_tokens', 0),
                model_used=result['model']
            )

        return {
            'sentiment': parsed.get('sentiment', 'neutral'),
            'intent': parsed.get('intent', 'other'),
            'suggested_action': parsed.get('suggested_action', 'flag_for_review'),
            'summary': parsed.get('summary', ''),
            'confidence': parsed.get('confidence', 0.5)
        }

    def score_lead(self, contact) -> int:
        """
        Score a lead based on available information.

        Returns:
            Score from 0-100
        """
        from crm.models import AIDecisionLog

        # Build contact context
        context_parts = [
            f"Name: {contact.name}",
            f"Email: {contact.email}",
            f"Company: {contact.company or 'Unknown'}",
            f"Website: {contact.website or 'Not provided'}",
            f"Domain Authority: {contact.domain_authority or 'Unknown'}",
            f"Source: {contact.source or 'Unknown'}",
            f"Contact Type: {contact.get_contact_type_display()}",
            f"Notes: {contact.notes or 'None'}",
        ]

        # Add deal history if exists
        deals = contact.deals.all()
        if deals.exists():
            deal_info = []
            for deal in deals[:5]:
                deal_info.append(f"- {deal.pipeline.name}: {deal.status} ({deal.emails_sent} emails sent)")
            context_parts.append(f"Deal History:\n" + "\n".join(deal_info))

        prompt = f"""Score this lead from 0-100 based on their likelihood to convert.

LEAD INFORMATION:
{chr(10).join(context_parts)}

Consider:
1. Company information completeness
2. Website presence and quality indicators (domain authority)
3. Source quality
4. Previous engagement (if any)
5. Company size/type indicators

Respond in JSON format:
{{
    "score": 0-100,
    "reasoning": "Brief explanation",
    "strengths": ["List of positive factors"],
    "weaknesses": ["List of concerns"]
}}"""

        result = self.ai_engine.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.2
        )

        if not result['success']:
            # Return a default middle score
            return 50

        try:
            parsed = json.loads(result['output'])
            score = int(parsed.get('score', 50))
            score = max(0, min(100, score))  # Clamp to 0-100
        except (json.JSONDecodeError, ValueError):
            score = 50

        # Update contact score
        contact.ai_score = score
        contact.save(update_fields=['ai_score'])

        # Log the decision
        AIDecisionLog.objects.create(
            contact=contact,
            decision_type='score_lead',
            reasoning=parsed.get('reasoning', '') if 'parsed' in dir() else 'Score calculation',
            action_taken=f"Scored lead at {score}/100",
            metadata=parsed if 'parsed' in dir() else {'score': score},
            tokens_used=result['usage'].get('prompt_tokens', 0) + result['usage'].get('completion_tokens', 0),
            model_used=result['model']
        )

        return score

    def generate_backlink_pitch(self, opportunity) -> dict:
        """
        Generate a personalized backlink outreach pitch.

        Returns:
            {'angle': str, 'email_subject': str, 'email_body': str}
        """
        prompt = f"""Create a personalized backlink outreach pitch.

TARGET WEBSITE:
- URL: {opportunity.target_url}
- Domain: {opportunity.target_domain}
- Domain Authority: {opportunity.domain_authority}

OUR CONTENT:
- URL: {opportunity.our_content_url}
- Suggested Anchor Text: {opportunity.anchor_text_suggestion or 'Not specified'}

Requirements:
1. Create a compelling angle that shows mutual benefit
2. Don't be pushy - focus on value we can provide
3. Keep it brief and professional
4. Suggest why our content would be valuable to their readers

Respond in JSON format:
{{
    "angle": "The outreach angle/hook",
    "email_subject": "Subject line for the pitch",
    "email_body": "The pitch email body"
}}"""

        result = self.ai_engine.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.5
        )

        if not result['success']:
            return {
                'angle': '',
                'email_subject': '',
                'email_body': '',
                'success': False
            }

        try:
            parsed = json.loads(result['output'])
        except json.JSONDecodeError:
            return {
                'angle': result['output'],
                'email_subject': 'Partnership Opportunity',
                'email_body': result['output'],
                'success': True
            }

        # Update the opportunity with the angle
        opportunity.outreach_angle = parsed.get('angle', '')
        opportunity.save(update_fields=['outreach_angle'])

        return {
            'angle': parsed.get('angle', ''),
            'email_subject': parsed.get('email_subject', ''),
            'email_body': parsed.get('email_body', ''),
            'success': True
        }

    def compose_email_from_context(self, context: dict) -> dict:
        """
        Compose an email based on provided context (without requiring a Deal).
        Used by the AI Email Composer for free-form email drafting.

        Args:
            context: Dict with keys:
                - email_type: 'sales_intro', 'sales_followup', 'backlink_outreach', 'partnership', 'custom'
                - tone: 'professional', 'friendly', 'formal', 'persuasive'
                - suggestions: User's ideas/key points
                - recipient_name, recipient_company, recipient_website, recipient_email (optional)
                - brand_name, brand_website, brand_description, value_proposition

        Returns:
            {'subject': str, 'body': str, 'success': bool}
        """
        from crm.models import AIDecisionLog

        email_type = context.get('email_type', 'sales_intro')
        tone = context.get('tone', 'professional')
        suggestions = context.get('suggestions', '')
        pipeline_type = context.get('pipeline_type', '')  # e.g., 'business', 'events', 'sales'
        pipeline_name = context.get('pipeline_name', '')
        recipient_name = context.get('recipient_name', '')
        recipient_email = context.get('recipient_email', '')
        recipient_company = context.get('recipient_company', '')
        recipient_website = context.get('recipient_website', '')
        brand_name = context.get('brand_name', 'Codeteki')
        brand_website = context.get('brand_website', '')
        brand_description = context.get('brand_description', 'a digital agency')
        value_proposition = context.get('value_proposition', '')

        # Generate smart salutation based on email/name/company
        smart_salutation = self.get_smart_salutation(
            email=recipient_email,
            name=recipient_name,
            company=recipient_company
        )

        # Map email types to descriptions
        email_type_descriptions = {
            # Desi Firms - Business Listings (NEW PLATFORM LAUNCHING)
            'directory_invitation': '''an invitation email to list their business on Desi Firms, a NEWLY LAUNCHING community platform for South Asians in Australia.
IMPORTANT CONTEXT: Desi Firms is brand new and just launching. We are NOT established yet - we're building this platform for the community.
Key points to convey:
- We've just built/launched this platform for the South Asian community
- Inviting established businesses like theirs to be FOUNDING MEMBERS
- Completely FREE to list - no fees, no credit card, no obligation
- Their presence would add value to the platform
- We're building something together for the community
- Be humble and genuine - we need their cooperation to build this
Tone: Respectful, humble, inviting them to join from the beginning''',

            'listing_benefits': '''an email highlighting the benefits of listing on Desi Firms FREE directory.
Context: NEW platform just launching. Focus on:
- Early visibility as platform grows
- Free plan with no hidden costs
- Community-focused marketplace
- Be part of building something for the community
- Founding member recognition''',

            'invitation_followup': '''a friendly follow-up to a previous invitation.
Context: We're a NEW platform that just reached out. Be gentle and:
- Remind them of the free opportunity
- Acknowledge they're busy
- Reiterate the founding member opportunity
- No pressure, just checking if they had questions''',

            'onboarding_help': 'a helpful email offering assistance with setting up their business listing. Be supportive and offer step-by-step help',

            # Desi Firms - Events (NEW PLATFORM)
            'event_invitation': '''an invitation email to event organizers to list their events on Desi Firms.
Context: NEW platform just launching a dedicated events section.
- Invite them to be among the first event organizers on the platform
- Free event listings
- Reach the South Asian community
- Build together as the platform grows''',

            'event_benefits': 'an email about the benefits of listing events on Desi Firms platform. Focus on community engagement and free exposure as platform grows',

            # Desi Firms - Real Estate (NEW PLATFORM LAUNCHING)
            'agent_invitation': '''an invitation email to real estate agents/agencies to list properties on Desi Firms.
IMPORTANT CONTEXT: Desi Firms has JUST LAUNCHED a dedicated real estate section. We are brand new.
Key points:
- We've recently built DesiFirms for the South Asian community in Australia
- Just launched a comprehensive real estate section
- Reaching out to established agencies like theirs
- Their presence would add strong value to this new platform
- Inviting them to be FOUNDING MEMBERS of this journey
- Building a trusted, community-focused real estate marketplace TOGETHER
- Completely FREE: no subscription, no credit card, no obligation
- Optional premium features with early access for founding agencies
Include simple signup steps:
1. Create account or sign up with Google
2. Access dashboard and select Real Estate
3. Register as Agent or Agency
4. Submit details for review
5. Get approved (usually 12-24 hours)
6. Start listing properties
Tone: Respectful, humble, we'd be honoured to have them join from the beginning''',

            'free_listing': '''an email emphasizing the FREE property listing opportunity on Desi Firms.
Context: NEW platform just launched. Focus on:
- Zero cost, zero obligation
- Early mover advantage as platform grows
- Community-focused real estate marketplace
- Be part of building something for South Asian community''',

            # Desi Firms - Classifieds (NEW PLATFORM)
            'classifieds_invitation': '''an invitation to post classified ads on Desi Firms.
Context: NEW platform with a classifieds section for the South Asian community.
- Free classified posting
- Community reach
- Join from the beginning as we launch''',

            # Codeteki - Sales
            'services_intro': 'an introduction email about Codeteki web development and AI-powered solutions. Focus on how AI can transform their business',
            'seo_services': 'a pitch email for Codeteki SEO services. Highlight: improved rankings, more traffic, data-driven approach',
            'sales_followup': 'a follow-up email for a previous sales outreach. Be helpful, offer value, remind of benefits',
            'proposal_followup': 'a follow-up after sending a proposal. Check interest, offer to answer questions, provide next steps',

            # Codeteki - Backlink
            'backlink_pitch': 'a backlink outreach email proposing a link partnership. Focus on mutual benefit, quality content, SEO value',
            'guest_post': 'a guest post pitch offering valuable content in exchange for a backlink. Highlight content quality and relevance',
            'backlink_followup': 'a follow-up to a previous backlink outreach. Be respectful, remind of the value proposition',

            # Codeteki - Partnership
            'partnership_intro': 'a partnership introduction email exploring collaboration opportunities. Focus on mutual benefits and synergies',
            'collaboration': 'a collaboration proposal email. Detail specific ways to work together',
            'partnership_followup': 'a follow-up to a partnership proposal. Check interest, offer to discuss further',

            # Generic
            'invitation': 'a professional invitation email',
            'followup': 'a professional follow-up email',
            'custom': 'a professional email based on the user suggestions',
        }
        email_desc = email_type_descriptions.get(email_type, 'a professional email')

        # Map tones
        tone_instructions = {
            'professional': 'Use a professional and polished tone. Be clear and confident.',
            'friendly': 'Use a warm, friendly, and conversational tone. Be approachable.',
            'formal': 'Use a formal and respectful tone. Be precise and courteous.',
            'persuasive': 'Use a persuasive tone that highlights benefits. Be compelling but not pushy.',
        }
        tone_desc = tone_instructions.get(tone, 'Be professional.')

        prompt = f"""Write {email_desc} with the following requirements:

SENDER INFORMATION:
- Company: {brand_name}
- Website: {brand_website}
- About Us: {brand_description}
- Value Proposition: {value_proposition}

PIPELINE CONTEXT:
- Pipeline: {pipeline_name if pipeline_name else 'General'}
- Category: {pipeline_type if pipeline_type else 'General outreach'}
(Use this context to tailor the email appropriately for this type of outreach)

RECIPIENT INFORMATION:
- Email: {recipient_email if recipient_email else 'Not specified'}
- Name: {recipient_name if recipient_name else 'Not specified'}
- Company: {recipient_company if recipient_company else 'Not specified'}
- Website: {recipient_website if recipient_website else 'Not specified'}

SALUTATION:
You MUST start the email body with exactly this placeholder: "{{{{SALUTATION}}}}"
This placeholder will be automatically replaced with a personalized greeting for each recipient when the email is sent.
Do NOT write an actual greeting like "Hi there," or "Hello" - use exactly {{{{SALUTATION}}}} as the first word.

TONE & STYLE:
{tone_desc}

USER SUGGESTIONS/KEY POINTS TO INCLUDE:
{suggestions if suggestions else 'No specific suggestions provided - write a general professional email.'}

Requirements:
1. IMPORTANT: Start the email body with exactly "{{{{SALUTATION}}}}" - this is a placeholder that gets personalized
2. Keep it concise (under 150 words)
3. Don't be pushy or salesy
4. Include a clear but soft call-to-action
5. Make it feel personalized, not templated
6. If recipient company info is available, reference it naturally
7. Sign off appropriately for the tone

Respond in JSON format:
{{
    "subject": "Email subject line",
    "body": "{{{{SALUTATION}}}} followed by the email content..."
}}"""

        result = self.ai_engine.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.6  # Slightly higher for more creative emails
        )

        if not result['success']:
            return {
                'subject': '',
                'body': '',
                'success': False,
                'error': result.get('error', 'AI generation failed')
            }

        # Clean up the output - remove markdown code blocks if present
        output = result['output'].strip()

        # Remove ```json ... ``` markers
        if output.startswith('```'):
            # Find the end of the first line (```json or ```)
            first_newline = output.find('\n')
            if first_newline != -1:
                output = output[first_newline + 1:]
            # Remove trailing ```
            if output.endswith('```'):
                output = output[:-3].strip()

        try:
            parsed = json.loads(output)
        except json.JSONDecodeError:
            # Try to find JSON object in the text
            import re
            json_match = re.search(r'\{[^{}]*"subject"[^{}]*"body"[^{}]*\}', output, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                except json.JSONDecodeError:
                    parsed = None

            if not parsed:
                # Fallback: try to extract from text
                lines = output.strip().split('\n')
                subject = lines[0] if lines else 'Following up'
                body = '\n'.join(lines[1:]) if len(lines) > 1 else output
                parsed = {'subject': subject, 'body': body}

        return {
            'subject': parsed.get('subject', 'Hello'),
            'body': parsed.get('body', ''),
            'success': True
        }

    def _build_deal_context(self, deal) -> str:
        """Build a context string for deal analysis."""
        from crm.models import EmailLog

        contact = deal.contact
        stage = deal.current_stage

        # Get recent email activity
        recent_emails = EmailLog.objects.filter(deal=deal).order_by('-created_at')[:5]
        email_info = []
        for email in recent_emails:
            status = []
            if email.sent_at:
                status.append(f"sent {email.sent_at.strftime('%Y-%m-%d')}")
            if email.opened:
                status.append("opened")
            if email.replied:
                status.append("replied")
            email_info.append(f"- {email.subject}: {', '.join(status) or 'draft'}")

        context_parts = [
            f"Contact: {contact.name} ({contact.email})",
            f"Company: {contact.company or 'Unknown'}",
            f"Website: {contact.website or 'Not provided'}",
            f"Contact Type: {contact.get_contact_type_display()}",
            f"Lead Score: {contact.ai_score}/100",
            "",
            f"Pipeline: {deal.pipeline.name} ({deal.pipeline.pipeline_type})",
            f"Current Stage: {stage.name if stage else 'Unknown'}",
            f"Stage Duration: {(timezone.now() - deal.stage_entered_at).days} days",
            f"Deal Status: {deal.status}",
            f"Deal Value: ${deal.value or 0}",
            "",
            f"Emails Sent: {deal.emails_sent}",
            f"Last Contact: {deal.last_contact_date.strftime('%Y-%m-%d') if deal.last_contact_date else 'Never'}",
            f"Next Action Due: {deal.next_action_date.strftime('%Y-%m-%d') if deal.next_action_date else 'Not set'}",
            "",
            "Recent Email Activity:",
            *(email_info if email_info else ["- No emails sent yet"]),
            "",
            f"AI Notes: {deal.ai_notes or 'None'}",
        ]

        return "\n".join(context_parts)
