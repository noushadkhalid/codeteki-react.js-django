"""
SEO Content Generator Service for Codeteki

Generates humanized, SEO-optimized content using OpenAI GPT-4.
Implements various techniques to make AI-generated content appear more natural
and avoid AI detection while maintaining SEO best practices.

Adapted from Desi Firms content generator for Codeteki's AI solutions focus.
"""

import re
import json
import hashlib
import logging
from django.conf import settings
from django.utils import timezone
from openai import OpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client with request timeout
client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', ''), timeout=180.0)

# System message for content generation
SYSTEM_MESSAGE = (
    "You are a skilled Australian blog writer who gives concrete, actionable advice. "
    "NEVER define common terms — the reader already knows what marketing, SEO, and AI are. "
    "Skip definitions. Jump straight to application: HOW to do it, with real examples and numbers. "
    "Short sentences (8-10 words average, never over 15). Simple words. Active voice. "
    "Australian English (colour, organise, centre). Paragraphs: 2-3 sentences. "
    "Every sentence must teach something new or give a concrete example. No filler. No fluff. "
    "Prefer short, common words over formal/academic ones. "
    "IMPORTANT: Always use the PRIMARY KEYWORD exactly as given — never rephrase or simplify words within it."
)

# Code-based word simplifications for readability improvement (no API cost).
WORD_SIMPLIFICATIONS = [
    (r'\bcomprehensive\b', 'full'),
    (r'\bstraightforward\b', 'simple'),
    (r'\badditionally\b', 'also'),
    (r'\bfurthermore\b', 'also'),
    (r'\bnevertheless\b', 'still'),
    (r'\bsubsequently\b', 'then'),
    (r'\bapproximately\b', 'about'),
    (r'\bnumerous\b', 'many'),
    (r'\bin order to\b', 'to'),
    (r'\bfacilitating\b', 'helping'),
    (r'\bfacilitate\b', 'help'),
    (r'\butilise\b', 'use'),
    (r'\butilising\b', 'using'),
    (r'\butilize\b', 'use'),
    (r'\butilizing\b', 'using'),
    (r'\bdemonstrate\b', 'show'),
    (r'\bdemonstrating\b', 'showing'),
    (r'\bimplementing\b', 'setting up'),
    (r'\bimplementation\b', 'setup'),
    (r'\bfunctionality\b', 'feature'),
    (r'\bmethodology\b', 'method'),
    (r'\bpredominantly\b', 'mostly'),
    (r'\bencompasses\b', 'covers'),
    (r'\beffectively\b', 'well'),
    (r'\bfortunately\b', 'luckily'),
    (r'\bcredibility\b', 'trust'),
    (r'\baccessibility\b', 'access'),
    (r'\bresponsiveness\b', 'speed'),
    (r'\bauthenticate\b', 'verify'),
    (r'\bauthenticated\b', 'verified'),
    (r'\bpromotional\b', 'promo'),
    (r'\bindependently\b', 'on your own'),
    (r'\bsignificantly\b', 'much'),
    (r'\bconsiderably\b', 'much'),
    (r'\bsubstantially\b', 'much'),
    (r'\bspecifically\b', 'just'),
    (r'\bentrepreneur\b', 'business owner'),
    (r'\bentrepreneurs\b', 'business owners'),
    (r'\binnovative\b', 'new'),
    (r'\bsubscription\b', 'plan'),
    (r'\bsubscriptions\b', 'plans'),
    (r'\bpurchasing\b', 'buying'),
    (r'\bidentify\b', 'spot'),
    (r'\bidentifying\b', 'spotting'),
    (r'\bensuring\b', 'making sure'),
    (r'\bopportunity\b', 'chance'),
    (r'\bopportunities\b', 'chances'),
    (r'\bsignificant\b', 'big'),
    (r'\bencouraging\b', 'asking'),
    (r'\beverything\b', 'all'),
    (r'\binformation\b', 'info'),
    (r'\bimportant\b', 'key'),
    (r'\bessential\b', 'key'),
    (r'\bimmediately\b', 'right away'),
    (r'\borganisation\b', 'group'),
    (r'\bestablishments\b', 'places'),
    (r'\bestablishment\b', 'place'),
    (r'\brecommendations\b', 'tips'),
    (r'\brecommendation\b', 'tip'),
    (r'\bdiscovering\b', 'finding'),
    (r'\bneglecting\b', 'skipping'),
    (r'\badvertisements\b', 'ads'),
    (r'\badvertisement\b', 'ad'),
    (r'\bparticularly\b', 'especially'),
    (r'\bregarding\b', 'about'),
    (r'\bfrequently\b', 'often'),
    (r'\boverwhelming\b', 'too much'),
    (r'\befficiently\b', 'fast'),
    (r'\befficient\b', 'fast'),
    (r'\btransparency\b', 'clarity'),
    (r'\bprofessionals\b', 'experts'),
    (r'\bprofessional\b', 'expert'),
    (r'\bcategories\b', 'types'),
    (r'\bcategory\b', 'type'),
    (r'\bverification\b', 'checks'),
    (r'\breliability\b', 'trust'),
    (r'\balternatives\b', 'options'),
    (r'\balternative\b', 'option'),
    (r'\bbeneficial\b', 'helpful'),
    (r'\bincorporating\b', 'adding'),
    (r'\bunfortunately\b', 'sadly'),
    (r'\bconsistently\b', 'always'),
    (r'\bgenerating\b', 'making'),
    (r'\bdetermining\b', 'finding'),
    (r'\bpreferences\b', 'choices'),
    (r'\bproviding\b', 'giving'),
    (r'\bevaluate\b', 'check'),
    (r'\bevaluating\b', 'checking'),
    (r'\bconvenient\b', 'handy'),
]

# House rules baked into every content generation prompt
HOUSE_RULES = """HOUSE RULES (always apply):

PURPOSE — EVERY article exists to promote Codeteki and its services:
- This is SEO content for Codeteki. The article MUST drive readers to use Codeteki's services: AI chatbots, voice AI, custom websites, business automation, and CRM.
- When keywords mention "tools", "platforms", "software", "solutions", or "services" — the answer is ALWAYS the relevant Codeteki service. NEVER recommend competing external tools or generic services as alternatives.
- Position Codeteki as THE solution, not one option among many.

CONTENT RULES:
- Do NOT invent facts, counts, or scale unless explicitly provided in creator instructions.
- Do NOT name real competing businesses or platforms. Do NOT recommend external apps or services.
- Write in Australian English (favourite, organise, centre, colour, analyse, defence, licence).
- Reduce repetition. Do not restate the same point in multiple sections.
- Clarity over fluff: fewer adjectives, more useful insight. Cut any sentence that doesn't add new information.
- Describe Codeteki as a Melbourne-based AI solutions agency that builds custom AI tools for businesses.
- Describe benefits using different angles: AI chatbots, voice AI agents, custom websites, automation, CRM, no monthly fees, flat-rate pricing, 24/7 support.
- ANTI-REPETITION: Before writing each section, check "Have I already said this?" Expand with different angles.
- LINKING: Only link to URLs from Creator Instructions. Do NOT invent URLs."""

# Humanization techniques and their descriptions
HUMANIZATION_TECHNIQUES = {
    'relatable_scenarios': 'Use relatable scenarios (not personal anecdotes) to illustrate points',
    'colloquialisms': 'Use casual expressions and conversational phrases',
    'varied_sentence_length': 'Mix short punchy sentences with longer complex ones',
    'rhetorical_questions': 'Include thought-provoking questions',
    'contractions': 'Use natural contractions (don\'t, won\'t, it\'s)',
    'imperfections': 'Add slight informal touches (starting with But, And)',
    'local_references': 'Include Australian cultural references where appropriate',
    'emotional_language': 'Add emotional undertones and empathetic language',
    'generic_examples': 'Include generic, non-identifiable real-world examples',
    'conversational_transitions': 'Use natural transition phrases (anyway, so, now)',
}

# Default humanization techniques
DEFAULT_HUMANIZATION = [
    'varied_sentence_length',
    'contractions',
    'conversational_transitions',
    'rhetorical_questions',
    'relatable_scenarios',
    'generic_examples',
]

# Structure variants to rotate article layout per topic (reduces AI footprint)
STRUCTURE_VARIANTS = [
    {
        "lead": "Start with a quick, practical answer in 2-3 sentences. Then a short checklist.",
        "takeaways_label": "Quick wins",
        "df_section_title": "How Codeteki fits in",
        "closing_cta": "One-line CTA. No hype.",
    },
    {
        "lead": "Start with a mistake people make, then show the better way.",
        "takeaways_label": "What to do first",
        "df_section_title": "Where Codeteki helps most",
        "closing_cta": "Soft CTA + invite to book a free strategy call.",
    },
    {
        "lead": "Start with a scenario (generic) and a clear outcome.",
        "takeaways_label": "Key points",
        "df_section_title": "How Codeteki solves this",
        "closing_cta": "CTA focused on booking a free strategy call at codeteki.au/contact.",
    },
]


def pick_structure_variant(seed_text: str) -> dict:
    """Pick a stable structure variant based on topic text."""
    h = hashlib.md5(seed_text.encode("utf-8")).hexdigest()
    idx = int(h[:2], 16) % len(STRUCTURE_VARIANTS)
    return STRUCTURE_VARIANTS[idx]


def classify_keyword(keyword: str) -> dict:
    """Classify keyword by search intent and characteristics."""
    kw = keyword.lower().strip()
    words = kw.split()

    classification = {
        'intent': 'informational',
        'is_question': False,
        'is_long_tail': len(words) > 5,
        'word_count_range': (1200, 1600),
        'max_exact_uses': 3,
        'intent_label': 'Broad informational',
    }

    question_starters = {
        'how', 'what', 'where', 'when', 'why', 'which', 'who',
        'can', 'do', 'does', 'is', 'are', 'should',
    }
    if (words and words[0] in question_starters) or kw.endswith('?'):
        classification['is_question'] = True
        classification['intent_label'] = 'Question-based'
        classification['word_count_range'] = (800, 1100)
        classification['max_exact_uses'] = 2

    commercial_words = {
        'best', 'top', 'review', 'reviews', 'compare',
        'comparison', 'vs', 'alternative', 'alternatives', 'trusted',
        'verified', 'recommended', 'reliable',
    }
    if any(w in commercial_words for w in words):
        classification['intent'] = 'commercial'
        classification['intent_label'] = 'Commercial comparison'
        classification['word_count_range'] = (900, 1200)

    transactional_words = {
        'price', 'pricing', 'cost', 'plan', 'plans', 'package',
        'packages', 'buy', 'purchase', 'subscribe', 'free',
        'trial', 'discount', 'affordable', 'cheap',
    }
    if any(w in transactional_words for w in words):
        classification['intent'] = 'transactional'
        classification['intent_label'] = 'Transactional'
        classification['word_count_range'] = (700, 1000)

    au_cities = {
        'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide',
        'canberra', 'hobart', 'darwin', 'gold coast', 'newcastle',
    }
    location_signals = {'near', 'nearby', 'local', 'area', 'suburb', 'region'}
    if (any(city in kw for city in au_cities) or
            any(w in location_signals for w in words) or 'near me' in kw):
        if classification['intent'] == 'informational':
            classification['intent'] = 'local'
            classification['intent_label'] = 'Local search'
            classification['word_count_range'] = (900, 1200)

    if classification['is_long_tail']:
        classification['max_exact_uses'] = 2

    return classification


_DENSITY_STOPWORDS = frozenset({
    'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
    'by', 'from', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
    'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might', 'can',
    'i', 'my', 'me', 'we', 'our', 'you', 'your', 'it', 'its',
    'where', 'what', 'when', 'how', 'which', 'who', 'whom',
    'this', 'that', 'these', 'those', 'not', 'no', 'so',
})


def calculate_keyword_density(content: str, keyword: str) -> float:
    """Calculate keyword density as a percentage."""
    if not content or not keyword:
        return 0.0

    clean = re.sub(r'[#*_\[\]()>`~|]', ' ', content)
    clean = re.sub(r'https?://\S+', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip().lower()

    total_words = len(clean.split())
    if total_words == 0:
        return 0.0

    keyword_lower = keyword.lower().strip()
    kw_parts = keyword_lower.split()

    if len(kw_parts) > 6:
        core = [w.rstrip('?.,!') for w in kw_parts
                if w.rstrip('?.,!') not in _DENSITY_STOPWORDS and len(w.rstrip('?.,!')) > 2]
        if len(core) >= 2:
            present = [w for w in core if re.search(r'\b' + re.escape(w) + r'\b', clean)]
            if len(present) >= 2:
                selected = sorted(present, key=len, reverse=True)[:4]
                term_densities = []
                for term in selected:
                    term_count = len(re.findall(r'\b' + re.escape(term) + r'\b', clean))
                    term_densities.append(term_count / total_words * 100)
                density = sum(term_densities) / len(term_densities)
                return round(density, 2)
            elif len(present) == 1:
                kw_parts = present
                keyword_lower = present[0]
            else:
                return 0.0

    exact_count = clean.count(keyword_lower)

    flex_count = 0
    if len(kw_parts) >= 2:
        filler = 3 if len(kw_parts) <= 4 else 4
        pattern = r'\b' + rf'\b(?:\s+\w+){{0,{filler}}}\s+\b'.join(
            re.escape(w) for w in kw_parts
        ) + r'\b'
        flex_count = len(re.findall(pattern, clean))

    count = max(exact_count, flex_count)
    density = (count * len(kw_parts)) / total_words * 100
    return round(density, 2)


def calculate_readability_score(content: str) -> float:
    """Calculate Flesch Reading Ease score."""
    if not content:
        return 0.0

    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = max(len(sentences), 1)

    words = content.split()
    num_words = max(len(words), 1)

    def count_syllables(word):
        word = word.lower()
        if len(word) <= 3:
            return 1
        vowels = "aeiou"
        count = 0
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        if word.endswith('e'):
            count -= 1
        return max(count, 1)

    num_syllables = sum(count_syllables(word) for word in words)

    score = 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (num_syllables / num_words)
    return round(max(0, min(100, score)), 1)


def _simplify_complex_words(content: str, primary_keyword: str = '') -> str:
    """Replace common high-syllable words with simpler alternatives."""
    protected = set()
    if primary_keyword:
        protected = {w.lower().rstrip('?.,!:;') for w in primary_keyword.split()}

    lines = content.split('\n')
    simplified = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('http') or stripped.startswith('!['):
            simplified.append(line)
            continue
        for pattern, replacement in WORD_SIMPLIFICATIONS:
            base_word = pattern.replace(r'\b', '').lower()
            if base_word in protected:
                continue
            line = re.sub(
                pattern,
                lambda m, r=replacement: (r[0].upper() + r[1:] if m.group()[0].isupper() else r),
                line,
                flags=re.IGNORECASE,
            )
        simplified.append(line)
    return '\n'.join(simplified)


def _split_long_sentences(content: str, max_words: int = 14) -> str:
    """Break long sentences at natural split points (free, no API cost)."""
    split_patterns = [', and ', ', but ', ', which ', ', so ', ', yet ', '; ']
    lines = content.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if (not stripped or stripped.startswith('#') or stripped.startswith('-')
                or stripped.startswith('*') or stripped.startswith('!')
                or stripped.startswith('[') or stripped.startswith('http')
                or stripped.startswith('|')):
            result.append(line)
            continue

        modified = line
        for pat in split_patterns:
            parts = modified.split(pat)
            if len(parts) <= 1:
                continue
            rebuilt = []
            for i, part in enumerate(parts):
                part = part.strip()
                if i == 0:
                    rebuilt.append(part.rstrip('.') + '.')
                else:
                    if len(part.split()) >= 4 and len(rebuilt[-1].split()) >= 4:
                        part = part[0].upper() + part[1:] if part else part
                        rebuilt.append(part if part.endswith('.') else part)
                    else:
                        rebuilt[-1] = rebuilt[-1].rstrip('.') + pat + part
            modified = ' '.join(rebuilt)

        result.append(modified)
    return '\n'.join(result)


def _build_internal_linking_block(existing_articles: list = None) -> str:
    """Build prompt block for internal linking to existing blog articles."""
    if not existing_articles:
        return ''
    numbered = '\n'.join(f'{i+1}. {a}' for i, a in enumerate(existing_articles))
    return f"""INTERNAL LINKING — OUR EXISTING BLOG ARTICLES:
{numbered}

- Link to 2-3 relevant articles using markdown links with descriptive anchor text.
- Only link where it genuinely adds value. Do NOT link to every article.
- Place internal links naturally in the body, not clustered together."""


def _remove_duplicate_titles(md: str) -> str:
    """Remove duplicate H1 headings that gpt-4o-mini sometimes outputs."""
    lines = md.splitlines()
    out = []
    seen_h1 = False
    last_title = None

    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip().lower()
            if last_title == title:
                continue
            last_title = title
            if seen_h1:
                continue
            seen_h1 = True
        out.append(line)
    return "\n".join(out).strip()


def _dedupe_near_duplicate_sentences(md: str) -> str:
    """Remove near-duplicate sentences that restate the same point."""
    lines = md.splitlines()
    seen = set()
    out = []

    for line in lines:
        stripped = line.strip()
        if (not stripped or stripped.startswith("#") or
                stripped.startswith("- ") or stripped.startswith("* ") or
                stripped.startswith("1.") or stripped.startswith("[")):
            out.append(line)
            continue

        key = re.sub(r'\W+', ' ', stripped.lower()).strip()
        if len(key) < 40:
            out.append(line)
            continue

        if key in seen:
            continue
        seen.add(key)
        out.append(line)

    return "\n".join(out).strip()


def _readability_edit_pass(content: str, current_score: float) -> dict:
    """Quick API call to improve readability when Flesch score is too low."""
    prompt = f"""Improve this article's readability. Current Flesch score: {current_score}. Target: 60-70.

DO THIS:
1. Break every sentence over 12 words into two shorter sentences. Aim for 8-10 words average.
2. Replace long words with short ones:
   utilise->use, facilitate->help, numerous->many, comprehensive->full, demonstrate->show,
   approximately->about, subsequently->then, furthermore->also, additionally->also,
   particularly->especially, significant->big, regarding->about, innovative->new,
   opportunity->chance, essential->key, information->info, important->key,
   ensuring->making sure, identifying->spotting, overwhelming->too much,
   establishments->places, recommendations->tips, efficiently->fast,
   advertisements->ads, professionals->experts, frequently->often.
3. Remove filler: "it is important to note", "in order to", "there are many", "it should be noted", "when it comes to", "the fact that", "at the end of the day".
4. Keep ALL markdown formatting, headings, links, and lists exactly as they are.
5. Do NOT add or remove sections. Do NOT change the meaning.

Output ONLY the improved article:

{content}"""

    try:
        output_tokens = max(4000, len(content.split()) * 2)
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You simplify text. Break long sentences. Use simple words. "
                        "Change nothing else. Keep all markdown formatting."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=output_tokens,
            temperature=0.3,
        )

        improved = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        new_score = calculate_readability_score(improved)

        if new_score > current_score + 1:
            logger.info(f"Readability edit pass improved: {current_score} -> {new_score}")
            return {
                'content': improved,
                'tokens_used': tokens_used,
                'improved': True,
                'new_score': new_score,
            }

        logger.info(
            f"Readability edit pass didn't help enough: {current_score} -> {new_score}"
        )
        return {
            'content': content,
            'tokens_used': tokens_used,
            'improved': False,
            'new_score': current_score,
        }
    except Exception as e:
        logger.error(f"Readability edit pass failed: {e}")
        return {
            'content': content,
            'tokens_used': 0,
            'improved': False,
            'new_score': current_score,
        }


def generate_content_prompt(
    title_prompt: str,
    content_type: str,
    tone: str,
    target_word_count: int,
    keywords: list,
    primary_keyword: str = '',
    keyword_density_target: float = 1.0,
    include_faq: bool = False,
    faq_count: int = 5,
    outline: str = '',
    additional_instructions: str = '',
    humanization_techniques: list = None,
    existing_articles: list = None
) -> str:
    """Generate the prompt for content creation."""

    if humanization_techniques is None:
        humanization_techniques = DEFAULT_HUMANIZATION

    classification = classify_keyword(primary_keyword) if primary_keyword else {
        'intent': 'informational', 'is_question': False, 'is_long_tail': False,
        'word_count_range': (1200, 1600), 'max_exact_uses': 3,
        'intent_label': 'Broad informational',
    }
    intent = classification['intent']
    is_question = classification['is_question']

    type_instructions = {
        'blog': 'Write an engaging blog post that educates and informs readers.',
        'guide': 'Create a step-by-step guide that explains the topic.',
        'news': 'Write a news-style article with facts, quotes, and timely information.',
        'comparison': 'Create a balanced comparison article weighing pros and cons.',
        'listicle': 'Write an engaging list-format article with clear numbered points.',
        'how_to': 'Create a practical how-to article with actionable steps.',
        'case_study': 'Write a detailed case study with real examples and outcomes.',
    }

    tone_instructions = {
        'professional': 'Maintain a professional, authoritative tone while being accessible.',
        'conversational': 'Write as if having a friendly conversation with the reader.',
        'educational': 'Focus on teaching and explaining concepts clearly.',
        'persuasive': 'Use persuasive language to convince readers of key points.',
        'friendly': 'Be warm, approachable, and relatable throughout.',
        'authoritative': 'Establish expertise and authority on the subject matter.',
    }

    if keywords:
        secondary_kws = [kw for kw in keywords if kw.lower().strip() != primary_keyword.lower().strip()] if primary_keyword else keywords
        keywords_text = '\n'.join(f'  - {kw}' for kw in secondary_kws[:20])
    else:
        keywords_text = '  (none provided)'

    wmax = target_word_count
    wmin = int(target_word_count * 0.85)

    additional_block = ''
    if additional_instructions:
        additional_block = f"""
=== CREATOR INSTRUCTIONS (HIGH PRIORITY) ===
{additional_instructions}
=== END CREATOR INSTRUCTIONS ===
"""

    humanization_lines = []
    for tech in humanization_techniques:
        if tech in HUMANIZATION_TECHNIQUES:
            humanization_lines.append(f"- {HUMANIZATION_TECHNIQUES[tech]}")
    humanization_text = '\n'.join(humanization_lines) if humanization_lines else "- Write naturally like a human expert"

    variant = pick_structure_variant(title_prompt + (primary_keyword or ""))

    max_uses = classification['max_exact_uses']
    kw_len = len(primary_keyword.split()) if primary_keyword else 0
    if classification['is_long_tail']:
        kw_block = f"""KEYWORD STRATEGY:
Primary keyword: "{primary_keyword}" ({classification['intent_label']}, {kw_len}-word keyword)
- Use exact phrase only {max_uses} times (title + intro or conclusion).
- Everywhere else: natural variations, shorter phrases, semantic equivalents.
- Google ranks semantic coverage, not repetition. Expand depth instead.
- NEVER repeat the same phrase in consecutive paragraphs."""
    else:
        kw_block = f"""KEYWORD STRATEGY:
Primary keyword: "{primary_keyword}" ({classification['intent_label']})
- Use exact phrase {max_uses} times max (title, intro, conclusion).
- Everywhere else: natural variations, synonyms, reworded versions.
- Google ranks semantic coverage, not repetition. Expand depth instead.
- NEVER repeat the same phrase in consecutive paragraphs."""

    if intent == 'informational' and is_question:
        structure_block = f"""ARTICLE STRUCTURE (question — answer first):
1. H1 title (include primary keyword or close variation)
2. Direct answer in 2-3 sentences — answer the question immediately
3. {variant["takeaways_label"]} (3-5 bullet points)
4. 4-6 H2 sections expanding the answer with practical detail
5. One "{variant["df_section_title"]}" H2 (in the middle, not at the end)
6. {variant["closing_cta"]}"""
    elif intent == 'commercial':
        structure_block = f"""ARTICLE STRUCTURE (commercial — help the reader decide):
1. H1 title (include primary keyword or close variation)
2. {variant["lead"]}
3. Decision criteria (4-6 factors to evaluate)
4. 5-7 H2 sections: comparison angles, trust factors, pros/cons, real examples
5. One "{variant["df_section_title"]}" H2 (in the middle, not at the end)
6. {variant["closing_cta"]}"""
    elif intent == 'transactional':
        structure_block = f"""ARTICLE STRUCTURE (transactional — practical and direct):
1. H1 title (include primary keyword or close variation)
2. {variant["lead"]}
3. 4-5 H2 sections: pricing factors, what affects cost, mistakes to avoid, decision framework
4. One "{variant["df_section_title"]}" H2 (in the middle, not at the end)
5. {variant["closing_cta"]}"""
    elif intent == 'local':
        structure_block = f"""ARTICLE STRUCTURE (local — geographic and trust signals):
1. H1 title (include primary keyword or close variation)
2. {variant["lead"]}
3. {variant["takeaways_label"]} (4-6 points)
4. 5-7 H2 sections: geographic signals, local examples, trust signals, practical steps
5. One "{variant["df_section_title"]}" H2 (in the middle, not at the end)
6. {variant["closing_cta"]}"""
    else:
        structure_block = f"""ARTICLE STRUCTURE:
1. H1 title (include primary keyword or close variation)
2. {variant["lead"]}
3. {variant["takeaways_label"]} (bullet list, 4-6 points)
4. 6-8 H2 sections with practical, detailed content
5. One "{variant["df_section_title"]}" H2 (in the middle, not at the end)
6. {variant["closing_cta"]}"""

    if include_faq:
        structure_block += f"\n- {faq_count} FAQ questions at the end using natural long-tail queries"
    structure_block += "\n- Most H2 sections should include a bullet or numbered list."

    faq_words = faq_count * 50 if include_faq else 0
    body_words = wmax - 150 - faq_words
    words_per_section = max(150, body_words // 7)

    prompt = f"""Write a blog article for Codeteki (codeteki.au).

TOPIC: {title_prompt}
TYPE: {content_type} — {type_instructions.get(content_type, type_instructions['blog'])}
TONE: {tone} — {tone_instructions.get(tone, tone_instructions['professional'])}
LENGTH: You MUST write at least {wmin} words (target {wmax}). Each H2 section should be {words_per_section}-{words_per_section + 50} words. Add more H2 sections if under {wmin} words. Do NOT pad with filler — add real content.
{additional_block}
{"OUTLINE:" + chr(10) + outline if outline else ""}

{kw_block}

Secondary keywords (weave in naturally):
{keywords_text}

{structure_block}

ENTITY COVERAGE:
Cover 10+ related subtopics naturally: AI chatbots, voice AI, automation, custom websites, CRM, Australian cities, small business challenges, ROI, productivity, customer experience. Depth beats repetition.

AUTHORITY SIGNALS (required):
- NEVER define common terms. Skip to HOW.
  BAD: "An AI chatbot is a software program that simulates human conversation."
  GOOD: "Most chatbots are glorified FAQ pages. Here's how to build one that actually converts."
- ONE counter-intuitive insight (something most readers get wrong).
- ONE common mistake with real consequences.
- ONE prioritisation framework (ranked list or "do X before Y").
- 3-5 red flags or warning signs to watch for.
- Concrete numbers, not abstract claims. "Boosts efficiency" -> "Cuts response time by 73%."

WRITING STYLE:
BAD: "AI chatbots are crucial for building trust. They provide genuine support to customers."
GOOD: "Chatbots matter. But only if they're smart. Dumb ones waste your time. Custom-built ones fix that."

Write like the GOOD examples. Short. Punchy. Human. Never academic or formal.

AVOID: "can feel overwhelming", "in today's digital world", "comprehensive guide", "this article will explore", "it's important to note", "when it comes to". Each H2 must add new value. No reworded repetition of earlier points.

{humanization_text}
- Use contractions (don't, won't, isn't).
- Start some sentences with But, And, So, Yet.
- Include Australian cities where relevant (Sydney, Melbourne, Brisbane, Perth).

{HOUSE_RULES}

ABOUT CODETEKI:
Melbourne-based AI solutions agency — custom-built AI chatbots, voice AI agents, websites, business automation, and CRM for Australian businesses. No monthly fees on many solutions, transparent flat-rate pricing. Services: AI chatbot development, AI voice assistants, custom website development, business automation, AI-powered CRM. Phone: 0424 538 777. Website: codeteki.au. Current year: 2026.
When the topic is about AI tools, chatbots, automation, or business technology — Codeteki builds custom solutions for this. Feature the relevant service prominently. Explain how it solves the reader's problem.

{_build_internal_linking_block(existing_articles)}

Use Markdown formatting throughout."""

    return prompt


def generate_meta_prompt(title: str, content_excerpt: str, primary_keyword: str, keywords: list) -> str:
    """Generate prompt for meta tags."""
    return f"""Based on this article:

Title: {title}
Primary Keyword: {primary_keyword}
Keywords: {', '.join(keywords) if keywords else 'general'}
Content Preview: {content_excerpt[:500]}...

Generate SEO-optimized meta tags:

1. META TITLE (50-60 characters, include primary keyword naturally):

2. META DESCRIPTION (150-160 characters, compelling and includes primary keyword):

3. EXCERPT/SUMMARY (2-3 sentences for previews):

4. SUGGESTED TAGS (5-8 comma-separated tags):

Output as JSON with keys: meta_title, meta_description, excerpt, tags"""


def generate_faq_schema(faq_items: list) -> dict:
    """Generate FAQ schema markup."""
    if not faq_items:
        return None

    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item.get('question', ''),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item.get('answer', '')
                }
            }
            for item in faq_items
        ]
    }


def generate_article_schema(
    title: str,
    description: str,
    url: str = '',
    author_name: str = 'Codeteki',
    published_date: str = None,
    image_url: str = ''
) -> dict:
    """Generate Article schema markup."""
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "author": {
            "@type": "Organization",
            "name": author_name
        },
        "publisher": {
            "@type": "Organization",
            "name": "Codeteki",
            "logo": {
                "@type": "ImageObject",
                "url": "https://codeteki.au/static/images/logo.png"
            }
        },
        "datePublished": published_date or timezone.now().isoformat(),
        "dateModified": timezone.now().isoformat(),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": url
        },
        "image": image_url if image_url else None
    }


def extract_faq_from_content(content: str) -> list:
    """Extract FAQ items from generated content."""
    faq_items = []

    faq_match = re.search(r'##?\s*(?:FAQ|Frequently Asked Questions)(.*?)(?=##|$)', content, re.IGNORECASE | re.DOTALL)

    if faq_match:
        faq_section = faq_match.group(1)

        qa_pattern = r'\*\*Q[:\.]?\s*(.+?)\*\*\s*\n\s*A[:\.]?\s*(.+?)(?=\*\*Q|\Z)'
        matches = re.findall(qa_pattern, faq_section, re.IGNORECASE | re.DOTALL)

        for q, a in matches:
            faq_items.append({
                'question': q.strip(),
                'answer': a.strip()
            })

        if not faq_items:
            alt_pattern = r'(?:^|\n)\s*\d+\.\s*\*\*(.+?)\*\*\s*\n(.+?)(?=\n\s*\d+\.|$)'
            matches = re.findall(alt_pattern, faq_section, re.DOTALL)
            for q, a in matches:
                faq_items.append({
                    'question': q.strip().rstrip('?') + '?',
                    'answer': a.strip()
                })

    return faq_items


def generate_content(
    title_prompt: str,
    content_type: str = 'blog',
    tone: str = 'professional',
    target_word_count: int = 1500,
    keywords: list = None,
    primary_keyword: str = '',
    keyword_density_target: float = 1.0,
    include_meta_tags: bool = True,
    include_schema: bool = True,
    include_faq: bool = False,
    faq_count: int = 5,
    humanization_enabled: bool = True,
    humanization_techniques: list = None,
    outline: str = '',
    additional_instructions: str = '',
    model: str = 'gpt-4o-mini',
    existing_articles: list = None
) -> dict:
    """
    Generate SEO-optimized, humanized content.

    Returns dict with:
    - title, content, meta_title, meta_description, excerpt, tags
    - faq, schema, word_count, readability_score, keyword_density, tokens_used
    """

    if keywords is None:
        keywords = []

    if humanization_techniques is None:
        humanization_techniques = DEFAULT_HUMANIZATION if humanization_enabled else []

    result = {
        'title': '',
        'content': '',
        'meta_title': '',
        'meta_description': '',
        'excerpt': '',
        'tags': '',
        'faq': [],
        'schema': None,
        'word_count': 0,
        'readability_score': 0,
        'keyword_density': 0,
        'tokens_used': 0,
        'error': None
    }

    try:
        classification = classify_keyword(primary_keyword) if primary_keyword else None
        if classification:
            wmin, wmax = classification['word_count_range']
            logger.info(
                f"Keyword classified: intent={classification['intent']}, "
                f"label={classification['intent_label']}, "
                f"word_range={wmin}-{wmax}, "
                f"max_exact={classification['max_exact_uses']}, "
                f"user_target={target_word_count}"
            )

        content_prompt = generate_content_prompt(
            title_prompt=title_prompt,
            content_type=content_type,
            tone=tone,
            target_word_count=target_word_count,
            keywords=keywords,
            primary_keyword=primary_keyword,
            keyword_density_target=keyword_density_target,
            include_faq=include_faq,
            faq_count=faq_count,
            outline=outline,
            additional_instructions=additional_instructions,
            humanization_techniques=humanization_techniques,
            existing_articles=existing_articles
        )

        effective_wc = max(target_word_count, classification['word_count_range'][1] if classification else 1500)
        output_tokens = max(5000, min(12000, int(effective_wc * 2.5)))

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": content_prompt}
            ],
            max_tokens=output_tokens,
            temperature=0.7,
        )

        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        content = _remove_duplicate_titles(content)

        title_match = re.search(r'^#\s*(.+?)$', content, re.MULTILINE)
        generated_title = title_match.group(1).strip() if title_match else title_prompt

        faq_items = []
        if include_faq:
            faq_items = extract_faq_from_content(content)

        result['title'] = generated_title
        result['content'] = content
        result['faq'] = faq_items
        result['tokens_used'] = tokens_used

        # Post-processing: code-based readability improvements (free)
        content = _simplify_complex_words(content, primary_keyword=primary_keyword)
        content = _split_long_sentences(content)
        result['content'] = content

        # Readability edit pass (API) if still too low
        readability_score = calculate_readability_score(content)
        for attempt in range(2):
            if readability_score >= 60:
                break
            logger.info(
                f"Readability {readability_score} < 60, running edit pass "
                f"(attempt {attempt + 1}/2)..."
            )
            edit_result = _readability_edit_pass(content, readability_score)
            if edit_result['improved']:
                content = edit_result['content']
                content = _simplify_complex_words(content, primary_keyword=primary_keyword)
                content = _split_long_sentences(content)
                result['content'] = content
                readability_score = calculate_readability_score(content)
                if include_faq:
                    faq_items = extract_faq_from_content(content)
                    result['faq'] = faq_items
            else:
                result['tokens_used'] += edit_result['tokens_used']
                break
            result['tokens_used'] += edit_result['tokens_used']

        # Deduplicate near-identical sentences (free)
        content = _dedupe_near_duplicate_sentences(content)
        result['content'] = content

        # Proofread pass (API)
        proof = proofread_content(content, model=model)
        if not proof.get('error'):
            content = proof['content']
            content = _simplify_complex_words(content, primary_keyword=primary_keyword)
            content = _split_long_sentences(content)
            result['content'] = content
            result['tokens_used'] += proof.get('tokens_used', 0)
            title_match = re.search(r'^#\s*(.+?)$', content, re.MULTILINE)
            if title_match:
                generated_title = title_match.group(1).strip()
                result['title'] = generated_title
            if include_faq:
                faq_items = extract_faq_from_content(content)
                result['faq'] = faq_items

        # Generate meta tags
        if include_meta_tags:
            meta_prompt = generate_meta_prompt(
                title=generated_title,
                content_excerpt=content[:1000],
                primary_keyword=primary_keyword,
                keywords=keywords
            )

            meta_response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an SEO expert. Output only valid JSON."},
                    {"role": "user", "content": meta_prompt}
                ],
                max_tokens=500,
                temperature=0.5,
            )

            meta_content = meta_response.choices[0].message.content
            result['tokens_used'] += meta_response.usage.total_tokens

            try:
                json_match = re.search(r'\{[^{}]*\}', meta_content, re.DOTALL)
                if json_match:
                    meta_data = json.loads(json_match.group())
                    result['meta_title'] = meta_data.get('meta_title', '')[:70]
                    result['meta_description'] = meta_data.get('meta_description', '')[:160]
                    result['excerpt'] = meta_data.get('excerpt', '')[:300]
                    result['tags'] = meta_data.get('tags', '')
            except json.JSONDecodeError:
                result['meta_title'] = generated_title[:60]
                result['meta_description'] = content[:160].replace('\n', ' ').strip()
                result['excerpt'] = content[:300].replace('\n', ' ').strip()

        # Generate schema if requested
        if include_schema:
            schema = generate_article_schema(
                title=generated_title,
                description=result['meta_description'] or content[:160]
            )
            if faq_items:
                faq_schema = generate_faq_schema(faq_items)
                result['schema'] = [schema, faq_schema]
            else:
                result['schema'] = schema

        # Calculate metrics
        result['word_count'] = len(content.split())
        result['readability_score'] = calculate_readability_score(content)
        if primary_keyword:
            result['keyword_density'] = calculate_keyword_density(content, primary_keyword)

    except Exception as e:
        logger.error(f"Content generation failed: {e}", exc_info=True)
        result['error'] = str(e)

    return result


def proofread_content(
    content: str,
    model: str = 'gpt-4o-mini'
) -> dict:
    """AI-powered proofreading: fix spelling, grammar, typos, and awkward phrasing."""

    if not content or not content.strip():
        return {'content': content, 'corrections': [], 'tokens_used': 0, 'error': 'No content to proofread'}

    prompt = f"""You are a professional proofreader. Fix ALL spelling mistakes, grammar errors, typos, and awkward phrasing in the following article.

RULES:
1. Fix every spelling error, typo, and grammatical mistake
2. Fix truncated/broken words (e.g. "eof hours" -> "every few hours", "miricky" -> "tricky")
3. Fix missing spaces between words (e.g. "timeexpect" -> "time zones, expect")
4. Preserve ALL markdown formatting (headings, bold, links, lists, etc.)
5. Preserve ALL URLs and markdown links exactly as they are
6. Do NOT change the meaning, tone, or style of the content
7. Do NOT add new content or remove existing content
8. Do NOT rephrase sentences unless they are grammatically broken
9. Keep the same structure and heading hierarchy
10. Use AUSTRALIAN English spelling (colour, flavour, fibre, organise, analyse, centre, defence, licence). Do NOT convert to American English.

IMPORTANT: Output ONLY the corrected article. Do NOT add any corrections list, summary of changes, or any other text after the article.

CONTENT TO PROOFREAD:
{content}"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a meticulous professional proofreader using Australian English. Fix errors precisely without changing the author's voice or meaning. Preserve all markdown formatting and links. Output ONLY the corrected article - never append corrections lists or summaries."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000,
            temperature=0.2,
        )

        result_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        proofread = result_text
        corrections_pattern = re.split(
            r'\n-{2,}\s*\n*\s*CORRECTIONS\s*-{0,}\s*\n',
            proofread, maxsplit=1, flags=re.IGNORECASE
        )
        if len(corrections_pattern) > 1:
            proofread = corrections_pattern[0].strip()

        lines = proofread.rstrip().split('\n')
        while lines and re.match(r'^[-\u2022*]\s*["\']?.+?["\']?\s*\u2192\s*.+', lines[-1]):
            lines.pop()
        proofread = '\n'.join(lines).rstrip()

        return {
            'content': proofread,
            'corrections': [],
            'tokens_used': tokens_used,
            'error': None
        }

    except Exception as e:
        logger.error(f"Proofreading failed: {e}", exc_info=True)
        return {
            'content': content,
            'corrections': [],
            'tokens_used': 0,
            'error': str(e)
        }


def suggest_topics_from_keywords(
    keywords: list,
    num_suggestions: int = 5,
    model: str = 'gpt-4o-mini',
    additional_instructions: str = '',
    existing_articles: list = None
) -> dict:
    """Analyze keywords and suggest blog topics with content type and search intent."""

    if not keywords:
        return {'suggestions': [], 'tokens_used': 0, 'error': 'No keywords provided'}

    keywords_text = '\n'.join(keywords)

    creator_block = ''
    if additional_instructions:
        creator_block = f"""
CREATOR INSTRUCTIONS (follow these closely):
{additional_instructions}
"""

    existing_block = ''
    if existing_articles:
        numbered = '\n'.join(f'{i+1}. {a}' for i, a in enumerate(existing_articles))
        existing_block = f"""
EXISTING ARTICLES ON OUR BLOG (DO NOT suggest overlapping topics):
{numbered}

Suggest topics that COMPLEMENT the above — different angles, subtopics, or themes NOT already covered.
"""

    prompt = f"""Analyze these keywords and suggest {num_suggestions} high-potential blog topics for Codeteki (codeteki.au), a Melbourne-based AI solutions agency building custom AI chatbots, voice AI agents, websites, and business automation for Australian businesses.

KEYWORDS:
{keywords_text}
{creator_block}{existing_block}
For each suggestion, provide:
1. A compelling, specific blog topic/title that INCLUDES the primary keyword (or its closest variation) in the title
2. Content type: blog, guide, listicle, how_to, comparison, case_study
3. Search intent: informational, commercial, transactional, navigational
4. A recommended primary keyword from the list above (the single best keyword to optimise for)
5. 8-12 secondary keywords from the list that should be used in the article
6. Why this topic would rank well (brief reasoning)

CRITICAL — SERVICE PROMOTION RULES:
- The ENTIRE PURPOSE of this blog is to SELL Codeteki's services: custom website development, AI chatbots, voice AI agents, business automation, CRM, and SEO.
- Every topic MUST be framed from the perspective of a BUSINESS OWNER who needs these services — NOT a developer learning to code.
- NEVER suggest topics that teach people how to build things themselves (tutorials, dev environments, learning resources, coding courses). Our readers are BUYERS, not builders.
- NEVER recommend external tools, platforms, frameworks, or competitors. Codeteki IS the solution.
- Topics should make readers think "I need to hire Codeteki" — not "I'll do it myself".

GOOD topic angles:
- "Why Your Business Needs a Custom Website (Not a DIY Builder)" — sells our web dev service
- "How Much Does a Professional Website Cost in Australia?" — captures commercial intent, positions Codeteki
- "What to Look for When Hiring a Web Development Agency in Melbourne" — positions Codeteki as the answer
- "How AI Chatbots Save Small Businesses 20+ Hours a Week" — sells our chatbot service

BAD topic angles (NEVER suggest these):
- "How to Set Up a Local Development Environment" — teaches DIY, doesn't sell our service
- "Recommended Online Courses for Full-Stack Development" — helps competitors learn, not our customers buy
- "Top Tools for Professional Web Development Workflows" — recommends tools instead of hiring us
- "Compare Popular Front-End JavaScript Frameworks" — developer content, not buyer content

SEO-AWARE TOPIC RULES:
- Each suggested title MUST contain a high-value keyword from the list.
- Titles should target search-intent phrases business owners actually type: "how much does", "cost of", "why you need", "benefits of hiring", "what to look for".
- Prioritise COMMERCIAL and TRANSACTIONAL intent keywords over purely informational ones.
- Suggest topics that naturally support TOPICAL AUTHORITY for web development services, AI solutions, and business automation.
- Do NOT append the year to titles unless genuinely time-sensitive.
- Topics MUST drive traffic to Codeteki — every article should make readers want to book a strategy call or request a quote.
- Do NOT suggest "Top 10" or "Best X" listicles unless the creator instructions explicitly request them.

Output as JSON array:
[
  {{
    "topic": "The complete title here",
    "content_type": "blog",
    "intent": "informational",
    "primary_keyword": "the single best keyword to target",
    "secondary_keywords": ["keyword1", "keyword2", "keyword3"],
    "reasoning": "Brief explanation of why this topic would rank well"
  }}
]

Return ONLY the JSON array, no other text."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an SEO content strategist for Codeteki, a Melbourne-based web development and AI agency. Your job is to suggest blog topics that SELL Codeteki's services to business owners. Never suggest developer tutorials or DIY content. Every topic must make readers want to hire Codeteki. Output only valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.7,
        )

        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        try:
            content = content.strip()
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            content = content.strip()

            suggestions = json.loads(content)

            for suggestion in suggestions:
                if 'topic' not in suggestion:
                    suggestion['topic'] = 'Untitled Topic'
                if 'content_type' not in suggestion:
                    suggestion['content_type'] = 'blog'
                if 'intent' not in suggestion:
                    suggestion['intent'] = 'informational'
                if 'reasoning' not in suggestion:
                    suggestion['reasoning'] = ''

            return {
                'suggestions': suggestions,
                'tokens_used': tokens_used,
                'error': None
            }

        except json.JSONDecodeError:
            return {
                'suggestions': [{
                    'topic': f"Blog post about: {', '.join(keywords[:3])}",
                    'content_type': 'blog',
                    'intent': 'informational',
                    'reasoning': 'Generated from provided keywords'
                }],
                'tokens_used': tokens_used,
                'error': None
            }

    except Exception as e:
        logger.error(f"Topic suggestion failed: {e}", exc_info=True)
        return {
            'suggestions': [],
            'tokens_used': 0,
            'error': str(e)
        }
