"""
Bulk-fix contacts with failed WhatsApp deliveries.
Sets has_whatsapp=False so future sends route to SMS.

Run with: python manage.py shell < fix_whatsapp_contacts.py
"""
from crm.models import EmailLog, Contact

# Find all phones with failed WhatsApp deliveries
failed_phones = list(
    EmailLog.objects.filter(channel='whatsapp', delivery_status='failed')
    .values_list('to_phone', flat=True)
    .distinct()
)

# Flip has_whatsapp=False for all of them
updated = Contact.objects.filter(phone__in=failed_phones, has_whatsapp=True).update(has_whatsapp=False)
print(f'Found {len(failed_phones)} phones with failed WhatsApp: {failed_phones}')
print(f'Fixed {updated} contacts — future sends will use SMS')
