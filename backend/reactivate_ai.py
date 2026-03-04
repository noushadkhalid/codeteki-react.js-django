"""Reactivate AI for all handoff conversations. Run: python manage.py shell < reactivate_ai.py"""
from crm.models import WhatsAppConversation

convos = WhatsAppConversation.objects.filter(ai_active=False)
for c in convos:
    print(f"{c.phone} ai_active={c.ai_active} phase={c.phase}")
    c.ai_active = True
    c.phase = 'active'
    c.save(update_fields=['ai_active', 'phase'])
    print(f"  -> Reactivated")

print(f"\nDone. Reactivated {convos.count()} conversations.")
