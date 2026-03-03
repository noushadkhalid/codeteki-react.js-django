"""
WhatsApp AI Auto-Responder for Desi Firms.

Handles inbound WhatsApp messages with AI-generated responses,
user classification, conversation tracking, and human handoff.
"""

import json
import logging
import re
from django.utils import timezone

logger = logging.getLogger(__name__)

# Maximum active handoffs before team is considered "busy"
MAX_ACTIVE_HANDOFFS = 5

# Base URL
BASE = 'https://desifirms.com.au'

# Correct URLs for Desi Firms actions
DESI_FIRMS_URLS = {
    'register': f'{BASE}/api/register/',
    'login': f'{BASE}/api/login/',
    'add_business': f'{BASE}/api/add-listing/',
    'add_event': f'{BASE}/api/add_event/',
    'add_deal': f'{BASE}/api/add_deal/',
    'browse_businesses': f'{BASE}/all-listings',
    'browse_events': f'{BASE}/events-list',
    'browse_deals': f'{BASE}/deals-list',
    'browse_classifieds': f'{BASE}/classifieds',
    'browse_realestate': f'{BASE}/realestate',
    'realestate_dashboard': f'{BASE}/realestate/dashboard/',
    'dashboard': f'{BASE}/dashboard/',
}

# Map intents to buttons the AI should suggest
INTENT_BUTTONS = {
    'register': [
        {'title': 'Register Now', 'url': DESI_FIRMS_URLS['register']},
    ],
    'list_business': [
        {'title': 'Register', 'url': DESI_FIRMS_URLS['register']},
        {'title': 'Add Business', 'url': DESI_FIRMS_URLS['add_business']},
    ],
    'realestate_agent': [
        {'title': 'Register', 'url': DESI_FIRMS_URLS['register']},
        {'title': 'Agent Dashboard', 'url': DESI_FIRMS_URLS['realestate_dashboard']},
    ],
    'post_event': [
        {'title': 'Register', 'url': DESI_FIRMS_URLS['register']},
        {'title': 'Post Event', 'url': DESI_FIRMS_URLS['add_event']},
    ],
    'post_deal': [
        {'title': 'Register', 'url': DESI_FIRMS_URLS['register']},
        {'title': 'Post Deal', 'url': DESI_FIRMS_URLS['add_deal']},
    ],
    'browse': [
        {'title': 'Browse Businesses', 'url': DESI_FIRMS_URLS['browse_businesses']},
    ],
    'browse_realestate': [
        {'title': 'Browse Properties', 'url': DESI_FIRMS_URLS['browse_realestate']},
    ],
}

DESI_FIRMS_KNOWLEDGE = f"""
Desi Firms (desifirms.com.au) is Australia's largest South Asian business directory and community platform.

HOW TO REGISTER (important — get these steps right):
- Go to the Register page (link button will be attached automatically)
- Fill in: Username, Email, Password, Confirm Password
- OR click "Sign up with Google" for quick registration
- If using email: you'll get an activation email — click the link to verify
- Once verified, you're redirected to your Desi Firms dashboard
- That's it! Takes under 2 minutes

WHAT YOU CAN DO ON DESI FIRMS:

1. LIST YOUR BUSINESS (Free):
   - Full profile with photos, hours, contact info, location map
   - Categories: restaurants, grocers, beauty, real estate, legal, medical, trades, IT, accounting, and 50+ more
   - Get discovered by thousands of South Asian Australians
   - Free basic plan — no hidden fees
   - Premium plans available: Standard $9.99/mo, Premium $14.99/mo (yearly savings)
   - Steps: Register first, then from your dashboard click "Add Business", fill in details, goes live after quick review

2. REAL ESTATE SECTION:
   - For agents/agencies: list properties, create agent profile, showcase portfolio
   - For buyers/renters: browse listings from South Asian real estate agents across Australia
   - Steps for agents: Register first, then go to Real Estate Dashboard to create your agent/agency profile

3. POST DEALS & PROMOTIONS:
   - Special offers, discounts, seasonal deals from your business
   - Great way to attract new customers
   - Steps: Register first, then "Post a Deal" from your dashboard

4. POST CLASSIFIEDS:
   - Jobs, buy/sell, rentals, services, vehicles
   - Free to post
   - Steps: Register first, then post from classifieds section

5. BROWSE & DISCOVER (for regular users):
   - Search businesses by category and location
   - Find deals, classifieds near you
   - Save favourites, get updates
   - All free to use

IMPORTANT: NEVER include URLs or web addresses in your text responses. Don't write "desifirms.com.au" or any URL. The system automatically attaches clickable link buttons below your message. Just tell the user what to do in plain language (e.g. "Just register and you can add your business listing!") and the links will appear automatically.
IMPORTANT: When explaining registration, ALWAYS use the exact steps: choose a username, enter email, create password, confirm password. Or mention Google sign-up option. NEVER make up extra fields.
"""

SYSTEM_PROMPT = """You are Desi Firms Smart Assistant — an AI-powered WhatsApp helper for Australia's South Asian business directory.

IDENTITY:
- You ARE an AI assistant — be upfront about it. In your first reply, mention you're the "Desi Firms Smart Assistant"
- Don't pretend to be human. If asked, confirm you're AI
- You're friendly, helpful, and knowledgeable about Desi Firms

VOICE & STYLE:
- Warm, humble, community-focused — like a helpful neighbour
- Keep messages short and WhatsApp-friendly (2-4 sentences max)
- Casual but respectful tone
- No corporate jargon
- One or two emojis max per message
- Ask one question at a time

CONVERSATION FLOW:
1. FIRST MESSAGE: Greet warmly, introduce yourself as Desi Firms Smart Assistant, ask what they're looking for
2. DISCOVERY: Ask what they need. Guide them with options like:
   - "Are you a business owner looking to list your business?"
   - "Are you a real estate agent or agency?"
   - "Looking to post events, deals, or classifieds?"
   - "Or are you looking to find businesses/services near you?"
3. INFO: Based on their answer, share specific relevant info from the knowledge base
   - Business owner → explain free listing, how to register, benefits
   - Real estate → explain agent profiles, property listings
   - Events → explain event posting, community reach
   - Deals/classifieds → explain those features
   - Just browsing → explain how to search, register for updates
4. GUIDE: Walk them through the specific steps for what they want to do
5. FOLLOW UP: Ask if they have more questions or need help with anything else

CRITICAL RULES ABOUT LINKS:
- NEVER write URLs or web addresses in your message. No "desifirms.com.au", no "visit our website", no links at all.
- Just tell the user what to do in plain language (e.g. "Just register and add your business!")
- Clickable link buttons are automatically attached to your message by the system.

{human_option_instruction}

IMPORTANT RULES:
- If asked about specific business listings, tell them to check the platform
- If they send a message in Hindi/Urdu/Punjabi, respond in English but acknowledge you understand
- Don't ask for sensitive info (passwords, payment details)
- Don't repeat the same info — keep the conversation progressing

{knowledge}

CONVERSATION HISTORY:
{history}

CONVERSATION SUMMARY:
{summary}

USER TYPE: {user_type}
CONVERSATION PHASE: {phase}
"""

HUMAN_AVAILABLE_INSTRUCTION = """HUMAN HANDOFF:
- If the customer asks something you genuinely can't answer, or they seem frustrated, you can offer to connect them with our team
- Say something like: "If you'd like to chat with someone from our team, just type 'human' and I'll connect you!"
- Only offer this when it naturally fits — don't push it in every message
- If they type "human" — let them know our team will get back to them shortly"""

HUMAN_BUSY_INSTRUCTION = """HUMAN HANDOFF:
- Do NOT offer to connect with a human or our team — the team is currently handling many conversations
- You are fully capable of answering their questions about Desi Firms
- If they specifically ask to talk to a person, say: "Our team is a bit tied up right now helping other customers. But I can help you with pretty much anything about Desi Firms! What would you like to know?"
- Keep helping them with AI — you have all the info they need about the platform"""


class WhatsAppAIService:
    """AI-powered WhatsApp auto-responder for Desi Firms."""

    def __init__(self):
        from core.services.ai_client import AIContentEngine
        self.ai = AIContentEngine()

    def handle_inbound(self, phone, message, sender_name=''):
        """Main entry point for processing an inbound WhatsApp message."""
        conversation = self._get_or_create_conversation(phone, sender_name)

        # Don't respond if AI is deactivated (human took over)
        if not conversation.ai_active:
            logger.info(f"WhatsApp AI inactive for {phone}, skipping")
            return None

        # Update stats
        conversation.message_count += 1
        conversation.last_inbound_at = timezone.now()

        # Check if user explicitly typed "human" and team has capacity
        if self._is_human_request(message) and self._team_has_capacity():
            self.trigger_handoff(conversation, reason='User requested human')
            return None

        # Classify user if still unknown (after first real message)
        if conversation.user_type == 'unknown' and conversation.message_count >= 1:
            self._classify_user(conversation, message)

        # Update phase based on message count
        self._update_phase(conversation)

        # Regenerate summary every 5 messages
        if conversation.message_count % 5 == 0 and conversation.message_count > 0:
            self._regenerate_summary(conversation)

        # Generate AI response
        raw_response = self._generate_response(conversation, message)
        if not raw_response:
            logger.error(f"Failed to generate AI response for {phone}")
            conversation.save()
            return None

        # Detect which buttons to attach based on context
        text, buttons = self._detect_buttons(raw_response, conversation, message)

        # Send response (with or without buttons)
        send_result = self._send_response(phone, text, buttons)
        if send_result:
            conversation.ai_message_count += 1
            conversation.last_outbound_at = timezone.now()

        conversation.save()

        # Only notify owner on handoff — regular AI chats don't need notification
        return text

    def _detect_buttons(self, ai_response, conversation, customer_message):
        """Auto-detect which buttons to attach based on context.

        Only attach links AFTER the customer has expressed intent —
        never on the greeting/discovery phase when AI is still asking questions.
        """
        text = ai_response
        # Strip any URLs the AI snuck in
        text = re.sub(r'https?://\S+', '', text).strip()
        text = re.sub(r'desifirms\.com\.au\S*', '', text, flags=re.IGNORECASE).strip()
        text = re.sub(r'  +', ' ', text)
        # Remove [BUTTONS:...] tag if AI added it
        text = re.sub(r'\[BUTTONS:\w+\]\s*$', '', text).strip()

        # Don't attach links in early conversation — let the customer speak first
        if conversation.phase in ('greeting', 'discovery') and conversation.message_count <= 2:
            return text, []

        # Only match against CUSTOMER message (not AI response which mentions everything)
        msg = customer_message.lower()

        # Detect intent from what the CUSTOMER said
        if any(w in msg for w in ['register', 'sign up', 'create account', 'get started']):
            if conversation.user_type == 'business_owner' or 'list' in msg or 'business' in msg:
                return text, INTENT_BUTTONS['list_business']
            if 'agent' in msg or 'agency' in msg or 'real estate' in msg or 'property' in msg:
                return text, INTENT_BUTTONS['realestate_agent']
            return text, INTENT_BUTTONS['register']

        if any(w in msg for w in ['list my business', 'add listing', 'add my business', 'list business']):
            return text, INTENT_BUTTONS['list_business']

        if any(w in msg for w in ['real estate', 'agent profile', 'agency', 'property listing', 'property']):
            return text, INTENT_BUTTONS['realestate_agent']

        if any(w in msg for w in ['post event', 'add event']):
            return text, INTENT_BUTTONS['post_event']

        if any(w in msg for w in ['post deal', 'add deal', 'promotion', 'deal']):
            return text, INTENT_BUTTONS['post_deal']

        if any(w in msg for w in ['browse', 'search', 'find business', 'looking for']):
            if 'real estate' in msg or 'property' in msg:
                return text, INTENT_BUTTONS['browse_realestate']
            return text, INTENT_BUTTONS['browse']

        return text, []

    def _is_human_request(self, message):
        """Check if user asked for a human."""
        msg = message.strip().lower().rstrip('?!.')
        # Exact matches
        if msg in ('human', 'human please', 'talk to human', 'speak to human', 'agent', 'operator'):
            return True
        # Partial matches — customer mentions wanting a human/person/someone
        human_phrases = ['speak to human', 'talk to human', 'speak to a human', 'talk to a person',
                         'speak to someone', 'talk to someone', 'need a human', 'want a human',
                         'real person', 'can i speak', 'can i talk', 'connect me']
        return any(phrase in msg for phrase in human_phrases)

    def _team_has_capacity(self):
        """Check if there are fewer than MAX_ACTIVE_HANDOFFS active handoffs."""
        from crm.models import WhatsAppConversation
        active_handoffs = WhatsAppConversation.objects.filter(
            ai_active=False,
            phase='handoff',
            handoff_at__isnull=False,
        ).count()
        has_capacity = active_handoffs < MAX_ACTIVE_HANDOFFS
        if not has_capacity:
            logger.info(
                f"Team at capacity ({active_handoffs} active handoffs). "
                f"AI will continue handling conversations."
            )
        return has_capacity

    def _get_or_create_conversation(self, phone, sender_name=''):
        """Get or create a WhatsAppConversation for this phone number."""
        from crm.models import WhatsAppConversation

        conversation, created = WhatsAppConversation.objects.get_or_create(
            phone=phone,
            defaults={
                'user_name': sender_name,
            }
        )

        if created:
            logger.info(f"Created new WhatsApp conversation for {phone}")
            contact = self._get_or_create_contact(phone, sender_name)
            conversation.contact = contact
            deal = self._create_whatsapp_deal(contact)
            conversation.deal = deal
            conversation.save(update_fields=['contact', 'deal'])
        elif sender_name and not conversation.user_name:
            conversation.user_name = sender_name
            conversation.save(update_fields=['user_name'])

        return conversation

    def _get_or_create_contact(self, phone, sender_name=''):
        """Get or auto-create a Contact under desifirms brand."""
        from crm.models import Contact, Brand

        contact = Contact.objects.filter(phone=phone).first()
        if not contact and len(phone) >= 10:
            contact = Contact.objects.filter(phone__endswith=phone[-10:]).first()

        if contact:
            if contact.has_whatsapp is not True:
                contact.has_whatsapp = True
                contact.save(update_fields=['has_whatsapp'])
            return contact

        brand = Brand.objects.filter(slug='desifirms').first()
        if not brand:
            logger.error("No brand with slug 'desifirms' found")
            return None

        name = sender_name or phone
        contact = Contact.objects.create(
            name=name,
            phone=phone,
            brand=brand,
            contact_type='lead',
            source='whatsapp_inbound',
            has_whatsapp=True,
        )
        logger.info(f"Created contact {contact.id} for WhatsApp lead {phone}")
        return contact

    def _create_whatsapp_deal(self, contact):
        """Create a Deal in the WhatsApp Inquiry pipeline."""
        if not contact:
            return None

        from crm.models import Pipeline, PipelineStage, Deal

        pipeline = Pipeline.objects.filter(
            pipeline_type='whatsapp_inquiry', is_active=True
        ).first()
        if not pipeline:
            logger.warning("No active whatsapp_inquiry pipeline found")
            return None

        first_stage = PipelineStage.objects.filter(
            pipeline=pipeline
        ).order_by('order').first()
        if not first_stage:
            return None

        existing = Deal.objects.filter(
            contact=contact, pipeline=pipeline, status='active'
        ).first()
        if existing:
            return existing

        deal = Deal.objects.create(
            contact=contact,
            pipeline=pipeline,
            current_stage=first_stage,
            status='active',
            ai_notes=f"WhatsApp inquiry from {contact.phone}",
        )
        logger.info(f"Created WhatsApp inquiry deal {deal.id} for {contact.name}")
        return deal

    def _classify_user(self, conversation, message):
        """Use AI to classify the user type from their message."""
        if not self.ai.enabled:
            return

        history = self._build_conversation_history(conversation.phone, limit=5)

        prompt = f"""Based on this WhatsApp conversation, classify the user.

Message history:
{history}

Latest message: "{message}"

Classify as ONE of:
- business_owner: They own or run a business and want to list it, or are asking about business features
- regular_user: They're looking for businesses/services, browsing, or general community member
- existing_member: They mention they already have an account/listing on Desi Firms

Reply with ONLY the classification word (business_owner, regular_user, or existing_member)."""

        result = self.ai.generate(
            prompt=prompt,
            temperature=0.1,
            system_prompt="You classify WhatsApp users. Reply with only the classification word.",
        )

        if result['success']:
            output = result['output'].strip().lower()
            if output in ('business_owner', 'regular_user', 'existing_member'):
                conversation.user_type = output
                logger.info(f"Classified {conversation.phone} as {output}")

    def _build_conversation_history(self, phone, limit=10):
        """Pull recent messages from EmailLog for context."""
        from crm.models import EmailLog

        messages = EmailLog.objects.filter(
            channel='whatsapp', to_phone=phone
        ).order_by('-sent_at')[:limit]

        lines = []
        for msg in reversed(messages):
            role = 'Customer' if msg.delivery_status == 'received' else 'Desi Firms Assistant'
            lines.append(f"{role}: {msg.body}")

        return '\n'.join(lines) if lines else '(No previous messages)'

    def _generate_response(self, conversation, message):
        """Generate an AI response using conversation context."""
        if not self.ai.enabled:
            return None

        history = self._build_conversation_history(conversation.phone, limit=10)

        if self._team_has_capacity():
            human_instruction = HUMAN_AVAILABLE_INSTRUCTION
        else:
            human_instruction = HUMAN_BUSY_INSTRUCTION

        system = SYSTEM_PROMPT.format(
            knowledge=DESI_FIRMS_KNOWLEDGE,
            history=history,
            summary=conversation.conversation_summary or '(New conversation)',
            user_type=conversation.get_user_type_display(),
            phase=conversation.get_phase_display(),
            human_option_instruction=human_instruction,
        )

        prompt = f"Customer says: \"{message}\"\n\nRespond naturally as the Desi Firms Smart Assistant. Keep it short and WhatsApp-friendly. NEVER include URLs or web addresses in your response."

        result = self.ai.generate(
            prompt=prompt,
            temperature=0.7,
            system_prompt=system,
        )

        if result['success']:
            return result['output']

        logger.error(f"AI generation failed: {result.get('error')}")
        return None

    def _send_response(self, phone, text, buttons=None):
        """Send AI response via WhatsApp and log it."""
        from crm.services.messaging_service import MetaWhatsAppService
        from crm.models import EmailLog

        wa = MetaWhatsAppService()
        if not wa.enabled:
            logger.error("MetaWhatsAppService not configured")
            return False

        if buttons:
            result = wa.send_text_with_links(to=phone, body=text, buttons=buttons)
        else:
            result = wa.send_text(to=phone, body=text)

        if result['success']:
            # Log text + button info
            log_body = text
            if buttons:
                btn_labels = ', '.join(b['title'] for b in buttons)
                log_body += f"\n[Buttons: {btn_labels}]"

            EmailLog.objects.create(
                channel='whatsapp',
                subject='AI WhatsApp Response',
                body=log_body,
                to_phone=phone,
                message_sid=result.get('message_id', ''),
                delivery_status='sent',
                sent_at=timezone.now(),
            )
            return True

        logger.error(f"Failed to send WhatsApp to {phone}: {result.get('error')}")
        return False

    def trigger_handoff(self, conversation, reason=''):
        """Hand off conversation to human — AI stops, owner notified."""
        conversation.ai_active = False
        conversation.phase = 'handoff'
        conversation.handoff_at = timezone.now()
        conversation.handoff_reason = reason
        conversation.save()

        if conversation.deal:
            from crm.models import PipelineStage
            handoff_stage = PipelineStage.objects.filter(
                pipeline=conversation.deal.pipeline,
                name='Handed Off',
            ).first()
            if handoff_stage:
                conversation.deal.current_stage = handoff_stage
                conversation.deal.save(update_fields=['current_stage'])

        handoff_msg = (
            "No worries! I'm connecting you with our team now. "
            "Someone will get back to you shortly. Thanks for your patience!"
        )
        self._send_response(conversation.phone, handoff_msg)

        self._notify_owner(
            conversation,
            f"[HANDOFF REQUESTED: {reason}]",
            handoff_msg,
            is_handoff=True,
        )

        logger.info(f"Handed off conversation {conversation.phone}: {reason}")

    def _update_phase(self, conversation):
        """Update conversation phase based on progress."""
        count = conversation.message_count
        if conversation.phase == 'greeting' and count >= 2:
            conversation.phase = 'discovery'
        elif conversation.phase == 'discovery' and count >= 4:
            conversation.phase = 'info_shared'
        elif conversation.phase == 'info_shared' and count >= 6:
            conversation.phase = 'engaged'

        if conversation.deal:
            self._sync_deal_stage(conversation)

    def _sync_deal_stage(self, conversation):
        """Keep deal stage in sync with conversation phase."""
        from crm.models import PipelineStage

        phase_to_stage = {
            'greeting': 'New Inquiry',
            'discovery': 'New Inquiry',
            'info_shared': 'Engaged',
            'engaged': 'Qualified',
        }
        target_stage_name = phase_to_stage.get(conversation.phase)
        if not target_stage_name:
            return

        target_stage = PipelineStage.objects.filter(
            pipeline=conversation.deal.pipeline,
            name=target_stage_name,
        ).first()

        if target_stage and conversation.deal.current_stage != target_stage:
            if target_stage.order > conversation.deal.current_stage.order:
                conversation.deal.current_stage = target_stage
                conversation.deal.save(update_fields=['current_stage'])

    def _regenerate_summary(self, conversation):
        """AI-generated rolling summary of the conversation."""
        if not self.ai.enabled:
            return

        history = self._build_conversation_history(conversation.phone, limit=20)

        result = self.ai.generate(
            prompt=f"Summarize this WhatsApp conversation in 2-3 sentences. Focus on what the customer wants and their situation:\n\n{history}",
            temperature=0.2,
            system_prompt="You summarize conversations concisely. Be factual and brief.",
        )

        if result['success']:
            conversation.conversation_summary = result['output']

    def _notify_owner(self, conversation, message, ai_response, is_handoff=False):
        """Enhanced owner notification with user type and summary."""
        import os
        owner_phone = os.environ.get('OWNER_NOTIFY_PHONE', '')
        owner_email = os.environ.get('OWNER_NOTIFY_EMAIL', '')

        user_type_label = conversation.get_user_type_display()
        phase_label = conversation.get_phase_display()
        name = conversation.user_name or conversation.phone

        if is_handoff:
            prefix = "HANDOFF"
        else:
            prefix = "AI Chat"

        if owner_phone:
            try:
                from crm.services.messaging_service import MetaWhatsAppService
                wa = MetaWhatsAppService()
                wa_msg = (
                    f"[{prefix}] {name} ({conversation.phone})\n"
                    f"Type: {user_type_label} | Phase: {phase_label}\n\n"
                    f"Customer: {message[:300]}\n"
                )
                if ai_response and not is_handoff:
                    wa_msg += f"\nAI replied: {ai_response[:200]}"
                if conversation.conversation_summary:
                    wa_msg += f"\n\nSummary: {conversation.conversation_summary[:200]}"

                # Try WhatsApp first, fall back to SMS
                sent = False
                if wa.enabled:
                    result = wa.send_text(to=owner_phone, body=wa_msg)
                    if result.get('success'):
                        sent = True
                        logger.info(f"Owner notified via WhatsApp: {owner_phone}")
                    else:
                        logger.warning(f"Owner WhatsApp failed: {result.get('error')}")

                # SMS fallback — send directly via Twilio (no opt-out check for owner)
                if not sent:
                    try:
                        from twilio.rest import Client
                        import os
                        sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
                        token = os.environ.get('TWILIO_AUTH_TOKEN', '')
                        from_num = os.environ.get('TWILIO_PHONE_NUMBER', '')
                        if sid and token and from_num:
                            client = Client(sid, token)
                            sms = client.messages.create(
                                body=wa_msg,
                                from_=from_num,
                                to=owner_phone,
                            )
                            logger.info(f"Owner notified via SMS: {owner_phone} SID={sms.sid}")
                        else:
                            logger.error("Twilio not configured for owner SMS fallback")
                    except Exception as sms_err:
                        logger.error(f"Owner SMS fallback failed: {sms_err}")
            except Exception as e:
                logger.error(f"Owner notify failed: {e}")

        if owner_email:
            try:
                from django.core.mail import send_mail
                subject = f"[{prefix}] WhatsApp from {name}"
                if is_handoff:
                    subject = f"[HANDOFF NEEDED] WhatsApp from {name}"

                body = (
                    f"WhatsApp Conversation Update\n"
                    f"{'=' * 40}\n\n"
                    f"Contact: {name} ({conversation.phone})\n"
                    f"User Type: {user_type_label}\n"
                    f"Phase: {phase_label}\n"
                    f"Messages: {conversation.message_count}\n"
                    f"AI Active: {'Yes' if conversation.ai_active else 'No'}\n\n"
                    f"Customer Message:\n{message}\n\n"
                )
                if ai_response:
                    body += f"AI Response:\n{ai_response}\n\n"
                if conversation.conversation_summary:
                    body += f"Conversation Summary:\n{conversation.conversation_summary}\n\n"
                body += "Reply via the WhatsApp Inbox in CRM admin."

                send_mail(
                    subject=subject,
                    message=body,
                    from_email=None,
                    recipient_list=[owner_email],
                    fail_silently=not is_handoff,
                )
                logger.info(f"Owner notified via email: {owner_email}")
            except Exception as e:
                logger.error(f"Owner email notify failed: {e}")
