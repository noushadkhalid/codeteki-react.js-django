# Update EmailLog default from_email from outreach@ to sales@

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0022_brand_zeptomail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emaillog',
            name='from_email',
            field=models.EmailField(default='sales@codeteki.au', max_length=254),
        ),
    ]
