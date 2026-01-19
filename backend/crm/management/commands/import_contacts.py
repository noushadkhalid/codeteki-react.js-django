"""
Management command to import contacts from CSV or Excel file.

Usage:
    python manage.py import_contacts contacts.csv --brand codeteki --type lead
    python manage.py import_contacts contacts.xlsx --brand codeteki --type lead
    python manage.py import_contacts backlinks.csv --brand codeteki --type backlink_target --create-deals
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from crm.models import Brand, Pipeline, ContactImport
from crm.services.csv_importer import ContactImporter, preview_file


class Command(BaseCommand):
    help = 'Import contacts from CSV or Excel file'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='Path to CSV or Excel file (.csv, .xlsx)')
        parser.add_argument(
            '--brand',
            type=str,
            required=True,
            help='Brand slug (e.g., codeteki, desifirms)'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['lead', 'backlink_target', 'partner'],
            default='lead',
            help='Contact type (default: lead)'
        )
        parser.add_argument(
            '--source',
            type=str,
            default='csv_import',
            help='Source label (default: csv_import)'
        )
        parser.add_argument(
            '--create-deals',
            action='store_true',
            help='Create deals for imported contacts'
        )
        parser.add_argument(
            '--pipeline',
            type=str,
            help='Pipeline slug for created deals (required if --create-deals)'
        )
        parser.add_argument(
            '--preview',
            action='store_true',
            help='Preview CSV without importing'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        brand_slug = options['brand']

        # Read file
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
        except FileNotFoundError:
            raise CommandError(f"File not found: {file_path}")

        filename = file_path.split('/')[-1]

        # Preview mode
        if options['preview']:
            result = preview_file(file_content, filename)
            if not result['success']:
                raise CommandError(f"Error parsing file: {result['error']}")

            self.stdout.write(self.style.SUCCESS(f"\n📄 File Preview: {file_path}"))
            self.stdout.write(f"Total rows: {result['total_rows']}")
            self.stdout.write(f"Has email column: {'✓' if result['has_email'] else '✗'}")
            self.stdout.write("\nColumn Mappings:")
            for col, field in result['mapped_columns'].items():
                status = '✓' if field else '?'
                self.stdout.write(f"  {status} {col} → {field or 'unmapped'}")

            self.stdout.write("\nSample Rows:")
            for i, row in enumerate(result['sample_rows'], 1):
                self.stdout.write(f"\n  Row {i}:")
                for k, v in row.items():
                    if v:
                        self.stdout.write(f"    {k}: {v[:50]}{'...' if len(v) > 50 else ''}")

            return

        # Get brand
        try:
            brand = Brand.objects.get(slug=brand_slug)
        except Brand.DoesNotExist:
            raise CommandError(f"Brand not found: {brand_slug}")

        # Get pipeline if creating deals
        pipeline = None
        if options['create_deals']:
            if not options['pipeline']:
                raise CommandError("--pipeline required when using --create-deals")
            try:
                pipeline = Pipeline.objects.get(
                    brand=brand,
                    name__icontains=options['pipeline']
                )
            except Pipeline.DoesNotExist:
                raise CommandError(f"Pipeline not found: {options['pipeline']}")

        # Create import record
        contact_import = ContactImport.objects.create(
            brand=brand,
            file_name=filename,
            contact_type=options['type'],
            source=options['source'],
            create_deals=options['create_deals'],
            pipeline=pipeline,
        )

        # Save file content
        contact_import.file.save(
            contact_import.file_name,
            ContentFile(file_content)
        )

        self.stdout.write(f"\n🚀 Starting import...")
        self.stdout.write(f"   File: {filename}")
        self.stdout.write(f"   Brand: {brand.name}")
        self.stdout.write(f"   Type: {options['type']}")
        self.stdout.write(f"   Source: {options['source']}")
        if pipeline:
            self.stdout.write(f"   Pipeline: {pipeline.name}")

        # Process import
        importer = ContactImporter(contact_import)
        result = importer.process()

        if result['success']:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Import completed!"))
            self.stdout.write(f"   Imported: {result['imported']}")
            self.stdout.write(f"   Skipped (duplicates): {result['skipped']}")
            self.stdout.write(f"   Errors: {result['errors']}")

            if result['error_details']:
                self.stdout.write(self.style.WARNING("\nErrors:"))
                for err in result['error_details'][:5]:
                    self.stdout.write(f"   Row {err['row']}: {err['error']}")
        else:
            self.stdout.write(self.style.ERROR(f"\n❌ Import failed: {result.get('error')}"))
