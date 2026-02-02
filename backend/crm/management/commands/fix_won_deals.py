"""
Fix won deals that were incorrectly assigned to "Not Interested" stage.

Usage:
    python manage.py fix_won_deals --dry-run  # Preview
    python manage.py fix_won_deals            # Apply
"""

from django.core.management.base import BaseCommand
from crm.models import Deal, PipelineStage


class Command(BaseCommand):
    help = 'Fix won deals incorrectly assigned to Not Interested stage'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Preview changes')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN\n'))
        
        # Find won deals in "Not Interested" stage
        won_deals = Deal.objects.filter(
            status='won',
            current_stage__name__icontains='not interested'
        )
        
        self.stdout.write(f'Found {won_deals.count()} won deals in "Not Interested" stage\n')
        
        for deal in won_deals:
            # Find the correct stage (Registered, Signed Up, Listed, etc.)
            stages = list(deal.pipeline.stages.order_by('order'))
            correct_stage = None
            
            for stage in stages:
                name_lower = stage.name.lower()
                if any(word in name_lower for word in ['registered', 'signed up', 'listed', 'listing', 'converted']):
                    correct_stage = stage
                    break
            
            if correct_stage:
                self.stdout.write(
                    f'  {deal.contact.name}: "{deal.current_stage.name}" -> "{correct_stage.name}"'
                )
                if not dry_run:
                    deal.current_stage = correct_stage
                    deal.save(update_fields=['current_stage'])
            else:
                self.stdout.write(
                    self.style.WARNING(f'  {deal.contact.name}: No suitable stage found')
                )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - no changes made'))
        else:
            self.stdout.write(self.style.SUCCESS('\nDone!'))
