import { sendText } from "../baileys/index.js";

/**
 * Controller: Send WhatsApp Message (Personal / Group)
 */
export const sendMessage = async (req, res) => {
  try {
    const { to, text, mentions } = req.body;

    if (!to || !text) {
      return res.status(400).json({
        ok: false,
        error: "to and text required",
      });
    }

    console.log("[CONTROLLER SEND]", {
      to,
      text,
      mentions,
      isGroup: to.endsWith("@g.us"),
    });

    await sendText(to, text, mentions);

    return res.json({
      ok: true,
      message: "sent",
    });
  } catch (err) {
    console.error("[SEND CONTROLLER ERROR]", err);

    return res.status(500).json({
      ok: false,
      error: err.message,
    });
  }
};
