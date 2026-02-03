import axios from "axios";
import { ENV } from "../config/index.js";
import { logger } from "../utils/logger.js";

/**
 * Transform Baileys payload to WHAPI-compatible format
 * agar bisa pakai handler yang sama di Python backend
 */
const transformToWhapiFormat = (payload) => {
  return {
    messages: [
      {
        from: payload.from,
        from_name: payload.pushName,
        pushname: payload.pushName,
        body: payload.text,
        text: { body: payload.text },
        id: payload.messageId,
        timestamp: payload.timestamp,
        // ✅ PENTING: Include mention data untuk group handling
        isMentioned: payload.isMentioned || false,
        mentionedJid: payload.mentionedJid || [],
        isGroup: payload.isGroup || false,
        // ✅ PENTING: Include participant untuk group messages
        // Participant = pengirim asli di grup (bukan group ID)
        participant: payload.participant || null,
        // ✅ Include group name
        groupName: payload.groupName || null,
      },
    ],
    // Marker untuk Python backend tahu ini dari Baileys
    source: "baileys",
  };
};

export const sendToBackend = async (payload) => {
  const webhookUrl = ENV.PYTHON_WEBHOOK_URL;

  if (!webhookUrl) {
    logger.error("PYTHON_WEBHOOK_URL not configured");
    return;
  }

  const transformedPayload = transformToWhapiFormat(payload);

  try {
    const response = await axios.post(webhookUrl, transformedPayload, {
      headers: {
        "Content-Type": "application/json",
        "x-api-key": ENV.INTERNAL_API_KEY,
      },
      timeout: 10000, // 10 second timeout
    });

    logger.info(`Webhook sent successfully: ${response.data?.status || "ok"}`);
    return response.data;
  } catch (error) {
    if (error.response) {
      logger.error(`Webhook failed: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
    } else if (error.request) {
      logger.error(`Webhook no response: ${error.message}`);
    } else {
      logger.error(`Webhook error: ${error.message}`);
    }
    throw error;
  }
};
