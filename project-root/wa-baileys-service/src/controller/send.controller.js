import { sendText } from "../baileys/index.js";

export const sendMessage = async (req, res) => {
  try {
    const { to, text } = req.body;

    if (!to || !text) {
      return res.status(400).json({ error: "to and text required" });
    }

    await sendText(to, text);
    res.json({ status: "sent" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "failed to send message" });
  }
};
