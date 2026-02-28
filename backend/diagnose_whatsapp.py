"""Run with: python manage.py shell < diagnose_whatsapp.py"""
from crm.models import EmailLog
from crm.services.messaging_service import MetaWhatsAppService

print("=" * 60)
print("1. Recent WhatsApp EmailLogs:")
print("=" * 60)
logs = EmailLog.objects.filter(channel='whatsapp').order_by('-created_at')[:5]
for l in logs:
    print(f"  {l.created_at} | {l.to_phone} | {l.delivery_status} | {l.body[:60]}")
if not logs:
    print("  NO WhatsApp EmailLogs found")

print()
print("=" * 60)
print("2. MetaWhatsAppService config:")
print("=" * 60)
wa = MetaWhatsAppService()
print(f"  Enabled: {wa.enabled}")
print(f"  Phone ID: {wa.phone_id}")
print(f"  Token set: {bool(wa.token)}")
if wa.token:
    print(f"  Token starts: {wa.token[:15]}...")

print()
print("=" * 60)
print("3. Testing send to +61424538777:")
print("=" * 60)
result = wa.send_text(to='+61424538777', body='Diagnostic test from server')
print(f"  Result: {result}")

print()
print("=" * 60)
print("4. WhatsApp Conversations:")
print("=" * 60)
try:
    from crm.models import WhatsAppConversation
    convos = WhatsAppConversation.objects.all()[:5]
    for c in convos:
        print(f"  {c.phone} | ai_active={c.ai_active} | phase={c.phase} | msgs={c.message_count}")
    if not convos:
        print("  No WhatsAppConversation records")
except Exception as e:
    print(f"  Error: {e}")
