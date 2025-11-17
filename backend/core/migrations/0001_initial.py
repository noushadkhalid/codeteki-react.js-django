from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='BusinessImpactSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=160)),
                ('description', models.TextField()),
                ('cta_label', models.CharField(max_length=80)),
                ('cta_href', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Business Impact Section',
            },
        ),
        migrations.CreateModel(
            name='HeroSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('badge', models.CharField(max_length=120)),
                ('title', models.CharField(max_length=255)),
                ('highlighted_text', models.CharField(max_length=120)),
                ('subheading', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField()),
                ('primary_cta_label', models.CharField(max_length=80)),
                ('primary_cta_href', models.CharField(max_length=200)),
                ('secondary_cta_label', models.CharField(max_length=80)),
                ('secondary_cta_href', models.CharField(max_length=200)),
                ('image_url', models.URLField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-updated_at'],
                'verbose_name': 'Hero Section',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=160)),
                ('slug', models.SlugField(unique=True)),
                ('badge', models.CharField(blank=True, max_length=120)),
                ('description', models.TextField()),
                ('icon', models.CharField(default='Sparkles', max_length=40)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='ContactMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=160)),
                ('description', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=120)),
                ('cta_label', models.CharField(max_length=80)),
                ('icon', models.CharField(default='Mail', max_length=40)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'Contact Method',
            },
        ),
        migrations.CreateModel(
            name='FAQCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=160)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'FAQ Category',
            },
        ),
        migrations.CreateModel(
            name='BusinessImpactLogo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('logo_url', models.URLField()),
                ('order', models.PositiveIntegerField(default=0)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logos', to='core.businessimpactsection')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='BusinessImpactMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=40)),
                ('label', models.CharField(max_length=120)),
                ('caption', models.CharField(max_length=255)),
                ('icon', models.CharField(default='MessageCircle', max_length=40)),
                ('theme_bg_class', models.CharField(default='bg-blue-100', max_length=40)),
                ('theme_text_class', models.CharField(default='text-blue-600', max_length=40)),
                ('order', models.PositiveIntegerField(default=0)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='core.businessimpactsection')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='HeroMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=120)),
                ('value', models.CharField(max_length=60)),
                ('order', models.PositiveIntegerField(default=0)),
                ('hero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='core.herosection')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='HeroPartnerLogo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('logo_url', models.URLField()),
                ('order', models.PositiveIntegerField(default=0)),
                ('hero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partner_logos', to='core.herosection')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='ServiceOutcome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('order', models.PositiveIntegerField(default=0)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outcomes', to='core.service')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='FAQItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255)),
                ('answer', models.TextField()),
                ('order', models.PositiveIntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='core.faqcategory')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
