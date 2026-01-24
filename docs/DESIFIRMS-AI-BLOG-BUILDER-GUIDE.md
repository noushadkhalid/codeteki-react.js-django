# AI Blog Builder Implementation Guide for Desi Firms

Complete guide to implementing the AI Blog Builder in the Desi Firms project. Copy and paste this with Claude Code to set up the feature.

---

## Overview

The AI Blog Builder:
- Auto-detects CSV type from Ubersuggest exports (prompts, keywords, competitors, backlinks)
- Extracts blog-worthy topics from any data source
- Generates human-like, SEO-optimized blog posts
- Aligns content with Desi Firms services naturally
- Avoids AI detection patterns

---

## Prerequisites

Ensure Desi Firms has:
- Django project set up
- Blog model (similar to `BlogPost`)
- Admin interface (Django Unfold recommended)
- OpenAI API configured
- Celery for background tasks (optional but recommended)

---

## Implementation Prompt for Claude Code

Copy and paste the following prompt:

```
I need to implement an AI Blog Builder in the Desi Firms project. Here's what to build:

## 1. Create BlogGenerationJob Model

Add to your main models file:

```python
class BlogGenerationJob(models.Model):
    """Tracks AI blog generation requests."""

    SOURCE_CHOICES = [
        ('auto_detect', '🔍 Auto-Detect CSV Type'),
        ('csv_prompts', '💡 Prompt Ideas CSV'),
        ('csv_keywords', '🔑 Keywords CSV'),
        ('csv_competitors', '🏆 Competitor Keywords'),
        ('csv_backlinks', '🔗 Backlink Opportunities'),
        ('manual_topics', '✏️ Manual Topics'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scanning', 'Scanning Data'),
        ('generating', 'Generating Content'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    STYLE_CHOICES = [
        ('conversational', 'Conversational (Recommended)'),
        ('professional', 'Professional'),
        ('technical', 'Technical/Expert'),
        ('casual', 'Casual/Friendly'),
    ]

    name = models.CharField(max_length=255, help_text="Descriptive name for this job")
    source_type = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='auto_detect')
    csv_file = models.FileField(upload_to='blog/generation/', blank=True, null=True)
    manual_topics = models.TextField(blank=True, help_text="One topic per line")

    # Settings
    target_word_count = models.PositiveIntegerField(default=1500)
    writing_style = models.CharField(max_length=50, choices=STYLE_CHOICES, default='conversational')
    include_services = models.BooleanField(default=True)
    auto_publish = models.BooleanField(default=False)
    target_category = models.ForeignKey('BlogCategory', null=True, blank=True, on_delete=models.SET_NULL)
    max_posts = models.PositiveIntegerField(default=5)

    # Results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    detected_type = models.CharField(max_length=50, blank=True)
    scan_results = models.JSONField(default=dict, blank=True)
    selected_topics = models.JSONField(default=list, blank=True)
    generated_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog Generation Job'

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
```

## 2. Create Blog Generator Service

Create `services/blog_generator.py`:

```python
import csv
import io
import re
import logging
from typing import Optional
from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)


# ============================================================================
# CSV TYPE DETECTION PATTERNS
# ============================================================================

CSV_TYPE_PATTERNS = {
    'prompts': {
        'headers': ['prompt', 'intent', 'brands', 'update'],
        'required': ['prompt'],
        'description': 'Prompt Ideas CSV from Ubersuggest',
    },
    'keywords': {
        'headers': ['keyword', 'search volume', 'sd', 'pd', 'cpc', 'trend'],
        'required': ['keyword'],
        'description': 'Keywords Export from Ubersuggest',
    },
    'competitors': {
        'headers': ['domain', 'traffic', 'keywords', 'backlinks', 'traffic cost'],
        'required': ['domain'],
        'description': 'Competitor Analysis CSV',
    },
    'backlinks': {
        'headers': ['source', 'target', 'anchor', 'domain authority', 'page authority'],
        'required': ['source', 'anchor'],
        'description': 'Backlink Opportunities CSV',
    },
}


# ============================================================================
# DESI FIRMS CONTEXT - CUSTOMIZE THIS FOR YOUR BUSINESS
# ============================================================================

DESIFIRMS_CONTEXT = """
About Desi Firms:
- Australia's premier South Asian business directory
- Services: Business listings, deals, events, AI tools for businesses
- Target audience: South Asian businesses and consumers in Australia
- Key features: Free business listings, promotional deals, event promotion
- Mission: Connecting the South Asian business community in Australia
"""

DESIFIRMS_SERVICES = {
    'business_listings': {
        'keywords': ['listing', 'directory', 'business profile', 'visibility', 'local business'],
        'service_page': '/list-your-business/',
    },
    'deals_promotions': {
        'keywords': ['deals', 'promotions', 'discounts', 'offers', 'coupons'],
        'service_page': '/deals/',
    },
    'events': {
        'keywords': ['events', 'community', 'cultural', 'networking', 'gatherings'],
        'service_page': '/events/',
    },
    'ai_tools': {
        'keywords': ['ai', 'automation', 'tools', 'technology', 'digital'],
        'service_page': '/ai-tools/',
    },
}


# ============================================================================
# HUMAN WRITING RULES - CRITICAL FOR AVOIDING AI DETECTION
# ============================================================================

HUMAN_WRITING_RULES = """
CRITICAL: Write like a real human expert, NOT an AI:

1. VARY your sentence length dramatically. Use fragments. Sometimes. Then write a longer, more complex sentence that flows naturally and provides depth to your argument.

2. Start some sentences with "And" or "But" or "So" - this is how people actually talk and write informally.

3. Include personal observations and anecdotes ("In my experience working with local businesses...", "I've seen this mistake countless times...")

4. Use Australian English spelling (colour, optimise, realise, centre, organisation)

5. Reference real Australian things (mention suburbs like Parramatta, Dandenong, Harris Park; reference Australian business culture, the ATO, ABN requirements)

6. AVOID these AI tells at all costs:
   - "In today's digital age/landscape"
   - "leverage" (use "use" instead)
   - "cutting-edge" or "state-of-the-art"
   - "In conclusion" (just conclude naturally)
   - "It's important to note that"
   - "First and foremost"
   - "Look no further"
   - Lists that all start with the same word
   - Perfect parallel structure in every list

7. Have opinions - don't be neutral on everything. Say things like "Honestly, most businesses get this wrong" or "I'm not a fan of..."

8. Include specific numbers and examples (not round numbers - "47% of small businesses" not "about 50%")

9. Use contractions naturally (don't, can't, won't, it's, that's, we've)

10. Break grammar rules occasionally for effect. Like this.

11. Include colloquialisms and idioms ("at the end of the day", "no worries", "give it a go", "heaps of")

12. Vary paragraph length - some short. Some much longer with multiple connected thoughts that build on each other.
"""


# ============================================================================
# SMART CSV SCANNER
# ============================================================================

class SmartCSVScanner:
    """Auto-detects CSV type and extracts blog-worthy topics."""

    def scan(self, file_content: str) -> dict:
        """Scan CSV and return detected type, columns, and extracted topics."""
        try:
            # Handle BOM
            if file_content.startswith('\ufeff'):
                file_content = file_content[1:]

            reader = csv.DictReader(io.StringIO(file_content))
            headers = [h.lower().strip() for h in (reader.fieldnames or [])]
            rows = list(reader)

            detected_type = self._detect_type(headers)
            topics = self._extract_topics(rows, detected_type, headers)

            return {
                'success': True,
                'detected_type': detected_type,
                'headers': headers,
                'row_count': len(rows),
                'sample_rows': rows[:5],
                'extracted_topics': topics,
            }
        except Exception as e:
            logger.error(f"CSV scan error: {e}")
            return {'success': False, 'error': str(e)}

    def _detect_type(self, headers: list) -> str:
        """Detect CSV type based on headers."""
        headers_lower = [h.lower() for h in headers]

        for csv_type, pattern in CSV_TYPE_PATTERNS.items():
            required_found = all(
                any(req in h for h in headers_lower)
                for req in pattern['required']
            )
            if required_found:
                return csv_type

        return 'unknown'

    def _extract_topics(self, rows: list, csv_type: str, headers: list) -> list:
        """Extract blog-worthy topics from CSV data."""
        topics = []

        if csv_type == 'prompts':
            prompt_col = self._find_column(headers, ['prompt'])
            intent_col = self._find_column(headers, ['intent'])

            for row in rows:
                prompt = row.get(prompt_col, '').strip()
                intent = row.get(intent_col, '').strip() if intent_col else ''

                if prompt and len(prompt) > 10:
                    topics.append({
                        'title': prompt,
                        'intent': intent,
                        'type': 'prompt',
                    })

        elif csv_type == 'keywords':
            keyword_col = self._find_column(headers, ['keyword'])
            volume_col = self._find_column(headers, ['search volume', 'volume'])

            for row in rows:
                keyword = row.get(keyword_col, '').strip()
                volume = row.get(volume_col, '0') if volume_col else '0'

                if keyword and len(keyword) > 5:
                    topics.append({
                        'title': keyword,
                        'search_volume': self._parse_number(volume),
                        'type': 'keyword',
                    })

            # Sort by search volume
            topics.sort(key=lambda x: x.get('search_volume', 0), reverse=True)

        elif csv_type == 'competitors':
            domain_col = self._find_column(headers, ['domain', 'url'])

            for row in rows:
                domain = row.get(domain_col, '').strip()
                if domain:
                    topics.append({
                        'title': f"Competitor Analysis: {domain}",
                        'domain': domain,
                        'type': 'competitor',
                    })

        elif csv_type == 'backlinks':
            anchor_col = self._find_column(headers, ['anchor', 'anchor text'])
            source_col = self._find_column(headers, ['source', 'source url'])

            seen_anchors = set()
            for row in rows:
                anchor = row.get(anchor_col, '').strip()
                if anchor and anchor not in seen_anchors and len(anchor) > 3:
                    seen_anchors.add(anchor)
                    topics.append({
                        'title': anchor,
                        'type': 'backlink_anchor',
                    })

        return topics[:50]  # Limit to 50 topics

    def _find_column(self, headers: list, possible_names: list) -> Optional[str]:
        """Find column name from possible variations."""
        for header in headers:
            for name in possible_names:
                if name in header.lower():
                    return header
        return None

    def _parse_number(self, value: str) -> int:
        """Parse number from string, handling commas and K/M suffixes."""
        try:
            value = str(value).strip().replace(',', '')
            if value.endswith('K'):
                return int(float(value[:-1]) * 1000)
            if value.endswith('M'):
                return int(float(value[:-1]) * 1000000)
            return int(float(value))
        except:
            return 0


# ============================================================================
# HUMAN-LIKE BLOG WRITER
# ============================================================================

class HumanLikeBlogWriter:
    """Generates human-like, SEO-optimized blog posts."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_blog_post(
        self,
        topic: dict,
        word_count: int = 1500,
        writing_style: str = 'conversational',
        include_services: bool = True,
    ) -> dict:
        """Generate a complete blog post from a topic."""

        # Build the prompt
        prompt = self._build_prompt(topic, word_count, writing_style, include_services)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a senior content writer at Desi Firms, Australia's premier South Asian business directory.

{DESIFIRMS_CONTEXT}

{HUMAN_WRITING_RULES}

Your writing should feel authentic, helpful, and naturally connect with the South Asian business community in Australia."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # Higher for more variety
                max_tokens=4000,
            )

            content = response.choices[0].message.content

            # Parse the generated content
            return self._parse_blog_content(content)

        except Exception as e:
            logger.error(f"Blog generation error: {e}")
            return {'success': False, 'error': str(e)}

    def _build_prompt(
        self,
        topic: dict,
        word_count: int,
        writing_style: str,
        include_services: bool,
    ) -> str:
        """Build the generation prompt."""

        title = topic.get('title', '')
        intent = topic.get('intent', 'informational')
        topic_type = topic.get('type', 'general')

        service_instruction = ""
        if include_services:
            matched_services = self._match_services(title)
            if matched_services:
                service_instruction = f"""
NATURAL SERVICE MENTIONS:
Naturally weave in references to these relevant Desi Firms features where appropriate:
{', '.join(matched_services)}

BUT NEVER:
- Sound like an advertisement
- Use "our team" or "contact us today"
- Force the mention awkwardly

Instead use phrases like:
- "Platforms like Desi Firms are helping businesses..."
- "Many South Asian businesses are turning to community directories..."
- "Getting listed on relevant business directories can..."
"""

        return f"""
Write a comprehensive blog post on: "{title}"

TARGET LENGTH: {word_count} words minimum
WRITING STYLE: {writing_style}
SEARCH INTENT: {intent}

STRUCTURE:
1. Hook opening (NO clichés like "In today's world" - be creative)
2. 3-5 main sections with H2 headers
3. Practical advice and real examples
4. Connection to South Asian business community in Australia
5. Natural conclusion (no "In conclusion")

{service_instruction}

AUSTRALIAN CONTEXT:
- Reference Australian locations (Sydney, Melbourne, Brisbane suburbs)
- Mention Australian business realities (ABN, GST, local regulations)
- Use Australian English spelling

OUTPUT FORMAT:
Return ONLY the blog post in Markdown:
- Title as H1
- Brief excerpt (2 sentences) right after title
- H2 for main sections
- Bullet points where natural
- NO meta information or commentary
"""

    def _match_services(self, topic: str) -> list:
        """Find relevant Desi Firms services to mention."""
        topic_lower = topic.lower()
        matched = []

        for service_name, service_info in DESIFIRMS_SERVICES.items():
            for keyword in service_info['keywords']:
                if keyword in topic_lower:
                    matched.append(service_name.replace('_', ' ').title())
                    break

        return matched[:2]  # Max 2 services per post

    def _parse_blog_content(self, content: str) -> dict:
        """Parse generated content into structured data."""
        lines = content.strip().split('\n')

        # Extract title (first H1)
        title = ''
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break

        # Extract excerpt (usually first paragraph after title)
        excerpt = ''
        in_content = False
        for line in lines:
            if line.startswith('# '):
                in_content = True
                continue
            if in_content and line.strip() and not line.startswith('#'):
                excerpt = line.strip()
                break

        # Generate slug
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

        return {
            'success': True,
            'title': title,
            'slug': slug,
            'excerpt': excerpt[:300],
            'content': content,
            'word_count': len(content.split()),
        }


# ============================================================================
# BLOG GENERATION PROCESSOR
# ============================================================================

class BlogGenerationProcessor:
    """Orchestrates the blog generation workflow."""

    def __init__(self):
        self.scanner = SmartCSVScanner()
        self.writer = HumanLikeBlogWriter()

    def scan_job(self, job) -> dict:
        """Scan CSV and detect topics."""
        job.status = 'scanning'
        job.save()

        try:
            if job.source_type == 'manual_topics':
                topics = [
                    {'title': line.strip(), 'type': 'manual'}
                    for line in job.manual_topics.split('\n')
                    if line.strip()
                ]
                result = {
                    'success': True,
                    'detected_type': 'manual',
                    'extracted_topics': topics,
                }
            else:
                file_content = job.csv_file.read().decode('utf-8-sig')
                result = self.scanner.scan(file_content)

            if result['success']:
                job.detected_type = result.get('detected_type', 'unknown')
                job.scan_results = result
                job.selected_topics = result.get('extracted_topics', [])[:job.max_posts]
                job.status = 'pending'
            else:
                job.status = 'failed'
                job.error_message = result.get('error', 'Scan failed')

            job.save()
            return result

        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
            return {'success': False, 'error': str(e)}

    def generate_blogs(self, job, blog_model, category_model=None) -> dict:
        """Generate blog posts from scanned topics."""
        job.status = 'generating'
        job.save()

        created_posts = []
        errors = []

        topics = job.selected_topics[:job.max_posts]

        for i, topic in enumerate(topics):
            try:
                result = self.writer.generate_blog_post(
                    topic=topic,
                    word_count=job.target_word_count,
                    writing_style=job.writing_style,
                    include_services=job.include_services,
                )

                if result['success']:
                    # Create blog post
                    post = blog_model(
                        title=result['title'],
                        slug=result['slug'],
                        excerpt=result['excerpt'],
                        content=result['content'],
                        status='published' if job.auto_publish else 'draft',
                    )

                    if job.target_category:
                        post.category = job.target_category

                    post.save()
                    created_posts.append(post.id)
                    job.generated_count = len(created_posts)
                    job.save()

            except Exception as e:
                errors.append(f"Topic {i+1}: {str(e)}")

        if created_posts:
            job.status = 'completed'
        else:
            job.status = 'failed'
            job.error_message = '; '.join(errors)

        job.save()

        return {
            'success': len(created_posts) > 0,
            'created_count': len(created_posts),
            'created_posts': created_posts,
            'errors': errors,
        }
```

## 3. Create Admin Interface

Add to your admin.py:

```python
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import BlogGenerationJob
from .services.blog_generator import BlogGenerationProcessor


@admin.register(BlogGenerationJob)
class BlogGenerationJobAdmin(ModelAdmin):
    list_display = ['name', 'source_type_badge', 'status_badge', 'generated_count', 'created_at']
    list_filter = ['status', 'source_type', 'auto_publish']
    search_fields = ['name']
    readonly_fields = ['status', 'detected_type', 'scan_results', 'generated_count', 'error_message']

    fieldsets = (
        ('Job Details', {
            'fields': ('name', 'source_type'),
        }),
        ('Data Source', {
            'fields': ('csv_file', 'manual_topics'),
        }),
        ('Generation Settings', {
            'fields': ('target_word_count', 'writing_style', 'target_category', 'include_services', 'auto_publish', 'max_posts'),
        }),
        ('Results', {
            'fields': ('status', 'detected_type', 'generated_count', 'error_message'),
            'classes': ('collapse',),
        }),
    )

    actions = ['scan_csv', 'generate_blogs', 'preview_topics']

    def source_type_badge(self, obj):
        colors = {
            'auto_detect': '#6366f1',
            'csv_prompts': '#8b5cf6',
            'csv_keywords': '#06b6d4',
            'csv_competitors': '#f59e0b',
            'csv_backlinks': '#10b981',
            'manual_topics': '#64748b',
        }
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; border-radius:4px; font-size:11px;">{}</span>',
            colors.get(obj.source_type, '#64748b'),
            obj.get_source_type_display()
        )
    source_type_badge.short_description = 'Source'

    def status_badge(self, obj):
        colors = {
            'pending': '#64748b',
            'scanning': '#3b82f6',
            'generating': '#f59e0b',
            'completed': '#10b981',
            'failed': '#ef4444',
        }
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; border-radius:4px; font-size:11px;">{}</span>',
            colors.get(obj.status, '#64748b'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    @action(description="🔍 Scan CSV & Detect Topics")
    def scan_csv(self, request, queryset):
        processor = BlogGenerationProcessor()
        for job in queryset:
            if job.status in ['pending', 'failed']:
                result = processor.scan_job(job)
                if result['success']:
                    self.message_user(request, f"✅ Scanned '{job.name}': Found {len(job.selected_topics)} topics")
                else:
                    self.message_user(request, f"❌ Scan failed: {result.get('error')}", level='error')

    @action(description="🚀 Generate Blog Posts")
    def generate_blogs(self, request, queryset):
        from .models import BlogPost  # Your blog model
        processor = BlogGenerationProcessor()
        for job in queryset:
            if job.selected_topics:
                result = processor.generate_blogs(job, BlogPost)
                if result['success']:
                    self.message_user(request, f"✅ Generated {result['created_count']} posts from '{job.name}'")
                else:
                    self.message_user(request, f"❌ Generation failed: {result.get('errors')}", level='error')

    @action(description="👁️ Preview Detected Topics")
    def preview_topics(self, request, queryset):
        for job in queryset:
            topics = job.selected_topics[:10]
            if topics:
                topic_list = ', '.join([t.get('title', 'Unknown')[:50] for t in topics])
                self.message_user(request, f"📋 {job.name}: {topic_list}")
            else:
                self.message_user(request, f"⚠️ {job.name}: No topics found. Run 'Scan CSV' first.", level='warning')
```

## 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## 5. Test the System

1. Go to Admin → Blog Generation Jobs → Add
2. Upload a CSV from Ubersuggest
3. Run "Scan CSV & Detect Topics" action
4. Preview the detected topics
5. Run "Generate Blog Posts" action
6. Check generated posts in Blog Posts list

Make sure to update the import in the admin action to use your actual BlogPost model name.
```

---

## CSV Formats Supported

### Prompt Ideas CSV (Ubersuggest)
```csv
Prompt,Intent,Brands Mentioned,Update
"Best Indian restaurants in Sydney",navigational,"-","-"
"How to start a small business in Australia",informational,"-","-"
```

### Keywords CSV
```csv
Keyword,Search Volume,SD,PD,CPC
indian restaurant sydney,12000,45,35,1.20
halal food melbourne,8500,38,42,0.95
```

### Competitor Keywords
```csv
Domain,Traffic,Keywords,Backlinks
competitor1.com,50000,1200,340
competitor2.com,35000,890,210
```

### Backlink Opportunities
```csv
Source URL,Target URL,Anchor Text,Domain Authority
example.com/blog,yoursite.com,best indian food,45
```

---

## Customization Points

### 1. Update Business Context

Modify `DESIFIRMS_CONTEXT` in the service file to match your actual business description.

### 2. Update Services

Modify `DESIFIRMS_SERVICES` dictionary to match your actual service offerings and their relevant keywords.

### 3. Writing Style

Adjust `HUMAN_WRITING_RULES` if you want different writing patterns or cultural references.

### 4. Model Integration

Update the `generate_blogs` method to use your actual BlogPost model fields.

---

## Verification Checklist

- [ ] BlogGenerationJob model created and migrated
- [ ] Blog generator service file created
- [ ] Admin registered with actions
- [ ] Test CSV upload works
- [ ] Scan detects correct CSV type
- [ ] Topics extracted correctly
- [ ] Blog posts generated with human-like content
- [ ] Posts saved to database correctly
- [ ] Australian English used in content
- [ ] No obvious AI detection patterns in generated content

---

*Last updated: January 2026*
