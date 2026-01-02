# 🎫 Ticket Queue System - Testing Guide

## Login Credentials

### Agent Account
- **Username**: `agent`
- **Password**: `agent123`
- **User ID**: 2

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **User ID**: 1

## How to Test the Ticket Queue System

### Step 1: Login sebagai Agent
1. Buka browser ke `http://localhost:3000/login`
2. Login dengan username `agent` dan password `agent123`
3. Akan redirect ke `/dashboard-agent`

### Step 2: Cek Dashboard Agent (Harusnya Kosong)
- Karena belum ada chat yang di-claim, dashboard akan kosong
- Klik button **Ticket Queue** (icon tiket) di sidebar kiri

### Step 3: Lihat Available Tickets
- Halaman `/dashboard-agent-queue` akan menampilkan semua chat yang belum di-assign
- Chat yang muncul adalah chat dengan `assigned_agent_id = NULL` dan `mode = 'bot'`
- Urutan: FIFO (First In First Out) - chat terlama muncul di atas

### Step 4: Ambil/Claim Ticket
1. Klik tombol **"🏃 AMBIL SEKARANG!"** pada salah satu ticket
2. Backend akan:
   - Set `assigned_agent_id` = 2 (agent ID kamu)
   - Set `mode` = 'agent'
   - Return chat details
3. Akan muncul alert "✅ Ticket berhasil diambil!"
4. Auto-redirect ke `/dashboard-agent`

### Step 5: Chat dengan Customer
- Di dashboard agent, sekarang ada chat yang sudah di-claim
- Klik chat untuk mulai komunikasi dengan customer
- Balas pesan customer seperti biasa

### Step 6: Test dari Agent Lain
1. Logout dari agent pertama
2. Login dengan agent lain (username: `agent1`, password: `agent123`)
3. Buka ticket queue - ticket yang sudah di-claim tidak muncul lagi
4. Agent lain hanya bisa claim ticket yang masih available

## Database Status Check

Check database untuk memastikan assignment berhasil:

```bash
cd /Users/mm/Desktop/Dashboard/backend-dashboard-python/backend-dashboard-python.backup
python3 -c "
from app.config.database import SessionLocal
from app.models.chat import Chat

db = SessionLocal()
chats = db.query(Chat).all()

print('=== CHATS STATUS ===')
for c in chats:
    status = 'AVAILABLE' if c.assigned_agent_id is None else f'ASSIGNED to Agent {c.assigned_agent_id}'
    print(f'Chat #{c.id} - {c.customer_name}: {status} (Mode: {c.mode})')

db.close()
"
```

## API Endpoints

### Get Available Tickets (Queue)
```bash
curl -s "http://localhost:8000/chats/queue/available" | python3 -m json.tool
```

### Claim Ticket
```bash
TOKEN="your-agent-token-here"
curl -X POST "http://localhost:8000/chats/8/claim" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Agent's Chats (Only Assigned)
```bash
TOKEN="your-agent-token-here"
curl -s "http://localhost:8000/chats/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## Expected Behavior

### ✅ Correct Behavior
- Agent dashboard **ONLY** shows chats assigned to that agent
- Ticket queue shows **ALL** unassigned chats
- After claiming, chat disappears from queue and appears in dashboard
- Other agents cannot see chats assigned to different agents
- Admin can see **ALL** chats regardless of assignment

### ❌ Common Issues

**"Fetching data terus" / Infinite Loading**
- Backend might be hanging - restart it
- Check browser console for errors
- Make sure token is valid

**"Ticket sudah diambil agent lain"**
- Expected! This is FIFO - siapa cepat dia dapat
- Refresh queue untuk lihat ticket baru

**Chat tidak muncul di dashboard setelah claim**
- Check backend logs
- Make sure `assigned_agent_id` di-set dengan benar
- Refresh halaman dashboard

## Testing Flow Summary

1. **Login** as Agent → Empty dashboard ✅
2. **Go to Queue** → See available tickets ✅
3. **Claim Ticket** → Success alert ✅
4. **Back to Dashboard** → See claimed chat ✅
5. **Reply to Customer** → Message sent ✅
6. **Other agents** → Can't see your claimed chats ✅

---

🎉 **Sistem Ticket Queue berhasil terintegrasi!**
