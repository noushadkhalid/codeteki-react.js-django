from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_update_site_contact_info"),
    ]

    operations = [
        migrations.AddField(
            model_name="herosection",
            name="page",
            field=models.CharField(
                choices=[
                    ("home", "Home Page"),
                    ("services", "Services Page"),
                    ("ai-tools", "AI Tools Page"),
                    ("demos", "Demos Page"),
                    ("faq", "FAQ Page"),
                    ("contact", "Contact Page"),
                ],
                default="home",
                help_text="Landing page this hero should be displayed on.",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="service",
            name="is_featured",
            field=models.BooleanField(default=False),
        ),
    ]
