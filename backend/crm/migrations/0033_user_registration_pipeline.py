from django.db import migrations, models


def create_user_registration_pipeline(apps, schema_editor):
    Brand = apps.get_model('crm', 'Brand')
    Pipeline = apps.get_model('crm', 'Pipeline')
    PipelineStage = apps.get_model('crm', 'PipelineStage')

    brand = Brand.objects.filter(slug='desifirms').first()
    if not brand:
        return

    # Create the unified User Registration pipeline
    pipeline, created = Pipeline.objects.get_or_create(
        brand=brand,
        pipeline_type='user_registration',
        defaults={
            'name': 'Desi Firms User Registration',
            'is_active': True,
        }
    )
    if created:
        stages = [
            {'name': 'Registered', 'order': 1, 'is_terminal': False, 'days_until_followup': 2},
            {'name': 'Business Listed', 'order': 2, 'is_terminal': False, 'days_until_followup': 3},
            {'name': 'Event Posted', 'order': 3, 'is_terminal': False, 'days_until_followup': 3},
            {'name': 'Agent/Agency Created', 'order': 4, 'is_terminal': False, 'days_until_followup': 3},
            {'name': 'Classified Posted', 'order': 5, 'is_terminal': False, 'days_until_followup': 3},
            {'name': 'Listing Approved', 'order': 6, 'is_terminal': True, 'days_until_followup': 0},
            {'name': 'Inactive', 'order': 7, 'is_terminal': True, 'days_until_followup': 0},
        ]
        for s in stages:
            PipelineStage.objects.create(pipeline=pipeline, **s)

    # Deactivate old Registered Users pipelines (preserve historical data)
    Pipeline.objects.filter(
        brand=brand,
        pipeline_type='registered_users',
        is_active=True,
    ).update(is_active=False)


def reverse_user_registration_pipeline(apps, schema_editor):
    Brand = apps.get_model('crm', 'Brand')
    Pipeline = apps.get_model('crm', 'Pipeline')

    brand = Brand.objects.filter(slug='desifirms').first()
    if not brand:
        return

    # Delete the new pipeline
    Pipeline.objects.filter(
        brand=brand,
        pipeline_type='user_registration',
    ).delete()

    # Re-activate old pipelines
    Pipeline.objects.filter(
        brand=brand,
        pipeline_type='registered_users',
    ).update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0032_create_phone_campaign_pipelines'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipeline',
            name='pipeline_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('sales', 'Sales'),
                    ('backlink', 'Backlink Outreach'),
                    ('partnership', 'Partnership'),
                    ('business', 'Business Listings'),
                    ('deals', 'Deals & Promotions'),
                    ('events', 'Events'),
                    ('realestate', 'Real Estate'),
                    ('classifieds', 'Classifieds'),
                    ('registered_users', 'Registered Users (Nudge)'),
                    ('user_registration', 'User Registration'),
                    ('phone_campaign', 'Phone Campaign (SMS/WhatsApp)'),
                ],
                default='',
                max_length=50,
            ),
        ),
        migrations.RunPython(
            create_user_registration_pipeline,
            reverse_user_registration_pipeline,
        ),
    ]
