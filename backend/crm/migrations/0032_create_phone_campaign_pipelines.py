from django.db import migrations


def create_phone_campaign_pipelines(apps, schema_editor):
    Brand = apps.get_model('crm', 'Brand')
    Pipeline = apps.get_model('crm', 'Pipeline')
    PipelineStage = apps.get_model('crm', 'PipelineStage')

    stages = [
        {'name': 'Lead Found', 'order': 1, 'is_terminal': False, 'days_until_followup': 0},
        {'name': 'Intro Message Sent', 'order': 2, 'is_terminal': False, 'days_until_followup': 3},
        {'name': 'Follow Up 1', 'order': 3, 'is_terminal': False, 'days_until_followup': 4},
        {'name': 'Follow Up 2', 'order': 4, 'is_terminal': False, 'days_until_followup': 7},
        {'name': 'Responded', 'order': 5, 'is_terminal': False, 'days_until_followup': 1},
        {'name': 'Call Booked', 'order': 6, 'is_terminal': False, 'days_until_followup': 2},
        {'name': 'Converted', 'order': 7, 'is_terminal': True, 'days_until_followup': 0},
        {'name': 'Lost', 'order': 8, 'is_terminal': True, 'days_until_followup': 0},
    ]

    for brand in Brand.objects.filter(is_active=True):
        pipeline, created = Pipeline.objects.get_or_create(
            brand=brand,
            pipeline_type='phone_campaign',
            defaults={
                'name': f'{brand.name} Phone Campaign',
                'is_active': True,
            }
        )
        if created:
            for s in stages:
                PipelineStage.objects.create(pipeline=pipeline, **s)


def remove_phone_campaign_pipelines(apps, schema_editor):
    Pipeline = apps.get_model('crm', 'Pipeline')
    Pipeline.objects.filter(pipeline_type='phone_campaign').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0031_combine_sms_whatsapp_into_phone_channel'),
    ]

    operations = [
        migrations.RunPython(create_phone_campaign_pipelines, remove_phone_campaign_pipelines),
    ]
