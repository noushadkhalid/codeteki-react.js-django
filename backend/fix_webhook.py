"""Run with: python manage.py shell < fix_webhook.py"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

token = os.environ.get('META_WHATSAPP_TOKEN', '')
waba_id = os.environ.get('META_WHATSAPP_BUSINESS_ID', '1483765046813764')
phone_id = os.environ.get('META_WHATSAPP_PHONE_ID', '1002787172916625')

headers = {'Authorization': f'Bearer {token}'}

print("=" * 60)
print("1. Check WABA subscription status:")
print("=" * 60)
r = requests.get(f'https://graph.facebook.com/v21.0/{waba_id}/subscribed_apps', headers=headers)
print(f"  {r.json()}")

print()
print("=" * 60)
print("2. Subscribe app to WABA webhooks:")
print("=" * 60)
r = requests.post(f'https://graph.facebook.com/v21.0/{waba_id}/subscribed_apps', headers=headers)
print(f"  {r.json()}")

print()
print("=" * 60)
print("3. Check phone number webhook status:")
print("=" * 60)
r = requests.get(f'https://graph.facebook.com/v21.0/{phone_id}', headers=headers, params={'fields': 'display_phone_number,verified_name,quality_rating,is_official_business_account'})
print(f"  {r.json()}")

print()
print("=" * 60)
print("4. Check WABA phone numbers:")
print("=" * 60)
r = requests.get(f'https://graph.facebook.com/v21.0/{waba_id}/phone_numbers', headers=headers)
print(f"  {r.json()}")
