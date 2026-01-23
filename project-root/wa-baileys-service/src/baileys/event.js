import { sendToBackend } from "../services/webhook.service.js";
import { logger } from "../utils/logger.js";
import { contactsCache } from "./socket.js";

/**
 * Normalize phone number from various WhatsApp formats
 * Handles: @s.whatsapp.net, @c.us, @lid (linked device ID)
 */
const normalizePhone = (jid, msg) => {
  if (!jid) return null;

  // Check if participant exists (for group messages or when JID is LID)
  if (msg?.key?.participant) {
    const participant = msg.key.participant;
    const phoneMatch = participant.match(/^(\d+)@/);
    if (phoneMatch) {
      return phoneMatch[1] + "@c.us";
    }
  }

  // LID format - check cache for resolved phone
  if (jid.endsWith("@lid")) {
    if (contactsCache.has(jid)) {
      const phone = contactsCache.get(jid);
      logger.info(`Resolved LID ${jid} to phone ${phone} from cache`);
      return phone;
    }
    // Can't resolve LID - return as is, pushName will be used for display
    logger.warn(`LID format: ${jid}. Using pushName for display.`);
    return jid;
  }

  // Standard formats: @s.whatsapp.net or @c.us
  if (jid.includes("@s.whatsapp.net") || jid.includes("@c.us")) {
    const phone = jid.split("@")[0];
    return phone + "@c.us";
  }

  // Group format @g.us - return as is
  if (jid.includes("@g.us")) {
    return jid;
  }

  return jid;
};

/**
 * Extract text from various message types
 */
const extractText = (message) => {
  if (!message) return null;

  // Regular text message
  if (message.conversation) {
    return message.conversation;
  }

  // Extended text (with preview, quoted, etc)
  if (message.extendedTextMessage?.text) {
    return message.extendedTextMessage.text;
  }

  // Image/Video/Document with caption
  if (message.imageMessage?.caption) {
    return `[Image] ${message.imageMessage.caption}`;
  }
  if (message.videoMessage?.caption) {
    return `[Video] ${message.videoMessage.caption}`;
  }
  if (message.documentMessage?.caption) {
    return `[Document] ${message.documentMessage.caption}`;
  }

  // Media without caption
  if (message.imageMessage) return "[Image]";
  if (message.videoMessage) return "[Video]";
  if (message.audioMessage) return "[Audio]";
  if (message.stickerMessage) return "[Sticker]";
  if (message.documentMessage) {
    return `[Document: ${message.documentMessage.fileName || "file"}]`;
  }
  if (message.contactMessage) {
    return `[Contact: ${message.contactMessage.displayName || "contact"}]`;
  }
  if (message.locationMessage) return "[Location]";

  // Button response
  if (message.buttonsResponseMessage?.selectedButtonId) {
    return message.buttonsResponseMessage.selectedDisplayText || message.buttonsResponseMessage.selectedButtonId;
  }

  // List response
  if (message.listResponseMessage?.singleSelectReply?.selectedRowId) {
    return message.listResponseMessage.title || message.listResponseMessage.singleSelectReply.selectedRowId;
  }

  return null;
};

export const registerEvents = (sock) => {
  // Listen for contacts updates to build LID-to-phone mapping
  sock.ev.on("contacts.update", (updates) => {
    for (const contact of updates) {
      if (contact.id && contact.lid) {
        const phone = contact.id.split("@")[0] + "@c.us";
        contactsCache.set(contact.lid, phone);
        logger.info(`Mapped LID ${contact.lid} -> ${phone}`);
      }
    }
  });

  sock.ev.on("contacts.upsert", (contacts) => {
    for (const contact of contacts) {
      if (contact.id && contact.lid) {
        const phone = contact.id.split("@")[0] + "@c.us";
        contactsCache.set(contact.lid, phone);
        logger.info(`Mapped LID ${contact.lid} -> ${phone} (upsert)`);
      }
    }
  });

  sock.ev.on("messages.upsert", async ({ messages, type }) => {
    // Hanya proses pesan baru (bukan history sync)
    if (type !== "notify") return;

    for (const msg of messages) {
      try {
        // Skip jika tidak ada message atau dari kita sendiri
        if (!msg?.message || msg.key.fromMe) continue;

        // Skip broadcast/status
        if (msg.key.remoteJid === "status@broadcast") continue;

        const text = extractText(msg.message);
        if (!text) {
          logger.warn(`Unsupported message type from ${msg.key.remoteJid}`);
          continue;
        }

        // Normalize phone number (handle LID format)
        const normalizedFrom = normalizePhone(msg.key.remoteJid, msg);

        const payload = {
          from: normalizedFrom,
          pushName: msg.pushName || null,
          text: text,
          timestamp: msg.messageTimestamp,
          messageId: msg.key.id,
          // Include original JID for reference
          originalJid: msg.key.remoteJid,
        };

        logger.info(`Incoming message from ${msg.pushName || msg.key.remoteJid}: ${text.substring(0, 50)}...`);

        await sendToBackend(payload);
      } catch (error) {
        logger.error(`Failed to process message: ${error.message}`);
      }
    }
  });

  logger.info("Message events registered");
};
