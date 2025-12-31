import requests
from app.config.confiq_whapi import settings

def send_text(to: str, text: str):
    url = f"{settings.WHAPI_BASE_URL}/messages/text"
    headers = {
        "Authorization": f"Bearer {settings.WHAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": to,
        "body": text
    }

    requests.post(url, json=payload, headers=headers, timeout=10)
