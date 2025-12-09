"""
Management command to sync all pages to PageSEO.
Creates SEO entries for all services, blog posts, and static pages.
"""
from django.core.management.base import BaseCommand
from core.models import PageSEO, Service, BlogPost


class Command(BaseCommand):
    help = 'Sync all pages (services, blogs, static) to PageSEO entries'

    def handle(self, *args, **options):
        created = 0
        updated = 0

        # Static pages
        static_pages = [
            ('home', 'Home', 'Codeteki - AI-Powered Business Solutions'),
            ('services', 'Services', 'Our Services - AI, Automation & Web Development'),
            ('ai-tools', 'AI Tools', 'AI Tools for Business Productivity'),
            ('demos', 'Demos', 'Product Demos & Showcases'),
            ('faq', 'FAQ', 'Frequently Asked Questions'),
            ('contact', 'Contact', 'Contact Us - Get in Touch'),
            ('about', 'About', 'About Codeteki'),
            ('pricing', 'Pricing', 'Pricing Plans'),
        ]

        for page_key, page_name, default_title in static_pages:
            seo, was_created = PageSEO.objects.get_or_create(
                page=page_key,
                service__isnull=True,
                blog_post__isnull=True,
                defaults={
                    'meta_title': default_title,
                    'meta_description': f'{page_name} - Codeteki provides AI-powered solutions for Australian businesses.',
                }
            )
            if was_created:
                created += 1
                self.stdout.write(f'  ✅ Created: {page_name}')
            else:
                updated += 1

        # Services
        for service in Service.objects.all():
            seo, was_created = PageSEO.objects.get_or_create(
                service=service,
                defaults={
                    'page': 'custom',
                    'meta_title': f'{service.title} | Codeteki',
                    'meta_description': service.description[:320] if service.description else f'{service.title} services for Australian businesses.',
                    'target_keyword': service.title.lower(),
                }
            )
            if was_created:
                created += 1
                self.stdout.write(f'  ✅ Created: Service - {service.title}')
            else:
                updated += 1

        # Blog Posts
        for post in BlogPost.objects.filter(status='published'):
            seo, was_created = PageSEO.objects.get_or_create(
                blog_post=post,
                defaults={
                    'page': 'custom',
                    'meta_title': f'{post.title} | Codeteki Blog',
                    'meta_description': post.excerpt[:320] if post.excerpt else f'{post.title}',
                    'target_keyword': post.title.lower()[:100],
                }
            )
            if was_created:
                created += 1
                self.stdout.write(f'  ✅ Created: Blog - {post.title}')
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Done! Created: {created}, Already existed: {updated}'
        ))
