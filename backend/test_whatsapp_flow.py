"""
Full end-to-end test of the WhatsApp pipeline.
Simulates: customer message → AI response → handoff → owner notification

Run with: python manage.py shell < test_whatsapp_flow.py
"""
import time
import os

TEST_PHONE = '+61400000000'  # Fake number — won't actually send WhatsApp

print("=" * 60)
print("WHATSAPP PIPELINE END-TO-END TEST")
print("=" * 60)

# Step 0: Clean up any previous test data
from crm.models import EmailLog, WhatsAppConversation
EmailLog.objects.filter(to_phone=TEST_PHONE).delete()
WhatsAppConversation.objects.filter(phone=TEST_PHONE).delete()
print("\n[CLEANUP] Removed previous test data")

# Step 1: Simulate first customer message
print("\n" + "=" * 60)
print("STEP 1: Customer sends first message")
print("=" * 60)
from crm.services.whatsapp_ai import WhatsAppAIService
service = WhatsAppAIService()

response1 = service.handle_inbound(TEST_PHONE, "Hi, I want to list my restaurant", "Test Customer")
print(f"  AI Response: {response1[:100] if response1 else 'NONE'}...")

conv = WhatsAppConversation.objects.filter(phone=TEST_PHONE).first()
if conv:
    print(f"  Conversation created: YES")
    print(f"    ai_active: {conv.ai_active}")
    print(f"    phase: {conv.phase}")
    print(f"    user_type: {conv.user_type}")
    print(f"    message_count: {conv.message_count}")
    print(f"    contact: {conv.contact}")
    print(f"    deal: {conv.deal}")
else:
    print("  ERROR: No conversation created!")

# Check EmailLog
logs = EmailLog.objects.filter(to_phone=TEST_PHONE).order_by('-sent_at')
print(f"  EmailLogs created: {logs.count()}")
for log in logs:
    print(f"    [{log.delivery_status}] {log.body[:60]}...")

# Step 2: Simulate second customer message
print("\n" + "=" * 60)
print("STEP 2: Customer sends follow-up message")
print("=" * 60)
response2 = service.handle_inbound(TEST_PHONE, "Yes I have an Indian restaurant in Sydney", "Test Customer")
print(f"  AI Response: {response2[:100] if response2 else 'NONE'}...")

conv.refresh_from_db()
print(f"  phase: {conv.phase}")
print(f"  user_type: {conv.user_type}")
print(f"  message_count: {conv.message_count}")

# Step 3: Customer requests human
print("\n" + "=" * 60)
print("STEP 3: Customer types 'talk to human'")
print("=" * 60)
response3 = service.handle_inbound(TEST_PHONE, "talk to human", "Test Customer")
print(f"  AI Response: {response3}")  # Should be None (handoff handles it)

conv.refresh_from_db()
print(f"  ai_active: {conv.ai_active} (should be False)")
print(f"  phase: {conv.phase} (should be handoff)")
print(f"  handoff_at: {conv.handoff_at}")
print(f"  handoff_reason: {conv.handoff_reason}")

if conv.deal:
    conv.deal.refresh_from_db()
    print(f"  deal stage: {conv.deal.current_stage}")

# Check handoff message was sent to customer
logs = EmailLog.objects.filter(to_phone=TEST_PHONE).order_by('-sent_at')
handoff_msg = logs.filter(body__icontains='connecting you').first()
print(f"  Handoff message to customer: {'YES' if handoff_msg else 'NOT FOUND'}")

# Step 4: Check owner notification
print("\n" + "=" * 60)
print("STEP 4: Owner notification check")
print("=" * 60)
owner_phone = os.environ.get('OWNER_NOTIFY_PHONE', '')
owner_email = os.environ.get('OWNER_NOTIFY_EMAIL', '')
print(f"  OWNER_NOTIFY_PHONE: {owner_phone}")
print(f"  OWNER_NOTIFY_EMAIL: {owner_email}")

# Check if SMS was sent to owner (look in Twilio logs indirectly via our logs)
# The _notify_owner sends WhatsApp first, then SMS fallback
# We can't check Twilio directly, but we logged it
print(f"  (Check server logs for 'Owner notified via SMS' or 'Owner notified via WhatsApp')")

# Step 5: Verify AI stops responding after handoff
print("\n" + "=" * 60)
print("STEP 5: Customer sends message after handoff (AI should NOT respond)")
print("=" * 60)
response4 = service.handle_inbound(TEST_PHONE, "Hello? Is anyone there?", "Test Customer")
print(f"  AI Response: {response4} (should be None — AI inactive)")

conv.refresh_from_db()
print(f"  ai_active: {conv.ai_active} (should still be False)")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
total_logs = EmailLog.objects.filter(to_phone=TEST_PHONE).count()
print(f"  Total EmailLogs for test: {total_logs}")
print(f"  Conversation phase: {conv.phase}")
print(f"  AI active: {conv.ai_active}")
print(f"  Handoff triggered: {'YES' if conv.handoff_at else 'NO'}")

# Cleanup option
print("\n" + "=" * 60)
print("CLEANUP")
print("=" * 60)
# Clean up test data
from crm.models import Deal, Contact, DealActivity
if conv.deal:
    DealActivity.objects.filter(deal=conv.deal).delete()
    conv.deal.delete()
    print("  Deleted test deal")
if conv.contact:
    conv.contact.delete()
    print("  Deleted test contact")
EmailLog.objects.filter(to_phone=TEST_PHONE).delete()
conv.delete()
print("  Deleted test conversation and logs")
print("\nDONE. Check server logs for owner notification delivery.")
