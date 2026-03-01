"""
Admin views for the Simple Blog Builder.

Single-page interface for creating blog posts:
1. Enter keywords (paste or CSV upload)
2. Get AI topic suggestions
3. Configure generation settings
4. Generate and preview content
5. Save draft or publish
"""

import json
import csv
import io
import logging
from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger(__name__)

from .models import BlogPost, BlogCategory
from .services.blog_content_generator import (
    generate_content,
    suggest_topics_from_keywords,
    proofread_content,
    DEFAULT_HUMANIZATION,
    HUMANIZATION_TECHNIQUES,
)


@method_decorator(staff_member_required, name='dispatch')
class SimpleBlogBuilderView(View):
    """
    Single-page blog builder with unified workflow:
    - Keyword input (textarea + CSV upload)
    - AI topic suggestions
    - Quick generation settings
    - Live preview and editing
    - One-click publish options
    """

    template_name = 'admin/core/simple_builder.html'

    def get(self, request):
        """Render the simple blog builder page."""
        self.request = request
        context = admin.site.each_context(request)
        context.update(self.get_context_data())
        return render(request, self.template_name, context)

    def get_context_data(self):
        """Get context data for the template."""
        categories = BlogCategory.objects.filter(is_active=True).order_by('name')

        # Get existing blog posts for content awareness panel
        existing_posts = list(
            BlogPost.objects.filter(
                status__in=['published', 'draft', 'review']
            ).order_by('-published_at', '-created_at')
            .values('title', 'focus_keyword', 'slug', 'status', 'blog_category__name')[:100]
        )

        # Tone choices for the UI
        tone_choices = [
            ('conversational', 'Conversational (Recommended)'),
            ('professional', 'Professional'),
            ('friendly', 'Friendly'),
            ('educational', 'Educational'),
            ('authoritative', 'Authoritative'),
        ]

        # Content type choices
        content_type_choices = [
            ('blog', 'Blog Post'),
            ('listicle', 'Listicle'),
            ('guide', 'Guide/Tutorial'),
            ('how_to', 'How-To Article'),
            ('comparison', 'Comparison'),
        ]

        return {
            'title': 'AI Blog Builder',
            'categories': categories,
            'existing_posts': existing_posts,
            'content_types': content_type_choices,
            'tone_choices': tone_choices,
            'humanization_techniques': HUMANIZATION_TECHNIQUES,
            'default_humanization': DEFAULT_HUMANIZATION,
        }

    def post(self, request):
        """Handle AJAX requests for various builder actions."""
        try:
            data = json.loads(request.body)
            action = data.get('action')

            if action == 'suggest_topics':
                return self.handle_suggest_topics(request, data)
            elif action == 'generate':
                return self.handle_generate(request, data)
            elif action == 'proofread':
                return self.handle_proofread(request, data)
            elif action == 'save_draft':
                return self.handle_save_draft(request, data)
            elif action == 'publish':
                return self.handle_publish(request, data)
            elif action == 'parse_csv':
                return self.handle_parse_csv(request, data)
            else:
                return JsonResponse({'error': f'Unknown action: {action}'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Blog builder error: {e}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    def handle_suggest_topics(self, request, data):
        """Get AI topic suggestions from keywords."""
        keywords = data.get('keywords', [])

        if not keywords:
            return JsonResponse({'error': 'No keywords provided'}, status=400)

        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split('\n') if k.strip()]

        # Get existing post titles for deduplication
        existing_posts_qs = BlogPost.objects.filter(
            status__in=['published', 'draft', 'review']
        ).values_list('title', 'focus_keyword')[:100]
        existing_titles = [
            f'"{t}" (keyword: {pk or "none"})' for t, pk in existing_posts_qs
        ]

        additional_instructions = data.get('additional_instructions', '')
        result = suggest_topics_from_keywords(
            keywords,
            additional_instructions=additional_instructions,
            existing_articles=existing_titles,
        )

        if result.get('error'):
            return JsonResponse({'error': result['error']}, status=500)

        return JsonResponse({
            'suggestions': result['suggestions'],
            'tokens_used': result.get('tokens_used', 0),
        })

    def handle_generate(self, request, data):
        """Generate blog content with simplified parameters."""
        topic = data.get('topic')
        if not topic:
            return JsonResponse({'error': 'Topic is required'}, status=400)

        keywords = data.get('keywords', [])
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split('\n') if k.strip()]

        tone = data.get('tone', 'conversational')
        word_count = data.get('word_count', 1500)
        include_faq = data.get('include_faq', True)
        content_type = data.get('content_type', 'blog')
        primary_keyword = data.get('primary_keyword', keywords[0] if keywords else '')

        humanization_techniques = data.get('humanization_techniques', DEFAULT_HUMANIZATION)
        additional_instructions = data.get('additional_instructions', '')

        # Get published posts for internal linking
        existing_posts_qs = BlogPost.objects.filter(
            status='published'
        ).order_by('-published_at').values_list('title', 'focus_keyword', 'slug')[:50]
        existing_articles = [
            f'"{t}" | keyword: {pk or "none"} | URL: https://codeteki.au/blog/{s}/'
            for t, pk, s in existing_posts_qs
        ]

        result = generate_content(
            title_prompt=topic,
            content_type=content_type,
            tone=tone,
            target_word_count=word_count,
            keywords=keywords,
            primary_keyword=primary_keyword,
            keyword_density_target=1.0,
            include_meta_tags=True,
            include_schema=True,
            include_faq=include_faq,
            faq_count=5,
            humanization_enabled=True,
            humanization_techniques=humanization_techniques,
            additional_instructions=additional_instructions,
            existing_articles=existing_articles,
        )

        if result.get('error'):
            return JsonResponse({'error': result['error']}, status=500)

        blog_post_id = None
        if data.get('create_draft', False):
            category = self._resolve_category(None, result['tags'], result['title'])
            post = BlogPost.objects.create(
                title=result['title'],
                slug=self._unique_slug(result['title']),
                content=result['content'],
                excerpt=result['excerpt'][:320] if result['excerpt'] else '',
                tags=result['tags'],
                meta_title=result['meta_title'],
                meta_description=result['meta_description'],
                focus_keyword=primary_keyword,
                blog_category=category,
                author='Codeteki Team',
                ai_generated=True,
                status='draft'
            )
            blog_post_id = post.id

        return JsonResponse({
            'title': result['title'],
            'content': result['content'],
            'meta_title': result['meta_title'],
            'meta_description': result['meta_description'],
            'excerpt': result['excerpt'],
            'tags': result['tags'],
            'faq': result['faq'],
            'schema': result['schema'],
            'word_count': result['word_count'],
            'readability_score': result['readability_score'],
            'keyword_density': result['keyword_density'],
            'tokens_used': result['tokens_used'],
            'blog_post_id': blog_post_id,
        })

    def handle_proofread(self, request, data):
        """AI proofreading - fix spelling, grammar, and typos."""
        content = data.get('content', '')

        if not content.strip():
            return JsonResponse({'error': 'No content to proofread'}, status=400)

        result = proofread_content(content)

        if result.get('error'):
            return JsonResponse({'error': result['error']}, status=500)

        return JsonResponse({
            'content': result['content'],
            'corrections': result['corrections'],
            'tokens_used': result['tokens_used'],
        })

    def _resolve_category(self, category_id, tags, title):
        """Resolve or auto-create a blog category."""
        if category_id:
            try:
                return BlogCategory.objects.get(id=category_id)
            except BlogCategory.DoesNotExist:
                pass

        tag_list = []
        if isinstance(tags, list):
            tag_list = [t.strip() for t in tags if t.strip()]
        elif isinstance(tags, str) and tags.strip():
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]

        for tag in tag_list:
            match = BlogCategory.objects.filter(
                name__iexact=tag, is_active=True
            ).first()
            if match:
                return match

        if tag_list:
            cat_name = tag_list[0].title()
            cat, _ = BlogCategory.objects.get_or_create(
                name__iexact=cat_name,
                defaults={
                    'name': cat_name,
                    'slug': slugify(cat_name)[:50] or 'general',
                    'is_active': True,
                }
            )
            return cat

        cat, _ = BlogCategory.objects.get_or_create(
            name__iexact='General',
            defaults={
                'name': 'General',
                'slug': 'general',
                'is_active': True,
            }
        )
        return cat

    def _unique_slug(self, title: str) -> str:
        """Generate a unique slug."""
        base_slug = slugify(title) or 'blog-post'
        slug = base_slug[:80]
        counter = 2
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug[:75]}-{counter}"
            counter += 1
        return slug

    def handle_save_draft(self, request, data):
        """Save content as a draft blog post."""
        title = data.get('title')
        content = data.get('content')

        if not title or not content:
            return JsonResponse({'error': 'Title and content are required'}, status=400)

        category = self._resolve_category(
            data.get('category_id'),
            data.get('tags', ''),
            title
        )

        post_id = data.get('blog_post_id')
        if post_id:
            try:
                post = BlogPost.objects.get(id=post_id)
                post.title = title
                post.content = content
                post.excerpt = data.get('excerpt', '')[:320]
                post.meta_title = data.get('meta_title', '')
                post.meta_description = data.get('meta_description', '')
                post.tags = data.get('tags', '')
                post.focus_keyword = data.get('primary_keyword', '')
                post.blog_category = category
                post.author = 'Codeteki Team'
                post.save()
            except BlogPost.DoesNotExist:
                post_id = None

        if not post_id:
            post = BlogPost.objects.create(
                title=title,
                slug=self._unique_slug(title),
                content=content,
                excerpt=data.get('excerpt', '')[:320],
                tags=data.get('tags', ''),
                meta_title=data.get('meta_title', ''),
                meta_description=data.get('meta_description', ''),
                focus_keyword=data.get('primary_keyword', ''),
                blog_category=category,
                author='Codeteki Team',
                ai_generated=True,
                status='draft'
            )

        return JsonResponse({
            'blog_post_id': post.id,
            'slug': post.slug,
            'message': 'Draft saved successfully',
        })

    def handle_publish(self, request, data):
        """Publish a blog post."""
        post_id = data.get('blog_post_id')

        if not post_id:
            result = self.handle_save_draft(request, data)
            result_data = json.loads(result.content)
            if 'error' in result_data:
                return result
            post_id = result_data['blog_post_id']

        try:
            post = BlogPost.objects.get(id=post_id)
            post.status = 'published'
            post.is_published = True
            post.published_at = timezone.now()
            post.save()

            return JsonResponse({
                'blog_post_id': post.id,
                'slug': post.slug,
                'url': f'/blog/{post.slug}/',
                'message': 'Published successfully',
            })
        except BlogPost.DoesNotExist:
            return JsonResponse({'error': 'Blog post not found'}, status=404)

    def handle_parse_csv(self, request, data):
        """Parse uploaded CSV and extract keywords."""
        csv_content = data.get('csv_content', '')

        if not csv_content:
            return JsonResponse({'error': 'No CSV content provided'}, status=400)

        keywords = []

        try:
            if csv_content.startswith('\ufeff'):
                csv_content = csv_content[1:]

            reader = csv.DictReader(io.StringIO(csv_content))

            fieldnames_lower = {fn.lower().strip(): fn for fn in (reader.fieldnames or [])}

            keyword_columns = ['keyword', 'prompt', 'topic', 'title', 'query', 'search query',
                              'search term', 'term', 'phrase', 'target keyword']

            keyword_col = None
            for col in keyword_columns:
                if col in fieldnames_lower:
                    keyword_col = fieldnames_lower[col]
                    break

            if not keyword_col:
                keyword_col = reader.fieldnames[0] if reader.fieldnames else None

            if keyword_col:
                for row in reader:
                    kw = row.get(keyword_col, '').strip()
                    if kw and not kw.isdigit():
                        keywords.append(kw)

            return JsonResponse({
                'keywords': keywords,
                'total_found': len(keywords),
            })

        except Exception as e:
            return JsonResponse({'error': f'CSV parsing failed: {str(e)}'}, status=400)


# Function-based view wrapper for URL registration
def simple_blog_builder_view(request):
    """Function-based view wrapper for the SimpleBlogBuilderView."""
    return SimpleBlogBuilderView.as_view()(request)
