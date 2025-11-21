# Generated migration for FAQ Page Sections

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_sitesettings_support_badge_and_more'),
    ]

    operations = [
        # FAQ Page Section
        migrations.CreateModel(
            name='FAQPageSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('badge', models.CharField(blank=True, max_length=100)),
                ('title', models.CharField(max_length=200, default='FAQ Hub')),
                ('description', models.TextField(default='Answers for every stage of your AI journey')),
                ('search_placeholder', models.CharField(max_length=100, default='Search FAQs...')),
                ('cta_text', models.CharField(max_length=100, default='Book strategy call')),
                ('cta_url', models.CharField(max_length=255, default='/contact')),
                ('secondary_cta_text', models.CharField(max_length=100, blank=True, default='Still stuck? Message the team')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'FAQ Page Section',
                'verbose_name_plural': 'FAQ Page Sections',
            },
        ),
        # FAQ Page Stats
        migrations.CreateModel(
            name='FAQPageStat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stats', to='core.faqpagesection')),
                ('value', models.CharField(max_length=60, help_text='e.g., < 24 hrs, 80+, 14')),
                ('label', models.CharField(max_length=120, help_text='e.g., Average response time')),
                ('detail', models.CharField(max_length=200, blank=True, help_text='Additional detail text')),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'FAQ Page Stat',
            },
        ),
        # Add icon and description fields to FAQCategory
        migrations.AddField(
            model_name='faqcategory',
            name='description',
            field=models.TextField(blank=True, help_text='Category description'),
        ),
        migrations.AddField(
            model_name='faqcategory',
            name='icon',
            field=models.CharField(blank=True, max_length=40, help_text='Icon name for the category'),
        ),
    ]
