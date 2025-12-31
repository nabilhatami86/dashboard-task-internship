user_state = {}

def handle_bot(user: str, message: str):
    state = user_state.get(user, "BOT")
    msg = message.lower().strip()

    if msg == "admin":
        user_state[user] = "admin"
        return "Baik, admin akan melayani Anda."

    if msg == "pause":
        user_state[user] = "PAUSE"
        return "Bot dihentikan sementara."

    if msg == "bot":
        user_state[user] = "BOT"
        return "Bot diaktifkan kembali."

    if state in ["AGENT", "PAUSE"]:
        return None

    return (
        "Halo 👋\n"
        "Silakan pilih:\n"
        "1️⃣ Info\n"
        "2️⃣ Bantuan\n\n"
        "Ketik *agent* untuk berbicara dengan manusia."
    )
