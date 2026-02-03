import { sendToBackend } from "../services/webhook.service.js";
import { logger } from "../utils/logger.js";
import { contactsCache } from "./socket.js";

// Message deduplication cache - prevents processing same message twice
// Key: messageId, Value: timestamp of processing
const processedMessages = new Map();
const MESSAGE_CACHE_TTL = 60000; // 60 seconds TTL
const MAX_CACHE_SIZE = 1000;

/**
 * Check if message was already processed
 * @param {string} messageId - The message ID to check
 * @returns {boolean} - True if already processed, false otherwise
 */
const isMessageProcessed = (messageId) => {
  if (!messageId) return false;

  // Clean old entries periodically
  if (processedMessages.size > MAX_CACHE_SIZE) {
    const now = Date.now();
    for (const [id, timestamp] of processedMessages) {
      if (now - timestamp > MESSAGE_CACHE_TTL) {
        processedMessages.delete(id);
      }
    }
  }

  return processedMessages.has(messageId);
};

/**
 * Mark message as processed
 * @param {string} messageId - The message ID to mark
 */
const markMessageProcessed = (messageId) => {
  if (messageId) {
    processedMessages.set(messageId, Date.now());
  }
};

const normalizeJid = (jid) => {
  if (!jid) return null;

  // buang device id (:4, :5, dst)
  const clean = jid.split(":")[0];

  // pastikan format @lid / @s.whatsapp.net tetap utuh
  if (clean.endsWith("@lid")) return clean;
  if (clean.endsWith("@s.whatsapp.net")) return clean;

  return clean;
};

const normalizePhone = async (jid, msg, sock) => {
  if (!jid) return null;

  // Check if participant exists (for group messages or when JID is LID)
  if (msg?.key?.participant) {
    const participant = msg.key.participant;
    const phoneMatch = participant.match(/^(\d+)@/);
    if (phoneMatch) {
      return phoneMatch[1] + "@c.us";
    }
  }

  // LID format - try multiple resolution methods
  if (jid.endsWith("@lid")) {
    // Method 1: Check cache for resolved phone
    if (contactsCache.has(jid)) {
      const phone = contactsCache.get(jid);
      logger.info(`Resolved LID ${jid} to phone ${phone} from cache`);
      return phone;
    }

    // Method 2: Extract from msg.key.senderPn (sender phone number) - THIS IS THE KEY!
    // senderPn contains the real phone number for LID accounts
    if (msg?.key?.senderPn) {
      const phone = msg.key.senderPn.split("@")[0] + "@c.us";
      contactsCache.set(jid, phone);
      logger.info(`✅ Resolved LID ${jid} to phone ${phone} from senderPn`);
      return phone;
    }

    // Method 3: Extract from LID itself (LID sometimes contains encoded phone)
    // LID format dapat berupa: <phone_encoded>@lid
    const lidNumber = jid.split("@")[0];

    // Method 4: Try to get from sock.user or message metadata
    // For personal chats, the sender phone might be in message metadata
    if (msg?.participant) {
      const phoneMatch = msg.participant.match(/^(\d+)@/);
      if (phoneMatch) {
        const phone = phoneMatch[1] + "@c.us";
        contactsCache.set(jid, phone);
        logger.info(`Resolved LID ${jid} to phone ${phone} from msg.participant`);
        return phone;
      }
    }

    // Method 4: Extract dari verifiedBizName atau contact info lainnya
    if (msg?.verifiedBizName) {
      logger.info(`Business account detected: ${msg.verifiedBizName} for LID ${jid}`);
    }

    // Method 5: Untuk personal chat, extract dari message properties
    // Cek apakah ada contact info di message
    if (msg?.pushName) {
      logger.info(`LID ${jid} has pushName: ${msg.pushName}`);
    }

    // Method 6: Try to query contact dari sock
    if (sock) {
      try {
        // WhatsApp onWhatsApp query dengan nomor dari LID
        // LID format biasanya: <some_number>@lid, coba query nomor tersebut
        const queryNum = lidNumber;
        logger.info(`Trying onWhatsApp query for: ${queryNum}`);
        const result = await sock.onWhatsApp(queryNum);
        logger.info(`onWhatsApp result for ${queryNum}: ${JSON.stringify(result)}`);

        if (result && result.length > 0 && result[0].jid) {
          const phone = result[0].jid.split("@")[0] + "@c.us";
          contactsCache.set(jid, phone);
          logger.info(`✅ Resolved LID ${jid} to phone ${phone} from onWhatsApp query`);
          return phone;
        }
      } catch (e) {
        logger.warn(`Failed to query onWhatsApp for ${lidNumber}: ${e.message}`);
      }
    }

    // Gagal resolve - return LID as is, pushName will be used for display
    logger.warn(`❌ Could not resolve LID: ${jid}. Will use pushName for display.`);
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

        // 🛡️ DEDUPLICATION: Skip if message was already processed
        const messageId = msg.key.id;
        if (isMessageProcessed(messageId)) {
          logger.info(`[DEDUP] Skipping duplicate message: ${messageId}`);
          continue;
        }

        // 🔄 LID RETRY WAIT: If LID format but no senderPn, skip and wait for retry
        // Baileys will retry the message and the retried version will have senderPn
        const remoteJid = msg.key.remoteJid;
        if (remoteJid?.endsWith("@lid") && !msg.key?.senderPn) {
          logger.info(`[LID WAIT] Skipping LID message without senderPn, waiting for retry: ${messageId}`);
          continue;
        }

        // DEBUG: Log full message object untuk lihat struktur
        logger.info(
          `DEBUG Full message object: ${JSON.stringify(
            {
              key: msg.key,
              pushName: msg.pushName,
              verifiedBizName: msg.verifiedBizName,
              messageTimestamp: msg.messageTimestamp,
              senderPn: msg.key?.senderPn || "N/A",
            },
            null,
            2,
          )}`,
        );

        // DEBUG: Log message content structure
        logger.info(`DEBUG Message content: ${JSON.stringify(msg.message, null, 2)}`);

        // If LID, log the extracted phone
        if (msg.key?.remoteJid?.endsWith("@lid") && msg.key?.senderPn) {
          logger.info(`📞 LID ${msg.key.remoteJid} -> Real phone: ${msg.key.senderPn}`);
        }

        const text = extractText(msg.message);
        logger.info(`DEBUG Extracted text: "${text}"`);

        if (!text) {
          logger.warn(`⚠️ Unsupported message type from ${msg.key.remoteJid} - No text extracted`);
          logger.warn(`Message keys: ${Object.keys(msg.message || {}).join(', ')}`);
          continue;
        }

        // Normalize phone number (handle LID format)
        // remoteJid already declared above
        const isGroup = remoteJid.endsWith("@g.us");

        // =========================
        // 🔥 DETEKSI BOT DI-TAG
        // =========================

        let isMentioned = false;
        let mentionedJid = [];

        if (isGroup) {
          const context = msg.message?.extendedTextMessage?.contextInfo;
          mentionedJid = context?.mentionedJid || [];

          isMentioned = mentionedJid.length > 0;

          logger.info(`[GROUP CHECK] mentioned=${isMentioned} mentionedJid=${JSON.stringify(mentionedJid)}`);
        }

        let from;
        let groupName = null;
        let participantPhone = null;
        let participantName = null;

        if (isGroup) {
          from = remoteJid;
          // Try to get group name
          try {
            const groupMeta = await sock.groupMetadata(remoteJid);
            groupName = groupMeta?.subject || null;
            logger.info(`[GROUP META] name="${groupName}" for ${remoteJid}`);
          } catch (e) {
            logger.warn(`Failed to get group metadata: ${e.message}`);
          }

          // 📱 RESOLVE PARTICIPANT: Ambil nomor telepon pengirim di grup
          const rawParticipant = msg.key.participant;
          if (rawParticipant) {
            // Check if participant is LID format
            if (rawParticipant.endsWith("@lid")) {
              // Try to resolve LID to phone number
              // Method 1: Check cache
              if (contactsCache.has(rawParticipant)) {
                participantPhone = contactsCache.get(rawParticipant);
                logger.info(`[GROUP] Resolved participant LID ${rawParticipant} to ${participantPhone} from cache`);
              }
              // Method 2: senderPn contains the real phone for LID
              else if (msg.key?.senderPn) {
                participantPhone = msg.key.senderPn.split("@")[0] + "@c.us";
                contactsCache.set(rawParticipant, participantPhone);
                logger.info(`[GROUP] Resolved participant LID ${rawParticipant} to ${participantPhone} from senderPn`);
              }
              // Method 3: Use LID number as fallback (won't work for mentions but at least shows something)
              else {
                participantPhone = rawParticipant.split("@")[0] + "@lid";
                logger.warn(`[GROUP] Could not resolve participant LID ${rawParticipant}, using as-is`);
              }
            } else {
              // Standard format: extract phone number
              const phoneMatch = rawParticipant.match(/^(\d+)@/);
              if (phoneMatch) {
                participantPhone = phoneMatch[1] + "@c.us";
              } else {
                participantPhone = rawParticipant;
              }
              logger.info(`[GROUP] Participant phone: ${participantPhone}`);
            }
          }

          // Get participant name from pushName
          participantName = msg.pushName || null;
          logger.info(`[GROUP] participant=${participantPhone} name="${participantName}" group="${groupName}"`);
        } else {
          from = await normalizePhone(remoteJid, msg, sock);
        }

        const payload = {
          from: from,
          isMentioned: isMentioned,
          mentionedJid: mentionedJid,
          isGroup: isGroup,
          pushName: msg.pushName || null,
          text: text,
          timestamp: msg.messageTimestamp,
          messageId: msg.key.id,
          originalJid: msg.key.remoteJid,
          participant: participantPhone || msg.key.participant || null,  // Resolved phone for group messages
          participantName: participantName,  // Name of sender in group
          groupName: groupName,  // Group name
        };
        logger.info(`[SEND BACKEND] isGroup=${isGroup} from=${from} text="${text}" mentioned=${isMentioned}`);
        logger.info(`[PAYLOAD] ${JSON.stringify(payload, null, 2)}`);

        // Mark as processed BEFORE sending to prevent race conditions
        markMessageProcessed(messageId);

        await sendToBackend(payload);
      } catch (error) {
        logger.error(`Failed to process message: ${error.message}`);
      }
    }
  });

  logger.info("Message events registered");
};
