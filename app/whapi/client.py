import logging
import requests
from app.config.confiq_whapi import settings

logger = logging.getLogger(__name__)


def send_text(to: str, text: str) -> dict:
    url = f"{settings.WHAPI_BASE_URL}/messages/text"
    headers = {
        "Authorization": f"Bearer {settings.WHAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"to": to, "body": text}

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        return {"ok": True, "status_code": resp.status_code, "body": body}
    except requests.RequestException as e:
        logger.exception("Failed to send WHAPI message")
        return {"ok": False, "error": str(e)}
