# Migration for adding registered_users pipeline type

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0019_add_nudge_email_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipeline',
            name='pipeline_type',
            field=models.CharField(
                max_length=20,
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
                ],
            ),
        ),
    ]
