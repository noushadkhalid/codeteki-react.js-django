# Add ZeptoMail fields to Brand model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0021_emaildraft_scheduling'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='zeptomail_api_key',
            field=models.CharField(
                blank=True,
                help_text='ZeptoMail API key (e.g., Zoho-enczapikey ...). If set, uses ZeptoMail instead of Zoho Mail.',
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name='brand',
            name='zeptomail_host',
            field=models.CharField(
                blank=True,
                default='api.zeptomail.com',
                help_text='ZeptoMail API host: api.zeptomail.com (US) or api.zeptomail.com.au (AU)',
                max_length=100,
            ),
        ),
    ]
