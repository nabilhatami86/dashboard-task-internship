import express from "express";
import { sendMessage, sendMedia } from "../controller/send.controller.js";

const router = express.Router();
router.post("/send", sendMessage);
router.post("/send-media", sendMedia);

export default router;
