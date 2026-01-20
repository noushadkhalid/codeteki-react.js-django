"""
Test Pipeline Flow - Send real emails to test the CRM autopilot

Usage:
    python manage.py test_pipeline_flow your@email.com
    python manage.py test_pipeline_flow your@email.com --pipeline realestate
    python manage.py test_pipeline_flow your@email.com --pipeline business
    python manage.py test_pipeline_flow your@email.com --dry-run  # Preview without sending
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from crm.models import Brand, Contact, Pipeline, Deal, EmailLog
from crm.services.email_service import get_email_service
from crm.services.ai_agent import CRMAIAgent


class Command(BaseCommand):
    help = 'Test the full pipeline flow by sending real emails'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Your email address for testing')
        parser.add_argument(
            '--pipeline',
            type=str,
            choices=['realestate', 'business', 'backlink', 'all'],
            default='all',
            help='Which pipeline to test (default: all)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview emails without sending'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='Test User',
            help='Name for the test contact'
        )
        parser.add_argument(
            '--company',
            type=str,
            default='Test Company Pty Ltd',
            help='Company name for the test contact'
        )

    def handle(self, *args, **options):
        email = options['email']
        pipeline_filter = options['pipeline']
        dry_run = options['dry_run']
        name = options['name']
        company = options['company']

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  CRM PIPELINE TEST - {'DRY RUN' if dry_run else 'LIVE'}")
        self.stdout.write(f"{'='*60}\n")

        # Get Desi Firms brand
        try:
            brand = Brand.objects.get(slug='desifirms')
            self.stdout.write(f"✓ Brand: {brand.name}")
        except Brand.DoesNotExist:
            self.stdout.write(self.style.ERROR("✗ Desi Firms brand not found. Run: python manage.py seed_crm_pipelines"))
            return

        # Get pipelines to test
        pipelines_to_test = []
        if pipeline_filter in ['realestate', 'all']:
            try:
                realestate = Pipeline.objects.get(brand=brand, pipeline_type='realestate')
                pipelines_to_test.append(realestate)
            except Pipeline.DoesNotExist:
                self.stdout.write(self.style.WARNING("⚠ Real Estate pipeline not found"))

        if pipeline_filter in ['business', 'all']:
            try:
                business = Pipeline.objects.get(brand=brand, pipeline_type='business')
                pipelines_to_test.append(business)
            except Pipeline.DoesNotExist:
                self.stdout.write(self.style.WARNING("⚠ Business Listings pipeline not found"))

        if pipeline_filter in ['backlink', 'all']:
            try:
                backlink = Pipeline.objects.get(brand=brand, pipeline_type='backlink')
                pipelines_to_test.append(backlink)
            except Pipeline.DoesNotExist:
                self.stdout.write(self.style.WARNING("⚠ Backlink pipeline not found"))

        if not pipelines_to_test:
            self.stdout.write(self.style.ERROR("✗ No pipelines found to test"))
            return

        self.stdout.write(f"✓ Found {len(pipelines_to_test)} pipeline(s) to test")

        # Initialize AI agent
        ai_agent = CRMAIAgent()

        # Get email service
        email_service = get_email_service(brand)
        if not email_service.enabled:
            self.stdout.write(self.style.WARNING("⚠ Email service not configured - will show preview only"))
            dry_run = True

        for pipeline in pipelines_to_test:
            self.stdout.write(f"\n{'-'*60}")
            self.stdout.write(f"  PIPELINE: {pipeline.name}")
            self.stdout.write(f"{'-'*60}\n")

            # Get email type based on pipeline
            email_type_map = {
                'realestate': 'agent_invitation',
                'business': 'directory_invitation',
                'backlink': 'backlink_pitch',
                'events': 'event_invitation',
                'classifieds': 'classifieds_invitation',
            }
            email_type = email_type_map.get(pipeline.pipeline_type, 'invitation')

            # Build context for AI
            context = {
                'email_type': email_type,
                'tone': 'friendly',
                'suggestions': '',
                'pipeline_type': pipeline.pipeline_type,
                'pipeline_name': pipeline.name,
                'recipient_email': email,
                'recipient_name': name,
                'recipient_company': company,
                'recipient_website': '',
                'brand_name': brand.name,
                'brand_website': brand.website or '',
                'brand_description': brand.ai_company_description or '',
                'value_proposition': brand.ai_value_proposition or '',
            }

            self.stdout.write("Generating AI email...")

            # Generate email with AI
            result = ai_agent.compose_email_from_context(context)

            if not result.get('success'):
                self.stdout.write(self.style.ERROR(f"✗ AI generation failed: {result.get('error', 'Unknown error')}"))
                continue

            subject = result.get('subject', '')
            body = result.get('body', '')

            # Apply smart salutation
            salutation = ai_agent.get_smart_salutation(
                email=email,
                name=name,
                company=company
            )
            body = body.replace('{{SALUTATION}}', salutation)

            self.stdout.write(f"\n📧 Generated Email:")
            self.stdout.write(f"   From: {brand.from_name} <{brand.from_email}>")
            self.stdout.write(f"   To: {email}")
            self.stdout.write(f"   Subject: {subject}")
            self.stdout.write(f"\n   Body:")
            self.stdout.write(f"   {'-'*50}")
            for line in body.split('\n'):
                self.stdout.write(f"   {line}")
            self.stdout.write(f"   {'-'*50}\n")

            if dry_run:
                self.stdout.write(self.style.WARNING("   [DRY RUN - Email not sent]"))
            else:
                # Create or get test contact
                contact, created = Contact.objects.get_or_create(
                    email=email,
                    brand=brand,
                    defaults={
                        'name': name,
                        'company': company,
                        'contact_type': 'lead',
                        'source': 'pipeline_test',
                    }
                )
                if created:
                    self.stdout.write(f"   ✓ Created test contact: {contact.name}")
                else:
                    self.stdout.write(f"   ✓ Using existing contact: {contact.name}")

                # Create deal in pipeline
                # Get the "Invited" stage (stage 2)
                invited_stage = pipeline.stages.filter(order=2).first()
                if not invited_stage:
                    invited_stage = pipeline.stages.first()

                deal = Deal.objects.create(
                    contact=contact,
                    pipeline=pipeline,
                    current_stage=invited_stage,
                    status='active',
                    stage_entered_at=timezone.now(),
                )
                self.stdout.write(f"   ✓ Created deal #{deal.id} in {pipeline.name}")

                # Send the email
                self.stdout.write("   Sending email via Zoho...")
                send_result = email_service.send(
                    to=email,
                    subject=subject,
                    body=body,
                    from_name=brand.from_name,
                )

                if send_result.get('success'):
                    # Log the email
                    email_log = EmailLog.objects.create(
                        deal=deal,
                        to_email=email,
                        from_email=brand.from_email or 'sales@desifirms.com.au',
                        subject=subject,
                        body=body,
                        sent_at=timezone.now(),
                        zoho_message_id=send_result.get('message_id', ''),
                        ai_generated=True,
                    )

                    # Update deal
                    deal.emails_sent = 1
                    deal.last_contact_date = timezone.now()
                    deal.save()

                    self.stdout.write(self.style.SUCCESS(f"   ✓ Email sent successfully! Message ID: {send_result.get('message_id', 'N/A')}"))
                else:
                    self.stdout.write(self.style.ERROR(f"   ✗ Failed to send: {send_result.get('error', 'Unknown error')}"))

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("  TEST COMPLETE")
        self.stdout.write(f"{'='*60}\n")

        if dry_run:
            self.stdout.write("To send real emails, run without --dry-run flag")
        else:
            self.stdout.write(f"Check your inbox at: {email}")
