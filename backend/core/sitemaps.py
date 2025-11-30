"""
Dynamic Sitemap generation for Codeteki.

Generates XML sitemaps that automatically update when:
- New blog posts are published
- New services are added
- New demos are created
- New AI tools are added
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings

from .models import (
    BlogPost, BlogCategory, Service, DemoShowcase,
    AITool, FAQCategory, HeroSection
)


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return [
            'home',
            'services',
            'ai-tools',
            'demos',
            'faq',
            'contact',
            'blog',
            'privacy-policy',
            'terms-of-service',
        ]

    def location(self, item):
        if item == 'home':
            return '/'
        return f'/{item}/'


class BlogSitemap(Sitemap):
    """Sitemap for blog posts."""
    changefreq = 'weekly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return BlogPost.objects.filter(
            status=BlogPost.STATUS_PUBLISHED
        ).order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class BlogCategorySitemap(Sitemap):
    """Sitemap for blog categories."""
    changefreq = 'weekly'
    priority = 0.5
    protocol = 'https'

    def items(self):
        return BlogCategory.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class ServiceSitemap(Sitemap):
    """Sitemap for services."""
    changefreq = 'monthly'
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Service.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/services/{obj.slug}/'


class DemoSitemap(Sitemap):
    """Sitemap for demo showcases."""
    changefreq = 'monthly'
    priority = 0.6
    protocol = 'https'

    def items(self):
        return DemoShowcase.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/demos/{obj.slug}/'


class AIToolSitemap(Sitemap):
    """Sitemap for AI tools."""
    changefreq = 'weekly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return AITool.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/ai-tools/{obj.slug}/'


# Dictionary of all sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogSitemap,
    'blog-categories': BlogCategorySitemap,
    'services': ServiceSitemap,
    'demos': DemoSitemap,
    'ai-tools': AIToolSitemap,
}
