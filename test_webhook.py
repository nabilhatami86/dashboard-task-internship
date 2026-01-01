#!/usr/bin/env python3
"""
Test script untuk simulasi WhatsApp webhook - Agent Warung Madura
"""
import requests
import json

# Test webhook endpoint
WEBHOOK_URL = "http://localhost:8000/webhook/whapi"

# Skenario testing untuk Agent Warung Madura
SCENARIOS = {
    "1": {
        "name": "Stock Habis",
        "from": "6281234567890@c.us",
        "from_name": "Warung Pak Budi",
        "message": "Min, stock indomie goreng habis. Kapan bisa restock?"
    },
    "2": {
        "name": "Masalah Pembayaran",
        "from": "6282345678901@c.us",
        "from_name": "Warung Bu Siti",
        "message": "Admin, ada customer bayar tapi belum masuk ke sistem"
    },
    "3": {
        "name": "Sistem Error",
        "from": "6283456789012@c.us",
        "from_name": "Warung Mas Agus",
        "message": "Sistemnya error, gak bisa input pesanan baru"
    },
    "4": {
        "name": "Promo",
        "from": "6284567890123@c.us",
        "from_name": "Warung Mbak Rina",
        "message": "Min, ada promo bulan ini gak? Customer banyak yang nanya"
    },
    "5": {
        "name": "Komplain Pengiriman",
        "from": "6285678901234@c.us",
        "from_name": "Warung Pak Joko",
        "message": "Pengiriman kemarin telat 3 jam, customer komplain"
    },
    "6": {
        "name": "Custom Message",
        "from": "6286789012345@c.us",
        "from_name": "Warung Test",
        "message": ""  # Will be input by user
    }
}

def print_menu():
    print("\n" + "=" * 60)
    print("TESTING AGENT WARUNG MADURA - WEBHOOK SIMULATOR")
    print("=" * 60)
    print("\nPilih Skenario Test:")
    print("-" * 60)
    for key, scenario in SCENARIOS.items():
        print(f"{key}. {scenario['name']}")
        if scenario['message']:
            print(f"   Pesan: \"{scenario['message']}\"")
    print("-" * 60)
    print("0. Exit")
    print()

def create_payload(scenario):
    """Create webhook payload from scenario"""
    import time
    return {
        "messages": [
            {
                "from": scenario["from"],
                "from_name": scenario["from_name"],
                "pushname": scenario["from_name"],
                "text": {
                    "body": scenario["message"]
                },
                "timestamp": int(time.time())
            }
        ]
    }

# Default test payload (if run without menu)
test_payload = {
    "messages": [
        {
            "from": "6281234567890@c.us",
            "from_name": "Warung Pak Budi",
            "pushname": "Warung Pak Budi",
            "text": {
                "body": "Min, stock indomie goreng habis. Kapan bisa restock?"
            },
            "timestamp": 1704123456
        }
    ]
}

def send_test_message(payload):
    """Send test message to webhook endpoint"""
    print("\n" + "=" * 60)
    print("Endpoint:", WEBHOOK_URL)
    print("=" * 60)
    print("\nPayload:")
    print(json.dumps(payload, indent=2))
    print("\nSending request...")
    print()

    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print("=" * 60)
        print("Response Status:", response.status_code)
        print("=" * 60)
        print()

        if response.status_code == 200:
            print("✅ SUCCESS! Chat & Bot Response created!")
            print()
            print("Response Body:")
            print(json.dumps(response.json(), indent=2))
            print()
            print("=" * 60)
            print("Next Steps:")
            print("=" * 60)
            print("1. Open dashboard: http://localhost:3000/login")
            print("2. Login: admin / admin123")
            print("3. Chat akan muncul di sidebar!")
            print("4. Klik chat untuk lihat bot response")
            print()
            return True
        else:
            print("❌ FAILED!")
            print()
            print("Response Body:")
            print(response.text)
            print()
            return False

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend!")
        print()
        print("Make sure backend is running:")
        print("  cd backend-dashboard-python")
        print("  python3 -m uvicorn app.main:app --reload")
        print()
        return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        return False


def main():
    """Main interactive menu"""
    while True:
        print_menu()
        choice = input("Pilih skenario (0-6): ").strip()

        if choice == "0":
            print("\n✅ Selamat testing! Bye!\n")
            break

        if choice not in SCENARIOS:
            print("❌ Pilihan tidak valid!")
            continue

        scenario = SCENARIOS[choice].copy()

        # Handle custom message
        if choice == "6":
            custom_msg = input("\nMasukkan pesan custom: ").strip()
            if not custom_msg:
                print("❌ Pesan tidak boleh kosong!")
                continue
            scenario["message"] = custom_msg

        # Create and send payload
        payload = create_payload(scenario)
        success = send_test_message(payload)

        if success:
            another = input("\nTest skenario lain? (y/n): ").strip().lower()
            if another != 'y':
                print("\n✅ Testing selesai!\n")
                break
        else:
            retry = input("\nRetry? (y/n): ").strip().lower()
            if retry != 'y':
                break


if __name__ == "__main__":
    # Check if running with interactive mode
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test mode - langsung kirim default payload
        print("\n🚀 Quick Test Mode - Sending default scenario...")
        send_test_message(test_payload)
    else:
        # Interactive menu mode
        main()
