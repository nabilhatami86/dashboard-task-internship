#!/usr/bin/env python3
"""
Setup WHAPI Webhook via API
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# WHAPI Configuration
WHAPI_BASE_URL = os.getenv("WHAPI_BASE_URL", "https://gate.whapi.cloud")
WHAPI_TOKEN = os.getenv("WHAPI_TOKEN", "vIjXz9hkpWKQc5vO17wbp1gGnzMN1kFR")

# Your ngrok URL - Updated automatically
NGROK_URL = "https://0d26230b35fb.ngrok-free.app"
WEBHOOK_URL = f"{NGROK_URL}/webhook/whapi"

print("=" * 70)
print("Setting up WHAPI Webhook")
print("=" * 70)
print(f"\nWHAPI Base URL: {WHAPI_BASE_URL}")
print(f"WHAPI Token: {WHAPI_TOKEN[:10]}...")
print(f"Webhook URL: {WEBHOOK_URL}")
print()

# Headers
headers = {
    "Authorization": f"Bearer {WHAPI_TOKEN}",
    "Content-Type": "application/json"
}

print("Step 1: Get current settings...")
try:
    response = requests.get(
        f"{WHAPI_BASE_URL}/settings",
        headers=headers,
        timeout=10
    )

    if response.status_code == 200:
        current_settings = response.json()
        print("✅ Current settings retrieved")
        print(json.dumps(current_settings, indent=2))
    else:
        print(f"⚠️  Status: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("Step 2: Update webhook settings...")
print("=" * 70)

# Webhook configuration
webhook_config = {
    "webhooks": [
        {
            "url": WEBHOOK_URL,
            "events": [
                {
                    "type": "messages",
                    "method": "post"
                }
            ],
            "mode": "method"
        }
    ]
}

print(f"\nWebhook config:")
print(json.dumps(webhook_config, indent=2))
print()

try:
    response = requests.patch(
        f"{WHAPI_BASE_URL}/settings",
        headers=headers,
        json=webhook_config,
        timeout=10
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code in [200, 201]:
        print("✅ SUCCESS! Webhook configured")
        print("\nResponse:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
    else:
        print("❌ FAILED!")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("Step 3: Test webhook...")
print("=" * 70)

try:
    response = requests.post(
        f"{WHAPI_BASE_URL}/settings/webhook_test",
        headers=headers,
        timeout=10
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Webhook test successful!")
        print(response.text)
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"⚠️  Cannot test webhook: {e}")

print("\n" + "=" * 70)
print("Next Steps:")
print("=" * 70)
print("1. Send WhatsApp message to: +62 877 3162 4016")
print("2. Monitor ngrok Web UI: http://127.0.0.1:4040")
print("3. Check backend logs for: 'Received webhook data'")
print("4. Check dashboard: http://localhost:3000/login")
print()
print("✅ Webhook should now be active!")
print("=" * 70)
