"""
Create Agents & Agencies pipeline for tracking registered agents through onboarding.

Usage:
    python manage.py create_agents_pipeline
    python manage.py create_agents_pipeline --force  # Recreate even if exists
"""

from django.core.management.base import BaseCommand
from crm.models import Pipeline, PipelineStage, Brand


class Command(BaseCommand):
    help = 'Create Agents & Agencies pipeline with stages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recreate pipeline even if it exists'
        )

    def handle(self, *args, **options):
        force = options['force']

        # Get Desi Firms brand
        brand = Brand.objects.filter(slug='desifirms').first()
        if not brand:
            self.stdout.write(self.style.ERROR('Desi Firms brand not found!'))
            return

        self.stdout.write(f'Brand: {brand.name}')

        # Check if pipeline exists
        existing = Pipeline.objects.filter(name__icontains='Agents & Agencies').first()
        if existing and not force:
            self.stdout.write(self.style.WARNING(f'Pipeline already exists: {existing.name}'))
            self.stdout.write('Use --force to recreate')
            return

        if existing and force:
            self.stdout.write(f'Deleting existing pipeline: {existing.name}')
            existing.delete()

        # Create the pipeline
        pipeline = Pipeline.objects.create(
            name='Agents & Agencies',
            brand=brand,
            pipeline_type='registered_users',
            description='Track registered agents through their onboarding journey: profile → agency → team → listings',
            is_active=True,
        )
        self.stdout.write(self.style.SUCCESS(f'Created pipeline: {pipeline.name}'))

        # Define stages
        stages = [
            {
                'name': 'Registered',
                'order': 1,
                'days_until_followup': 1,
                'is_terminal': False,
                'description': 'User registered, needs to complete agent profile'
            },
            {
                'name': 'Profile Complete',
                'order': 2,
                'days_until_followup': 2,
                'is_terminal': False,
                'description': 'Agent profile done, encourage agency creation'
            },
            {
                'name': 'Agency Created',
                'order': 3,
                'days_until_followup': 2,
                'is_terminal': False,
                'description': 'Agency set up, encourage team invites'
            },
            {
                'name': 'Team Invited',
                'order': 4,
                'days_until_followup': 3,
                'is_terminal': False,
                'description': 'Team invited, encourage first listing'
            },
            {
                'name': 'First Listing',
                'order': 5,
                'days_until_followup': 3,
                'is_terminal': False,
                'description': 'First property listed, encourage more listings'
            },
            {
                'name': 'Active Lister',
                'order': 6,
                'days_until_followup': 0,
                'is_terminal': True,
                'description': 'Fully onboarded and actively listing properties'
            },
        ]

        for stage_data in stages:
            stage = PipelineStage.objects.create(
                pipeline=pipeline,
                name=stage_data['name'],
                order=stage_data['order'],
                days_until_followup=stage_data['days_until_followup'],
                is_terminal=stage_data['is_terminal'],
            )
            self.stdout.write(f'  Created stage: {stage.name}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Pipeline created successfully!'))
        self.stdout.write('')
        self.stdout.write('Stages:')
        for s in pipeline.stages.order_by('order'):
            terminal = ' (Terminal)' if s.is_terminal else ''
            self.stdout.write(f'  {s.order}. {s.name} - {s.days_until_followup} days{terminal}')
