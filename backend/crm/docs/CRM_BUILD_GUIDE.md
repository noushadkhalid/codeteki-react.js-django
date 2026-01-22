# CRM Build Guide for Claude Code

Execute these commands to build a CRM for a new client.

---

## Quick Start

Ask the client for:
1. **Brand name** (e.g., "Sydney Business Hub")
2. **Brand slug** (e.g., "sydney-biz-hub")
3. **Website URL** (e.g., "https://sydneybusinesshub.com.au")
4. **Primary color** (hex, e.g., "#0093E9")
5. **Sender email** (e.g., "hello@sydneybusinesshub.com.au")
6. **Sender name** (e.g., "Sarah from Sydney Business Hub")
7. **CRM Type**: real_estate | business_directory | b2b_sales
8. **Business description** (2-3 sentences about what they do)
9. **Target audience** (who are they reaching out to)

---

## Build Commands

### Option 1: Run Management Command

```bash
python manage.py setup_client_crm \
    --name="Client Brand Name" \
    --slug="client-slug" \
    --type="real_estate|business_directory|b2b_sales" \
    --website="https://example.com" \
    --color="#0093E9" \
    --email="hello@example.com" \
    --sender="John from Example"
```

### Option 2: Django Shell Script

```bash
python manage.py shell
```

Then paste the appropriate script below.

---

## Type 1: Real Estate CRM

**Use case:** Real estate portals inviting agents to register/list properties.

```python
from crm.models import Brand, Pipeline, PipelineStage

# === EDIT THESE VALUES ===
BRAND_NAME = "Client Real Estate Portal"
BRAND_SLUG = "client-realestate"
WEBSITE = "https://clientrealestate.com.au"
PRIMARY_COLOR = "#0093E9"
FROM_EMAIL = "hello@clientrealestate.com.au"
FROM_NAME = "Sarah from Client Real Estate"
BUSINESS_DESC = "Australia's premier real estate agent directory connecting home buyers with top local agents."
TARGET_AUDIENCE = "Real estate agents and agencies across Australia looking to increase their online presence and get more listings."
# === END EDIT ===

# Create Brand
brand, created = Brand.objects.update_or_create(
    slug=BRAND_SLUG,
    defaults={
        'name': BRAND_NAME,
        'website': WEBSITE,
        'primary_color': PRIMARY_COLOR,
        'from_email': FROM_EMAIL,
        'from_name': FROM_NAME,
        'ai_business_updates': f"""
- Platform: {BRAND_NAME}
- Offering: FREE agent profile listing
- Key benefit: Get found by home buyers in your area
- Current promotion: Early adopters get featured placement
""",
        'ai_target_context': TARGET_AUDIENCE,
        'ai_approach_style': 'problem_solving',
        'is_active': True,
    }
)
print(f"{'Created' if created else 'Updated'} brand: {brand.name}")

# Create Pipeline
pipeline, created = Pipeline.objects.update_or_create(
    brand=brand,
    slug=f"{BRAND_SLUG}-realestate",
    defaults={
        'name': f"{BRAND_NAME} - Real Estate Outreach",
        'pipeline_type': 'real_estate',
        'is_active': True,
        'is_default': True,
    }
)
print(f"{'Created' if created else 'Updated'} pipeline: {pipeline.name}")

# Create Stages
stages = [
    {'name': 'Identified', 'stage_type': 'regular', 'order': 1, 'days_until_next': 0, 'auto_send_email': False},
    {'name': 'Invitation Sent', 'stage_type': 'regular', 'order': 2, 'days_until_next': 3, 'auto_send_email': True},
    {'name': 'Follow-up 1', 'stage_type': 'regular', 'order': 3, 'days_until_next': 4, 'auto_send_email': True},
    {'name': 'Follow-up 2', 'stage_type': 'regular', 'order': 4, 'days_until_next': 5, 'auto_send_email': True},
    {'name': 'Responded', 'stage_type': 'regular', 'order': 5, 'days_until_next': 0, 'auto_send_email': False},
    {'name': 'Registered', 'stage_type': 'won', 'order': 6, 'days_until_next': 0, 'auto_send_email': True},
    {'name': 'Listing', 'stage_type': 'won', 'order': 7, 'days_until_next': 0, 'auto_send_email': False},
    {'name': 'Lost', 'stage_type': 'lost', 'order': 8, 'days_until_next': 0, 'auto_send_email': False},
]

for stage_data in stages:
    stage, created = PipelineStage.objects.update_or_create(
        pipeline=pipeline,
        name=stage_data['name'],
        defaults=stage_data
    )
    print(f"  {'Created' if created else 'Updated'} stage: {stage.name}")

print(f"\n✅ Real Estate CRM ready!")
print(f"   Pipeline board: /admin/crm/pipeline/{pipeline.id}/board/")
print(f"   Brand admin: /admin/crm/brand/{brand.id}/change/")
```

---

## Type 2: Business Directory CRM

**Use case:** Business directories inviting local businesses to claim free listings.

```python
from crm.models import Brand, Pipeline, PipelineStage

# === EDIT THESE VALUES ===
BRAND_NAME = "Client Business Directory"
BRAND_SLUG = "client-directory"
WEBSITE = "https://clientdirectory.com.au"
PRIMARY_COLOR = "#22c55e"
FROM_EMAIL = "hello@clientdirectory.com.au"
FROM_NAME = "Mike from Client Directory"
BUSINESS_DESC = "The go-to directory for local businesses. Get found by customers searching for services in your area."
TARGET_AUDIENCE = "Local businesses including restaurants, cafes, retail shops, tradies, and professional services looking for more online visibility."
# === END EDIT ===

# Create Brand
brand, created = Brand.objects.update_or_create(
    slug=BRAND_SLUG,
    defaults={
        'name': BRAND_NAME,
        'website': WEBSITE,
        'primary_color': PRIMARY_COLOR,
        'from_email': FROM_EMAIL,
        'from_name': FROM_NAME,
        'ai_business_updates': f"""
- Platform: {BRAND_NAME}
- Offering: List your business FREE FOREVER
- Key benefit: Get found on Google, increase foot traffic
- Features: Business profile, photos, reviews, contact info
- No credit card required, no hidden fees
""",
        'ai_target_context': TARGET_AUDIENCE,
        'ai_approach_style': 'problem_solving',
        'is_active': True,
    }
)
print(f"{'Created' if created else 'Updated'} brand: {brand.name}")

# Create Pipeline
pipeline, created = Pipeline.objects.update_or_create(
    brand=brand,
    slug=f"{BRAND_SLUG}-business",
    defaults={
        'name': f"{BRAND_NAME} - Business Outreach",
        'pipeline_type': 'business_directory',
        'is_active': True,
        'is_default': True,
    }
)
print(f"{'Created' if created else 'Updated'} pipeline: {pipeline.name}")

# Create Stages
stages = [
    {'name': 'Business Found', 'stage_type': 'regular', 'order': 1, 'days_until_next': 0, 'auto_send_email': False},
    {'name': 'Invited', 'stage_type': 'regular', 'order': 2, 'days_until_next': 3, 'auto_send_email': True},
    {'name': 'Follow Up 1', 'stage_type': 'regular', 'order': 3, 'days_until_next': 4, 'auto_send_email': True},
    {'name': 'Follow Up 2', 'stage_type': 'regular', 'order': 4, 'days_until_next': 5, 'auto_send_email': True},
    {'name': 'Responded', 'stage_type': 'regular', 'order': 5, 'days_until_next': 0, 'auto_send_email': False},
    {'name': 'Signed Up', 'stage_type': 'won', 'order': 6, 'days_until_next': 0, 'auto_send_email': True},
    {'name': 'Listed', 'stage_type': 'won', 'order': 7, 'days_until_next': 0, 'auto_send_email': False},
    {'name': 'Lost', 'stage_type': 'lost', 'order': 8, 'days_until_next': 0, 'auto_send_email': False},
]

for stage_data in stages:
    stage, created = PipelineStage.objects.update_or_create(
        pipeline=pipeline,
        name=stage_data['name'],
        defaults=stage_data
    )
    print(f"  {'Created' if created else 'Updated'} stage: {stage.name}")

print(f"\n✅ Business Directory CRM ready!")
print(f"   Pipeline board: /admin/crm/pipeline/{pipeline.id}/board/")
print(f"   Brand admin: /admin/crm/brand/{brand.id}/change/")
```

---

## Type 3: B2B Sales CRM

**Use case:** Service agencies nurturing leads from intro to client.

```python
from crm.models import Brand, Pipeline, PipelineStage

# === EDIT THESE VALUES ===
BRAND_NAME = "Client Agency"
BRAND_SLUG = "client-agency"
WEBSITE = "https://clientagency.com.au"
PRIMARY_COLOR = "#8b5cf6"
FROM_EMAIL = "hello@clientagency.com.au"
FROM_NAME = "Alex from Client Agency"
BUSINESS_DESC = "Digital agency specializing in web development and AI solutions for growing businesses."
TARGET_AUDIENCE = "Small to medium businesses needing websites, apps, or AI automation. Decision makers like founders, marketing managers, and operations leads."
# === END EDIT ===

# Create Brand
brand, created = Brand.objects.update_or_create(
    slug=BRAND_SLUG,
    defaults={
        'name': BRAND_NAME,
        'website': WEBSITE,
        'primary_color': PRIMARY_COLOR,
        'from_email': FROM_EMAIL,
        'from_name': FROM_NAME,
        'ai_business_updates': f"""
- Company: {BRAND_NAME}
- Services: Web development, AI automation, digital solutions
- Recent work: Just launched several successful client projects
- Approach: We solve business problems with technology
- Book a free discovery call to discuss your needs
""",
        'ai_target_context': TARGET_AUDIENCE,
        'ai_approach_style': 'problem_solving',
        'is_active': True,
    }
)
print(f"{'Created' if created else 'Updated'} brand: {brand.name}")

# Create Pipeline
pipeline, created = Pipeline.objects.update_or_create(
    brand=brand,
    slug=f"{BRAND_SLUG}-sales",
    defaults={
        'name': f"{BRAND_NAME} - Sales Pipeline",
        'pipeline_type': 'sales',
        'is_active': True,
        'is_default': True,
    }
)
print(f"{'Created' if created else 'Updated'} pipeline: {pipeline.name}")

# Create Stages
stages = [
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

for stage_data in stages:
    stage, created = PipelineStage.objects.update_or_create(
        pipeline=pipeline,
        name=stage_data['name'],
        defaults=stage_data
    )
    print(f"  {'Created' if created else 'Updated'} stage: {stage.name}")

print(f"\n✅ B2B Sales CRM ready!")
print(f"   Pipeline board: /admin/crm/pipeline/{pipeline.id}/board/")
print(f"   Brand admin: /admin/crm/brand/{brand.id}/change/")
```

---

## After Setup: Import Contacts

### From CSV File

```python
import csv
from crm.models import Contact, Brand

BRAND_SLUG = "client-slug"  # Edit this
CSV_PATH = "/path/to/contacts.csv"  # Edit this

brand = Brand.objects.get(slug=BRAND_SLUG)

with open(CSV_PATH, 'r') as f:
    reader = csv.DictReader(f)
    created_count = 0
    for row in reader:
        contact, created = Contact.objects.get_or_create(
            email=Contact.normalize_email(row['email']),
            brand=brand,
            defaults={
                'name': row.get('name', ''),
                'company': row.get('company', ''),
                'phone': row.get('phone', ''),
                'source': row.get('source', 'csv_import'),
            }
        )
        if created:
            created_count += 1

print(f"✅ Imported {created_count} new contacts")
```

### Create Deals for Contacts

```python
from crm.models import Contact, Deal, Pipeline, PipelineStage

BRAND_SLUG = "client-slug"  # Edit this

pipeline = Pipeline.objects.get(brand__slug=BRAND_SLUG, is_default=True)
first_stage = pipeline.stages.order_by('order').first()
contacts = Contact.objects.filter(brand__slug=BRAND_SLUG)

created_count = 0
for contact in contacts:
    deal, created = Deal.objects.get_or_create(
        contact=contact,
        pipeline=pipeline,
        defaults={
            'stage': first_stage,
            'status': 'active',
        }
    )
    if created:
        created_count += 1

print(f"✅ Created {created_count} deals in pipeline")
```

---

## Verify Setup

```python
from crm.models import Brand, Pipeline, PipelineStage, Contact, Deal

BRAND_SLUG = "client-slug"  # Edit this

brand = Brand.objects.get(slug=BRAND_SLUG)
pipeline = Pipeline.objects.get(brand=brand, is_default=True)
stages = pipeline.stages.all()
contacts = Contact.objects.filter(brand=brand)
deals = Deal.objects.filter(pipeline=pipeline)

print(f"""
=== CRM Setup Verification ===

Brand: {brand.name}
  - Website: {brand.website}
  - Email: {brand.from_email}
  - AI Style: {brand.ai_approach_style}

Pipeline: {pipeline.name}
  - Type: {pipeline.pipeline_type}
  - Stages: {stages.count()}

Stages:
{chr(10).join(f'  {s.order}. {s.name} ({s.stage_type})' for s in stages)}

Contacts: {contacts.count()}
Deals: {deals.count()}

URLs:
  - Pipeline Board: /admin/crm/pipeline/{pipeline.id}/board/
  - Brand Settings: /admin/crm/brand/{brand.id}/change/
  - Contacts: /admin/crm/contact/?brand__id__exact={brand.id}
""")
```

---

## Quick Reference

### Brand AI Configuration

```python
# Update AI settings anytime
brand = Brand.objects.get(slug="client-slug")

brand.ai_business_updates = """
- New feature: Premium listings now available
- Promotion: First 50 businesses get featured placement
- Update: Added Google Maps integration
"""

brand.ai_target_context = """
Local restaurants and cafes in Sydney CBD.
Pain points: Low foot traffic, no online presence.
"""

brand.ai_approach_style = "problem_solving"  # or: value_driven, relationship, direct

brand.save()
```

### Stage Timing

```python
# Adjust follow-up timing
from crm.models import PipelineStage

stage = PipelineStage.objects.get(pipeline__brand__slug="client-slug", name="Follow Up 1")
stage.days_until_next = 5  # Wait 5 days before next action
stage.save()
```

### Pipeline Stats

```python
from crm.models import Deal, Pipeline
from django.db.models import Count

pipeline = Pipeline.objects.get(brand__slug="client-slug", is_default=True)

stats = Deal.objects.filter(pipeline=pipeline).values('status').annotate(count=Count('id'))
print("Pipeline Stats:")
for s in stats:
    print(f"  {s['status']}: {s['count']}")
```

---

## Troubleshooting

### "Brand not found"
```python
from crm.models import Brand
print(list(Brand.objects.values_list('slug', flat=True)))
```

### "Pipeline has no stages"
```python
from crm.models import Pipeline
p = Pipeline.objects.get(brand__slug="client-slug")
print(f"Stages: {p.stages.count()}")
# Re-run the stage creation script if 0
```

### "Emails not sending"
```python
from crm.models import Brand
brand = Brand.objects.get(slug="client-slug")
print(f"From email: {brand.from_email}")
print(f"Active: {brand.is_active}")
# Check Zoho credentials in environment
```

---

**Document Version:** 1.0
**For use by:** Claude Code / Developers
