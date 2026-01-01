import os
import time
from typing import Optional

# simple in-memory state stores; replace with persistent storage for production
user_state = {}
last_human_reply = {}


def _load_admins() -> set:
    raw = os.environ.get("WHAPI_ADMINS", "")
    return {p.strip() for p in raw.split(",") if p.strip()}


ADMINS = _load_admins()


def _generate_ai_reply(user: str, message: str) -> str:
    """Generate a reply using an external AI provider if available.

    Falls back to a canned response when no provider is configured.
    """
    try:
        import openai

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        openai.api_key = api_key
        prompt = (
            "You are a helpful customer support assistant. Reply concisely and politely "
            f"to the user message: \"{message}\""
        )
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Customer support assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        # fallback canned reply
        return (
            "Terima kasih atas pesannya. Saya adalah asisten otomatis — "
            "kami akan membantu Anda segera. Jika Anda ingin berbicara dengan manusia, ketik 'agent'."
        )


def handle_bot(user: str, message: str) -> Optional[str]:
    """Handle incoming message from `user` and return a reply string or None.

    Behavior:
    - If sender is an admin and sends management commands, adjust state.
    - If user is in `AGENT` or `PAUSE`, return None to indicate no bot reply.
    - Otherwise, generate AI reply (or canned fallback).
    """
    msg = message.strip()
    # admin commands: assign/unassign/reply
    if user in ADMINS:
        parts = msg.split(maxsplit=2)
        cmd = parts[0].lower() if parts else ""
        if cmd == "assign" and len(parts) >= 2:
            target = parts[1]
            user_state[target] = "AGENT"
            return f"Assigned agent for {target}."
        if cmd == "unassign" and len(parts) >= 2:
            target = parts[1]
            user_state[target] = "BOT"
            return f"Unassigned agent for {target}."
        if cmd == "reply" and len(parts) >= 3:
            target = parts[1]
            text = parts[2]
            # record that admin replied for the target so subsequent messages use human
            last_human_reply[target] = time.time()
            # returning a special string lets the caller deliver the message
            return f"__ADMIN_REPLY__|{target}|{text}"
        # admins don't receive AI replies
        return None

    state = user_state.get(user, "BOT")
    lower = msg.lower()
    if lower == "agent":
        user_state[user] = "AGENT"
        return None
    if lower == "pause":
        user_state[user] = "PAUSE"
        return "Bot dihentikan sementara."
    if lower == "bot":
        user_state[user] = "BOT"
        return "Bot diaktifkan kembali."

    if state in ["AGENT", "PAUSE"]:
        return None

    # if a human recently replied for this user, prefer human flow (no AI)
    last = last_human_reply.get(user)
    if last and time.time() - last < 60 * 60:  # 1 hour window
        # do not auto-reply when human recently handled
        return None

    # generate AI reply
    return _generate_ai_reply(user, message)
