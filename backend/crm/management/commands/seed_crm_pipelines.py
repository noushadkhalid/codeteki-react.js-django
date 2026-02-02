"""
Seed CRM Pipelines Management Command

Creates:
- Default brands (Codeteki, Desi Firms)
- Pipelines and stages for each brand
- AI prompt templates

Usage:
    python manage.py seed_crm_pipelines
    python manage.py seed_crm_pipelines --force  # Recreate even if exists
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from crm.models import Brand, Pipeline, PipelineStage, EmailSequence, SequenceStep, AIPromptTemplate


class Command(BaseCommand):
    help = 'Seed default CRM brands, pipelines, stages, and AI prompt templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recreate pipelines even if they already exist',
        )

    def handle(self, *args, **options):
        force = options['force']

        with transaction.atomic():
            # Create Brands first
            codeteki_brand = self._create_codeteki_brand()
            desifirms_brand = self._create_desifirms_brand()

            # Create Codeteki pipelines (sales & backlink)
            self._create_sales_pipeline(codeteki_brand, force)
            self._create_backlink_pipeline(codeteki_brand, force)

            # Create Desi Firms listing acquisition pipelines
            # Note: No Deals pipeline - deals are a feature for listed businesses (plan-based)
            self._create_desifirms_business_pipeline(desifirms_brand, force)
            self._create_desifirms_backlink_pipeline(desifirms_brand, force)
            self._create_desifirms_events_pipeline(desifirms_brand, force)
            self._create_desifirms_realestate_pipeline(desifirms_brand, force)
            self._create_desifirms_classifieds_pipeline(desifirms_brand, force)

            # Create AI Prompt Templates (shared + brand-specific)
            self._create_ai_prompts(force)

        self.stdout.write(self.style.SUCCESS('Successfully seeded CRM brands, pipelines and templates'))

    def _create_codeteki_brand(self):
        """Create Codeteki brand."""
        brand, created = Brand.objects.get_or_create(
            slug='codeteki',
            defaults={
                'name': 'Codeteki',
                'website': 'https://www.codeteki.au',
                'description': 'AI-powered web solutions and SEO services',
                'from_email': 'outreach@codeteki.au',
                'from_name': 'Codeteki Team',
                'ai_company_description': 'Codeteki is a digital agency specializing in AI-powered web solutions, SEO services, and custom software development for businesses.',
                'ai_value_proposition': 'We help businesses grow with cutting-edge AI technology, beautiful web design, and data-driven SEO strategies.',
                'backlink_content_types': ['AI tools', 'SEO guides', 'Web development tutorials'],
                'primary_color': '#f9cb07',
            }
        )
        if created:
            self.stdout.write(f'Created Codeteki brand')
        else:
            self.stdout.write(f'Codeteki brand already exists')
        return brand

    def _create_desifirms_brand(self):
        """Create Desi Firms brand."""
        brand, created = Brand.objects.get_or_create(
            slug='desifirms',
            defaults={
                'name': 'Desi Firms',
                'website': 'https://www.desifirms.com.au',
                'description': 'South Asian Business Directory & Marketplace (Australia)',
                'from_email': 'outreach@desifirms.com.au',
                'from_name': 'Desi Firms Team',
                'ai_company_description': 'Desi Firms is Australia\'s premier South Asian business directory and marketplace, connecting local businesses with their community.',
                'ai_value_proposition': 'We help South Asian businesses in Australia reach their target audience through our directory, marketplace, and AI-powered tools.',
                'backlink_content_types': ['Business directory listings', 'Community resources', 'Local business guides', 'AI tools for businesses'],
                'primary_color': '#E53935',
            }
        )
        if created:
            self.stdout.write(f'Created Desi Firms brand')
        else:
            self.stdout.write(f'Desi Firms brand already exists')
        return brand

    def _create_sales_pipeline(self, brand, force=False, brand_prefix=''):
        """Create Sales/Acquisition Pipeline with stages for a brand."""
        # Desi Firms: Business Acquisition (inviting businesses to list)
        # Codeteki: Sales Pipeline (selling services)
        if brand and 'desi' in brand.name.lower():
            pipeline_name = f'{brand.name} Business Acquisition'
        else:
            pipeline_name = f'{brand.name} Sales Pipeline' if brand else 'Sales Pipeline'

        pipeline, created = Pipeline.objects.get_or_create(
            brand=brand,
            pipeline_type='sales',
            defaults={
                'name': pipeline_name,
                'description': f'Pipeline for {brand.name if brand else "lead"} acquisition and conversion',
                'is_active': True,
            }
        )

        if not created and not force:
            self.stdout.write(f'{pipeline.name} already exists (id: {pipeline.id})')
            return

        if not created and force:
            # Update pipeline name and delete old stages
            pipeline.name = pipeline_name
            pipeline.save(update_fields=['name'])
            pipeline.stages.all().delete()
            self.stdout.write(f'Updated and reset: {pipeline_name}')

        # Desi Firms: Business Directory Listing Acquisition Pipeline
        # Goal: Invite South Asian businesses to list on the free directory
        if brand and 'desi' in brand.name.lower():
            stages = [
                {
                    'name': 'Business Found',
                    'order': 1,
                    'auto_actions': {'action': 'queue_invitation'},
                    'days_until_followup': 0,
                    'is_terminal': False,
                },
                {
                    'name': 'Invited',
                    'order': 2,
                    'auto_actions': {'action': 'wait_for_reply'},
                    'days_until_followup': 4,
                    'is_terminal': False,
                },
                {
                    'name': 'Follow Up 1',
                    'order': 3,
                    'auto_actions': {'action': 'send_followup', 'email_type': 'invitation_followup_1'},
                    'days_until_followup': 5,
                    'is_terminal': False,
                },
                {
                    'name': 'Follow Up 2',
                    'order': 4,
                    'auto_actions': {'action': 'send_followup', 'email_type': 'invitation_followup_2'},
                    'days_until_followup': 7,
                    'is_terminal': False,
                },
                {
                    'name': 'Follow Up 3 (Final)',
                    'order': 5,
                    'auto_actions': {'action': 'send_followup', 'email_type': 'invitation_followup_3'},
                    'days_until_followup': 7,  # Auto-mark as Not Interested after 7 days
                    'is_terminal': False,
                },
                {
                    'name': 'Responded',
                    'order': 6,
                    'auto_actions': {'action': 'classify_response'},
                    'days_until_followup': 2,
                    'is_terminal': False,
                },
                {
                    'name': 'Signed Up',
                    'order': 7,
                    'auto_actions': {'action': 'send_onboarding_help'},
                    'days_until_followup': 3,
                    'is_terminal': False,
                },
                {
                    'name': 'Listed',
                    'order': 8,
                    'auto_actions': {'action': 'send_welcome'},
                    'days_until_followup': 0,
                    'is_terminal': True,
                },
                {
                    'name': 'Not Interested',
                    'order': 9,
                    'auto_actions': {'action': 'archive'},
                    'days_until_followup': 0,
                    'is_terminal': True,
                },
            ]
        else:
            # Codeteki: Selling web development, AI solutions & SEO services
            stages = [
                {
                    'name': 'Prospect Found',
                    'order': 1,
                    'auto_actions': {'action': 'queue_outreach'},
                    'days_until_followup': 0,
                    'is_terminal': False,
                },
                {
                    'name': 'Intro Sent',
                    'order': 2,
                    'auto_actions': {'action': 'wait_for_reply'},
                    'days_until_followup': 4,
                    'is_terminal': False,
                },
                {
                    'name': 'Follow Up 1',
                    'order': 3,
                    'auto_actions': {'action': 'send_followup'},
                    'days_until_followup': 5,
                    'is_terminal': False,
                },
                {
                    'name': 'Follow Up 2',
                    'order': 4,
                    'auto_actions': {'action': 'send_followup'},
                    'days_until_followup': 7,
                    'is_terminal': False,
                },
                {
                    'name': 'Responded',
                    'order': 5,
                    'auto_actions': {'action': 'classify_response'},
                    'days_until_followup': 1,
                    'is_terminal': False,
                },
                {
                    'name': 'Discovery Call',
                    'order': 6,
                    'auto_actions': {'action': 'schedule_call'},
                    'days_until_followup': 2,
                    'is_terminal': False,
                },
                {
                    'name': 'Proposal Sent',
                    'order': 7,
                    'auto_actions': {'action': 'send_proposal_followup'},
                    'days_until_followup': 3,
                    'is_terminal': False,
                },
                {
                    'name': 'Negotiating',
                    'order': 8,
                    'auto_actions': {'action': 'ai_monitor'},
                    'days_until_followup': 5,
                    'is_terminal': False,
                },
                {
                    'name': 'Client',
                    'order': 9,
                    'auto_actions': {'action': 'send_welcome'},
                    'days_until_followup': 0,
                    'is_terminal': True,
                },
                {
                    'name': 'Lost',
                    'order': 10,
                    'auto_actions': {'action': 'archive'},
                    'days_until_followup': 0,
                    'is_terminal': True,
                },
            ]

        for stage_data in stages:
            PipelineStage.objects.create(pipeline=pipeline, **stage_data)

        self.stdout.write(f'Created {pipeline_name} with {len(stages)} stages')

        # Create email sequence for sales
        self._create_sales_email_sequence(pipeline, brand)

    def _create_backlink_pipeline(self, brand, force=False, brand_prefix=''):
        """Create Backlink/Real Estate Pipeline with stages for a brand."""
        # Desi Firms: Real Estate Agent Acquisition (inviting agents to list properties)
        # Codeteki: Backlink Outreach (SEO link building)
        if brand and 'desi' in brand.name.lower():
            pipeline_name = f'{brand.name} Real Estate Acquisition'
        else:
            pipeline_name = f'{brand.name} Backlink Outreach' if brand else 'Backlink Outreach'

        # Set appropriate description
        if brand and 'desi' in brand.name.lower():
            description = 'Invite real estate agents & agencies to list properties for FREE'
        else:
            description = f'Backlink outreach pipeline for {brand.name if brand else "acquiring backlinks"}'

        pipeline, created = Pipeline.objects.get_or_create(
            brand=brand,
            pipeline_type='backlink',
            defaults={
                'name': pipeline_name,
                'description': description,
                'is_active': True,
            }
        )

        if not created and not force:
            self.stdout.write(f'{pipeline.name} already exists (id: {pipeline.id})')
            return

        if not created and force:
            # Update pipeline name and delete old stages
            pipeline.name = pipeline_name
            pipeline.description = description
            pipeline.save(update_fields=['name', 'description'])
            pipeline.stages.all().delete()
            self.stdout.write(f'Updated and reset: {pipeline_name}')

        # Desi Firms: Real Estate Agent/Agency Acquisition Pipeline
        # Goal: Invite real estate agents & agencies to list properties (FREE)
        if brand and 'desi' in brand.name.lower():
            stages = [
                {
                    'name': 'Agent Found',
                    'order': 1,
                    'auto_actions': {'action': 'queue_invitation'},
                    'days_until_followup': 0,
                    'is_terminal': False,
                },
                {
                    'name': 'Invited',
                    'order': 2,
                    'auto_actions': {'action': 'wait_for_reply'},
                    'days_until_followup': 4,
                    'is_terminal': False,
                },
                {
                    'name': 'Follow Up 1',
                    'order': 3,
                    'auto_actions': {'action': 'send_followup', 'email_type': 'agent_followup_1'},
                    'days_until_followup': 5,
                    'is_terminal': False,
                },
                {
                    'name': 'Follow Up 2',
                    'order': 4,
                    'auto_actions': {'action': 'send_followup', 'email_type': 'agent_followup_2'},
                    'days_until_followup': 7,
                    'is_terminal': False,
                },
                {
                    'name': 'Follow Up 3 (Final)',
                    'order': 5,
                    'auto_actions': {'action': 'send_followup', 'email_type': 'agent_followup_3'},
                    'days_until_followup': 7,  # Auto-mark as Not Interested after 7 days
                    'is_terminal': False,
                },
                {
                    'name': 'Responded',
                    'order': 6,
                    'auto_actions': {'action': 'classify_response'},
                    'days_until_followup': 2,
                    'is_terminal': False,
                },
                {
                    'name': 'Registered',
                    'order': 7,
                    'auto_actions': {'action': 'send_onboarding'},
                    'days_until_followup': 3,
                    'is_terminal': False,
                },
                {
                    'name': 'Listing Properties',
                    'order': 8,
                    'auto_actions': {'action': 'send_welcome'},
                    'days_until_followup': 0,
                    'is_terminal': True,
                },
                {
                    'name': 'Not Interested',
                    'order': 9,
                    'auto_actions': {'action': 'archive'},
                    'days_until_followup': 0,
                    'is_terminal': True,
                },
            ]
        else:
            # Codeteki: SEO Backlink Outreach (link building)
            stages = [
                {
                    'name': 'Target Found',
                    'order': 1,
                    'auto_actions': {'action': 'queue_pitch'},
                    'days_until_followup': 0,
                    'is_terminal': False,
                },
                {
                    'name': 'Pitch Sent',
                    'order': 2,
                    'auto_actions': {'action': 'wait_for_reply'},
                    'days_until_followup': 5,
                    'is_terminal': False,
                },
                {
                    'name': 'Follow Up 1',
                    'order': 3,
                    'auto_actions': {'action': 'send_followup'},
                    'days_until_followup': 5,
                    'is_terminal': False,
                },
                {
                    'name': 'Follow Up 2',
                    'order': 4,
                    'auto_actions': {'action': 'send_followup'},
                    'days_until_followup': 7,
                    'is_terminal': False,
                },
                {
                    'name': 'Responded',
                    'order': 5,
                    'auto_actions': {'action': 'classify_response'},
                    'days_until_followup': 2,
                    'is_terminal': False,
                },
                {
                    'name': 'Link Placed',
                    'order': 6,
                    'auto_actions': {'action': 'verify_link'},
                    'days_until_followup': 0,
                    'is_terminal': True,
                },
                {
                    'name': 'Rejected',
                    'order': 7,
                    'auto_actions': {'action': 'archive'},
                    'days_until_followup': 0,
                    'is_terminal': True,
                },
            ]

        for stage_data in stages:
            PipelineStage.objects.create(pipeline=pipeline, **stage_data)

        self.stdout.write(f'Created {pipeline_name} with {len(stages)} stages')

        # Create email sequence for backlink
        self._create_backlink_email_sequence(pipeline, brand)

    # ==========================================
    # DESI FIRMS LISTING ACQUISITION PIPELINES
    # ==========================================

    def _create_desifirms_business_pipeline(self, brand, force=False):
        """
        Desi Firms: Business Listing Acquisition Pipeline
        Goal: Invite South Asian businesses to list on the FREE directory
        """
        pipeline_name = 'Desi Firms Business Listings'
        description = 'Invite South Asian businesses to list on our FREE directory'

        pipeline, created = Pipeline.objects.get_or_create(
            brand=brand,
            pipeline_type='business',
            defaults={
                'name': pipeline_name,
                'description': description,
                'is_active': True,
            }
        )

        if not created and not force:
            self.stdout.write(f'{pipeline.name} already exists (id: {pipeline.id})')
            return

        if not created and force:
            pipeline.name = pipeline_name
            pipeline.description = description
            pipeline.save(update_fields=['name', 'description'])
            pipeline.stages.all().delete()
            self.stdout.write(f'Updated and reset: {pipeline_name}')

        stages = [
            {
                'name': 'Business Found',
                'order': 1,
                'auto_actions': {'action': 'queue_invitation'},
                'days_until_followup': 0,
                'is_terminal': False,
            },
            {
                'name': 'Invited',
                'order': 2,
                'auto_actions': {'action': 'wait_for_reply'},
                'days_until_followup': 4,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 1',
                'order': 3,
                'auto_actions': {'action': 'send_followup'},
                'days_until_followup': 5,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 2',
                'order': 4,
                'auto_actions': {'action': 'send_followup', 'email_type': 'directory_followup_2'},
                'days_until_followup': 7,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 3 (Final)',
                'order': 5,
                'auto_actions': {'action': 'send_followup', 'email_type': 'directory_followup_3'},
                'days_until_followup': 7,  # Auto-mark as Not Interested after 7 days
                'is_terminal': False,
            },
            {
                'name': 'Responded',
                'order': 6,
                'auto_actions': {'action': 'classify_response'},
                'days_until_followup': 2,
                'is_terminal': False,
            },
            {
                'name': 'Signed Up',
                'order': 7,
                'auto_actions': {'action': 'send_onboarding_help'},
                'days_until_followup': 3,
                'is_terminal': False,
            },
            {
                'name': 'Listed',
                'order': 8,
                'auto_actions': {'action': 'send_welcome'},
                'days_until_followup': 0,
                'is_terminal': True,
            },
            {
                'name': 'Not Interested',
                'order': 9,
                'auto_actions': {'action': 'archive'},
                'days_until_followup': 0,
                'is_terminal': True,
            },
        ]

        for stage_data in stages:
            PipelineStage.objects.create(pipeline=pipeline, **stage_data)

        self.stdout.write(f'Created {pipeline_name} with {len(stages)} stages')

    def _create_desifirms_backlink_pipeline(self, brand, force=False):
        """
        Desi Firms: Backlink Outreach Pipeline
        Goal: SEO link building for Desi Firms website
        """
        pipeline_name = 'Desi Firms Backlink Outreach'
        description = 'SEO backlink outreach for desifirms.com.au'

        pipeline, created = Pipeline.objects.get_or_create(
            brand=brand,
            pipeline_type='backlink',
            defaults={
                'name': pipeline_name,
                'description': description,
                'is_active': True,
            }
        )

        if not created and not force:
            self.stdout.write(f'{pipeline.name} already exists (id: {pipeline.id})')
            return

        if not created and force:
            pipeline.name = pipeline_name
            pipeline.description = description
            pipeline.save(update_fields=['name', 'description'])
            pipeline.stages.all().delete()
            self.stdout.write(f'Updated and reset: {pipeline_name}')

        stages = [
            {
                'name': 'Target Found',
                'order': 1,
                'auto_actions': {'action': 'queue_pitch'},
                'days_until_followup': 0,
                'is_terminal': False,
            },
            {
                'name': 'Pitch Sent',
                'order': 2,
                'auto_actions': {'action': 'wait_for_reply'},
                'days_until_followup': 5,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 1',
                'order': 3,
                'auto_actions': {'action': 'send_followup'},
                'days_until_followup': 5,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 2',
                'order': 4,
                'auto_actions': {'action': 'send_followup'},
                'days_until_followup': 7,
                'is_terminal': False,
            },
            {
                'name': 'Responded',
                'order': 5,
                'auto_actions': {'action': 'classify_response'},
                'days_until_followup': 2,
                'is_terminal': False,
            },
            {
                'name': 'Link Placed',
                'order': 6,
                'auto_actions': {'action': 'verify_link'},
                'days_until_followup': 0,
                'is_terminal': True,
            },
            {
                'name': 'Rejected',
                'order': 7,
                'auto_actions': {'action': 'archive'},
                'days_until_followup': 0,
                'is_terminal': True,
            },
        ]

        for stage_data in stages:
            PipelineStage.objects.create(pipeline=pipeline, **stage_data)

        self.stdout.write(f'Created {pipeline_name} with {len(stages)} stages')

        # Create email sequence for backlink outreach
        self._create_backlink_email_sequence(pipeline, brand)

    def _create_desifirms_deals_pipeline(self, brand, force=False):
        """
        Desi Firms: Deals & Promotions Acquisition Pipeline
        Goal: Invite businesses to post deals/promotions on the platform
        """
        pipeline_name = 'Desi Firms Deals & Promotions'
        description = 'Invite businesses to post their deals and promotions'

        pipeline, created = Pipeline.objects.get_or_create(
            brand=brand,
            pipeline_type='deals',
            defaults={
                'name': pipeline_name,
                'description': description,
                'is_active': True,
            }
        )

        if not created and not force:
            self.stdout.write(f'{pipeline.name} already exists (id: {pipeline.id})')
            return

        if not created and force:
            pipeline.name = pipeline_name
            pipeline.description = description
            pipeline.save(update_fields=['name', 'description'])
            pipeline.stages.all().delete()
            self.stdout.write(f'Updated and reset: {pipeline_name}')

        stages = [
            {
                'name': 'Business Found',
                'order': 1,
                'auto_actions': {'action': 'queue_invitation'},
                'days_until_followup': 0,
                'is_terminal': False,
            },
            {
                'name': 'Invited',
                'order': 2,
                'auto_actions': {'action': 'wait_for_reply'},
                'days_until_followup': 4,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 1',
                'order': 3,
                'auto_actions': {'action': 'send_followup'},
                'days_until_followup': 5,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 2',
                'order': 4,
                'auto_actions': {'action': 'send_followup'},
                'days_until_followup': 7,
                'is_terminal': False,
            },
            {
                'name': 'Responded',
                'order': 5,
                'auto_actions': {'action': 'classify_response'},
                'days_until_followup': 2,
                'is_terminal': False,
            },
            {
                'name': 'Deal Posted',
                'order': 6,
                'auto_actions': {'action': 'send_confirmation'},
                'days_until_followup': 0,
                'is_terminal': True,
            },
            {
                'name': 'Not Interested',
                'order': 7,
                'auto_actions': {'action': 'archive'},
                'days_until_followup': 0,
                'is_terminal': True,
            },
        ]

        for stage_data in stages:
            PipelineStage.objects.create(pipeline=pipeline, **stage_data)

        self.stdout.write(f'Created {pipeline_name} with {len(stages)} stages')

    def _create_desifirms_events_pipeline(self, brand, force=False):
        """
        Desi Firms: Events Acquisition Pipeline
        Goal: Invite event companies/organizers to list their events
        """
        pipeline_name = 'Desi Firms Events'
        description = 'Invite event companies and organizers to list their events'

        pipeline, created = Pipeline.objects.get_or_create(
            brand=brand,
            pipeline_type='events',
            defaults={
                'name': pipeline_name,
                'description': description,
                'is_active': True,
            }
        )

        if not created and not force:
            self.stdout.write(f'{pipeline.name} already exists (id: {pipeline.id})')
            return

        if not created and force:
            pipeline.name = pipeline_name
            pipeline.description = description
            pipeline.save(update_fields=['name', 'description'])
            pipeline.stages.all().delete()
            self.stdout.write(f'Updated and reset: {pipeline_name}')

        stages = [
            {
                'name': 'Organizer Found',
                'order': 1,
                'auto_actions': {'action': 'queue_invitation'},
                'days_until_followup': 0,
                'is_terminal': False,
            },
            {
                'name': 'Invited',
                'order': 2,
                'auto_actions': {'action': 'wait_for_reply'},
                'days_until_followup': 4,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 1',
                'order': 3,
                'auto_actions': {'action': 'send_followup'},
                'days_until_followup': 5,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 2',
                'order': 4,
                'auto_actions': {'action': 'send_followup', 'email_type': 'events_followup_2'},
                'days_until_followup': 7,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 3 (Final)',
                'order': 5,
                'auto_actions': {'action': 'send_followup', 'email_type': 'events_followup_3'},
                'days_until_followup': 7,  # Auto-mark as Not Interested after 7 days
                'is_terminal': False,
            },
            {
                'name': 'Responded',
                'order': 6,
                'auto_actions': {'action': 'classify_response'},
                'days_until_followup': 2,
                'is_terminal': False,
            },
            {
                'name': 'Signed Up',
                'order': 7,
                'auto_actions': {'action': 'send_onboarding'},
                'days_until_followup': 3,
                'is_terminal': False,
            },
            {
                'name': 'Event Listed',
                'order': 8,
                'auto_actions': {'action': 'send_welcome'},
                'days_until_followup': 0,
                'is_terminal': True,
            },
            {
                'name': 'Not Interested',
                'order': 9,
                'auto_actions': {'action': 'archive'},
                'days_until_followup': 0,
                'is_terminal': True,
            },
        ]

        for stage_data in stages:
            PipelineStage.objects.create(pipeline=pipeline, **stage_data)

        self.stdout.write(f'Created {pipeline_name} with {len(stages)} stages')

    def _create_desifirms_realestate_pipeline(self, brand, force=False):
        """
        Desi Firms: Real Estate Agent/Agency Acquisition Pipeline
        Goal: Invite real estate agents & agencies to list properties (FREE)
        """
        pipeline_name = 'Desi Firms Real Estate'
        description = 'Invite real estate agents & agencies to list properties for FREE'

        pipeline, created = Pipeline.objects.get_or_create(
            brand=brand,
            pipeline_type='realestate',
            defaults={
                'name': pipeline_name,
                'description': description,
                'is_active': True,
            }
        )

        if not created and not force:
            self.stdout.write(f'{pipeline.name} already exists (id: {pipeline.id})')
            return

        if not created and force:
            pipeline.name = pipeline_name
            pipeline.description = description
            pipeline.save(update_fields=['name', 'description'])
            pipeline.stages.all().delete()
            self.stdout.write(f'Updated and reset: {pipeline_name}')

        stages = [
            {
                'name': 'Agent Found',
                'order': 1,
                'auto_actions': {'action': 'queue_invitation'},
                'days_until_followup': 0,
                'is_terminal': False,
            },
            {
                'name': 'Invited',
                'order': 2,
                'auto_actions': {'action': 'wait_for_reply'},
                'days_until_followup': 4,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 1',
                'order': 3,
                'auto_actions': {'action': 'send_followup'},
                'days_until_followup': 5,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 2',
                'order': 4,
                'auto_actions': {'action': 'send_followup', 'email_type': 'realestate_followup_2'},
                'days_until_followup': 7,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 3 (Final)',
                'order': 5,
                'auto_actions': {'action': 'send_followup', 'email_type': 'realestate_followup_3'},
                'days_until_followup': 7,  # Auto-mark as Not Interested after 7 days
                'is_terminal': False,
            },
            {
                'name': 'Responded',
                'order': 6,
                'auto_actions': {'action': 'classify_response'},
                'days_until_followup': 2,
                'is_terminal': False,
            },
            {
                'name': 'Registered',
                'order': 7,
                'auto_actions': {'action': 'send_onboarding'},
                'days_until_followup': 3,
                'is_terminal': False,
            },
            {
                'name': 'Listing Properties',
                'order': 8,
                'auto_actions': {'action': 'send_welcome'},
                'days_until_followup': 0,
                'is_terminal': True,
            },
            {
                'name': 'Not Interested',
                'order': 9,
                'auto_actions': {'action': 'archive'},
                'days_until_followup': 0,
                'is_terminal': True,
            },
        ]

        for stage_data in stages:
            PipelineStage.objects.create(pipeline=pipeline, **stage_data)

        self.stdout.write(f'Created {pipeline_name} with {len(stages)} stages')

    def _create_desifirms_classifieds_pipeline(self, brand, force=False):
        """
        Desi Firms: Classifieds Acquisition Pipeline
        Goal: Invite people to post classified ads (jobs, items, services)
        """
        pipeline_name = 'Desi Firms Classifieds'
        description = 'Invite people to post classified ads (jobs, items, services)'

        pipeline, created = Pipeline.objects.get_or_create(
            brand=brand,
            pipeline_type='classifieds',
            defaults={
                'name': pipeline_name,
                'description': description,
                'is_active': True,
            }
        )

        if not created and not force:
            self.stdout.write(f'{pipeline.name} already exists (id: {pipeline.id})')
            return

        if not created and force:
            pipeline.name = pipeline_name
            pipeline.description = description
            pipeline.save(update_fields=['name', 'description'])
            pipeline.stages.all().delete()
            self.stdout.write(f'Updated and reset: {pipeline_name}')

        stages = [
            {
                'name': 'Lead Found',
                'order': 1,
                'auto_actions': {'action': 'queue_invitation'},
                'days_until_followup': 0,
                'is_terminal': False,
            },
            {
                'name': 'Invited',
                'order': 2,
                'auto_actions': {'action': 'wait_for_reply'},
                'days_until_followup': 4,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 1',
                'order': 3,
                'auto_actions': {'action': 'send_followup'},
                'days_until_followup': 5,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 2',
                'order': 4,
                'auto_actions': {'action': 'send_followup', 'email_type': 'classifieds_followup_2'},
                'days_until_followup': 7,
                'is_terminal': False,
            },
            {
                'name': 'Follow Up 3 (Final)',
                'order': 5,
                'auto_actions': {'action': 'send_followup', 'email_type': 'classifieds_followup_3'},
                'days_until_followup': 7,  # Auto-mark as Not Interested after 7 days
                'is_terminal': False,
            },
            {
                'name': 'Responded',
                'order': 6,
                'auto_actions': {'action': 'classify_response'},
                'days_until_followup': 2,
                'is_terminal': False,
            },
            {
                'name': 'Ad Posted',
                'order': 7,
                'auto_actions': {'action': 'send_confirmation'},
                'days_until_followup': 0,
                'is_terminal': True,
            },
            {
                'name': 'Not Interested',
                'order': 8,
                'auto_actions': {'action': 'archive'},
                'days_until_followup': 0,
                'is_terminal': True,
            },
        ]

        for stage_data in stages:
            PipelineStage.objects.create(pipeline=pipeline, **stage_data)

        self.stdout.write(f'Created {pipeline_name} with {len(stages)} stages')

    def _create_sales_email_sequence(self, pipeline, brand):
        """Create default email sequence for sales pipeline."""
        brand_name = brand.name if brand else 'Team'
        sequence_name = f'{brand_name} Sales Outreach Sequence'

        sequence, created = EmailSequence.objects.get_or_create(
            pipeline=pipeline,
            name=sequence_name,
            defaults={
                'description': f'Email sequence for {brand_name} sales leads',
                'is_active': True,
            }
        )

        if not created:
            return

        steps = [
            {
                'order': 1,
                'delay_days': 0,
                'subject_template': 'Quick question about {company}',
                'body_template': f'''Hi {{contact_name}},

I noticed {{company}} and wanted to reach out. We help businesses like yours improve their online presence with AI-powered solutions.

Would you be open to a quick chat about how we could potentially help {{company}}?

Best,
{brand_name} Team''',
                'ai_personalize': True,
            },
            {
                'order': 2,
                'delay_days': 3,
                'subject_template': 'Following up - {company}',
                'body_template': f'''Hi {{contact_name}},

Just wanted to follow up on my previous email. I understand you're busy, but I think there's a real opportunity here.

Are you available for a brief call this week?

Best,
{brand_name} Team''',
                'ai_personalize': True,
            },
            {
                'order': 3,
                'delay_days': 5,
                'subject_template': 'Last chance to connect',
                'body_template': f'''Hi {{contact_name}},

I'll keep this brief - I've reached out a couple of times about helping {{company}} with your digital presence.

If now isn't the right time, no worries at all. But if you'd like to chat, just reply to this email.

Best,
{brand_name} Team''',
                'ai_personalize': True,
            },
        ]

        for step_data in steps:
            SequenceStep.objects.create(sequence=sequence, **step_data)

        self.stdout.write(f'Created {sequence_name} with {len(steps)} steps')

    def _create_backlink_email_sequence(self, pipeline, brand):
        """Create default email sequence for backlink outreach."""
        brand_name = brand.name if brand else 'Team'
        sequence_name = f'{brand_name} Backlink Outreach Sequence'

        sequence, created = EmailSequence.objects.get_or_create(
            pipeline=pipeline,
            name=sequence_name,
            defaults={
                'description': f'Backlink outreach sequence for {brand_name}',
                'is_active': True,
            }
        )

        if not created:
            return

        steps = [
            {
                'order': 1,
                'delay_days': 0,
                'subject_template': 'Resource suggestion for {target_domain}',
                'body_template': f'''Hi there,

I came across your article at {{target_url}} and thought it was really well done.

I recently published a comprehensive guide on a related topic that your readers might find valuable: {{our_content_url}}

Would you consider adding it as a resource in your article?

Thanks for your time,
{brand_name} Team''',
                'ai_personalize': True,
            },
            {
                'order': 2,
                'delay_days': 5,
                'subject_template': 'Re: Resource for {target_domain}',
                'body_template': f'''Hi,

Just wanted to follow up on my previous email about the resource I mentioned.

I think it would genuinely add value for your readers. Happy to discuss any questions you might have.

Best,
{brand_name} Team''',
                'ai_personalize': True,
            },
            {
                'order': 3,
                'delay_days': 7,
                'subject_template': 'Final follow-up',
                'body_template': f'''Hi,

This will be my last email about this. I completely understand if you're not interested or too busy.

If you ever need quality content resources in the future, feel free to reach out.

Best wishes,
{brand_name} Team''',
                'ai_personalize': True,
            },
        ]

        for step_data in steps:
            SequenceStep.objects.create(sequence=sequence, **step_data)

        self.stdout.write(f'Created {sequence_name} with {len(steps)} steps')

    def _create_ai_prompts(self, force=False):
        """Create default AI prompt templates."""
        prompts = [
            {
                'name': 'Sales Initial Email',
                'prompt_type': 'email_compose',
                'prompt_text': '''Write a professional initial outreach email for a sales lead.

Context:
- Contact: {contact_name} at {company}
- Their website: {website}
- Our service: AI-powered web solutions and SEO

Requirements:
- Keep it under 100 words
- Be friendly but professional
- Focus on their potential needs
- Include a soft call-to-action
- Don't be pushy

Return only the email body text.''',
                'system_prompt': 'You are a professional sales copywriter for Codeteki, a digital agency.',
                'variables': ['contact_name', 'company', 'website'],
            },
            {
                'name': 'Sales Follow-up Email',
                'prompt_type': 'email_followup',
                'prompt_text': '''Write a follow-up email for a sales lead who hasn't responded.

Context:
- Contact: {contact_name} at {company}
- Emails already sent: {emails_sent}
- Days since last contact: {days_since_contact}

Requirements:
- Keep it under 75 words
- Reference the previous outreach
- Provide additional value or insight
- Gentle call-to-action

Return only the email body text.''',
                'system_prompt': 'You are a professional sales copywriter for Codeteki, a digital agency.',
                'variables': ['contact_name', 'company', 'emails_sent', 'days_since_contact'],
            },
            {
                'name': 'Backlink Pitch Email',
                'prompt_type': 'backlink_pitch',
                'prompt_text': '''Write a backlink outreach email.

Context:
- Target site: {target_domain}
- Target page: {target_url}
- Our content to promote: {our_content_url}
- Suggested anchor text: {anchor_text}

Requirements:
- Keep it under 100 words
- Explain why our content adds value to their readers
- Be genuine, not spammy
- Soft ask for the link

Return only the email body text.''',
                'system_prompt': 'You are a professional outreach specialist for Codeteki.',
                'variables': ['target_domain', 'target_url', 'our_content_url', 'anchor_text'],
            },
            {
                'name': 'Reply Classifier',
                'prompt_type': 'reply_classify',
                'prompt_text': '''Classify this email reply.

Email content:
{email_content}

Classify the reply into one of these categories:
- interested: Wants to learn more or schedule a call
- not_interested: Explicitly declining
- question: Asking for more information
- out_of_office: Auto-reply or vacation message
- unsubscribe: Wants to stop receiving emails
- other: Doesn't fit other categories

Also determine:
- sentiment: positive, negative, or neutral
- suggested_action: What should we do next?

Return JSON: {{"intent": "...", "sentiment": "...", "suggested_action": "...", "summary": "..."}}''',
                'system_prompt': 'You are an email classification AI.',
                'variables': ['email_content'],
            },
            {
                'name': 'Lead Scorer',
                'prompt_type': 'lead_score',
                'prompt_text': '''Score this lead from 0-100 based on likelihood to convert.

Lead information:
- Name: {name}
- Company: {company}
- Website: {website}
- Domain Authority: {domain_authority}
- Source: {source}
- Notes: {notes}

Scoring criteria:
- 80-100: High-quality lead, likely to convert
- 60-79: Good lead, moderate potential
- 40-59: Average lead, needs nurturing
- 20-39: Low-quality lead, low potential
- 0-19: Very poor fit

Return JSON: {{"score": N, "reasoning": "...", "strengths": [...], "weaknesses": [...]}}''',
                'system_prompt': 'You are a lead scoring AI for a digital agency.',
                'variables': ['name', 'company', 'website', 'domain_authority', 'source', 'notes'],
            },
        ]

        created_count = 0
        for prompt_data in prompts:
            prompt, created = AIPromptTemplate.objects.get_or_create(
                name=prompt_data['name'],
                prompt_type=prompt_data['prompt_type'],
                defaults={
                    'prompt_text': prompt_data['prompt_text'],
                    'system_prompt': prompt_data.get('system_prompt', ''),
                    'variables': prompt_data.get('variables', []),
                    'is_active': True,
                }
            )
            if created:
                created_count += 1

        if created_count > 0:
            self.stdout.write(f'Created {created_count} AI prompt templates')
        else:
            self.stdout.write('AI prompt templates already exist')
