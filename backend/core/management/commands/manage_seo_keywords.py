"""
Management command to manage SEO keywords.
Useful when you have 1000s of keywords and need to bulk operations.
"""
from django.core.management.base import BaseCommand, CommandError
from core.models import SEODataUpload, SEOKeyword, SEOKeywordCluster, AISEORecommendation


class Command(BaseCommand):
    help = "Manage SEO keywords - clear, filter, or regenerate"

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['clear-all', 'clear-keywords', 'clear-clusters', 'clear-recommendations', 'stats', 'filter-relevant'],
            help='Action to perform'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm destructive action'
        )
        parser.add_argument(
            '--min-volume',
            type=int,
            default=100,
            help='Minimum search volume to keep (for filter-relevant)'
        )
        parser.add_argument(
            '--max-difficulty',
            type=int,
            default=50,
            help='Maximum SEO difficulty to keep (for filter-relevant)'
        )

    def handle(self, *args, **options):
        action = options['action']

        if action == 'stats':
            self.show_stats()
        elif action == 'clear-all':
            if not options['confirm']:
                raise CommandError("Use --confirm to delete all SEO data")
            self.clear_all()
        elif action == 'clear-keywords':
            if not options['confirm']:
                raise CommandError("Use --confirm to delete all keywords")
            self.clear_keywords()
        elif action == 'clear-clusters':
            if not options['confirm']:
                raise CommandError("Use --confirm to delete all clusters")
            self.clear_clusters()
        elif action == 'clear-recommendations':
            if not options['confirm']:
                raise CommandError("Use --confirm to delete all recommendations")
            self.clear_recommendations()
        elif action == 'filter-relevant':
            self.filter_relevant(
                min_volume=options['min_volume'],
                max_difficulty=options['max_difficulty'],
                confirm=options['confirm']
            )

    def show_stats(self):
        self.stdout.write("\n=== SEO Data Statistics ===\n")
        self.stdout.write(f"Uploads: {SEODataUpload.objects.count()}")
        self.stdout.write(f"Keywords: {SEOKeyword.objects.count()}")
        self.stdout.write(f"Clusters: {SEOKeywordCluster.objects.count()}")
        self.stdout.write(f"AI Recommendations: {AISEORecommendation.objects.count()}")

        # Show volume distribution
        self.stdout.write("\n=== Volume Distribution ===")
        vol_0_100 = SEOKeyword.objects.filter(search_volume__lt=100).count()
        vol_100_500 = SEOKeyword.objects.filter(search_volume__gte=100, search_volume__lt=500).count()
        vol_500_1000 = SEOKeyword.objects.filter(search_volume__gte=500, search_volume__lt=1000).count()
        vol_1000_plus = SEOKeyword.objects.filter(search_volume__gte=1000).count()

        self.stdout.write(f"  0-99 volume: {vol_0_100}")
        self.stdout.write(f"  100-499 volume: {vol_100_500}")
        self.stdout.write(f"  500-999 volume: {vol_500_1000}")
        self.stdout.write(f"  1000+ volume: {vol_1000_plus}")

        # Show difficulty distribution
        self.stdout.write("\n=== Difficulty Distribution ===")
        diff_easy = SEOKeyword.objects.filter(seo_difficulty__lt=30).count()
        diff_medium = SEOKeyword.objects.filter(seo_difficulty__gte=30, seo_difficulty__lt=50).count()
        diff_hard = SEOKeyword.objects.filter(seo_difficulty__gte=50).count()

        self.stdout.write(f"  Easy (0-29): {diff_easy}")
        self.stdout.write(f"  Medium (30-49): {diff_medium}")
        self.stdout.write(f"  Hard (50+): {diff_hard}")

    def clear_all(self):
        kw_count = SEOKeyword.objects.count()
        cluster_count = SEOKeywordCluster.objects.count()
        rec_count = AISEORecommendation.objects.count()
        upload_count = SEODataUpload.objects.count()

        SEOKeyword.objects.all().delete()
        SEOKeywordCluster.objects.all().delete()
        AISEORecommendation.objects.all().delete()
        SEODataUpload.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(
            f"Deleted: {kw_count} keywords, {cluster_count} clusters, "
            f"{rec_count} recommendations, {upload_count} uploads"
        ))

    def clear_keywords(self):
        count = SEOKeyword.objects.count()
        SEOKeyword.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} keywords"))

    def clear_clusters(self):
        count = SEOKeywordCluster.objects.count()
        SEOKeywordCluster.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} clusters"))

    def clear_recommendations(self):
        count = AISEORecommendation.objects.count()
        AISEORecommendation.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} recommendations"))

    def filter_relevant(self, min_volume, max_difficulty, confirm):
        """Keep only relevant keywords based on volume and difficulty."""

        # Find keywords to delete
        to_delete = SEOKeyword.objects.filter(
            search_volume__lt=min_volume
        ) | SEOKeyword.objects.filter(
            seo_difficulty__gt=max_difficulty
        )

        delete_count = to_delete.count()
        keep_count = SEOKeyword.objects.count() - delete_count

        self.stdout.write(f"\nFilter: min_volume={min_volume}, max_difficulty={max_difficulty}")
        self.stdout.write(f"Keywords to DELETE: {delete_count}")
        self.stdout.write(f"Keywords to KEEP: {keep_count}")

        if not confirm:
            self.stdout.write(self.style.WARNING("\nUse --confirm to apply this filter"))
            return

        to_delete.delete()
        self.stdout.write(self.style.SUCCESS(f"\nDeleted {delete_count} low-value keywords. {keep_count} remaining."))
