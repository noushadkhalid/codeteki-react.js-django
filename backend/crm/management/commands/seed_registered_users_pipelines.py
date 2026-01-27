"""
Management command to create pipelines for registered but inactive users.

Usage:
    python manage.py seed_registered_users_pipelines
"""

from django.core.management.base import BaseCommand
from crm.models import Brand, Pipeline, PipelineStage


class Command(BaseCommand):
    help = 'Create pipelines for nurturing registered but inactive users'

    def handle(self, *args, **options):
        # Get Desi Firms brand
        try:
            brand = Brand.objects.get(slug='desifirms')
        except Brand.DoesNotExist:
            self.stdout.write(self.style.ERROR('Desi Firms brand not found!'))
            return

        # Pipeline configurations
        # Format: (stage_name, order, days_until_followup, email_type)
        pipelines_config = [
            {
                'name': 'Registered Users - Business',
                'description': 'Nurture registered users who haven\'t listed their business yet',
                'pipeline_type': 'registered_users',
                'stages': [
                    ('Registered', 0, 0, None),  # Just registered, no email yet
                    ('Nudge 1', 1, 3, 'business_nudge'),  # First nudge after 3 days
                    ('Nudge 2', 2, 5, 'business_nudge_2'),  # Second nudge after 5 days
                    ('Responded', 3, 0, None),  # They replied
                    ('Listed', 4, 0, None),  # Success! They listed
                    ('Not Interested', 5, 0, None),  # Archive
                ]
            },
            {
                'name': 'Registered Users - Real Estate',
                'description': 'Nurture registered users who haven\'t created agent profile',
                'pipeline_type': 'registered_users',
                'stages': [
                    ('Registered', 0, 0, None),
                    ('Nudge 1', 1, 3, 'realestate_nudge'),
                    ('Nudge 2', 2, 5, 'realestate_nudge_2'),
                    ('Responded', 3, 0, None),
                    ('Agent Profile Created', 4, 0, None),
                    ('Not Interested', 5, 0, None),
                ]
            },
            {
                'name': 'Registered Users - Events',
                'description': 'Nurture registered users who haven\'t posted events',
                'pipeline_type': 'registered_users',
                'stages': [
                    ('Registered', 0, 0, None),
                    ('Nudge 1', 1, 3, 'events_nudge'),
                    ('Nudge 2', 2, 5, 'events_nudge_2'),
                    ('Responded', 3, 0, None),
                    ('Event Posted', 4, 0, None),
                    ('Not Interested', 5, 0, None),
                ]
            },
        ]

        created_count = 0

        for config in pipelines_config:
            # Check if pipeline already exists
            pipeline, created = Pipeline.objects.get_or_create(
                brand=brand,
                name=config['name'],
                defaults={
                    'description': config['description'],
                    'pipeline_type': config['pipeline_type'],
                    'is_active': True,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created pipeline: {config["name"]}'))
                created_count += 1

                # Create stages
                for stage_name, order, days, email_type in config['stages']:
                    # Build auto_actions dict if email_type specified
                    auto_actions = {}
                    if email_type:
                        auto_actions = {
                            'action': 'send_email',
                            'template': email_type,
                        }

                    PipelineStage.objects.create(
                        pipeline=pipeline,
                        name=stage_name,
                        order=order,
                        days_until_followup=days,
                        auto_actions=auto_actions,
                    )
                    auto_tag = f' (auto: {email_type})' if email_type else ''
                    self.stdout.write(f'   - {stage_name}{auto_tag}')
            else:
                self.stdout.write(self.style.WARNING(f'Pipeline already exists: {config["name"]}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Done! {created_count} new pipeline(s) created.'))
        self.stdout.write('')
        self.stdout.write('Usage in Email Composer:')
        self.stdout.write('  1. Select registered users (contacts or manual emails)')
        self.stdout.write('  2. Choose email type: "Nudge: List Your Business" (or similar)')
        self.stdout.write('  3. Select pipeline: "Registered Users - Business" (or similar)')
        self.stdout.write('  4. Send - contacts will be added to pipeline for AI autopilot')
