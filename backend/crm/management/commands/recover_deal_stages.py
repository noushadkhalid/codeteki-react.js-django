"""
Recovery script to reassign deals to pipeline stages after seed --force accident.

This script assigns deals to stages based on:
- emails_sent count
- deal status (won/lost/open)
- pipeline type

Usage:
    python manage.py recover_deal_stages --dry-run  # Preview changes
    python manage.py recover_deal_stages            # Apply changes
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from crm.models import Deal, Pipeline, PipelineStage


class Command(BaseCommand):
    help = 'Recover deal stages after accidental reset'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying them',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made\n'))
        
        # Get all deals without a stage
        orphan_deals = Deal.objects.filter(current_stage__isnull=True)
        total = orphan_deals.count()
        
        self.stdout.write(f'Found {total} deals without stages\n')
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No orphan deals found!'))
            return
        
        # Process each deal
        recovered = 0
        errors = 0
        
        for deal in orphan_deals:
            try:
                new_stage = self._determine_stage(deal)
                
                if new_stage:
                    self.stdout.write(
                        f'  Deal: {deal.contact.name if deal.contact else "Unknown"} | '
                        f'Pipeline: {deal.pipeline.name if deal.pipeline else "None"} | '
                        f'Emails: {deal.emails_sent} | '
                        f'Status: {deal.status} | '
                        f'-> Stage: {new_stage.name}'
                    )
                    
                    if not dry_run:
                        deal.current_stage = new_stage
                        deal.save(update_fields=['current_stage'])
                    
                    recovered += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  Could not determine stage for deal: {deal.contact.name if deal.contact else deal.id}'
                        )
                    )
                    errors += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  Error processing deal {deal.id}: {e}')
                )
                errors += 1
        
        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would recover {recovered} deals, {errors} errors'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Recovered {recovered} deals, {errors} errors'))

    def _determine_stage(self, deal):
        """Determine the appropriate stage for a deal based on its data."""
        
        if not deal.pipeline:
            return None
        
        # Get all stages for this pipeline, ordered
        stages = list(deal.pipeline.stages.order_by('order'))
        
        if not stages:
            return None
        
        # If deal is won, find "Won" or "Converted" stage
        if deal.status == 'won':
            for stage in stages:
                if any(word in stage.name.lower() for word in ['won', 'converted', 'closed won', 'success']):
                    return stage
            # Default to last stage
            return stages[-1]
        
        # If deal is lost, find "Lost" or "Not Interested" stage
        if deal.status == 'lost':
            for stage in stages:
                if any(word in stage.name.lower() for word in ['lost', 'not interested', 'closed lost', 'unqualified']):
                    return stage
            # Default to last stage
            return stages[-1]
        
        # For open deals, determine based on emails_sent
        emails = deal.emails_sent or 0
        
        # Find stages by email count logic
        # Typically: 0 emails = New Lead, 1 = Contacted, 2 = Follow Up 1, 3 = Follow Up 2, etc.
        
        if emails == 0:
            # New Lead - first stage
            return stages[0]
        
        elif emails == 1:
            # Contacted/Invitation Sent - second stage typically
            for stage in stages:
                if any(word in stage.name.lower() for word in ['contacted', 'invitation sent', 'sent', 'outreach']):
                    return stage
            return stages[1] if len(stages) > 1 else stages[0]
        
        elif emails == 2:
            # Follow Up 1
            for stage in stages:
                if 'follow up 1' in stage.name.lower() or 'follow-up 1' in stage.name.lower():
                    return stage
                if 'follow up' in stage.name.lower() and '2' not in stage.name and '3' not in stage.name:
                    return stage
            return stages[2] if len(stages) > 2 else stages[-1]
        
        elif emails == 3:
            # Follow Up 2
            for stage in stages:
                if 'follow up 2' in stage.name.lower() or 'follow-up 2' in stage.name.lower():
                    return stage
            return stages[3] if len(stages) > 3 else stages[-1]
        
        elif emails >= 4:
            # Follow Up 3 or later
            for stage in stages:
                if 'follow up 3' in stage.name.lower() or 'follow-up 3' in stage.name.lower():
                    return stage
            # Find any "final" stage
            for stage in stages:
                if 'final' in stage.name.lower():
                    return stage
            return stages[min(4, len(stages) - 1)]
        
        # Default to first stage
        return stages[0]
