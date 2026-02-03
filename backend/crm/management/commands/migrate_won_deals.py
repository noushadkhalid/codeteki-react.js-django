"""
Migrate existing won deals to their corresponding Registered Users pipelines.

Usage:
    python manage.py migrate_won_deals --dry-run  # Preview
    python manage.py migrate_won_deals            # Apply
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from crm.models import Deal, Pipeline, DealActivity


class Command(BaseCommand):
    help = 'Migrate won deals to Registered Users pipelines'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Preview changes')

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - no changes will be made\n'))

        # Pipeline type to Registered Users pipeline mapping
        pipeline_mapping = {
            'realestate': 'Registered Users - Real Estate',
            'business': 'Registered Users - Business',
            'events': 'Registered Users - Events',
        }

        # Find won deals in main pipelines (not already in registered users)
        won_deals = Deal.objects.filter(
            status='won'
        ).exclude(
            pipeline__pipeline_type='registered_users'
        ).select_related('contact', 'pipeline')

        self.stdout.write(f'Found {won_deals.count()} won deals in main pipelines\n')

        created_count = 0
        skipped_count = 0

        for deal in won_deals:
            source_type = deal.pipeline.pipeline_type if deal.pipeline else None
            target_pipeline_name = pipeline_mapping.get(source_type)

            if not target_pipeline_name:
                self.stdout.write(f'  SKIP: {deal.contact.name} - no mapping for {source_type}')
                skipped_count += 1
                continue

            # Find target pipeline
            target_pipeline = Pipeline.objects.filter(
                name__iexact=target_pipeline_name,
                is_active=True
            ).first()

            if not target_pipeline:
                self.stdout.write(
                    self.style.WARNING(f'  SKIP: {deal.contact.name} - target pipeline not found: {target_pipeline_name}')
                )
                skipped_count += 1
                continue

            # Check if already exists
            existing = Deal.objects.filter(
                contact=deal.contact,
                pipeline=target_pipeline,
                status='active'
            ).exists()

            if existing:
                self.stdout.write(f'  SKIP: {deal.contact.name} - already in {target_pipeline_name}')
                skipped_count += 1
                continue

            # Get first stage
            first_stage = target_pipeline.stages.order_by('order').first()
            if not first_stage:
                self.stdout.write(
                    self.style.WARNING(f'  SKIP: {deal.contact.name} - no stages in {target_pipeline_name}')
                )
                skipped_count += 1
                continue

            self.stdout.write(
                self.style.SUCCESS(f'  CREATE: {deal.contact.name} ({deal.contact.email}) → {target_pipeline_name}')
            )

            if not dry_run:
                new_deal = Deal.objects.create(
                    contact=deal.contact,
                    pipeline=target_pipeline,
                    current_stage=first_stage,
                    status='active',
                    next_action_date=timezone.now(),
                    ai_notes=f"Migrated from won deal in {deal.pipeline.name}",
                )
                DealActivity.objects.create(
                    deal=new_deal,
                    activity_type='stage_change',
                    description=f"Migrated from won deal in {deal.pipeline.name}",
                )

            created_count += 1

        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would create {created_count} deals, skip {skipped_count}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created {created_count} deals, skipped {skipped_count}'))
