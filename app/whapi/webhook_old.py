from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
import logging
from app.whapi.client import send_text
from app.services.bot_service import handle_bot

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhook/whapi")
async def whapi_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")

    msgs = data.get("messages")
    if not msgs or not isinstance(msgs, list):
        return {"status": "ignored"}

    msg = msgs[0]
    sender = msg.get("from") or msg.get("sender")

    text = None
    if isinstance(msg.get("text"), dict):
        text = msg["text"].get("body")
    else:
        text = msg.get("body") or msg.get("message") or msg.get("text")

    if not sender or not text:
        logger.info("webhook ignored: missing sender or text")
        return {"status": "ignored"}

    try:
        reply = handle_bot(sender, text)
    except Exception:
        logger.exception("bot handler failed")
        return {"status": "error"}

    if reply:
        background_tasks.add_task(send_text, sender, reply)

    return {"status": "ok"}
