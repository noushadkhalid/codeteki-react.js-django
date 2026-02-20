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

    SYSTEM_PROMPT = """You are an expert personal assistant specializing in business communication for two Australian brands:

**DESI FIRMS** (desifirms.com.au):
CRITICAL: Desi Firms is a BRAND NEW platform that has JUST LAUNCHED. We are NOT established.
- NEW community platform for South Asian businesses in Australia - JUST LAUNCHED
- We are BUILDING this platform and inviting businesses to JOIN from the beginning
- FREE directory - no fees, no credit card, no obligation
- Tone: Humble, warm, inviting them to be FOUNDING MEMBERS
- Key message: "We're building something new, and we'd love for you to be part of it"
- NEVER pretend we're established or can "help with their challenges" - we're ASKING them to join
- NEVER say "we understand your challenges" or "we can help you" - be HUMBLE
- Real Estate section: Just launched, inviting agents to be founding members

WHY WE BUILT THIS - RESEARCH-BACKED INITIATIVE (add as a HIGHLIGHT/BENEFIT, not a claim):
Our team researched the South Asian community in Australia and found:
- 1.6 million South Asians live in Australia (6% of population) - this is COMMUNITY SIZE
- Indian community is the second-largest migrant group in Australia
- 200,000+ Australian-born second generation now in their 20s-40s (digitally native, disposable income)
- South Asian migration is the primary driver of Australia's population growth
- NO dedicated platform existed to connect this community with businesses - THAT'S WHY we built Desi Firms

HOW TO PRESENT THIS (CRITICAL - as a highlighted benefit, not false claims):
- WRONG: "1.6 million actively searching for properties" (FALSE - they're not all searching)
- WRONG: "1.6 million looking for businesses like yours" (FALSE claim about behavior)
- WRONG: "potential customers searching" (implies they're all searching)

- RIGHT: Present as a HIGHLIGHT BOX or benefit section:
  "📊 Why We Built This:
   Our research found 1.6 million South Asians in Australia - a thriving community with no dedicated platform.
   That's the gap we're filling."

- RIGHT: "Built on research: 1.6M strong community, zero dedicated platforms - until now"
- RIGHT: "Our research showed a clear gap in the market - that's why we created Desi Firms"

NEVER claim people are "actively searching" or "looking for" - just state the community exists and has no platform

**CODETEKI** (codeteki.au):
- Established digital agency offering AI-powered web solutions, SEO, development
- Target: Businesses needing websites, SEO, AI automation
- Tone: Professional, confident, consultative (like a trusted advisor)
- Key message: "We help businesses solve real problems with smart technology"

YOUR APPROACH FOR CODETEKI:
- Lead with THEIR problem, not our solution - show you understand their world
- Be specific: "Most [industry] businesses struggle with [specific problem]..."
- Quantify value when possible: "save hours", "increase leads", "reduce manual work"
- Use conversational confidence, not corporate speak
- Ask thought-provoking questions: "When was the last time you got a lead from your website?"
- Make the next step easy and low-commitment: "quick chat", "15-minute call", "just reply"
- AVOID: generic phrases, feature lists, buzzwords without context
- GOOD opener: "I noticed [specific observation about their business]..."
- BAD opener: "I hope this email finds you well..."

YOUR APPROACH FOR DESI FIRMS:
- Be HUMBLE - we're a new platform asking for their cooperation
- Emphasize: FREE, founding member, building together, part of from beginning
- NEVER sound like we're doing them a favor - THEY would be adding value to US
- Say things like: "We'd be honored to have you" NOT "We can help you"
- Keep it genuine, friendly, and non-pushy

CRITICAL RULES:
1. NEVER mention specific prices in emails (say "FREE" or "affordable plans")
2. NEVER be salesy - be genuinely helpful
3. For Desi Firms: NEVER pretend to be established - we are NEW and BUILDING
4. Personalize based on available context
5. Include soft but clear calls-to-action
6. NEVER use phrases like "I hope this finds you well" - too generic"""

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

    def analyze_deal(self, deal, engagement_profile=None) -> dict:
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
        context = self._build_deal_context(deal, engagement_profile=engagement_profile)

        # Build engagement-aware instructions
        engagement_instructions = ""
        if engagement_profile:
            engagement_instructions = f"""
CRITICAL - ENGAGEMENT-AWARE DECISIONS:
- Engagement Tier: {engagement_profile.tier.upper()}
- Open Rate: {engagement_profile.open_rate:.0%} ({engagement_profile.total_opened}/{engagement_profile.total_sent}) after {engagement_profile.total_sent} emails
- Consecutive Unopened: {engagement_profile.consecutive_unopened}
- Burnout Risk: {'YES' if engagement_profile.is_burnout_risk else 'No'}
- System Recommendation: {engagement_profile.recommended_action}

ENGAGEMENT RULES (follow these strictly):
1. If open rate is 0% after 2+ emails → suggest 'change_approach' or 'pause', NOT another similar email
2. If they opened but didn't reply → try a different angle, shorter email, or stronger CTA
3. If burnout risk is detected → recommend 'wait' with 5-7 days
4. NEVER suggest sending another similar email to someone who hasn't opened any
5. If tier is 'engaged' or 'hot' → be more responsive, shorter wait times
6. If tier is 'cold' → suggest changing subject line approach or wait longer
"""

        prompt = f"""Analyze this deal and recommend the next action.

DEAL CONTEXT:
{context}
{engagement_instructions}
Based on the deal's current state, what should we do next?

Consider:
1. How long has it been since last contact?
2. What stage is the deal in?
3. Have we sent emails? Were they opened/replied?
4. What is the contact's engagement level?
5. ENGAGEMENT DATA: Use the engagement profile above to make smarter decisions.

Respond in JSON format:
{{
    "action": "send_email" | "move_stage" | "wait" | "change_approach" | "flag_for_review" | "pause",
    "reasoning": "Brief explanation of why this action",
    "suggested_stage": "If action is move_stage, which stage name",
    "email_type": "If action is send_email, what type: initial, followup_1, followup_2, custom",
    "wait_days": "If action is wait or change_approach, how many days to wait"
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

    def compose_email(self, deal, template: Optional[str] = None, context: dict = None, engagement_profile=None) -> dict:
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
        sender_name = 'Noushad'
        sender_company = brand.name if brand else 'Codeteki'
        company_description = brand.ai_company_description if brand else 'a digital agency specializing in AI-powered web solutions and SEO services'
        value_proposition = brand.ai_value_proposition if brand else 'helping businesses grow their online presence through cutting-edge technology'

        # Brand-specific signature
        if brand and ('desi' in brand.name.lower() or 'desifirms' in brand.slug.lower()):
            email_signature = """Noushad
Desi Firms
📱 0424 538 777
🌐 https://desifirms.com.au/"""
        else:
            email_signature = """Noushad
Codeteki Digital Services
📱 0424 538 777
🌐 https://codeteki.au/"""

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

        # Engagement-aware instructions for AI
        engagement_context = ""
        if engagement_profile:
            engagement_context = f"""
ENGAGEMENT CONTEXT (USE THIS TO TAILOR YOUR EMAIL):
- This contact has received {engagement_profile.total_sent} emails so far
- Open rate: {engagement_profile.open_rate:.0%}
- They {'have opened' if engagement_profile.total_opened > 0 else 'have NOT opened'} previous emails
- {'They clicked a link' if engagement_profile.total_clicked > 0 else 'No link clicks'}
- Engagement tier: {engagement_profile.tier}

SMART ADAPTATION:
- If they haven't opened: Try a COMPLETELY DIFFERENT subject line approach
- If they opened but didn't reply: They're interested but not convinced - add more value
- If they clicked: They're warm - be more direct with CTA
"""

        # Brand-specific instructions
        is_desi_firms = brand and ('desi' in brand.name.lower() or 'desifirms' in brand.slug.lower())
        is_real_estate = deal.pipeline.pipeline_type == 'real_estate'

        if is_desi_firms and is_real_estate:
            brand_instructions = """
CRITICAL BRAND CONTEXT - DESI FIRMS REAL ESTATE:
Desi Firms is a BRAND NEW platform that has JUST LAUNCHED. We are NOT established.

WHY WE BUILT THIS (present as a HIGHLIGHT/BENEFIT section, not false claims):
Our team's research found:
- 1.6 million South Asians in Australia - a thriving community
- 200,000+ second generation now in their 20s-40s - many entering the property market
- NO dedicated real estate platform existed for this community - that's the gap
- Many in this community prefer agents who understand their cultural needs

FRAMING (CRITICAL - avoid false claims about behavior):
- WRONG: "1.6 million searching for properties" (FALSE - not all searching)
- WRONG: "1.6 million potential customers searching for agents" (FALSE claim)
- WRONG: "actively searching" or "actively looking" (implies behavior we can't prove)

- RIGHT: Add as a highlighted benefit section:
  "📊 Built on Research: 1.6M South Asians in Australia, no dedicated real estate platform - until now."
- RIGHT: "Our research showed a gap - that's why we built this"
- RIGHT: "A community of 1.6 million with no dedicated platform to connect with agents"

TONE & MESSAGING RULES:
- We are HUMBLY INVITING them to join as FOUNDING MEMBERS
- We are BUILDING something new for the South Asian community
- THEY would add value to US, not the other way around
- Completely FREE - no fees, no credit card, no obligation
- NEVER say "I hope this finds you well" - too generic
- NEVER say "we understand your challenges" - too presumptuous
- NEVER say "we can help you" - we're ASKING for their cooperation
- NEVER pretend to be an established platform

GOOD PHRASES TO USE:
- "We've just launched a dedicated real estate section..."
- "We're building something new for the South Asian community..."
- "Our research found a gap: 1.6 million South Asians in Australia with no dedicated real estate platform"
- "We saw this gap and built a real estate section to fill it"
- "We'd love for [Company] to be part of it from the beginning"
- "We'd be honored to have you as a founding member"
- "It's completely FREE - no subscription, no credit card"
- Include a highlight: "📊 Built on Research: 1.6M community, zero dedicated platforms - until now"

NEVER SAY:
- "1.6 million searching for property" (FALSE)
- "actively looking for agents" (FALSE)
- "potential customers searching" (FALSE)

BAD PHRASES - NEVER USE:
- "I hope this message finds you well"
- "We understand your challenges"
- "We can help you reach your target audience"
- "Our platform offers tools to help you"
- Any language that sounds like we're established or doing them a favor

FOR FOLLOW-UPS:
- Keep it short (under 80 words)
- Acknowledge they're busy
- Gentle reminder about the FREE opportunity
- Don't repeat all the stats - just reference "the growing community"
- No pressure, just checking if they had questions"""
        elif is_desi_firms:
            brand_instructions = """
CRITICAL BRAND CONTEXT - DESI FIRMS:
Desi Firms is a NEW platform, not established. We're inviting businesses to JOIN from the beginning.
- Tone: Humble, warm, community-focused
- Emphasize: FREE listing, founding member opportunity, building together
- NEVER pretend to be established or say "we can help you"
- Be genuine and inviting, not salesy

WHY WE BUILT THIS (present as a HIGHLIGHT, not false claims):
- Our research found 1.6 million South Asians in Australia - a community with no dedicated platform
- Second generation (200,000+) in their 20s-40s - digitally native
- No platform existed for this community - that's the gap we're filling

AVOID FALSE CLAIMS:
- WRONG: "1.6 million searching for businesses" or "actively looking"
- WRONG: "potential customers with nowhere to search" (implies they're all searching)
- RIGHT: Add as highlight: "📊 Built on research: 1.6M community, no dedicated platform - we're changing that" """
        else:
            brand_instructions = """
BRAND CONTEXT - CODETEKI:
Established Australian digital agency specializing in AI-powered business solutions.

WRITING APPROACH:
1. OPEN with a specific observation about THEIR business (website, online presence, industry)
2. IDENTIFY a likely pain point they face (based on their industry/size)
3. BRIDGE to how we've helped similar businesses
4. OFFER low-commitment next step

TONE & STYLE:
- Consultative and confident (like a trusted advisor, not a salesperson)
- Conversational but professional
- Specific > Generic (mention their company name, industry, observed details)
- Short paragraphs, easy to scan

COMPELLING TECHNIQUES:
- Use "you" more than "we" (focus on them)
- Ask a thought-provoking question early
- Include a subtle proof point: "We recently helped a [similar business] achieve [result]"
- Make the CTA feel easy: "Just reply" or "Quick 15-min chat"

AVOID:
- "I hope this finds you well" - too generic
- Long feature lists - focus on outcomes
- Pushy language - be helpful, not desperate
- Jargon without explanation"""

        prompt = f"""Write a professional {email_type} email for this {deal.pipeline.pipeline_type} campaign.
{brand_instructions}

SENDER INFORMATION:
- Sender Name: {sender_name}
- Company: {sender_company}

RECIPIENT INFORMATION:
- Name: {contact.name}
- Company: {contact.company or 'Unknown'}
- Website: {contact.website or 'Not available'}

CAMPAIGN CONTEXT:
- Pipeline: {deal.pipeline.name}
- Current Stage: {deal.current_stage.name if deal.current_stage else 'Initial'}
- Emails Already Sent: {deal.emails_sent}
- AI Notes: {deal.ai_notes or 'None'}

{f'TEMPLATE TO PERSONALIZE:{chr(10)}{template}' if template else ''}
{engagement_context}
Requirements:
1. Keep it concise (under 100 words for initial, under 80 for follow-ups)
2. Follow the brand tone guidelines above STRICTLY
3. Include a soft call-to-action
4. Don't be pushy or salesy
5. NEVER use placeholder text like [Your Name], [Contact], [Your Position] - use real values
6. End with this EXACT signature (copy exactly, including emojis) - DO NOT DUPLICATE:

Warm regards,

{email_signature}

CRITICAL:
- Copy the signature EXACTLY as shown above - ONLY ONCE at the end
- DO NOT add a second signature
- DO NOT add anything after the signature

Respond in JSON format:
{{
    "subject": "Email subject line",
    "body": "Email body text ending with the signature above (NOT duplicated)"
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
        # New context fields for smarter AI
        business_updates = context.get('business_updates', '')  # Recent news/updates to mention
        target_context = context.get('target_context', '')  # Who we're targeting and why
        approach_style = context.get('approach_style', 'problem_solving')  # How to approach

        # Generate smart salutation based on email/name/company
        smart_salutation = self.get_smart_salutation(
            email=recipient_email,
            name=recipient_name,
            company=recipient_company
        )

        # Map email types to descriptions
        email_type_descriptions = {
            # Desi Firms - Business Listings (NEW PLATFORM LAUNCHING)
            'directory_invitation': '''an INTRO PARAGRAPH ONLY for a business directory invitation email.
IMPORTANT: This is a HYBRID template - the template already has Benefits box, CTA button, and Signature.
You are ONLY writing the opening intro. DO NOT include signature, benefits list, or CTA.

CONTEXT:
- Desi Firms = Community platform for South Asian BUSINESSES in Australia
- This is a NEW platform we just launched

WRITE THIS EXACT STRUCTURE:

{{SALUTATION}}

We've just launched Desi Firms, a community platform dedicated to connecting South Asian businesses in Australia, and we'd love to invite [Company Name] to be among our founding members.

📊 **Why We Built This**
Our research found that Australia's 1.6 million-strong South Asian community - with a growing second generation now in their 20s-40s - has no dedicated platform to discover local businesses. We're building that bridge.

As a founding member, you'll be part of something new from day one - completely free, no strings attached.

---

CRITICAL RULES:
- Keep the 📊 **Why We Built This** section VISIBLE (not buried in paragraph)
- Mention their company name if available
- DO NOT add signature, benefits list, or CTA - template has those
- DO NOT claim people are "searching" or "looking" - just state the community exists''',

            'listing_benefits': '''an INTRO PARAGRAPH ONLY for a business listing benefits email.
IMPORTANT: This is a HYBRID template - the template already has Benefits box, CTA button, and Signature.
You are ONLY writing the opening intro. DO NOT include signature, benefits list, or CTA.

CONTEXT:
- Desi Firms = Community platform for South Asian BUSINESSES in Australia
- This is a NEW platform - emphasize the FREE listing opportunity

WRITE THIS EXACT STRUCTURE:

{{SALUTATION}}

We'd love to invite [Company Name] to join Desi Firms, a new community platform for South Asian businesses in Australia. Listing is completely FREE - no hidden fees, no credit card required.

📊 **Why We Built This**
Our research found that Australia's 1.6 million-strong South Asian community has no dedicated platform to discover local businesses like yours. We're changing that, and we'd be honored to have you as a founding member.

---

CRITICAL RULES:
- Keep the 📊 **Why We Built This** section VISIBLE
- Emphasize FREE listing
- DO NOT add signature, benefits list, or CTA - template has those
- DO NOT claim people are "searching" - just state the community exists with no platform''',

            'invitation_followup': '''a SHORT follow-up message ONLY (no signature - template has one).
HYBRID TEMPLATE: Just write the follow-up message, template handles CTA and signature.

Write 2-3 short paragraphs:
1. Acknowledge they're busy, follow up on previous invite
2. Brief reminder: FREE listing, founding member opportunity
3. Subtle mention of "growing community" or "first dedicated platform"

Keep it under 80 words. Friendly, not pushy.
DO NOT include signature, CTA, or benefits list.''',

            'onboarding_help': 'a helpful email offering assistance with setting up their business listing. Be supportive and offer step-by-step help',

            # Business Directory Follow-ups
            'directory_followup_1': '''a follow-up message ONLY for business directory (no signature - template has one).
HYBRID TEMPLATE: Just write the follow-up message, template handles reminder box, CTA, and signature.

WRITE THIS STRUCTURE:

{{SALUTATION}}

Quick follow-up on our invitation to list your business on Desi Firms. I know you're busy, so I'll keep this brief.

📊 **The Opportunity**
Our research shows 1.6 million South Asians live in Australia with no dedicated business directory - we're building that. With a growing second-generation community now in their 20s-40s, there's real demand.

As a founding member, you'd be among the first businesses featured on the platform.

---

CRITICAL RULES:
- Keep the 📊 **The Opportunity** section VISIBLE
- Acknowledge they're busy, be respectful
- Don't promise "free" - focus on the opportunity
- DO NOT include signature, CTA, or benefits list - template has those
- Keep it under 100 words total''',

            'directory_followup_2': '''a SECOND follow-up / quick reminder message for business directory (no signature - template has one).
HYBRID TEMPLATE: Just write the message, template handles benefits box, CTA, and signature.

WRITE THIS STRUCTURE:

{{SALUTATION}}

Quick reminder about listing your business on Desi Firms.

📊 **Why Desi Firms?**
- Australia's South Asian community platform - a growing market
- Get discovered by customers looking for local businesses
- Direct inquiries from interested customers

I know you're busy, but didn't want you to miss this opportunity.

---

CRITICAL RULES:
- Keep the 📊 section factual (don't claim "1.6M actively looking")
- Don't promise "free" - just mention the opportunity
- Be friendly, not pushy
- DO NOT include signature, CTA, or benefits box - template has those
- Keep it under 80 words total''',

            'directory_followup_3': '''a CLOSING THE LOOP message for businesses - this is the LAST email before we stop contacting them.
HYBRID TEMPLATE: Just write a brief farewell message. Template handles "save this email" box with reply instructions, CTA, and signature.

WRITE THIS STRUCTURE:

{{SALUTATION}}

Just closing the loop on my previous emails about listing your business on Desi Firms.

I don't want to keep filling your inbox. This will be my last message.

Wishing you continued success with your business!

---

CRITICAL RULES:
- Keep it SHORT (under 50 words)
- Be respectful and warm
- Acknowledge this is the last email
- End with a positive wish (NOT "just reply" - template box has that)
- DO NOT include signature, CTA, or "save this email" message - template has those''',

            # Desi Firms - Events (NEW PLATFORM)
            'event_invitation': '''an INTRO PARAGRAPH ONLY for an events invitation email.
HYBRID TEMPLATE: Template already has Benefits box, CTA button, and Signature.
You ONLY write the intro. DO NOT include signature, benefits, or CTA.

CONTEXT:
- Desi Firms = Community platform with an Events section
- Events is a NEW section we just launched

WRITE THIS STRUCTURE:

{{SALUTATION}}

We've just launched an Events section on Desi Firms, our community platform for South Asian businesses in Australia, and we'd love to invite [Company/Organizer Name] to list your events with us.

📊 **Why We Built This**
Our research found that Australia's 1.6 million-strong South Asian community has no dedicated platform to discover local events. We're building that, and we'd be honored to have you as a founding event partner.

---

CRITICAL RULES:
- Keep the 📊 **Why We Built This** section VISIBLE
- DO NOT add signature, benefits list, or CTA - template has those
- Mention their company/organization name if available''',

            'event_benefits': '''an email about the benefits of listing events on Desi Firms platform.
WHY WE BUILT THIS (highlight section):
Our research shows:
- 1.6 million South Asians in Australia - a vibrant community
- Second generation digitally native, use online platforms
- Growing interest from wider Australian community in South Asian events
- No dedicated events platform existed - we're filling that gap

AVOID: "searching for events" or "looking for events" (false claims about behavior)
RIGHT: "A community of 1.6 million with no dedicated events platform - until now"

Focus on: free exposure, founding member status, being part of something new for the community''',

            # Events Follow-ups
            'events_followup_1': '''a follow-up message ONLY for event organizers (no signature - template has one).
HYBRID TEMPLATE: Just write the follow-up message, template handles CTA and signature.

WRITE THIS STRUCTURE:

{{SALUTATION}}

Quick follow-up on our invitation to list your events on Desi Firms. I know you're busy, so I'll keep this brief.

📊 **The Opportunity**
Australia's 1.6 million South Asians have no dedicated platform to discover community events - we're building that. With a growing second-generation now in their 20s-40s, there's real demand for cultural and community events.

As a founding event partner, you'd be among the first to connect with this community.

---

CRITICAL RULES:
- Keep the 📊 **The Opportunity** section VISIBLE
- Acknowledge they're busy, be respectful
- Don't promise "free" - focus on the founding partner opportunity
- DO NOT include signature or CTA - template has those
- Keep it under 100 words total''',

            'events_followup_2': '''a SECOND follow-up / quick reminder message for event organizers (no signature - template has one).
HYBRID TEMPLATE: Just write the message, template handles benefits box, CTA, and signature.

WRITE THIS STRUCTURE:

{{SALUTATION}}

Quick reminder about listing your events on Desi Firms.

📊 **Why Desi Firms?**
- Australia's South Asian community platform - a growing market
- Connect with people looking for community and cultural events
- Direct inquiries from interested attendees

I know you're busy, but didn't want you to miss this opportunity.

---

CRITICAL RULES:
- Keep the 📊 section factual (don't claim "1.6M looking for events")
- Don't promise "free" - just mention the opportunity
- Be friendly, not pushy
- DO NOT include signature, CTA, or benefits box - template has those
- Keep it under 80 words total''',

            'events_followup_3': '''a CLOSING THE LOOP message for event organizers - this is the LAST email before we stop contacting them.
HYBRID TEMPLATE: Just write a brief farewell message. Template handles "save this email" box with reply instructions, CTA, and signature.

WRITE THIS STRUCTURE:

{{SALUTATION}}

Just closing the loop on my previous emails about listing your events on Desi Firms.

I don't want to keep filling your inbox. This will be my last message.

Wishing you great success with your upcoming events!

---

CRITICAL RULES:
- Keep it SHORT (under 50 words)
- Be respectful and warm
- Acknowledge this is the last email
- End with a positive wish (NOT "just reply" - template box has that)
- DO NOT include signature, CTA, or "save this email" message - template has those''',

            # Desi Firms - Real Estate (NEW PLATFORM LAUNCHING)
            'agent_invitation': '''an INTRO PARAGRAPH ONLY for a real estate invitation email.
IMPORTANT: This is a HYBRID template - the template already has Benefits, Steps, CTA and Signature.
You are ONLY writing the opening intro. DO NOT include signature, steps, or benefits.

CONTEXT:
- Desi Firms = Community platform for South Asian BUSINESSES in Australia
- Real Estate = NEW SECTION we just added (one part of the platform)

WRITE THIS EXACT STRUCTURE (copy the format, personalize the content):

{{SALUTATION}}

We've just launched a dedicated real estate section on Desi Firms, our community platform for South Asian businesses in Australia, and we'd love to invite [Company Name] to be among our founding members.

📊 **Why We Built This**
Our research found that Australia's 1.6 million-strong South Asian community - with 200,000+ second-generation members now entering the property market - has no dedicated platform to connect with real estate professionals. We're building that bridge.

As a founding member, you'll have the opportunity to connect with this growing community from day one - completely free, no strings attached.

---

OPTIONAL: If the recipient appears to be an established agent/agency, briefly mention that they can import their entire portfolio from any CRM in under 2 minutes via CSV Bulk Import. Keep it to one sentence.

CRITICAL RULES:
- Keep the 📊 **Why We Built This** section as a VISIBLE HIGHLIGHT (not buried in paragraph)
- Mention their company name if available
- Keep it warm but professional
- DO NOT add signature, steps, or benefits - template has those
- The research stats should stand out visually''',

            'agent_followup_1': '''a follow-up message ONLY for real estate agents (no signature - template has one).
HYBRID TEMPLATE: Just write the follow-up message, template handles reminder box, CTA, and signature.

WRITE THIS STRUCTURE:

{{SALUTATION}}

Quick follow-up on our invitation to join Desi Firms' real estate section. I know you're busy, so I'll keep this brief.

📊 **The Opportunity**
Our research shows 1.6 million South Asians live in Australia with no dedicated property platform - and a growing second-generation is now entering the property market. We built this to fill that gap.

As a founding member, you'd be among the first agents to connect with this community.

---

OPTIONAL: If relevant, briefly mention our new CSV Bulk Import feature - they can import their entire portfolio from AgentBox, Rex, VaultRE or any CRM in under 2 minutes. This can be a compelling re-engagement hook. Keep it to one sentence.

CRITICAL RULES:
- Keep the 📊 **The Opportunity** section VISIBLE (not buried)
- Acknowledge they're busy, be respectful of their time
- Don't promise "free" - focus on the opportunity
- DO NOT include signature, CTA, or reminder box - template has those
- Keep it under 100 words total''',

            'agent_followup_2': '''a SECOND follow-up / quick reminder message for real estate agents (no signature - template has one).
HYBRID TEMPLATE: Just write the message, template handles benefits box, CTA, and signature.

WRITE THIS STRUCTURE:

{{SALUTATION}}

Quick reminder about listing your properties on Desi Firms.

📊 **Why Desi Firms?**
- Australia's South Asian community platform - a growing market
- No dedicated property platform for this community until now
- Direct inquiries from interested buyers

I know you're busy, but didn't want you to miss being a founding member.

---

CRITICAL RULES:
- Keep the 📊 section factual (don't claim "1.6M actively looking for properties")
- Don't promise "free" or "unlimited" - just mention the opportunity
- Be friendly, not pushy
- DO NOT include signature, CTA, or benefits box - template has those
- Keep it under 80 words total''',

            'agent_followup_3': '''a CLOSING THE LOOP message for real estate agents - this is the LAST email before we stop contacting them.
HYBRID TEMPLATE: Just write a brief farewell message. Template handles new feature box, "save this email" box, CTA, and signature.

WRITE THIS STRUCTURE:

{{SALUTATION}}

Just a quick note to close the loop on my previous emails about listing properties on Desi Firms.

I know you're busy, and I don't want to keep filling your inbox. This will be my last message - but one thing has changed: we've added CSV Bulk Import so you can bring your entire portfolio from any CRM in under 2 minutes.

Wishing you continued success with your real estate business!

---

CRITICAL RULES:
- Keep it SHORT (under 60 words)
- Be respectful and warm
- Acknowledge this is the last email
- Briefly mention CSV Bulk Import as something new since last contact
- End with a positive wish (NOT "just reply" - template box has that)
- DO NOT include signature, CTA, or "save this email" message - template has those''',

            'realestate_followup_3': '''a CLOSING THE LOOP message for real estate agents - this is the LAST email before we stop contacting them.
HYBRID TEMPLATE: Just write a brief farewell message. Template handles new feature box, "save this email" box, CTA, and signature.

WRITE THIS STRUCTURE:

{{SALUTATION}}

Just closing the loop on my previous emails about listing properties on Desi Firms.

I don't want to keep filling your inbox. This will be my last message - but one thing has changed: we've added CSV Bulk Import so you can bring your entire portfolio from any CRM in under 2 minutes.

Wishing you continued success with your real estate business!

---

CRITICAL RULES:
- Keep it SHORT (under 60 words)
- Be respectful and warm
- Acknowledge this is the last email
- Briefly mention CSV Bulk Import as something new since last contact
- End with a positive wish (NOT "just reply" - template box has that)
- DO NOT include signature, CTA, or "save this email" message - template has those''',

            'agent_responded': '''a thank you email after a real estate agent responds positively.
Context: They showed interest in listing on Desi Firms.
Key points:
- Thank them for their response
- Provide clear next steps for registration
- Offer to help with any questions
- Be warm and welcoming
Tone: Excited, helpful, welcoming''',

            'agent_registered': '''a welcome email after a real estate agent has registered on Desi Firms.
Context: They've created an account and registered as an agent/agency.
Key points:
- Welcome them to the platform
- Guide them on listing their first property
- Mention available features
- Offer support if needed
Tone: Warm, helpful, encouraging''',

            'realestate_registered': '''a WELCOME MESSAGE ONLY for a real estate agent who just registered.
HYBRID TEMPLATE: Template already has Getting Started box, CTA buttons, and Signature.
You ONLY write the welcome/greeting paragraph.

Write 2-3 short paragraphs:
1. Warm welcome, congratulate them on registering
2. Thank them for joining as a founding member
3. Brief mention they can start adding properties right away - either one-by-one or by importing via CSV

DO NOT include signature, steps, CTA, or getting started instructions - template has those.
Keep it personal and warm, under 80 words.''',

            'business_signedup': '''a WELCOME MESSAGE ONLY for a business owner who just signed up.
HYBRID TEMPLATE: Template already has Complete Your Listing box, CTA buttons, and Signature.
You ONLY write the welcome/greeting paragraph.

Write 2-3 short paragraphs:
1. Warm welcome, congratulate them on creating their account
2. Thank them for being a founding member
3. Express excitement about featuring their business

DO NOT include signature, steps, CTA, or listing instructions - template has those.
Keep it personal and warm, under 80 words.''',

            'events_signedup': '''a WELCOME MESSAGE ONLY for an event organizer who just signed up.
HYBRID TEMPLATE: Template already has Create Your Event box, CTA buttons, and Signature.
You ONLY write the welcome/greeting paragraph.

Write 2-3 short paragraphs:
1. Warm welcome, congratulate them on joining
2. Thank them for being a founding event partner
3. Express excitement about their upcoming events

DO NOT include signature, steps, CTA, or event instructions - template has those.
Keep it personal and warm, under 80 words.''',

            'realestate_listing': '''a CONGRATULATIONS MESSAGE ONLY for an agent who listed their first property.
HYBRID TEMPLATE: Template already has Pro Tips box, CTA buttons, and Signature.
You ONLY write the congratulatory message.

Write 2-3 short paragraphs:
1. Celebrate their first listing - this is a milestone!
2. Thank them for being active on the platform
3. Brief mention of their property being visible to the community

DO NOT include signature, tips, CTA, or next steps - template has those.
Keep it celebratory and encouraging, under 80 words.''',

            'business_listed': '''a CONGRATULATIONS MESSAGE ONLY for a business that went live on the platform.
HYBRID TEMPLATE: Template already has Tips for Success box, CTA buttons, and Signature.
You ONLY write the congratulatory message.

Write 2-3 short paragraphs:
1. Celebrate their business going live!
2. Thank them for completing their listing
3. Brief mention of being part of the community now

DO NOT include signature, tips, CTA, or suggestions - template has those.
Keep it celebratory and encouraging, under 80 words.''',

            'events_listed': '''a CONGRATULATIONS MESSAGE ONLY for an organizer who listed their first event.
HYBRID TEMPLATE: Template already has Tips for Maximum Reach box, CTA buttons, and Signature.
You ONLY write the congratulatory message.

Write 2-3 short paragraphs:
1. Celebrate their event going live!
2. Thank them for sharing with the community
3. Brief mention of reaching the South Asian community

DO NOT include signature, tips, CTA, or promotion suggestions - template has those.
Keep it celebratory and encouraging, under 80 words.''',

            'business_nudge': '''a GENTLE INTRO ONLY for a nudge email to complete their listing.
HYBRID TEMPLATE: Template already has Benefits box, CTA, and Signature.
You ONLY write the intro message.

Write 2-3 short paragraphs:
1. Friendly check-in about their account
2. Gentle reminder about FREE listing opportunity
3. We'd love to have their business featured

DO NOT include signature, benefits, CTA - template has those.
Keep it friendly and non-pushy, under 80 words.''',

            'business_nudge2': '''a SHORT FOLLOW-UP ONLY for final nudge to complete listing.
HYBRID TEMPLATE: Template already has What You're Missing box, CTA, and Signature.
You ONLY write the follow-up message.

Write 2 short paragraphs:
1. Quick follow-up, acknowledge they're busy
2. Final gentle mention of the opportunity

DO NOT include signature, benefits, or CTA - template has those.
Keep it brief and respectful, under 60 words.''',

            'realestate_nudge': '''a GENTLE INTRO ONLY for a nudge email to real estate agents.
HYBRID TEMPLATE: Template already has What You Can Do box, Stats, CTA, and Signature.
You ONLY write the intro message.

Write 2-3 short paragraphs:
1. Friendly check-in about their account registration
2. Mention it's easier than they think - they can import their entire property portfolio from any CRM in under 2 minutes via CSV
3. We'd love to have them listing properties

DO NOT include signature, features, CTA - template has those.
Keep it friendly and non-pushy, under 80 words.''',

            'realestate_nudge2': '''a SHORT FOLLOW-UP ONLY for final nudge to real estate agents.
HYBRID TEMPLATE: Template already has Quick Steps box, CTA, and Signature.
You ONLY write the follow-up message.

Write 2 short paragraphs:
1. Quick follow-up, acknowledge they're busy
2. Final gentle mention - they can import from AgentBox, Rex or any CRM in minutes, no manual entry needed

DO NOT include signature, steps, or CTA - template has those.
Keep it brief and respectful, under 60 words.''',

            'events_nudge': '''a GENTLE INTRO ONLY for a nudge email to event organizers.
HYBRID TEMPLATE: Template already has Why List Events box, CTA, and Signature.
You ONLY write the intro message.

Write 2-3 short paragraphs:
1. Friendly check-in about listing events
2. Gentle reminder about FREE event promotion
3. We'd love to feature their events

DO NOT include signature, benefits, CTA - template has those.
Keep it friendly and non-pushy, under 80 words.''',

            'events_nudge2': '''a SHORT FOLLOW-UP ONLY for final nudge to event organizers.
HYBRID TEMPLATE: Template already has Quick Benefits box, CTA, and Signature.
You ONLY write the follow-up message.

Write 2 short paragraphs:
1. Quick follow-up, acknowledge they're busy
2. Final gentle mention of free event listing

DO NOT include signature, benefits, or CTA - template has those.
Keep it brief and respectful, under 60 words.''',

            'directory_responded': '''a THANK YOU MESSAGE ONLY for a business that responded positively.
HYBRID TEMPLATE: Template already has Next Steps box, CTA, and Signature.
You ONLY write the thank you message.

Write 2-3 short paragraphs:
1. Thank them warmly for their response
2. Express excitement about having them join
3. Brief mention of next steps coming

DO NOT include signature, steps, or CTA - template has those.
Keep it warm and welcoming, under 80 words.''',

            'events_responded': '''a THANK YOU MESSAGE ONLY for an event organizer who responded positively.
HYBRID TEMPLATE: Template already has Next Steps box, CTA, and Signature.
You ONLY write the thank you message.

Write 2-3 short paragraphs:
1. Thank them warmly for their interest
2. Express excitement about their events
3. Brief mention of next steps coming

DO NOT include signature, steps, or CTA - template has those.
Keep it warm and welcoming, under 80 words.''',

            'agent_listing': '''a congratulations email after a real estate agent lists their first property.
Context: They've successfully listed at least one property.
Key points:
- Congratulate them on their first listing
- Share tips for getting more visibility
- Mention upcoming features
- Thank them for being a founding member
Tone: Celebratory, supportive''',

            'free_listing': '''an email emphasizing the FREE property listing opportunity on Desi Firms.
Context: NEW platform just launched.

WHY WE BUILT THIS (include as highlight):
Our research found:
- 1.6 million South Asians in Australia - a large, growing community
- Second generation (200,000+) now entering property market as first-time buyers
- No dedicated real estate platform existed for this community

AVOID FALSE CLAIMS:
- WRONG: "buyers looking for agents" or "searching for agents"
- RIGHT: "A community of 1.6 million with no dedicated real estate platform"

FOCUS ON:
- Zero cost, zero obligation - completely FREE
- Early mover advantage on a new platform
- Community-focused real estate marketplace
- Be part of building something the community has needed
- Connect with a community that had no dedicated platform before''',

            # Desi Firms - Classifieds (NEW PLATFORM)
            'classifieds_invitation': '''an invitation to post classified ads on Desi Firms.
Context: NEW platform with a classifieds section for the South Asian community.
- Free classified posting
- Community reach
- Join from the beginning as we launch''',

            # Codeteki - Sales
            'services_intro': '''an introduction email about Codeteki's AI-powered business solutions.
APPROACH:
- Open with a specific observation about their website or online presence
- Identify a likely pain point: outdated website, no leads from online, manual processes eating time
- Ask a thought-provoking question: "When was the last time your website brought in a new customer?"
- Position AI as the differentiator: "What if your website could answer customer questions 24/7?"
- Offer a free, no-obligation consultation or website audit
KEY POINTS TO WEAVE IN:
- AI chatbots that handle inquiries while they sleep
- Modern websites that actually convert visitors
- Automation that saves hours of manual work
- Data-driven decisions, not guesswork
CTA: Quick 15-minute discovery call or "just reply with questions"
Tone: Consultative expert, genuinely curious about their business''',

            'seo_services': '''a pitch email for Codeteki SEO services.
APPROACH:
- Open with something specific: "I searched for [their service] in [their area] and noticed..."
- Paint the problem: competitors showing up first, missing out on ready-to-buy customers
- Offer proof: "We helped a [similar business] go from page 3 to position 1 in 4 months"
- Make it tangible: "That's X more people finding you every month"
KEY POINTS:
- Technical SEO audit (what's broken under the hood)
- Local SEO (Google Maps, "near me" searches)
- Content strategy (ranking for searches your customers actually make)
- No fluff metrics - focus on leads and revenue
CTA: Free SEO audit or quick call to discuss opportunities
Tone: Data-driven expert who speaks in results, not jargon''',

            'sales_followup': '''a follow-up email for a previous outreach.
APPROACH:
- Acknowledge you reached out before (briefly, no guilt)
- Add NEW value: share a tip, insight, or observation about their industry
- Re-state the core benefit in a fresh way
- Make it easy to respond
STRUCTURE:
1. "I reached out last week about [topic]"
2. "I was thinking about [their company] and noticed [new observation or tip]"
3. "If [pain point] is something you're dealing with, I'd love to share how we've helped others"
4. "No pressure - just reply if you'd like to chat"
Keep it SHORT - under 100 words. Respect their time.''',

            'proposal_followup': '''a follow-up after sending a proposal.
APPROACH:
- Warm, not pushy - they're probably busy
- Offer to clarify anything in the proposal
- Subtly remind of the main benefit/outcome
- Provide an easy next step
STRUCTURE:
1. "Just checking in on the proposal I sent for [project]"
2. "Happy to jump on a quick call if you have questions about [specific section]"
3. "We're excited about the potential to help [their company] achieve [main goal]"
4. "What works best for a 15-minute chat this week?"
Tone: Helpful and patient, not desperate''',

            # Codeteki - Backlink
            'backlink_pitch': '''a backlink outreach email proposing a link partnership.
APPROACH:
- Compliment something SPECIFIC about their content (show you actually read it)
- Explain WHY your content would add value for their readers
- Make it mutually beneficial - not just asking for a favor
- Be brief and respectful of their time
STRUCTURE:
1. "I came across your article on [topic] and really appreciated [specific point]"
2. "We recently published [content] that expands on [related topic]"
3. "I thought your readers might find it valuable because [specific reason]"
4. "Would you consider linking to it from [specific page]?"
Tone: Peer-to-peer, respectful, not spammy''',

            'guest_post': '''a guest post pitch offering valuable content.
APPROACH:
- Show you understand their audience and content style
- Pitch a SPECIFIC topic idea (not generic)
- Highlight your expertise briefly
- Make it easy to say yes
STRUCTURE:
1. "I've been following [their site] and love how you cover [topic area]"
2. "I'd love to contribute a piece on [specific topic idea]"
3. "I think your readers would benefit because [reason]"
4. "Here's a rough outline: [2-3 key points]"
5. "Let me know if this sounds interesting!"
Tone: Collaborative, not transactional''',

            'backlink_followup': '''a follow-up to a previous backlink outreach.
Keep it SHORT and respectful:
1. "Just floating this back to the top of your inbox"
2. Re-state the value briefly
3. "No worries if it's not a fit - appreciate your time either way"
Tone: Friendly, zero pressure''',

            # Codeteki - Partnership
            'partnership_intro': '''a partnership introduction email.
APPROACH:
- Show you've researched their business (mention something specific)
- Identify a clear synergy or complementary offering
- Focus on how THEIR clients/customers would benefit
- Propose a specific partnership model if possible
STRUCTURE:
1. "I've been impressed by [specific thing about their company]"
2. "At Codeteki, we [brief positioning - AI/web/SEO]"
3. "I see a potential opportunity to [specific partnership idea]"
4. "This could help your clients [benefit] while you [their benefit]"
5. "Would you be open to a quick chat to explore this?"
Tone: Strategic peer, mutual respect''',

            'collaboration': '''a specific collaboration proposal.
APPROACH:
- Be concrete about what you're proposing
- Outline what each party brings to the table
- Explain the win-win clearly
- Suggest a clear next step
STRUCTURE:
1. Hook: What sparked this idea
2. The Opportunity: Specific collaboration concept
3. What We Bring: Our capabilities
4. What You Bring: Their strengths
5. The Win-Win: Benefits for both sides
6. Next Step: "Shall we explore this over a quick call?"
Tone: Business-minded but personable''',

            'partnership_followup': '''a follow-up to a partnership proposal.
Keep it brief and add value:
1. "Circling back on the partnership idea I shared"
2. Add a new thought or observation if possible
3. "I'd still love to explore how we could work together"
4. "Happy to adjust the approach based on what works for you"
Tone: Patient, flexible, still interested''',

            # Re-engagement / Existing Customers
            'existing_customer_update': '''a re-engagement email to an EXISTING customer/user who registered before recent platform updates.
CONTEXT: This person already knows us and has used our platform before. We've made significant improvements.
Key approach:
- Acknowledge they're a valued existing user/early supporter
- Highlight what's NEW since they last visited (new features, improvements)
- For Desi Firms: mention image search, real estate section, events - still FREE forever
- Make them feel special - they were here from the beginning
- Invite them to check out the improvements
- NO prices mentioned - just "still FREE" or "even better now"
Tone: Warm, appreciative, exciting news to share''',

            'win_back': '''a win-back email to re-engage someone who hasn't been active.
CONTEXT: They registered but haven't engaged recently.
Key approach:
- Acknowledge it's been a while (without guilt)
- Share what's improved/new since they left
- Ask if they had any issues we can help with
- Make it easy to come back - no barriers
- Emphasize it's still FREE (for Desi Firms)
Tone: Friendly, helpful, understanding''',

            'feature_announcement': '''an announcement email about new features or updates.
CONTEXT: Exciting news to share with existing users/contacts.
Key approach:
- Lead with how this helps THEM (problem it solves)
- Explain the new feature in simple terms
- For Desi Firms: image search helps customers find them, real estate expands reach
- Clear CTA to try it out
- No prices - focus on value
Tone: Excited but genuine''',

            'pricing_update': '''an email about platform improvements and accessibility.
CONTEXT: We've made the platform more accessible.
Key approach:
- Focus on accessibility and value, NOT specific prices
- For Desi Firms: "List your business FREE forever" - that's the message
- Mention there are optional premium features for those who want more
- Don't list price tiers - just say "affordable" or "free to start"
- Emphasize no obligation, no credit card required
Tone: Welcoming, no-pressure''',

            # Codeteki - Prospect Audit Outreach (based on real website scan data)
            'prospect_audit_outreach': '''a personalized outreach email based on REAL website scan data.

CRITICAL: This email is based on an ACTUAL scan of their website. You have REAL findings.
This is NOT a generic email. Use the specific data from the scan.

The user's suggestions field contains the scan findings, matched services, and roadmap.
You MUST reference the SPECIFIC findings from their website scan.

EMAIL RULES:
1. Open by mentioning you looked at THEIR specific website
2. Lead with THEIR biggest pain point (not your service list)
3. Explain BUSINESS IMPACT in plain language:
   - No chat = "customers visiting after 6pm have no way to get answers"
   - Slow site = "half your mobile visitors leave before the page even loads"
   - No booking = "people who want to book have to call - most won't bother"
   - Paying for HubSpot = "you're paying $800/mo for features you use 10% of"
   - Wix site = "you're renting your website - you don't own it, and it limits what you can do"
4. Mention ONE specific thing Codeteki can build/fix for them
5. If subscription trap detected, mention the savings angle
6. Hint at the roadmap: "start with X, and down the line we can also..."
7. CTA: Free consultation or quick demo
8. MAX 120 words - busy business owners won't read more

TONE: Like a helpful tech-savvy friend pointing out something they missed.
NOT a salesperson. NOT corporate. NOT jargon-heavy.

GOOD EXAMPLE:
"Hey - I was checking out bombaycurry.com.au and noticed there's no way
for customers to book a table or order from their phone. With 70% of
restaurant searches happening on mobile, that's a lot of missed orders.

We build AI-powered booking and ordering systems - one of our clients
saw online orders jump 40% in the first month. Happy to show you a
quick demo of what it'd look like for Bombay Curry.

- Team Codeteki"

BAD EXAMPLE:
"Dear Sir/Madam, we are a leading digital solutions provider offering
AI workforce solutions, web development, business automation..."''',

            # Codeteki - Sector-Specific Outreach (for businesses found via Google Places)
            'sector_outreach': '''a sector-specific outreach email for a local business.

CRITICAL: This is NOT a website pitch. You are pitching BUSINESS TOOLS that solve THEIR specific industry problems.

The user's suggestions field contains: INDUSTRY, BUSINESS NAME, ADDRESS, PHONE, WEBSITE STATUS, GOOGLE RATING.

SECTOR-SPECIFIC PITCHES — use the one matching their industry:

RESTAURANT/CAFE:
- Online ordering system (no more phone orders during rush)
- Table booking with AI confirmation
- Digital menu with photos (QR code on tables)
- Review management (auto-respond to Google reviews)
- "Your competitors on Google have online ordering — you're losing delivery orders"

TRADES (plumber, electrician, etc.):
- Instant quoting tool (customer describes job, AI generates quote)
- Job scheduling + dispatch system
- Before/after photo gallery for marketing
- "Stop spending evenings writing quotes — our AI tool generates them from a photo"

HEALTH & BEAUTY:
- Online booking (24/7, no phone tag)
- Client history + preferences system
- Appointment reminders (reduce no-shows by 40%)
- "Your clients want to book at midnight — let them"

RETAIL:
- Simple online store (keep 100% of sales, no Shopify fees)
- Inventory tracking
- Customer loyalty program
- "You're losing sales to online competitors — let's fix that"

FITNESS:
- Class booking + membership management
- Progress tracking for clients
- Automated check-in system

MEDICAL:
- Patient booking portal
- Intake forms (digital, not paper)
- Appointment reminders

PROFESSIONAL SERVICES / LEGAL / ACCOUNTING:
- Client portal with document sharing
- Appointment booking
- Automated intake questionnaires

REAL ESTATE:
- Property listing website with virtual tours
- Lead capture forms
- Automated follow-up sequences

ACCOMMODATION:
- Direct booking system (skip OTA commission fees)
- Guest communication automation
- Review management

EMAIL RULES:
1. Lead with ONE specific problem for THEIR industry
2. Frame it as saving time or making money, not "digital transformation"
3. Keep it under 100 words — these are busy owners
4. CTA: "Happy to show you a 2-minute demo" or "Can I send you a quick video?"
5. Tone: like a neighboring business owner, not a tech company

CRITICAL: These businesses may not be tech-savvy. Use ZERO jargon.
Say "booking system" not "SaaS platform". Say "app" not "application".
Say "online orders" not "e-commerce solution".''',

            # Generic
            'invitation': 'a professional invitation email',
            'followup': 'a professional follow-up email',
            'custom': '''a professional email STRICTLY following the user's suggestions below.
CRITICAL: The user has provided specific content/points they want in this email.
Your email MUST incorporate ALL the user's suggestions and key points.
DO NOT write a generic email - use the exact content/direction provided by the user.
The user's suggestions are your PRIMARY guide for this email.''',
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

        # Brand-specific signatures
        if 'desi' in brand_name.lower() or 'desifirms' in brand_name.lower():
            email_signature = """Noushad
Desi Firms
📱 0424 538 777
🌐 https://desifirms.com.au/"""
            company_tag = "Desi Firms"
        else:
            email_signature = """Noushad
Codeteki Digital Services
📱 0424 538 777
🌐 https://codeteki.au/"""
            company_tag = "Codeteki"

        # Build approach instructions based on style (problem_solving is default and recommended)
        approach_instructions = {
            'problem_solving': '''APPROACH: Problem-Solving (RECOMMENDED DEFAULT)
- Think about what challenges/problems the recipient likely faces
- For business owners: visibility, finding customers, online presence, time management
- For real estate: reaching buyers, showcasing properties, building trust
- Position our platform/service as a SOLUTION to their specific problem
- Frame everything from THEIR perspective - "you" not "we"
- Don't sell features - solve problems
- Example: Instead of "We have a directory" → "Get found by customers searching for businesses like yours"

FOR DESI FIRMS - PRESENT RESEARCH AS A HIGHLIGHT (not false claims):
- WRONG: "1.6 million searching for businesses" or "actively looking" (FALSE claims about behavior)
- WRONG: "reaching 1.6 million potential customers" (implies they're all potential customers)
- RIGHT: Add a highlight section: "📊 Why We Built This: 1.6M South Asians in Australia, no dedicated platform - until now"
- RIGHT: "Our research found a gap - a community of 1.6 million with no dedicated platform"
- Position as: we identified an underserved community, built something to fill the gap''',
            'value_driven': '''APPROACH: Value-Driven
- Lead with clear benefits and outcomes they'll get
- For Desi Firms: free visibility, community reach, new customers
- For Codeteki: more leads, better SEO, modern website
- Focus on what they GAIN, not what we offer
- Make the value proposition crystal clear
- Still avoid hard selling - let value speak for itself''',
            'relationship': '''APPROACH: Relationship-First
- Build connection and rapport first
- Show genuine interest in their business/work
- For Desi Firms: emphasize community, growing together
- Don't pitch heavily in first email - establish trust
- Be human, warm, and authentic
- Follow up with value after relationship is built''',
            'direct': '''APPROACH: Direct & Concise
- Get to the point quickly (busy people appreciate this)
- Respect their time - no fluff
- Clear, simple messaging
- Obvious but soft CTA
- Good for follow-ups or busy professionals'''
        }
        approach_desc = approach_instructions.get(approach_style, approach_instructions['problem_solving'])

        # Hybrid templates - these have their own signature, benefits, steps in the template
        # AI should only write the intro paragraph, NOT include signature
        hybrid_templates = [
            # Invitations
            'agent_invitation', 'directory_invitation', 'listing_benefits', 'event_invitation',
            # Follow-ups (1, 2, and 3/Final)
            'agent_followup_1', 'agent_followup_2', 'agent_followup_3',
            'directory_followup_1', 'directory_followup_2', 'directory_followup_3',
            'invitation_followup', 'invitation_followup_3',
            'events_followup_1', 'events_followup_2', 'events_followup_3',
            'realestate_followup_3',
            # Responded (thank you emails)
            'agent_responded', 'directory_responded', 'events_responded',
            # Registered/Signedup (welcome emails)
            'realestate_registered', 'business_signedup', 'events_signedup',
            # Listed (congrats emails)
            'realestate_listing', 'business_listed', 'events_listed',
            # Nudge emails
            'business_nudge', 'business_nudge2', 'realestate_nudge', 'realestate_nudge2',
            'events_nudge', 'events_nudge2',
        ]
        is_hybrid = email_type in hybrid_templates

        # Build signature instruction based on template type
        if is_hybrid:
            signature_instruction = """
DO NOT include a signature - the email template already has one.
DO NOT include benefits list, steps, or CTA - the template has those.
ONLY write the intro paragraph as specified above."""
        else:
            signature_instruction = f"""10. End with this EXACT signature (copy exactly, including emojis):

Warm regards,

{email_signature}

CRITICAL: Copy the signature EXACTLY as shown above. Do not modify, do not add brackets, do not use placeholders."""

        prompt = f"""Write {email_desc} with the following requirements:

{approach_desc}

SENDER INFORMATION:
- Company: {brand_name}
- Website: {brand_website}
- About Us: {brand_description}
- Value Proposition: {value_proposition}
- Sender Name: Noushad
- Contact: 0424 538 777
- Company Tag: {company_tag}

{f'''BUSINESS UPDATES (use these naturally if relevant):
{business_updates}
''' if business_updates else ''}
{f'''TARGET CONTEXT (understand who we're reaching):
{target_context}
''' if target_context else ''}
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
Start the email with ONLY the placeholder "{{{{SALUTATION}}}}" on its own line.
Then add a blank line before the body content.
DO NOT add any other greeting like "Hi", "Hello", "Dear" - the placeholder will be replaced with a personalized greeting.
WRONG: "{{{{SALUTATION}}}} Dear John," or "Hi, I hope..."
CORRECT: "{{{{SALUTATION}}}}\n\nI hope this message finds you well..."

TONE & STYLE:
{tone_desc}

USER SUGGESTIONS/KEY POINTS TO INCLUDE:
{suggestions if suggestions else 'No specific suggestions provided - use the context above to write an appropriate email.'}

STRICT FORMATTING RULES:
1. Start with "{{{{SALUTATION}}}}" on its OWN LINE, followed by a blank line
2. The email body starts AFTER the blank line (NOT on same line as salutation)
3. Keep it concise (under 150 words)
4. Don't be pushy or salesy
5. Include a clear but soft call-to-action
6. Make it feel personalized, not templated
7. If recipient company info is available, reference it naturally
8. NEVER use placeholder text like [Your Name], [Contact], [Your Position], [Your Company] - always use real values
9. NEVER write URLs in markdown format like [text](url) - write plain URLs
{signature_instruction}

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

        parsed = None
        import re

        # Try direct JSON parse first
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError:
            pass

        # If direct parse failed, use regex extraction (handles multiline body)
        if not parsed:
            # Extract subject - look for "subject": "..."
            subject_match = re.search(r'"subject"\s*:\s*"([^"]*)"', output)

            # Extract body - find "body": " and then capture until the closing pattern
            # The body ends with " followed by optional whitespace and }
            body_start_match = re.search(r'"body"\s*:\s*"', output)

            if subject_match and body_start_match:
                subject = subject_match.group(1)

                # Find the body content: start after "body": " and end before final "}
                body_start = body_start_match.end()

                # Find the end - last " before the final }
                # Work backwards from the end
                body_content = output[body_start:]

                # Find the last occurrence of "} or "\n}
                end_patterns = ['"\n}', '"}', '" }', '"\r\n}']
                end_idx = -1
                for pattern in end_patterns:
                    idx = body_content.rfind(pattern)
                    if idx > end_idx:
                        end_idx = idx

                if end_idx > 0:
                    body = body_content[:end_idx]
                else:
                    # Fallback: just remove trailing characters
                    body = body_content.rstrip().rstrip('}').rstrip().rstrip('"')

                # Clean up escape sequences
                body = body.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')

                parsed = {'subject': subject, 'body': body}

        if not parsed:
            # Last resort: treat the whole output as body
            lines = output.strip().split('\n')
            subject = 'Follow Up' if lines else 'Hello'
            body = output
            parsed = {'subject': subject, 'body': body}

        return {
            'subject': parsed.get('subject', 'Hello'),
            'body': parsed.get('body', ''),
            'success': True
        }

    def _build_deal_context(self, deal, engagement_profile=None) -> str:
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

        # Add engagement profile if available
        if engagement_profile:
            from crm.services.engagement_engine import get_engagement_summary_for_ai
            context_parts.append("")
            context_parts.append(get_engagement_summary_for_ai(deal))

        return "\n".join(context_parts)
