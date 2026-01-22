"""
Management command to set up a new client CRM.

Usage:
    python manage.py setup_client_crm \
        --name="Client Brand Name" \
        --slug="client-slug" \
        --type="real_estate" \
        --website="https://example.com" \
        --color="#0093E9" \
        --email="hello@example.com" \
        --sender="John from Example"

Types: real_estate, business_directory, b2b_sales
"""

from django.core.management.base import BaseCommand, CommandError
from crm.models import Brand, Pipeline, PipelineStage


# Stage configurations for each CRM type
CRM_CONFIGS = {
    'real_estate': {
        'pipeline_name_suffix': 'Real Estate Outreach',
        'pipeline_type': 'real_estate',
        'ai_template': """
- Platform: {brand_name}
- Offering: FREE agent profile listing
- Key benefit: Get found by home buyers in your area
- Current promotion: Early adopters get featured placement
""",
        'stages': [
            {'name': 'Identified', 'stage_type': 'regular', 'order': 1, 'days_until_next': 0, 'auto_send_email': False},
            {'name': 'Invitation Sent', 'stage_type': 'regular', 'order': 2, 'days_until_next': 3, 'auto_send_email': True},
            {'name': 'Follow-up 1', 'stage_type': 'regular', 'order': 3, 'days_until_next': 4, 'auto_send_email': True},
            {'name': 'Follow-up 2', 'stage_type': 'regular', 'order': 4, 'days_until_next': 5, 'auto_send_email': True},
            {'name': 'Responded', 'stage_type': 'regular', 'order': 5, 'days_until_next': 0, 'auto_send_email': False},
            {'name': 'Registered', 'stage_type': 'won', 'order': 6, 'days_until_next': 0, 'auto_send_email': True},
            {'name': 'Listing', 'stage_type': 'won', 'order': 7, 'days_until_next': 0, 'auto_send_email': False},
            {'name': 'Lost', 'stage_type': 'lost', 'order': 8, 'days_until_next': 0, 'auto_send_email': False},
        ]
    },
    'business_directory': {
        'pipeline_name_suffix': 'Business Outreach',
        'pipeline_type': 'business_directory',
        'ai_template': """
- Platform: {brand_name}
- Offering: List your business FREE FOREVER
- Key benefit: Get found on Google, increase foot traffic
- Features: Business profile, photos, reviews, contact info
- No credit card required, no hidden fees
""",
        'stages': [
            {'name': 'Business Found', 'stage_type': 'regular', 'order': 1, 'days_until_next': 0, 'auto_send_email': False},
            {'name': 'Invited', 'stage_type': 'regular', 'order': 2, 'days_until_next': 3, 'auto_send_email': True},
            {'name': 'Follow Up 1', 'stage_type': 'regular', 'order': 3, 'days_until_next': 4, 'auto_send_email': True},
            {'name': 'Follow Up 2', 'stage_type': 'regular', 'order': 4, 'days_until_next': 5, 'auto_send_email': True},
            {'name': 'Responded', 'stage_type': 'regular', 'order': 5, 'days_until_next': 0, 'auto_send_email': False},
            {'name': 'Signed Up', 'stage_type': 'won', 'order': 6, 'days_until_next': 0, 'auto_send_email': True},
            {'name': 'Listed', 'stage_type': 'won', 'order': 7, 'days_until_next': 0, 'auto_send_email': False},
            {'name': 'Lost', 'stage_type': 'lost', 'order': 8, 'days_until_next': 0, 'auto_send_email': False},
        ]
    },
    'b2b_sales': {
        'pipeline_name_suffix': 'Sales Pipeline',
        'pipeline_type': 'sales',
        'ai_template': """
- Company: {brand_name}
- Services: Professional services and solutions
- Approach: We solve business problems
- Book a free discovery call to discuss your needs
""",
        'stages': [
            {'name': 'Lead Found', 'stage_type': 'regular', 'order': 1, 'days_until_next': 0, 'auto_send_email': False},
            {'name': 'Intro Sent', 'stage_type': 'regular', 'order': 2, 'days_until_next': 3, 'auto_send_email': True},
            {'name': 'Follow Up 1', 'stage_type': 'regular', 'order': 3, 'days_until_next': 4, 'auto_send_email': True},
            {'name': 'Follow Up 2', 'stage_type': 'regular', 'order': 4, 'days_until_next': 7, 'auto_send_email': True},
            {'name': 'Responded', 'stage_type': 'regular', 'order': 5, 'days_until_next': 0, 'auto_send_email': False},
            {'name': 'Discovery Call', 'stage_type': 'regular', 'order': 6, 'days_until_next': 0, 'auto_send_email': True},
            {'name': 'Proposal Sent', 'stage_type': 'regular', 'order': 7, 'days_until_next': 3, 'auto_send_email': True},
            {'name': 'Negotiating', 'stage_type': 'regular', 'order': 8, 'days_until_next': 0, 'auto_send_email': False},
            {'name': 'Client', 'stage_type': 'won', 'order': 9, 'days_until_next': 0, 'auto_send_email': True},
            {'name': 'Lost', 'stage_type': 'lost', 'order': 10, 'days_until_next': 0, 'auto_send_email': False},
        ]
    }
}


class Command(BaseCommand):
    help = 'Set up a new client CRM with brand, pipeline, and stages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='Brand name (e.g., "Sydney Business Hub")'
        )
        parser.add_argument(
            '--slug',
            type=str,
            required=True,
            help='URL-safe slug (e.g., "sydney-biz-hub")'
        )
        parser.add_argument(
            '--type',
            type=str,
            required=True,
            choices=['real_estate', 'business_directory', 'b2b_sales'],
            help='CRM type: real_estate, business_directory, or b2b_sales'
        )
        parser.add_argument(
            '--website',
            type=str,
            required=True,
            help='Brand website URL'
        )
        parser.add_argument(
            '--color',
            type=str,
            default='#0093E9',
            help='Primary brand color (hex, default: #0093E9)'
        )
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Sender email address'
        )
        parser.add_argument(
            '--sender',
            type=str,
            required=True,
            help='Sender display name (e.g., "John from Example")'
        )
        parser.add_argument(
            '--target',
            type=str,
            default='',
            help='Target audience description (optional)'
        )
        parser.add_argument(
            '--description',
            type=str,
            default='',
            help='Business description (optional)'
        )

    def handle(self, *args, **options):
        crm_type = options['type']
        config = CRM_CONFIGS[crm_type]

        brand_name = options['name']
        brand_slug = options['slug']

        self.stdout.write(f"\n{'='*50}")
        self.stdout.write(f"Setting up {crm_type.upper()} CRM for: {brand_name}")
        self.stdout.write(f"{'='*50}\n")

        # Create Brand
        ai_updates = config['ai_template'].format(brand_name=brand_name)

        brand, created = Brand.objects.update_or_create(
            slug=brand_slug,
            defaults={
                'name': brand_name,
                'website': options['website'],
                'primary_color': options['color'],
                'from_email': options['email'],
                'from_name': options['sender'],
                'ai_business_updates': ai_updates,
                'ai_target_context': options['target'] or f"Target audience for {brand_name}",
                'ai_approach_style': 'problem_solving',
                'is_active': True,
            }
        )
        status = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f"✓ {status} brand: {brand.name}"))

        # Create Pipeline
        pipeline_slug = f"{brand_slug}-{config['pipeline_type']}"
        pipeline_name = f"{brand_name} - {config['pipeline_name_suffix']}"

        pipeline, created = Pipeline.objects.update_or_create(
            brand=brand,
            slug=pipeline_slug,
            defaults={
                'name': pipeline_name,
                'pipeline_type': config['pipeline_type'],
                'is_active': True,
                'is_default': True,
            }
        )
        status = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f"✓ {status} pipeline: {pipeline.name}"))

        # Create Stages
        self.stdout.write("\nCreating pipeline stages:")
        for stage_data in config['stages']:
            stage, created = PipelineStage.objects.update_or_create(
                pipeline=pipeline,
                name=stage_data['name'],
                defaults=stage_data
            )
            status = '✓' if created else '↻'
            self.stdout.write(f"  {status} {stage.order}. {stage.name} ({stage.stage_type})")

        # Summary
        self.stdout.write(f"\n{'='*50}")
        self.stdout.write(self.style.SUCCESS("✅ CRM Setup Complete!"))
        self.stdout.write(f"{'='*50}")
        self.stdout.write(f"""
Brand: {brand.name} ({brand.slug})
Pipeline: {pipeline.name}
Stages: {pipeline.stages.count()}
Type: {crm_type}

Admin URLs:
  Brand Settings: /admin/crm/brand/{brand.id}/change/
  Pipeline Board: /admin/crm/pipeline/{pipeline.id}/board/
  Add Contacts:   /admin/crm/contact/add/?brand={brand.id}

Next Steps:
  1. Update AI context in brand settings if needed
  2. Import contacts (CSV or manual)
  3. Create deals from contacts
  4. Start sending emails!
""")
