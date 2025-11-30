# Generated migration to move SocialLink from SiteSettings to FooterSection

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_add_social_links'),
    ]

    operations = [
        # Remove old FK to SiteSettings
        migrations.RemoveField(
            model_name='sociallink',
            name='site_settings',
        ),
        # Add new FK to FooterSection
        migrations.AddField(
            model_name='sociallink',
            name='footer_section',
            field=models.ForeignKey(
                default=1,  # Temporary default, will be updated
                on_delete=django.db.models.deletion.CASCADE,
                related_name='social_links',
                to='core.footersection'
            ),
            preserve_default=False,
        ),
    ]
