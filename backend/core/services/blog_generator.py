"""
AI Blog Generator Service

Generates human-like, SEO-optimized blog posts from multiple data sources:
- Ubersuggest keyword CSVs
- Prompt ideas CSVs
- Competitor keyword analysis
- Backlink opportunities
- Manual topics

Key Features:
- Smart CSV scanning and auto-detection
- Human-like writing to avoid AI detection
- Codeteki service alignment
- SEO optimization
"""

from __future__ import annotations

import csv
import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from django.utils import timezone
from django.utils.text import Truncator, slugify

from ..models import BlogPost, BlogCategory, BlogGenerationJob
from .ai_client import AIContentEngine


# =============================================================================
# CSV TYPE DETECTION PATTERNS
# =============================================================================

CSV_TYPE_PATTERNS = {
    'prompts': {
        'headers': ['prompt', 'intent', 'brands', 'update', 'brands_mentioned'],
        'required': ['prompt'],
        'topic_field': 'prompt',
    },
    'keywords': {
        'headers': ['keyword', 'keywords', 'search_volume', 'volume', 'sd', 'pd', 'cpc', 'seo_difficulty'],
        'required': ['keyword', 'keywords'],
        'topic_field': 'keyword',
    },
    'competitors': {
        'headers': ['domain', 'competitor', 'traffic', 'keywords_count', 'organic_keywords'],
        'required': ['domain', 'competitor'],
        'topic_field': 'domain',
    },
    'backlinks': {
        'headers': ['source_url', 'target_url', 'anchor_text', 'anchor', 'domain_authority', 'da'],
        'required': ['source_url', 'anchor_text', 'anchor'],
        'topic_field': 'anchor_text',
    },
}


# =============================================================================
# CODETEKI SERVICE ALIGNMENT
# =============================================================================

CODETEKI_SERVICES = {
    'ai_chatbots': {
        'keywords': ['chatbot', 'chat bot', 'customer service', 'support', 'ai assistant', '24/7', 'live chat'],
        'name': 'AI Chatbot Development',
        'url': '/services/ai-chatbot-development/',
        'mention': 'AI chatbots that handle customer inquiries 24/7',
    },
    'voice_ai': {
        'keywords': ['voice', 'phone', 'call', 'ivr', 'receptionist', 'ai voice', 'phone automation'],
        'name': 'AI Voice Assistant',
        'url': '/services/ai-voice-assistant/',
        'mention': 'AI voice agents that answer calls and book appointments',
    },
    'web_development': {
        'keywords': ['website', 'web design', 'web development', 'ecommerce', 'custom website', 'landing page'],
        'name': 'Custom Website Development',
        'url': '/services/custom-website/',
        'mention': 'custom-built websites with AI integration',
    },
    'automation': {
        'keywords': ['automation', 'workflow', 'integration', 'efficiency', 'automate', 'process'],
        'name': 'Business Automation',
        'url': '/services/business-automation/',
        'mention': 'workflow automation that eliminates repetitive tasks',
    },
    'crm': {
        'keywords': ['crm', 'sales', 'leads', 'pipeline', 'outreach', 'email marketing', 'sales automation'],
        'name': 'AI-Powered CRM',
        'url': '/services/ai-crm/',
        'mention': 'AI-powered CRM that automates your sales pipeline',
    },
}


# =============================================================================
# HUMAN-LIKE WRITING INSTRUCTIONS
# =============================================================================

HUMAN_WRITING_RULES = """
CRITICAL: Write like a real human expert, NOT like AI. Your writing MUST:

1. VARY sentence length dramatically. Short punchy ones. Then longer, more complex sentences that wind through multiple ideas before finally arriving at their conclusion.

2. Start sentences with "And" or "But" occasionally - it's how humans actually write.

3. Use Australian English: colour, optimise, realise, analyse, centre, travelled.

4. Include personal observations: "In my experience...", "What I've noticed is...", "Here's the thing..."

5. Reference specific Australian things: mention Melbourne, Sydney, Brisbane, tradies, small business culture.

6. AVOID these AI giveaways at all costs:
   - "In today's digital age" / "In today's fast-paced world"
   - "Leverage" / "Utilize" (just say "use")
   - "Cutting-edge" / "State-of-the-art"
   - "It's important to note that..."
   - "In conclusion" (just wrap up naturally)
   - "Whether you're a... or a..."
   - Starting multiple paragraphs the same way

7. Have OPINIONS. Don't be wishy-washy. Say "This approach works better" not "This approach might potentially work better for some businesses".

8. Use contractions naturally: don't, can't, won't, it's, they're, we've.

9. Include specific numbers and examples: "A Melbourne cafe reduced their phone calls by 73%" not "businesses have seen significant reductions".

10. Break grammar rules for effect. Fragment sentences. Like this. For emphasis.

11. Use casual interjections: "Look," "Here's the thing," "The reality is," "Honestly,".

12. End some paragraphs with short, punchy statements. Makes an impact.
"""


CODETEKI_CONTEXT = """
About Codeteki (the company publishing this blog):
- Melbourne-based AI solutions agency
- Services: AI chatbots, voice agents, custom websites, business automation, CRM
- Key differentiator: No monthly fees on many solutions, transparent pricing
- Target audience: Australian small-to-medium businesses
- Expertise: Custom-built solutions, not cookie-cutter templates
- Phone: 0424 538 777
- Website: codeteki.au

When mentioning Codeteki:
- Be subtle and natural, never salesy
- Use phrases like "At agencies like Codeteki, we've seen..."
- Reference as a local example: "Melbourne-based solutions like..."
- Don't force the name in - only mention where genuinely relevant
"""


# =============================================================================
# SMART CSV SCANNER
# =============================================================================

class SmartCSVScanner:
    """Auto-detects CSV type and extracts blog-worthy topics."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.headers: List[str] = []
        self.rows: List[Dict] = []
        self.detected_type: str = ''

    def scan(self) -> Dict:
        """
        Scan the CSV file and return analysis results.

        Returns:
            dict with: detected_type, headers, row_count, sample_data, suggested_topics
        """
        self._parse_csv()
        self.detected_type = self._detect_type()
        topics = self._extract_topics()

        return {
            'detected_type': self.detected_type,
            'headers': self.headers,
            'row_count': len(self.rows),
            'sample_data': self.rows[:5],
            'suggested_topics': topics[:50],  # Limit to top 50
        }

    def _parse_csv(self):
        """Parse CSV file with flexible encoding handling."""
        path = Path(self.file_path)

        # Try different encodings
        for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    self.headers = [self._normalize_header(h) for h in (reader.fieldnames or [])]
                    self.rows = list(reader)
                return
            except (UnicodeDecodeError, csv.Error):
                continue

        raise ValueError(f"Could not parse CSV file: {self.file_path}")

    def _normalize_header(self, header: str) -> str:
        """Normalize header to lowercase with underscores."""
        if not header:
            return ''
        return re.sub(r'[^a-z0-9]+', '_', header.strip().lower()).strip('_')

    def _detect_type(self) -> str:
        """Detect CSV type based on headers."""
        headers_lower = [h.lower() for h in self.headers]

        for csv_type, pattern in CSV_TYPE_PATTERNS.items():
            # Check if any required field is present
            required_found = any(
                any(req in h for h in headers_lower)
                for req in pattern['required']
            )
            if required_found:
                return csv_type

        return 'unknown'

    def _extract_topics(self) -> List[Dict]:
        """Extract blog-worthy topics from the data."""
        if not self.rows:
            return []

        topics = []
        topic_field = self._get_topic_field()

        for row in self.rows:
            # Get the topic text
            topic_text = self._get_value(row, topic_field)
            if not topic_text or len(topic_text) < 10:
                continue

            # Extract additional metadata
            intent = self._get_value(row, 'intent') or 'informational'
            volume = self._safe_int(self._get_value(row, 'search_volume', 'volume', 'searches'))

            topics.append({
                'topic': topic_text.strip(),
                'intent': intent.lower().strip(),
                'search_volume': volume,
                'original_row': row,
            })

        # Sort by search volume if available, otherwise by topic length
        topics.sort(key=lambda x: (x['search_volume'] or 0, len(x['topic'])), reverse=True)
        return topics

    def _get_topic_field(self) -> str:
        """Get the field name that contains topics."""
        pattern = CSV_TYPE_PATTERNS.get(self.detected_type, {})
        return pattern.get('topic_field', 'keyword')

    def _get_value(self, row: Dict, *field_names: str) -> Optional[str]:
        """Get value from row, trying multiple possible field names."""
        for field in field_names:
            # Try exact match
            if field in row:
                return row[field]
            # Try normalized match
            for key in row.keys():
                if self._normalize_header(key) == field:
                    return row[key]
        return None

    def _safe_int(self, value: Optional[str]) -> Optional[int]:
        """Safely convert to integer."""
        if not value:
            return None
        try:
            # Remove commas, extract digits
            digits = re.sub(r'[^\d]', '', str(value))
            return int(digits) if digits else None
        except (ValueError, TypeError):
            return None


# =============================================================================
# HUMAN-LIKE BLOG WRITER
# =============================================================================

class HumanLikeBlogWriter:
    """
    Generates blog posts that read naturally and avoid AI detection.

    Uses sophisticated prompting to produce content that:
    - Varies sentence structure
    - Includes personal observations
    - Uses Australian English
    - References real places and examples
    - Avoids common AI writing patterns
    """

    def __init__(self, ai_engine: Optional[AIContentEngine] = None):
        self.ai_engine = ai_engine or AIContentEngine()

    def generate(
        self,
        topic: str,
        *,
        intent: str = 'informational',
        keywords: Optional[List[str]] = None,
        word_count: int = 1500,
        writing_style: str = 'conversational',
        include_services: bool = True,
        related_services: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate a human-like blog post.

        Args:
            topic: The main topic/title for the blog post
            intent: Search intent (informational, commercial, transactional)
            keywords: Additional keywords to include
            word_count: Target word count
            writing_style: conversational, professional, technical, casual
            include_services: Whether to naturally reference Codeteki services
            related_services: Specific services to potentially reference

        Returns:
            dict with: title, excerpt, content, keywords, meta_description
        """
        # Find relevant services if not specified
        if include_services and not related_services:
            related_services = self._find_related_services(topic, keywords or [])

        # Build the prompt
        prompt = self._build_prompt(
            topic=topic,
            intent=intent,
            keywords=keywords or [],
            word_count=word_count,
            writing_style=writing_style,
            related_services=related_services or [],
        )

        # Generate content
        result = self.ai_engine.generate(
            prompt=prompt,
            temperature=0.7,  # Higher for more human-like variation
            system_prompt=self._get_system_prompt(writing_style),
        )

        if not result.get('success'):
            raise ValueError(f"AI generation failed: {result.get('error', 'Unknown error')}")

        # Parse the response
        return self._parse_response(result.get('output', ''), topic)

    def _find_related_services(self, topic: str, keywords: List[str]) -> List[str]:
        """Find Codeteki services relevant to the topic."""
        topic_lower = topic.lower()
        all_text = ' '.join([topic_lower] + [k.lower() for k in keywords])

        related = []
        for service_key, service_data in CODETEKI_SERVICES.items():
            for keyword in service_data['keywords']:
                if keyword in all_text:
                    related.append(service_key)
                    break

        return related[:2]  # Limit to 2 services per post

    def _get_system_prompt(self, style: str) -> str:
        """Get system prompt based on writing style."""
        style_instructions = {
            'conversational': "You're having a chat with a business owner friend. Be helpful, relatable, and real.",
            'professional': "You're a respected industry consultant. Authoritative but approachable.",
            'technical': "You're a senior developer explaining to other technical folks. Be precise but not dry.",
            'casual': "You're a friendly local expert. Keep it light, practical, and unpretentious.",
        }

        return f"""You are a senior content writer for Codeteki, a Melbourne-based AI solutions agency.

{style_instructions.get(style, style_instructions['conversational'])}

{CODETEKI_CONTEXT}

{HUMAN_WRITING_RULES}

Remember: Your goal is to write content that helps businesses, not content that sells services.
The best marketing is genuinely useful content. Be that.
"""

    def _build_prompt(
        self,
        topic: str,
        intent: str,
        keywords: List[str],
        word_count: int,
        writing_style: str,
        related_services: List[str],
    ) -> str:
        """Build the content generation prompt."""

        # Service context if applicable
        service_context = ""
        if related_services:
            services_info = []
            for svc_key in related_services:
                svc = CODETEKI_SERVICES.get(svc_key, {})
                if svc:
                    services_info.append(f"- {svc['name']}: {svc['mention']}")
            if services_info:
                service_context = f"""
RELEVANT CODETEKI SERVICES (mention naturally if appropriate, don't force):
{chr(10).join(services_info)}
"""

        keywords_str = ', '.join(keywords) if keywords else 'derive from topic'

        return f"""Write a comprehensive blog post about:

TOPIC: {topic}

SEARCH INTENT: {intent}
TARGET KEYWORDS: {keywords_str}
TARGET LENGTH: {word_count} words minimum
STYLE: {writing_style}
{service_context}

STRUCTURE REQUIREMENTS:
1. Title (H1) - Compelling, keyword-rich but natural
2. Excerpt - 2 sentences that hook the reader (put this right after the title)
3. Introduction - Hook them immediately, no clichés
4. 3-5 main sections (H2) - Each with practical value
5. Conclusion - Natural wrap-up with subtle CTA

FORMAT:
Return the blog post in clean Markdown format:
- Start with # for title
- Put excerpt as the first paragraph (2 sentences max)
- Use ## for section headers
- Use bullet points and numbered lists where natural
- Include bold text for emphasis on key points

DO NOT include:
- Meta information like "Title:" or "Excerpt:"
- Word count notes
- Instructions or commentary
- Markdown code fences around the content

Just write the blog post as if it's going straight to publication.
"""

    def _parse_response(self, raw_output: str, original_topic: str) -> Dict:
        """Parse AI response into structured blog data."""
        content = raw_output.strip()

        # Extract title (first H1)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else original_topic

        # Extract excerpt (first paragraph after title)
        excerpt = ''
        lines = content.split('\n')
        in_content = False
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                in_content = True
                continue
            if in_content and line and not line.startswith('#'):
                excerpt = line
                break

        # Truncate excerpt to 300 chars
        if len(excerpt) > 300:
            excerpt = excerpt[:297] + '...'

        # Generate meta description from excerpt
        meta_description = excerpt[:155] + '...' if len(excerpt) > 155 else excerpt

        # Extract keywords from content
        keywords = self._extract_keywords(content)

        return {
            'title': title,
            'excerpt': excerpt,
            'content': content,
            'keywords': keywords,
            'meta_description': meta_description,
        }

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract likely keywords from content."""
        # Simple extraction: find bold text and H2 headers
        keywords = []

        # Bold text
        bold_matches = re.findall(r'\*\*([^*]+)\*\*', content)
        keywords.extend([b.lower().strip() for b in bold_matches[:5]])

        # H2 headers
        h2_matches = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        for h2 in h2_matches[:3]:
            # Clean and add
            clean = re.sub(r'[^\w\s]', '', h2.lower()).strip()
            if len(clean) < 50:
                keywords.append(clean)

        return list(set(keywords))[:10]


# =============================================================================
# BLOG GENERATION JOB PROCESSOR
# =============================================================================

class BlogGenerationProcessor:
    """Processes BlogGenerationJob to create blog posts."""

    def __init__(self, job: BlogGenerationJob):
        self.job = job
        self.scanner = None
        self.writer = HumanLikeBlogWriter()

    def scan(self) -> Dict:
        """Scan the CSV file and update job with results."""
        if not self.job.csv_file:
            if self.job.source_type == BlogGenerationJob.SOURCE_MANUAL_TOPICS:
                return self._scan_manual_topics()
            raise ValueError("No CSV file uploaded")

        self.job.status = BlogGenerationJob.STATUS_SCANNING
        self.job.save(update_fields=['status'])

        try:
            self.scanner = SmartCSVScanner(self.job.csv_file.path)
            results = self.scanner.scan()

            self.job.detected_type = results['detected_type']
            self.job.scan_results = results
            self.job.status = BlogGenerationJob.STATUS_PENDING
            self.job.save(update_fields=['detected_type', 'scan_results', 'status'])

            return results

        except Exception as e:
            self.job.status = BlogGenerationJob.STATUS_FAILED
            self.job.error_message = str(e)
            self.job.save(update_fields=['status', 'error_message'])
            raise

    def _scan_manual_topics(self) -> Dict:
        """Scan manual topics from text field."""
        topics = []
        for line in (self.job.manual_topics or '').strip().split('\n'):
            line = line.strip()
            if line and len(line) > 10:
                topics.append({
                    'topic': line,
                    'intent': 'informational',
                    'search_volume': None,
                    'original_row': {},
                })

        results = {
            'detected_type': 'manual',
            'headers': [],
            'row_count': len(topics),
            'sample_data': [],
            'suggested_topics': topics,
        }

        self.job.detected_type = 'manual'
        self.job.scan_results = results
        self.job.save(update_fields=['detected_type', 'scan_results'])

        return results

    def generate(self, topics: Optional[List[Dict]] = None) -> List[BlogPost]:
        """Generate blog posts from selected topics."""
        if topics is None:
            # Use topics from scan results
            topics = self.job.scan_results.get('suggested_topics', [])

        if not topics:
            raise ValueError("No topics to generate content for")

        # Limit to max_posts
        topics = topics[:self.job.max_posts]

        self.job.status = BlogGenerationJob.STATUS_GENERATING
        self.job.selected_topics = [t['topic'] for t in topics]
        self.job.save(update_fields=['status', 'selected_topics'])

        created_posts = []
        errors = []

        for i, topic_data in enumerate(topics):
            try:
                post = self._generate_single_post(topic_data, i)
                created_posts.append(post)
                self.job.generated_count = len(created_posts)
                self.job.save(update_fields=['generated_count'])

            except Exception as e:
                errors.append(f"Topic '{topic_data['topic'][:50]}': {str(e)}")
                continue

        # Update final status
        if created_posts:
            self.job.status = BlogGenerationJob.STATUS_COMPLETED
        else:
            self.job.status = BlogGenerationJob.STATUS_FAILED
            self.job.error_message = '\n'.join(errors)

        self.job.save(update_fields=['status', 'error_message'])

        return created_posts

    def _generate_single_post(self, topic_data: Dict, index: int) -> BlogPost:
        """Generate a single blog post."""
        topic = topic_data['topic']
        intent = topic_data.get('intent', 'informational')

        # Generate content
        result = self.writer.generate(
            topic=topic,
            intent=intent,
            word_count=self.job.target_word_count,
            writing_style=self.job.writing_style,
            include_services=self.job.include_services,
        )

        # Create unique slug
        slug = self._unique_slug(result['title'])

        # Create blog post
        post = BlogPost.objects.create(
            title=result['title'],
            slug=slug,
            excerpt=Truncator(result['excerpt']).chars(320),
            content=result['content'],
            author='Codeteki Team',
            blog_category=self.job.target_category,
            tags=', '.join(result['keywords']),
            focus_keyword=topic[:100],
            meta_title=result['title'][:70],
            meta_description=result['meta_description'][:160],
            status='published' if self.job.auto_publish else 'draft',
            is_published=self.job.auto_publish,
            published_at=timezone.now() if self.job.auto_publish else None,
            ai_generated=True,
            reading_time_minutes=max(3, self.job.target_word_count // 200),
        )

        return post

    def _unique_slug(self, title: str) -> str:
        """Generate a unique slug."""
        base_slug = slugify(title) or 'blog-post'
        slug = base_slug[:80]  # Limit length
        counter = 2

        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug[:75]}-{counter}"
            counter += 1

        return slug


# =============================================================================
# LEGACY SUPPORT - Keep existing BlogContentGenerator for backward compatibility
# =============================================================================

class BlogContentGenerator:
    """Legacy blog generator from SEO keyword clusters."""

    def __init__(self, upload, ai_engine: AIContentEngine | None = None):
        self.upload = upload
        self.ai_engine = ai_engine or AIContentEngine()

    def generate(self, *, cluster_limit: int = 3, category: str = "Insights") -> Dict[str, object]:
        """Generate blogs from SEO keyword clusters."""
        clusters = list(
            self.upload.clusters.order_by("-priority_score", "-avg_volume")[:cluster_limit]
        )
        if not clusters:
            raise ValueError("Upload must have processed keyword clusters before generating blogs.")

        cluster_payload = [
            {
                "label": cluster.label,
                "intent": cluster.intent,
                "avg_volume": cluster.avg_volume,
                "priority_score": float(cluster.priority_score),
                "top_keywords": [
                    keyword.keyword
                    for keyword in cluster.keywords.order_by("-priority_score")[:5]
                ],
            }
            for cluster in clusters
        ]

        prompt = (
            "You are a senior content strategist at Codeteki. Based on the keyword clusters below, "
            "propose detailed blog drafts that will perform well organically.\n"
            f"Keyword data: {json.dumps(cluster_payload, ensure_ascii=False)}\n"
            "Return ONLY a JSON array. Each item requires:\n"
            "  - title: Compelling H1\n"
            "  - excerpt: 2 sentence summary under 300 characters\n"
            "  - outline: bullet list of H2/H3 structure\n"
            "  - content: markdown blog draft 600-800 words referencing the provided keywords\n"
            "  - keywords: array of keywords you used in the article\n"
            "No markdown fences, no commentary, just raw JSON."
        )

        result = self.ai_engine.generate(prompt=prompt, temperature=0.4)
        if not result.get("success"):
            error = result.get("error") or "AI blog generation failed."
            raise ValueError(error)

        posts_payload = self._parse_response(result.get("output", ""))
        created_posts = self._persist_posts(posts_payload, category)

        return {
            "created": len(created_posts),
            "post_ids": [post.id for post in created_posts],
            "ai_enabled": self.ai_engine.enabled,
            "model": self.ai_engine.model,
        }

    def _parse_response(self, raw_output: str) -> List[Dict[str, object]]:
        json_blob = self._extract_json(raw_output)
        try:
            data = json.loads(json_blob)
        except json.JSONDecodeError as exc:
            raise ValueError(f"AI response could not be parsed: {exc}") from exc

        if isinstance(data, dict):
            possible = data.get("posts") or data.get("blog_posts")
            if possible:
                data = possible
            else:
                data = [data]
        if not isinstance(data, list):
            raise ValueError("AI response was not a list of blog drafts.")
        return data

    @staticmethod
    def _extract_json(raw_output: str) -> str:
        text = raw_output.strip()
        if text.startswith("```"):
            parts = text.split("```")
            if len(parts) >= 3:
                text = parts[1 if parts[1].strip() else 2]
        text = text.strip()
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1:
            return text[start : end + 1]
        return text

    def _persist_posts(self, posts_payload: List[Dict[str, object]], category: str) -> List[BlogPost]:
        created: List[BlogPost] = []
        for entry in posts_payload:
            title = (entry.get("title") or "").strip()
            content = (entry.get("content") or "").strip()
            if not title or not content:
                continue

            excerpt = (entry.get("excerpt") or "").strip()
            if not excerpt:
                excerpt = Truncator(content).chars(300)
            keywords = entry.get("keywords") or []
            tags = ", ".join(keywords)[:255]

            slug = self._unique_slug(title)
            post = BlogPost.objects.create(
                title=title,
                slug=slug,
                excerpt=Truncator(excerpt).chars(320),
                content=content,
                author="Codeteki Automation",
                category=category,
                tags=tags,
                is_featured=False,
                is_published=False,
                ai_generated=True,
            )
            created.append(post)
        return created

    def _unique_slug(self, title: str) -> str:
        base = slugify(title) or slugify(f"{self.upload.name}-{len(title)}") or "blog-post"
        slug = base
        counter = 2
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base}-{counter}"
            counter += 1
        return slug
