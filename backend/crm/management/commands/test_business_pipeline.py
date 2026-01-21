"""
Test Full Business Listings Pipeline Flow - All Stages

This simulates a complete Business Directory outreach sequence:
1. Business Found → Initial contact added
2. Invited → First invitation email sent
3. Follow Up 1 → First follow-up sent
4. Follow Up 2 → Second follow-up sent
5. Responded → Business replied (positive)
6. Signed Up → Business created account
7. Listed → Business has a live listing (SUCCESS)
8. Not Interested → Alternative ending (DECLINED)

Usage:
    python manage.py test_business_pipeline your@email.com
    python manage.py test_business_pipeline your@email.com --dry-run
    python manage.py test_business_pipeline your@email.com --stage 3  # Only stage 3
"""

import time
from django.core.management.base import BaseCommand
from django.utils import timezone

from crm.models import Brand, Contact, Pipeline, PipelineStage, Deal, EmailLog
from crm.services.email_service import get_email_service
from crm.services.ai_agent import CRMAIAgent
from crm.services.email_templates import get_styled_email


class Command(BaseCommand):
    help = 'Test the full Business Listings pipeline flow with all stages'

    # Stage configurations
    STAGES = {
        1: {
            'name': 'Business Found',
            'email_type': None,  # No email - just contact added
            'description': 'Contact discovered and added to pipeline',
        },
        2: {
            'name': 'Invited',
            'email_type': 'directory_invitation',
            'description': 'Initial invitation email sent',
        },
        3: {
            'name': 'Follow Up 1',
            'email_type': 'directory_followup_1',
            'description': 'First follow-up (4 days after invite)',
        },
        4: {
            'name': 'Follow Up 2',
            'email_type': 'directory_followup_2',
            'description': 'Final follow-up (5 days after FU1)',
        },
        5: {
            'name': 'Responded',
            'email_type': 'business_responded',
            'description': 'Business responded positively',
        },
        6: {
            'name': 'Signed Up',
            'email_type': 'business_signedup',
            'description': 'Business registered on platform',
        },
        7: {
            'name': 'Listed',
            'email_type': 'business_listed',
            'description': 'Business has a live listing (SUCCESS)',
            'terminal': True,
        },
        8: {
            'name': 'Not Interested',
            'email_type': None,  # No email - just archived
            'description': 'Business declined (CLOSED)',
            'terminal': True,
        },
    }

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Your email address for testing')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview emails without sending'
        )
        parser.add_argument(
            '--stage',
            type=int,
            choices=[2, 3, 4, 5, 6, 7],
            help='Test only a specific stage (2-7)'
        )
        parser.add_argument(
            '--delay',
            type=int,
            default=3,
            help='Seconds between emails (default: 3)'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='Priya Sharma',
            help='Business owner name for test contact'
        )
        parser.add_argument(
            '--company',
            type=str,
            default='Sharma Spices & Groceries',
            help='Business name for test contact'
        )

    def handle(self, *args, **options):
        email = options['email']
        dry_run = options['dry_run']
        single_stage = options['stage']
        delay = options['delay']
        name = options['name']
        company = options['company']

        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(f"  BUSINESS LISTINGS PIPELINE - FULL FLOW TEST {'(DRY RUN)' if dry_run else '(LIVE)'}")
        self.stdout.write(f"{'='*70}\n")

        # Get Desi Firms brand
        try:
            brand = Brand.objects.get(slug='desifirms')
            self.stdout.write(f"✓ Brand: {brand.name}")
        except Brand.DoesNotExist:
            self.stdout.write(self.style.ERROR("✗ Desi Firms brand not found"))
            return

        # Get Business Listings pipeline
        try:
            pipeline = Pipeline.objects.get(brand=brand, pipeline_type='business')
            self.stdout.write(f"✓ Pipeline: {pipeline.name}")
        except Pipeline.DoesNotExist:
            self.stdout.write(self.style.ERROR("✗ Business Listings pipeline not found"))
            self.stdout.write("Run: python manage.py seed_crm_pipelines")
            return

        # Initialize services
        ai_agent = CRMAIAgent()
        email_service = get_email_service(brand)

        if not email_service.enabled and not dry_run:
            self.stdout.write(self.style.WARNING("⚠ Email service not configured"))
            dry_run = True

        # Show pipeline stages
        self.stdout.write(f"\n📋 Pipeline Stages:")
        for stage_num, config in self.STAGES.items():
            email_indicator = "📧" if config['email_type'] else "  "
            terminal = " [TERMINAL]" if config.get('terminal') else ""
            self.stdout.write(f"   {stage_num}. {email_indicator} {config['name']}{terminal}")
            self.stdout.write(f"      └─ {config['description']}")

        # Determine which stages to run
        if single_stage:
            stages_to_run = [single_stage]
        else:
            # Run stages 2-7 (skip 1 as no email, skip 8 as it's negative ending)
            stages_to_run = [2, 3, 4, 5, 6, 7]

        self.stdout.write(f"\n{'─'*70}")
        self.stdout.write(f"  Testing stages: {stages_to_run}")
        self.stdout.write(f"  Recipient: {email}")
        self.stdout.write(f"  Contact: {name} at {company}")
        self.stdout.write(f"{'─'*70}\n")

        # Create/get test contact
        contact, created = Contact.objects.get_or_create(
            email=email,
            brand=brand,
            defaults={
                'name': name,
                'company': company,
                'contact_type': 'lead',
                'source': 'business_pipeline_test',
            }
        )
        if created:
            self.stdout.write(f"✓ Created test contact: {contact.name}")
        else:
            self.stdout.write(f"✓ Using existing contact: {contact.name}")
            # Update name/company if different
            if contact.name != name or contact.company != company:
                contact.name = name
                contact.company = company
                contact.save()

        # Run each stage
        for i, stage_num in enumerate(stages_to_run):
            config = self.STAGES[stage_num]

            self.stdout.write(f"\n{'━'*70}")
            self.stdout.write(f"  STAGE {stage_num}: {config['name']}")
            self.stdout.write(f"{'━'*70}\n")

            if not config['email_type']:
                self.stdout.write(f"   ℹ No email for this stage")
                continue

            # Build context for AI
            context = {
                'email_type': config['email_type'],
                'tone': 'friendly',
                'suggestions': '',
                'pipeline_type': 'business',
                'pipeline_name': pipeline.name,
                'recipient_email': email,
                'recipient_name': name,
                'recipient_company': company,
                'recipient_website': '',
                'brand_name': brand.name,
                'brand_website': brand.website or 'https://www.desifirms.com.au',
                'brand_description': brand.ai_company_description or '',
                'value_proposition': brand.ai_value_proposition or '',
            }

            self.stdout.write("   Generating AI email...")

            # Generate email
            result = ai_agent.compose_email_from_context(context)

            if not result.get('success'):
                self.stdout.write(self.style.ERROR(f"   ✗ AI failed: {result.get('error')}"))
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

            # Display email
            self.stdout.write(f"\n   📧 EMAIL #{i+1} - {config['name']}")
            self.stdout.write(f"   {'─'*60}")
            self.stdout.write(f"   From: {brand.from_name} <{brand.from_email}>")
            self.stdout.write(f"   To: {email}")
            self.stdout.write(f"   Subject: {subject}")
            self.stdout.write(f"\n   Body:")
            for line in body.split('\n'):
                self.stdout.write(f"   │ {line}")
            self.stdout.write(f"   {'─'*60}")

            if dry_run:
                self.stdout.write(self.style.WARNING("   [DRY RUN - Not sent]"))
            else:
                # Create deal for this stage
                pipeline_stage = pipeline.stages.filter(order=stage_num).first()
                deal = Deal.objects.create(
                    contact=contact,
                    pipeline=pipeline,
                    current_stage=pipeline_stage,
                    status='active',
                    stage_entered_at=timezone.now(),
                    emails_sent=stage_num - 1,
                )

                # Get styled HTML email
                self.stdout.write("   Rendering styled HTML email...")
                styled_content = get_styled_email(
                    brand_slug=brand.slug,
                    pipeline_type='business',
                    email_type=config['email_type'],
                    recipient_name=name.split()[0] if name else 'there',
                    recipient_email=email,
                    recipient_company=company,
                    subject=subject,
                    body=body
                )

                html_body = styled_content['html']
                self.stdout.write(f"   ✓ HTML template rendered ({len(html_body)} chars)")

                # Send HTML email
                self.stdout.write("   Sending styled HTML via Zoho...")
                send_result = email_service.send(
                    to=email,
                    subject=subject,
                    body=html_body,
                    from_name=brand.from_name,
                )

                if send_result.get('success'):
                    # Log email
                    EmailLog.objects.create(
                        deal=deal,
                        to_email=email,
                        from_email=brand.from_email or 'sales@desifirms.com.au',
                        subject=subject,
                        body=body,
                        sent_at=timezone.now(),
                        zoho_message_id=send_result.get('message_id', ''),
                        ai_generated=True,
                    )
                    deal.emails_sent += 1
                    deal.last_contact_date = timezone.now()
                    deal.save()

                    self.stdout.write(self.style.SUCCESS(f"   ✓ SENT! Message ID: {send_result.get('message_id', 'N/A')[:20]}..."))
                else:
                    self.stdout.write(self.style.ERROR(f"   ✗ Failed: {send_result.get('error')}"))

            # Delay between emails
            if i < len(stages_to_run) - 1 and not dry_run:
                self.stdout.write(f"\n   ⏳ Waiting {delay}s before next email...")
                time.sleep(delay)

        # Summary
        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(f"  TEST COMPLETE")
        self.stdout.write(f"{'='*70}\n")

        if dry_run:
            self.stdout.write("To send real emails, run without --dry-run flag")
        else:
            self.stdout.write(f"Check your inbox at: {email}")
            self.stdout.write(f"You should have received {len(stages_to_run)} emails.")
            self.stdout.write(f"\nView deals at: /admin/crm/dashboard/")
