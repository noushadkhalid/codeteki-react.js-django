"""
Django signals for auto-creating PageSEO entries when new Services or BlogPosts are created.
This ensures all pages have SEO settings automatically.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='core.Service')
def create_service_seo(sender, instance, created, **kwargs):
    """Auto-create PageSEO entry when a new Service is created."""
    if created:
        from core.models import PageSEO
        PageSEO.objects.get_or_create(
            service=instance,
            defaults={
                'page': 'custom',
                'meta_title': f'{instance.title} | Codeteki',
                'meta_description': instance.description[:320] if instance.description else f'{instance.title} services for Australian businesses.',
                'target_keyword': instance.title.lower(),
            }
        )


@receiver(post_save, sender='core.BlogPost')
def create_blog_seo(sender, instance, created, **kwargs):
    """Auto-create PageSEO entry when a new BlogPost is published."""
    if instance.status == 'published':
        from core.models import PageSEO
        # Use get_or_create to handle both new posts and posts becoming published
        PageSEO.objects.get_or_create(
            blog_post=instance,
            defaults={
                'page': 'custom',
                'meta_title': f'{instance.title} | Codeteki Blog',
                'meta_description': instance.excerpt[:320] if instance.excerpt else instance.title,
                'target_keyword': instance.title.lower()[:100],
            }
        )
