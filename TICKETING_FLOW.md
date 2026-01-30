# 🎫 Automatic Ticketing Flow

## Overview

Sistem otomatis mengubah message customer WhatsApp menjadi ticket dalam queue yang siap diambil agent.

## Flow Process

```
┌─────────────────────────────────────────────────────────────┐
│ Customer sends WhatsApp message                              │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ wa-baileys-service receives message via Baileys library      │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ Webhook POST to /webhook/baileys                             │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
    PRIVATE CHAT          GROUP CHAT
    (Process bot)    (Must be mentioned)
        │                       │
        └───────────┬───────────┘
                    ▼
        ┌──────────────────────┐
        │ Save to Chat model    │
        │ Save Message          │
        └───────────┬───────────┘
                    │
                    ▼
        ┌──────────────────────────────────────┐
        │ ✅ Auto-create TICKET (status=pending)│
        │ 📝 Set chat.mode = 'agent'            │
        └───────────┬─────────────────────────┘
                    │
        ┌───────────┴────────────┐
        ▼                        ▼
   FIRST MESSAGE         AGENT JOINS CHAT
   Bot replies to first    (chat.mode already
   message, generates      'agent')
   response (for quick
   ack)
        │                        │
        └───────────┬────────────┘
                    ▼
        ┌──────────────────────────┐
        │ Message queued in:        │
        │ - Queue for agents        │
        │ - Ticket dashboard        │
        │ - Pending tickets view    │
        └──────────────────────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │ Agent views /tickets/queue│
        │ Lihat pending tickets     │
        └──────────────────────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │ Agent POST /tickets/claim │
        │ to claim ticket           │
        └──────────────────────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │ ✅ Ticket assigned to agent│
        │ 📝 status=assigned        │
        │ 📝 assigned_at=now()      │
        └──────────────────────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │ Agent handles conversation│
        │ (can send replies)        │
        └──────────────────────────┘
```

## Key Changes in webhook.py

### 1. Auto-create Ticket

```python
ticket = get_or_create_ticket(db, chat, priority=TicketPriority.medium)
```

- Membuat ticket dengan status `pending`
- Chat mode diubah ke `agent` agar message berikutnya langsung ke agent queue

### 2. Skip Bot Processing for Agent Chats

```python
if chat.mode == ChatMode.agent:
    continue  # Skip bot, message goes to agent queue
```

- Jika chat sudah ada ticket (mode=agent), bot tidak memproses
- Message langsung masuk queue agent

### 3. Message Queuing

- **Database**: Message disimpan ke `messages` table
- **Ticket**: Ticket dibuat dengan `status=pending`, `created_at=now()`
- **Queue**: Semua agent bisa lihat di `/tickets/queue`

## Endpoints

### Agent Actions

**GET /tickets/queue**

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/tickets/queue
```

- Lihat semua pending tickets (FIFO order)
- Sorted by priority + created_at

**POST /tickets/{ticket_id}/claim**

```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/tickets/123/claim
```

- Agent mengklaim ticket dari queue
- Status berubah: `pending` → `assigned`
- Ticket di-assign ke agent yang claim

**GET /tickets/my-tickets**

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/tickets/my-tickets
```

- Lihat tickets yang sudah di-assign ke agent
- Filter by status jika perlu

### Admin Actions

**POST /tickets/{ticket_id}/assign**

```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": 5, "reason": "overflow"}' \
  http://localhost:8000/api/tickets/123/assign
```

- Admin manually assign ticket ke specific agent

**GET /tickets/all**

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/tickets/all?status=pending&priority=urgent
```

- Admin lihat semua tickets
- Filter by status dan priority

## Ticket States

| Status             | Meaning                    | Action               |
| ------------------ | -------------------------- | -------------------- |
| `pending`          | Baru masuk, menunggu agent | Agent claim          |
| `assigned`         | Sudah di-assign ke agent   | Agent start handle   |
| `in_progress`      | Agent sedang proses        | Agent complete/pause |
| `waiting_customer` | Menunggu response customer | Auto-timeout?        |
| `resolved`         | Sudah selesai              | Close ticket         |
| `escalated`        | Di-eskalasi ke admin       | Admin handle         |
| `closed`           | Ditutup                    | Archive              |

## Features

✅ **Automatic Ticket Creation** - Message otomatis jadi ticket
✅ **FIFO Queue** - Agent lihat pending tickets by created_at
✅ **Priority Levels** - Dapat di-set (default: medium)
✅ **Agent Claim** - Agent bisa ambil ticket dari queue
✅ **Manual Assignment** - Admin bisa assign ke specific agent
✅ **Chat Mode Tracking** - Mode: `bot` → `agent` saat ticket dibuat
✅ **Message History** - Semua message tersimpan di database
✅ **Timestamps** - created_at, assigned_at untuk tracking

## Configuration

Default priority saat ticket dibuat:

```python
ticket = get_or_create_ticket(db, chat, priority=TicketPriority.medium)
```

Ubah ke `high` atau `urgent` jika perlu:

```python
ticket = get_or_create_ticket(db, chat, priority=TicketPriority.high)
```

## Testing

1. **Send WhatsApp message** → Check `/tickets/queue`
2. **See pending ticket** → Ticket status should be `pending`
3. **Agent claim** → POST `/tickets/123/claim`
4. **Verify assigned** → Ticket now shows agent name, status=`assigned`
5. **Agent respond** → Send message in conversation
6. **Mark resolved** → Admin/Agent change status to `resolved`

## Debug Logs

Backend logs akan menunjukkan:

```
[TICKET] ✅ Created new ticket #123 for chat #45 (priority=medium)
[CHAT] Mode changed to 'agent' - future messages will go to agent queue
[SKIP BOT] Chat mode is 'agent', message will go to agent queue
```

---

**System Design**: First message creates ticket + auto bot reply for acknowledgment, then agent takes over immediately
