from django.db import migrations


def create_no_website_pipeline(apps, schema_editor):
    """Create Business Without Website pipeline with stages for Codeteki."""
    Brand = apps.get_model('crm', 'Brand')
    Pipeline = apps.get_model('crm', 'Pipeline')
    PipelineStage = apps.get_model('crm', 'PipelineStage')

    brand = Brand.objects.filter(slug='codeteki').first()

    pipeline = Pipeline.objects.create(
        brand=brand,
        name='Business Without Website',
        pipeline_type='no_website',
        description='Outreach to local businesses found via Google Places that don\'t have a website.',
        is_active=True,
    )

    stages = [
        ('New Lead', 0, 2, False),
        ('Contacted', 1, 3, False),
        ('Interested', 2, 2, False),
        ('Proposal Sent', 3, 5, False),
        ('Won', 4, 0, True),
        ('Lost', 5, 0, True),
    ]

    for name, order, days, is_terminal in stages:
        PipelineStage.objects.create(
            pipeline=pipeline,
            name=name,
            order=order,
            days_until_followup=days,
            is_terminal=is_terminal,
        )


def reverse_migration(apps, schema_editor):
    Pipeline = apps.get_model('crm', 'Pipeline')
    Pipeline.objects.filter(pipeline_type='no_website').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0038_whatsapp_inquiry_pipeline'),
    ]

    operations = [
        migrations.RunPython(create_no_website_pipeline, reverse_migration),
    ]
