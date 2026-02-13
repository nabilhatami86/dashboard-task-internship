import axios from "axios";
import { sendText, sendImage, sendDocument } from "../baileys/index.js";

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

/**
 * Controller: Send WhatsApp Media (Image / Document)
 * Expects: { to, mediaUrl, mediaType, caption?, filename?, mentions? }
 * mediaUrl is a relative path like "/uploads/filename.jpg" which we fetch from the Python backend
 */
export const sendMedia = async (req, res) => {
  try {
    const { to, mediaUrl, mediaType, caption, filename, mentions } = req.body;

    if (!to || !mediaUrl || !mediaType) {
      return res.status(400).json({
        ok: false,
        error: "to, mediaUrl, and mediaType required",
      });
    }

    console.log("[CONTROLLER SEND-MEDIA]", {
      to,
      mediaUrl,
      mediaType,
      caption,
      filename,
      isGroup: to.endsWith("@g.us"),
    });

    // Download file from Python backend
    const backendUrl = process.env.PYTHON_BACKEND_URL || "http://localhost:8000";
    const fullUrl = `${backendUrl}${mediaUrl}`;

    console.log(`[SEND-MEDIA] Downloading from: ${fullUrl}`);

    const response = await axios.get(fullUrl, {
      responseType: "arraybuffer",
      timeout: 30000,
    });

    const buffer = Buffer.from(response.data);
    const contentType = response.headers["content-type"] || "application/octet-stream";

    console.log(`[SEND-MEDIA] Downloaded ${buffer.length} bytes, type: ${contentType}`);

    if (mediaType === "image") {
      await sendImage(to, buffer, caption || "", contentType, mentions || []);
    } else {
      await sendDocument(to, buffer, filename || "file", contentType, caption || "", mentions || []);
    }

    return res.json({
      ok: true,
      message: "media sent",
    });
  } catch (err) {
    console.error("[SEND-MEDIA CONTROLLER ERROR]", err);

    return res.status(500).json({
      ok: false,
      error: err.message,
    });
  }
};
