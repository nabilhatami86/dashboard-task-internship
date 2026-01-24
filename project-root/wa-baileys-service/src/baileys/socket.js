import makeWASocket, {
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
} from "@whiskeysockets/baileys";
import qrcode from "qrcode-terminal";
import { logger } from "../utils/logger.js";
import { registerEvents } from "./event.js";
import { waState } from "../services/wa-state.service.js";

// Simple contacts cache for LID resolution
const contactsCache = new Map();

let sock;
let isConnecting = false;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const initSocket = async () => {
  // 🛑 cegah init dobel (penting untuk nodemon)
  if (isConnecting) return;
  isConnecting = true;
  waState.setStatus("connecting");

  try {
    const { state, saveCreds } = await useMultiFileAuthState("auth_info");
    const { version } = await fetchLatestBaileysVersion();

    logger.info(`Using Baileys version: ${version.join(".")}`);

    sock = makeWASocket({
      auth: state,
      version,
      browser: ["Dashboard WA", "Chrome", "1.0.0"],
      syncFullHistory: false,
      markOnlineOnConnect: true,
    });

    // 🔔 EVENT CONNECTION
    sock.ev.on("connection.update", async (update) => {
      const { qr, connection, lastDisconnect } = update;

      // 📱 QR Code - tampilkan di terminal DAN simpan ke state untuk API
      if (qr) {
        // Simpan QR ke state (untuk API/frontend)
        waState.setQR(qr);

        // Tampilkan di terminal juga
        console.log("\n");
        logger.info("╔════════════════════════════════════════════╗");
        logger.info("║   SCAN QR CODE DENGAN WHATSAPP ANDA        ║");
        logger.info("║   WhatsApp > Linked Devices > Link Device  ║");
        logger.info("║   Atau buka Dashboard > WhatsApp Settings  ║");
        logger.info("╚════════════════════════════════════════════╝");
        console.log("\n");
        qrcode.generate(qr, { small: true });
        console.log("\n");
      }

      // ✅ CONNECTED
      if (connection === "open") {
        logger.success("WhatsApp CONNECTED successfully!");
        const user = sock.user;
        if (user) {
          logger.info(`Logged in as: ${user.name || user.id}`);
          waState.setUser({
            id: user.id,
            name: user.name || user.id.split("@")[0],
            phone: user.id.split("@")[0],
          });
        }
        waState.clearQR();
        isConnecting = false;
        reconnectAttempts = 0;
      }

      // ❌ DISCONNECTED
      if (connection === "close") {
        const statusCode = lastDisconnect?.error?.output?.statusCode;
        const shouldReconnect = statusCode !== DisconnectReason.loggedOut;

        logger.warn(`Connection closed. Status code: ${statusCode}`);
        waState.setStatus("disconnected");
        waState.setError(`Disconnected with code: ${statusCode}`);

        if (statusCode === DisconnectReason.loggedOut) {
          logger.error("WhatsApp logged out. Delete auth_info folder dan restart untuk scan QR baru.");
          isConnecting = false;
          waState.reset();
        } else if (shouldReconnect && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts++;
          const waitTime = Math.min(reconnectAttempts * 2000, 10000);
          logger.warn(`Reconnecting in ${waitTime / 1000}s... (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
          isConnecting = false;
          await delay(waitTime);
          initSocket();
        } else {
          logger.error("Max reconnect attempts reached. Restart manually.");
          isConnecting = false;
        }
      }
    });

    // 💾 SIMPAN SESSION (INI WAJIB)
    sock.ev.on("creds.update", saveCreds);

    // 📞 CONTACTS SYNC - untuk build LID mapping
    sock.ev.on("contacts.set", ({ contacts }) => {
      logger.info(`Received ${contacts.length} contacts from sync`);
      for (const contact of contacts) {
        if (contact.lid && contact.id) {
          const phone = contact.id.split("@")[0] + "@c.us";
          contactsCache.set(contact.lid, phone);
          logger.info(`Contacts sync: LID ${contact.lid} -> ${phone} (${contact.name || contact.notify})`);
        }
      }
    });

    // 📩 REGISTER MESSAGE EVENTS - forward ke Python backend
    registerEvents(sock);
  } catch (error) {
    logger.error(`Failed to initialize socket: ${error.message}`);
    waState.setError(error.message);
    waState.setStatus("disconnected");
    isConnecting = false;

    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      await delay(3000);
      initSocket();
    }
  }
};

// 🔌 DISCONNECT
export const disconnectSocket = async () => {
  if (sock) {
    try {
      sock.end();
      sock = null;
    } catch (e) {
      logger.warn(`Disconnect warning: ${e.message}`);
    }
  }
  isConnecting = false;
  reconnectAttempts = 0;
};

// 📊 GET STATUS
export const getConnectionStatus = () => {
  return waState.getState();
};

// ✉️ KIRIM PESAN
export const sendText = async (jid, text) => {
  if (!sock) {
    throw new Error("WA socket not initialized");
  }
  return sock.sendMessage(jid, { text });
};

// Export contacts cache for LID resolution
export { contactsCache };

// Get socket instance
export const getSocket = () => sock;
