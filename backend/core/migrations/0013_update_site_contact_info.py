from django.db import migrations


def update_contact_info(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.filter(primary_phone="+61 123 456 789").update(
        primary_phone="+61 469 754 386"
    )
    SiteSettings.objects.filter(secondary_phone="+61 123 456 789").update(
        secondary_phone="+61 424 538 777"
    )
    SiteSettings.objects.filter(primary_email="info@codeteki.com").update(
        primary_email="info@codeteki.au"
    )


def reverse_update_contact_info(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.filter(primary_phone="+61 469 754 386").update(
        primary_phone="+61 123 456 789"
    )
    SiteSettings.objects.filter(secondary_phone="+61 424 538 777").update(
        secondary_phone="+61 123 456 789"
    )
    SiteSettings.objects.filter(primary_email="info@codeteki.au").update(
        primary_email="info@codeteki.com"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_faq_page_sections"),
    ]

    operations = [
        migrations.RunPython(update_contact_info, reverse_update_contact_info),
    ]
