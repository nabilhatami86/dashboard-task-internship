from fastapi import APIRouter, Request
from app.whapi.client import send_text
from app.services.bot_service import handle_bot

router = APIRouter()

@router.post("/webhook/whapi")
async def whapi_webhook(request: Request):
    data = await request.json()

    if "messages" not in data:
        return {"status": "ignored"}

    msg = data["messages"][0]
    sender = msg["from"]
    text = msg["text"]["body"]

    reply = handle_bot(sender, text)
    if reply:
        send_text(sender, reply)

    return {"status": "ok"}
