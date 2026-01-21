"""
Clean up malformed contact emails and merge duplicates.

This command:
1. Normalizes email addresses (extracts email from "Name <email>" format)
2. Merges duplicate contacts with the same normalized email
3. Preserves unsubscribe status across merges

Usage:
    python manage.py cleanup_contacts --dry-run  # Preview changes
    python manage.py cleanup_contacts            # Apply changes
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from crm.models import Contact


class Command(BaseCommand):
    help = 'Clean up malformed contact emails and merge duplicates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying them'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  CONTACT CLEANUP {'(DRY RUN)' if dry_run else '(LIVE)'}")
        self.stdout.write(f"{'='*60}\n")

        # Find all contacts with malformed emails
        malformed = []
        duplicates = {}

        all_contacts = Contact.objects.all()
        self.stdout.write(f"Scanning {all_contacts.count()} contacts...\n")

        for contact in all_contacts:
            original_email = contact.email
            normalized = Contact.normalize_email(original_email)

            if original_email != normalized:
                malformed.append({
                    'contact': contact,
                    'original': original_email,
                    'normalized': normalized,
                })

            # Track normalized emails to find duplicates
            if normalized:
                if normalized not in duplicates:
                    duplicates[normalized] = []
                duplicates[normalized].append(contact)

        # Report malformed emails
        if malformed:
            self.stdout.write(self.style.WARNING(f"Found {len(malformed)} malformed emails:"))
            for item in malformed:
                self.stdout.write(f"  • {item['original']}")
                self.stdout.write(f"    → {item['normalized']}")
        else:
            self.stdout.write(self.style.SUCCESS("No malformed emails found."))

        # Find actual duplicates (same normalized email AND same brand)
        # Different brands = legitimate separate contacts
        true_dup_groups = {}
        multi_brand_emails = {}

        for email, contacts in duplicates.items():
            if len(contacts) <= 1:
                continue

            # Group by brand
            by_brand = {}
            for c in contacts:
                brand_key = c.brand.slug if c.brand else 'none'
                if brand_key not in by_brand:
                    by_brand[brand_key] = []
                by_brand[brand_key].append(c)

            # Check for same-brand duplicates
            for brand_key, brand_contacts in by_brand.items():
                if len(brand_contacts) > 1:
                    key = f"{email}|{brand_key}"
                    true_dup_groups[key] = brand_contacts

            # Track multi-brand emails (not duplicates, just FYI)
            if len(by_brand) > 1:
                multi_brand_emails[email] = contacts

        dup_groups = true_dup_groups

        if multi_brand_emails:
            self.stdout.write(self.style.NOTICE(f"\nFound {len(multi_brand_emails)} emails with multiple brands (not duplicates):"))
            for email, contacts in multi_brand_emails.items():
                brands = [c.brand.slug if c.brand else 'None' for c in contacts]
                self.stdout.write(f"  • {email}: {', '.join(brands)}")

        if dup_groups:
            self.stdout.write(self.style.WARNING(f"\nFound {len(dup_groups)} true duplicate groups (same email + brand):"))
            for key, contacts in dup_groups.items():
                email, brand = key.split('|')
                self.stdout.write(f"\n  Email: {email} (brand: {brand})")
                for c in contacts:
                    unsub_status = "UNSUB" if c.is_unsubscribed else ""
                    brand_unsub = f"unsub:{c.unsubscribed_brands}" if c.unsubscribed_brands else ""
                    self.stdout.write(f"    - ID: {str(c.id)[:8]}... | Status: {c.status} {unsub_status} {brand_unsub}")
        else:
            self.stdout.write(self.style.SUCCESS("\nNo true duplicates found (same email + same brand)."))

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] No changes made. Run without --dry-run to apply."))
            return

        # Apply fixes
        with transaction.atomic():
            # 1. Merge duplicates first
            merged_count = 0
            for email, contacts in dup_groups.items():
                if len(contacts) <= 1:
                    continue

                # Pick the primary contact (prefer one with more data, or most recent)
                primary = max(contacts, key=lambda c: (
                    bool(c.brand),
                    c.email_count,
                    c.is_unsubscribed or bool(c.unsubscribed_brands),
                    c.created_at,
                ))

                # Merge unsubscribe data from all contacts
                all_unsub_brands = set(primary.unsubscribed_brands or [])
                any_global_unsub = primary.is_unsubscribed

                for other in contacts:
                    if other.id == primary.id:
                        continue

                    # Merge unsubscribe status
                    if other.is_unsubscribed:
                        any_global_unsub = True
                    if other.unsubscribed_brands:
                        all_unsub_brands.update(other.unsubscribed_brands)

                    # Move deals to primary contact
                    other.deals.all().update(contact=primary)

                    # Delete duplicate
                    self.stdout.write(f"  Deleting duplicate: {other.email} (ID: {str(other.id)[:8]}...)")
                    other.delete()
                    merged_count += 1

                # Update primary with merged unsubscribe data
                primary.is_unsubscribed = any_global_unsub
                primary.unsubscribed_brands = list(all_unsub_brands)
                primary.email = email  # Ensure normalized
                primary.save()
                self.stdout.write(f"  Updated primary: {primary.email} (unsub_brands: {primary.unsubscribed_brands})")

            # 2. Fix remaining malformed emails
            fixed_count = 0
            for item in malformed:
                contact = item['contact']
                normalized_email = item['normalized']
                try:
                    contact.refresh_from_db()
                except Contact.DoesNotExist:
                    # Already deleted as duplicate
                    continue

                if contact.email == normalized_email:
                    continue

                # Check if normalized email already exists
                existing = Contact.objects.filter(email__iexact=normalized_email).exclude(id=contact.id).first()

                if existing:
                    # Merge into existing contact
                    self.stdout.write(f"  Merging malformed contact into existing...")
                    self.stdout.write(f"    Malformed: {contact.email} (ID: {str(contact.id)[:8]}...)")
                    self.stdout.write(f"    Existing:  {existing.email} (ID: {str(existing.id)[:8]}...)")

                    # Merge unsubscribe data
                    if contact.is_unsubscribed:
                        existing.is_unsubscribed = True
                    if contact.unsubscribed_brands:
                        existing_brands = set(existing.unsubscribed_brands or [])
                        existing_brands.update(contact.unsubscribed_brands)
                        existing.unsubscribed_brands = list(existing_brands)

                    # Merge email stats
                    existing.email_count = max(existing.email_count, contact.email_count)
                    if contact.last_emailed_at:
                        if not existing.last_emailed_at or contact.last_emailed_at > existing.last_emailed_at:
                            existing.last_emailed_at = contact.last_emailed_at

                    existing.save()

                    # Move deals to existing contact
                    contact.deals.all().update(contact=existing)

                    # Delete malformed contact
                    contact.delete()
                    merged_count += 1
                    self.stdout.write(f"    → Merged and deleted malformed contact")
                else:
                    # Safe to just fix the email
                    contact.email = normalized_email
                    contact.save()
                    fixed_count += 1

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"  CLEANUP COMPLETE"))
        self.stdout.write(f"  • Merged: {merged_count} duplicates")
        self.stdout.write(f"  • Fixed: {fixed_count} malformed emails")
        self.stdout.write(f"{'='*60}\n")
