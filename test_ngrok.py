#!/usr/bin/env python3
"""
Test ngrok webhook integration
"""
import requests
import json
import sys

def test_ngrok_webhook(ngrok_url):
    """Test webhook via ngrok URL"""

    # Remove trailing slash
    ngrok_url = ngrok_url.rstrip('/')

    webhook_endpoint = f"{ngrok_url}/webhook/whapi"

    # Test payload
    payload = {
        "messages": [{
            "from": "628123456789@c.us",
            "from_name": "Test via ngrok",
            "pushname": "Test User",
            "text": {
                "body": "Halo, test dari ngrok!"
            }
        }]
    }

    print("=" * 70)
    print("Testing ngrok Webhook Integration")
    print("=" * 70)
    print(f"\nngrok URL: {ngrok_url}")
    print(f"Webhook endpoint: {webhook_endpoint}")
    print("\nPayload:")
    print(json.dumps(payload, indent=2))
    print("\nSending request...\n")

    try:
        response = requests.post(
            webhook_endpoint,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "ngrok-skip-browser-warning": "true"
            },
            timeout=10
        )

        print("=" * 70)
        print(f"Response Status: {response.status_code}")
        print("=" * 70)
        print()

        if response.status_code == 200:
            print("✅ SUCCESS! Webhook working via ngrok!")
            print("\nResponse:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)

            print("\n" + "=" * 70)
            print("Next Steps:")
            print("=" * 70)
            print(f"1. Set webhook di WHAPI.cloud:")
            print(f"   {webhook_endpoint}")
            print()
            print("2. Check database:")
            print("   curl http://localhost:8000/chats/")
            print()
            print("3. Open dashboard:")
            print("   http://localhost:3000/login")
            print("   Login: admin / admin123")
            print()
            print("4. Send WhatsApp message to bot number")
            print("   Message will appear in dashboard!")

        else:
            print(f"❌ FAILED! Status code: {response.status_code}")
            print("\nResponse:")
            print(response.text[:500])

    except requests.exceptions.ConnectionError as e:
        print("❌ CONNECTION ERROR!")
        print(f"\nError: {e}")
        print("\n" + "=" * 70)
        print("Troubleshooting:")
        print("=" * 70)
        print("1. Check if ngrok is running:")
        print("   ps aux | grep ngrok")
        print()
        print("2. Check ngrok URL is correct")
        print("   Should look like: https://xxx.ngrok-free.app")
        print()
        print("3. Check if backend is running:")
        print("   curl http://localhost:8000/")

    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_ngrok.py <ngrok-url>")
        print()
        print("Example:")
        print("  python3 test_ngrok.py https://abc123.ngrok-free.app")
        print()
        print("Get your ngrok URL from ngrok terminal output:")
        print("  Forwarding    https://xxx.ngrok-free.app -> http://localhost:8000")
        sys.exit(1)

    ngrok_url = sys.argv[1]
    test_ngrok_webhook(ngrok_url)
