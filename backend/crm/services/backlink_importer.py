"""
Backlink Opportunity Importer Service

Handles bulk import of backlink opportunities from:
- Ubersuggest backlink exports
- Ahrefs backlink exports
- SEMrush backlink exports
- Moz backlink exports

Supported formats: CSV, Excel (.xlsx)
"""

import logging
from typing import Dict, List, Tuple
from urllib.parse import urlparse
from django.utils import timezone
from django.db import transaction

from .csv_importer import parse_file_to_rows

logger = logging.getLogger(__name__)

# Column mappings for different export sources
COLUMN_MAPPINGS = {
    # Target URL variations
    'url': 'target_url',
    'page url': 'target_url',
    'target url': 'target_url',
    'source url': 'target_url',
    'referring page': 'target_url',
    'backlink': 'target_url',
    'from url': 'target_url',

    # Domain variations
    'domain': 'target_domain',
    'source domain': 'target_domain',
    'referring domain': 'target_domain',
    'root domain': 'target_domain',

    # Domain Authority variations
    'domain authority': 'domain_authority',
    'da': 'domain_authority',
    'dr': 'domain_authority',  # Ahrefs Domain Rating
    'domain rating': 'domain_authority',
    'authority': 'domain_authority',
    'authority score': 'domain_authority',

    # Page Authority
    'page authority': 'page_authority',
    'pa': 'page_authority',
    'ur': 'page_authority',  # Ahrefs URL Rating
    'url rating': 'page_authority',

    # Traffic
    'traffic': 'traffic',
    'organic traffic': 'traffic',
    'monthly traffic': 'traffic',
    'visits': 'traffic',

    # Anchor text
    'anchor': 'anchor_text',
    'anchor text': 'anchor_text',

    # Contact info (if available)
    'email': 'email',
    'contact email': 'email',
    'webmaster email': 'email',

    # Notes
    'notes': 'notes',
    'comments': 'notes',
}


class BacklinkImporter:
    """Import backlink opportunities from CSV or Excel files."""

    def __init__(self, backlink_import):
        """
        Initialize importer with a BacklinkImport instance.

        Args:
            backlink_import: BacklinkImport model instance
        """
        self.backlink_import = backlink_import
        self.brand = backlink_import.brand
        self.source = backlink_import.source
        self.our_content_url = backlink_import.our_content_url
        self.min_da = backlink_import.min_domain_authority
        self.create_contacts = backlink_import.create_contacts

        self.imported = []
        self.skipped = []
        self.errors = []

    def process(self) -> Dict:
        """
        Process the file and import backlink opportunities.

        Returns:
            Dict with import results
        """
        from crm.models import BacklinkOpportunity, Contact

        self.backlink_import.status = 'processing'
        self.backlink_import.save()

        try:
            # Read and parse file
            file_content = self.backlink_import.file.read()
            filename = self.backlink_import.file_name or self.backlink_import.file.name
            headers, rows = parse_file_to_rows(file_content, filename)

            self.backlink_import.total_rows = len(rows)
            self.backlink_import.save()

            # Map columns
            column_map = self._map_columns(headers)

            if 'target_url' not in column_map.values() and 'target_domain' not in column_map.values():
                raise ValueError("File must have a 'url' or 'domain' column")

            # Process rows
            for row_num, row in enumerate(rows, start=2):
                try:
                    result = self._process_row(row, column_map, row_num)
                    if result == 'imported':
                        self.imported.append(row_num)
                    elif result == 'skipped':
                        self.skipped.append(row_num)
                except Exception as e:
                    self.errors.append({
                        'row': row_num,
                        'error': str(e),
                        'data': dict(row)
                    })

            # Update import record
            self.backlink_import.status = 'completed'
            self.backlink_import.imported_count = len(self.imported)
            self.backlink_import.skipped_count = len(self.skipped)
            self.backlink_import.error_count = len(self.errors)
            self.backlink_import.errors = self.errors[:100]
            self.backlink_import.completed_at = timezone.now()
            self.backlink_import.save()

            logger.info(
                f"Backlink import completed: {len(self.imported)} imported, "
                f"{len(self.skipped)} skipped, {len(self.errors)} errors"
            )

            return {
                'success': True,
                'imported': len(self.imported),
                'skipped': len(self.skipped),
                'errors': len(self.errors),
                'error_details': self.errors[:10]
            }

        except Exception as e:
            logger.error(f"Backlink import failed: {e}")
            self.backlink_import.status = 'failed'
            self.backlink_import.errors = [{'error': str(e)}]
            self.backlink_import.save()

            return {
                'success': False,
                'error': str(e)
            }

    def _map_columns(self, fieldnames: List[str]) -> Dict[str, str]:
        """Map file column names to model fields."""
        column_map = {}

        for col in fieldnames:
            col_lower = col.lower().strip()
            if col_lower in COLUMN_MAPPINGS:
                column_map[col] = COLUMN_MAPPINGS[col_lower]
            else:
                # Try partial matching
                for key, field in COLUMN_MAPPINGS.items():
                    if key in col_lower or col_lower in key:
                        column_map[col] = field
                        break

        return column_map

    def _process_row(self, row: Dict, column_map: Dict, row_num: int) -> str:
        """Process a single row and create BacklinkOpportunity."""
        from crm.models import BacklinkOpportunity, Contact

        # Extract mapped values
        data = {}
        for csv_col, model_field in column_map.items():
            value = row.get(csv_col, '').strip()
            if value:
                data[model_field] = value

        # Get target URL or domain
        target_url = data.get('target_url', '')
        target_domain = data.get('target_domain', '')

        # Extract domain from URL if not provided
        if target_url and not target_domain:
            try:
                parsed = urlparse(target_url)
                target_domain = parsed.netloc.lower()
                if target_domain.startswith('www.'):
                    target_domain = target_domain[4:]
            except:
                pass

        # If only domain provided, create a URL
        if target_domain and not target_url:
            target_url = f"https://{target_domain}"

        if not target_domain:
            raise ValueError("Could not determine target domain")

        # Check for duplicate
        existing = BacklinkOpportunity.objects.filter(
            brand=self.brand,
            target_domain=target_domain
        ).first()
        if existing:
            return 'skipped'

        # Parse domain authority
        da = 0
        if 'domain_authority' in data:
            try:
                da = int(float(data['domain_authority']))
                da = max(0, min(100, da))
            except (ValueError, TypeError):
                pass

        # Skip if below minimum DA
        if da < self.min_da:
            return 'skipped'

        # Parse traffic
        traffic = 0
        if 'traffic' in data:
            try:
                traffic_str = data['traffic'].replace(',', '').replace('K', '000').replace('M', '000000')
                traffic = int(float(traffic_str))
            except (ValueError, TypeError):
                pass

        # Create backlink opportunity
        with transaction.atomic():
            opportunity = BacklinkOpportunity.objects.create(
                brand=self.brand,
                target_url=target_url,
                target_domain=target_domain,
                domain_authority=da,
                our_content_url=self.our_content_url or '',
                anchor_text_suggestion=data.get('anchor_text', ''),
                notes=data.get('notes', ''),
                status='new',
            )

            # Create contact if email found and option enabled
            if self.create_contacts and 'email' in data:
                email = data['email'].lower()
                if '@' in email:
                    contact, created = Contact.objects.get_or_create(
                        email=email,
                        defaults={
                            'brand': self.brand,
                            'name': email.split('@')[0].title(),
                            'company': target_domain,
                            'website': target_url,
                            'contact_type': 'backlink_target',
                            'source': f'backlink_import_{self.source}',
                            'domain_authority': da,
                        }
                    )
                    opportunity.contact = contact
                    opportunity.save()

        return 'imported'


def preview_backlink_file(file_content: bytes, filename: str = 'file.csv', max_rows: int = 5) -> Dict:
    """
    Preview backlink file contents and detected columns.

    Args:
        file_content: Raw file bytes
        filename: Filename (used to detect format)
        max_rows: Maximum rows to preview

    Returns:
        Dict with headers, mapped_columns, and sample_rows
    """
    try:
        headers, all_rows = parse_file_to_rows(file_content, filename)

        # Map columns
        mapped = {}
        for col in headers:
            col_lower = col.lower().strip()
            if col_lower in COLUMN_MAPPINGS:
                mapped[col] = COLUMN_MAPPINGS[col_lower]
            else:
                for key, field in COLUMN_MAPPINGS.items():
                    if key in col_lower or col_lower in key:
                        mapped[col] = field
                        break
                if col not in mapped:
                    mapped[col] = None

        # Get sample rows
        sample_rows = all_rows[:max_rows]

        # Check for required columns
        has_url = 'target_url' in mapped.values() or 'target_domain' in mapped.values()

        return {
            'success': True,
            'headers': headers,
            'mapped_columns': mapped,
            'sample_rows': sample_rows,
            'total_rows': len(all_rows),
            'has_url': has_url,
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
