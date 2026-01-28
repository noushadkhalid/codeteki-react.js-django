# Generated migration for email scheduling fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0020_add_registered_users_pipeline_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='emaildraft',
            name='scheduled_for',
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text='Schedule email to be sent at this time (Australia/Sydney timezone)'
            ),
        ),
        migrations.AddField(
            model_name='emaildraft',
            name='schedule_status',
            field=models.CharField(
                choices=[
                    ('not_scheduled', 'Not Scheduled'),
                    ('scheduled', 'Scheduled'),
                    ('sending', 'Sending'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                    ('failed', 'Failed'),
                ],
                default='not_scheduled',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='emaildraft',
            name='schedule_error',
            field=models.TextField(
                blank=True,
                help_text='Error message if scheduled send failed'
            ),
        ),
    ]
