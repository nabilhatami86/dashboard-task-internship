# 🚀 Quick Start Guide - Sistem Ticketing

## Arsitektur Sistem

```
Customer WhatsApp → Nomor Whapi (+628xxx)
                        ↓
                    Webhook
                        ↓
                    Backend API
                    (Create Ticket)
                        ↓
                    Queue System
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
    Agent A         Agent B         Agent C
    (Ambil!)       (Ambil!)       (Ambil!)
        ↓
    Reply pakai nomor Whapi yang sama
```

**Konsep:**
- **1 Nomor WhatsApp** terdaftar di Whapi.cloud
- **Multiple Agents** bisa balas chat dari nomor yang sama
- **Ticketing System** untuk distribusi customer
- **First-Come-First-Serve** - Agent cepat-cepatan ambil ticket

---

## 📋 Prerequisites

Yang harus sudah ada:
- ✅ PostgreSQL installed & running
- ✅ Python 3.8+ installed
- ✅ Node.js 16+ installed
- ✅ Akun Whapi.cloud dengan nomor terdaftar
- ✅ Git (untuk clone/manage code)

---

## 🔧 Step 1: Setup Backend

### 1.1 Navigate ke Backend Folder
```bash
cd /Users/mm/Desktop/Dashboard/backend-dashboard-python/backend-dashboard-python.backup
```

### 1.2 Setup .env File
```bash
# Check .env file exists
ls -la .env

# Isi .env harus seperti ini:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dashboard_db
DB_USER=postgres
DB_PASSWORD=123

# Whapi configuration
WHAPI_TOKEN=your_whapi_token_here
WHAPI_BASE_URL=https://gate.whapi.cloud
```

### 1.3 Install Dependencies
```bash
# Jika ada venv, activate dulu
source .venv/bin/activate  # Mac/Linux
# atau
.venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt
```

### 1.4 Create Database
```bash
# Login ke PostgreSQL
psql -U postgres

# Buat database (jika belum ada)
CREATE DATABASE dashboard_db;

# Exit
\q
```

### 1.5 Run Migration
```bash
# Check migration status
alembic current

# Run migration untuk create tables baru
alembic upgrade head

# Output yang benar:
# INFO  [alembic.runtime.migration] Running upgrade xxx -> 487460ac0762, add_ticket_queue_system
```

### 1.6 Verify Tables Created
```bash
psql -U postgres -d dashboard_db

# List tables
\dt

# Harus ada tables:
# - users
# - chats
# - messages
# - admin_messages
# - tickets              ← NEW
# - agent_profiles       ← NEW
# - queue_assignments    ← NEW
# - agent_metrics        ← NEW

\q
```

---

## 👥 Step 2: Create Agent Profiles

### 2.1 Create Users (Agents)
```bash
# Run Python shell
python

# Execute:
from app.config.database import SessionLocal
from app.models.user import User, UserRole
from passlib.context import CryptContext

db = SessionLocal()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create Agent A
agent_a = User(
    name="Agent John",
    email="john@company.com",
    username="agent_john",
    password=pwd_context.hash("password123"),
    phone="081234567890",
    role=UserRole.agent
)

# Create Agent B
agent_b = User(
    name="Agent Sarah",
    email="sarah@company.com",
    username="agent_sarah",
    password=pwd_context.hash("password123"),
    phone="081234567891",
    role=UserRole.agent
)

# Create Agent C
agent_c = User(
    name="Agent Mike",
    email="mike@company.com",
    username="agent_mike",
    password=pwd_context.hash("password123"),
    phone="081234567892",
    role=UserRole.agent
)

db.add_all([agent_a, agent_b, agent_c])
db.commit()

print("✅ Agents created!")
exit()
```

### 2.2 Create Agent Profiles
```bash
psql -U postgres -d dashboard_db

-- Get user IDs first
SELECT id, name, role FROM users WHERE role = 'agent';

-- Insert agent profiles (ganti user_id sesuai hasil query di atas)
INSERT INTO agent_profiles (
    user_id,
    display_name,
    signature,
    status,
    is_available,
    max_concurrent_tickets,
    priority_score
) VALUES
    (2, 'Agent John', '-John', 'online', true, 5, 100),
    (3, 'Agent Sarah', '-Sarah', 'online', true, 5, 100),
    (4, 'Agent Mike', '-Mike', 'online', true, 5, 100);

-- Verify
SELECT ap.id, ap.display_name, ap.signature, ap.is_available, u.name
FROM agent_profiles ap
JOIN users u ON ap.user_id = u.id;

\q
```

---

## 🚀 Step 3: Run Backend Server

```bash
# Dari folder backend
cd /Users/mm/Desktop/Dashboard/backend-dashboard-python/backend-dashboard-python.backup

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Output yang benar:
# ✅ PostgreSQL CONNECTED
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

### Test Backend API
```bash
# Buka browser baru, test:
http://localhost:8000/

# Harus return: {"status": "ok"}

# Check API docs:
http://localhost:8000/docs

# Harus lihat semua endpoints termasuk /tickets/*
```

---

## 🎨 Step 4: Run Frontend

### 4.1 Navigate & Install
```bash
# Buka terminal baru
cd /Users/mm/Desktop/Dashboard/dashboard-message-center

# Install dependencies
npm install

# Check .env.local
cat .env.local

# Harus ada:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4.2 Run Development Server
```bash
npm run dev

# Output:
# ▲ Next.js 14.x.x
# - Local:   http://localhost:3000
# - Ready in X.Xs
```

---

## 🧪 Step 5: Test Full Flow

### 5.1 Login sebagai Admin
1. Buka: http://localhost:3000/login
2. Login dengan admin credentials
3. Masuk ke dashboard admin

### 5.2 Create Test Chat (Manual)
```bash
# Via psql atau Python
psql -U postgres -d dashboard_db

-- Create test chat
INSERT INTO chats (
    customer_name,
    customer_phone,
    channel,
    mode,
    online,
    unread_count
) VALUES
    ('Test Customer', '6281999999999@c.us', 'WhatsApp', 'agent', true, 0);

-- Get chat_id
SELECT id, customer_name FROM chats ORDER BY id DESC LIMIT 1;

\q
```

### 5.3 Verify Ticket Auto-Created
```bash
psql -U postgres -d dashboard_db

-- Check ticket
SELECT t.id, t.status, t.priority, c.customer_name, u.name as agent_name
FROM tickets t
JOIN chats c ON t.chat_id = c.id
LEFT JOIN users u ON t.assigned_agent_id = u.id
ORDER BY t.id DESC;

-- Harus lihat ticket baru dengan status 'assigned' atau 'pending'

\q
```

### 5.4 Test Admin Monitoring
1. Login sebagai admin
2. Buka: http://localhost:3000/dashboard-admin-monitoring
3. **Harus lihat:**
   - Total agents: 3
   - Stats (pending, in progress, etc.)
   - Agent performance table
   - Ticket list

### 5.5 Test Agent Queue

**Terminal 1 - Agent John:**
```bash
# Buka browser normal
http://localhost:3000/login

Username: agent_john
Password: password123

# Setelah login, buka:
http://localhost:3000/dashboard-agent-queue

# Harus lihat:
# - Pending tickets di queue
# - Button "AMBIL SEKARANG!"
```

**Terminal 2 - Agent Sarah (Incognito/Private):**
```bash
# Buka browser incognito/private
http://localhost:3000/login

Username: agent_sarah
Password: password123

# Buka:
http://localhost:3000/dashboard-agent-queue

# Lihat ticket yang sama dengan Agent John
```

**Test Competition:**
1. Kedua agent lihat ticket #1 di queue
2. Klik "AMBIL SEKARANG!" secara bersamaan
3. **Expected:**
   - 1 agent berhasil: "✅ Ticket berhasil diambil!"
   - 1 agent gagal: "❌ Ticket sudah diambil agent lain"

### 5.6 Test Chat & Reply
1. Agent yang berhasil claim, klik "Open Chat"
2. Masuk ke /dashboard-agent
3. Lihat chat dengan customer
4. Reply ke customer
5. Check di Whapi → Reply terkirim dari nomor Whapi

---

## 🔍 Troubleshooting

### Backend Issues

**Error: "No module named 'app'"**
```bash
# Pastikan ada di folder yang benar
pwd
# Harus di: .../backend-dashboard-python.backup

# Reinstall
pip install -e .
```

**Error: "PostgreSQL CONNECTION FAILED"**
```bash
# Check PostgreSQL running
brew services list | grep postgresql
# atau
sudo systemctl status postgresql

# Start PostgreSQL
brew services start postgresql
# atau
sudo systemctl start postgresql

# Test connection
psql -U postgres -c "SELECT 1"
```

**Error: "Failed to fetch tickets"**
```bash
# Check backend running
curl http://localhost:8000/

# Check JWT token valid
# Login ulang di frontend
```

### Frontend Issues

**Error: "Failed to fetch"**
```bash
# Check API_URL
cat .env.local

# Check backend running
curl http://localhost:8000/tickets/queue
# Harus error 401 (butuh auth), bukan connection refused

# Check CORS
# Di backend main.py harus ada:
# allow_origins=["http://localhost:3000"]
```

**Error: "Cannot claim ticket"**
```bash
# Check agent profile exists
psql -U postgres -d dashboard_db -c "SELECT * FROM agent_profiles WHERE user_id = 2;"

# Check is_available = true
# Check max_concurrent_tickets tidak tercapai
```

---

## 📊 Monitoring & Debugging

### Check Logs

**Backend Logs:**
```bash
# Terminal yang run uvicorn
# Lihat log real-time

# Search for errors
grep ERROR logs.txt
```

**Database Queries:**
```sql
-- Active tickets per agent
SELECT
    u.name as agent_name,
    COUNT(*) as active_tickets
FROM tickets t
JOIN users u ON t.assigned_agent_id = u.id
WHERE t.status IN ('assigned', 'in_progress')
GROUP BY u.name;

-- Queue status
SELECT status, priority, COUNT(*)
FROM tickets
GROUP BY status, priority;

-- Agent availability
SELECT
    u.name,
    ap.status,
    ap.is_available,
    ap.max_concurrent_tickets
FROM agent_profiles ap
JOIN users u ON ap.user_id = u.id;
```

---

## 🎯 Common Scenarios

### Scenario 1: Customer Kirim WhatsApp
```
1. Customer kirim pesan ke nomor Whapi
2. Whapi forward ke webhook: POST /webhook/whapi
3. Backend:
   - Create/update chat
   - Save message
   - Check mode = 'agent' → create ticket
   - Auto-assign jika ada agent available
4. Ticket masuk queue atau langsung assigned
5. Agent lihat di /dashboard-agent-queue
```

### Scenario 2: Agent Ambil Ticket
```
1. Agent buka /dashboard-agent-queue
2. Lihat list pending tickets
3. Klik "AMBIL SEKARANG!" pada ticket
4. Backend:
   - Check agent available
   - Check not at capacity
   - Claim ticket (atomic operation)
   - Create queue_assignment record
5. Success → Ticket assigned to agent
6. Agent bisa chat dengan customer
```

### Scenario 3: Agent Balas Customer
```
1. Agent buka chat di /dashboard-agent
2. Ketik pesan + signature (otomatis atau manual)
3. Klik send
4. Backend:
   - Save message dengan agent_id
   - Call Whapi API send_text()
   - Whapi kirim dari nomor terdaftar
5. Customer terima pesan dari nomor Whapi
```

---

## ✅ Success Criteria

Sistem berjalan dengan baik jika:

- ✅ Backend running tanpa error
- ✅ Frontend bisa login
- ✅ Admin bisa lihat monitoring dashboard
- ✅ Agent bisa lihat queue
- ✅ Agent bisa claim ticket
- ✅ Multiple agent compete untuk ticket yang sama
- ✅ Hanya 1 agent berhasil claim (race condition handled)
- ✅ Agent bisa chat dengan customer
- ✅ Reply terkirim via Whapi

---

## 🚀 Production Deployment

Setelah testing berhasil:

1. **Setup Whapi Webhook:**
```bash
python setup_whapi_webhook.py
```

2. **Update Environment:**
```bash
# .env production
DB_HOST=production_host
WHAPI_TOKEN=production_token
```

3. **Run with Docker:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📞 Support

Jika masih ada yang error:
1. Check logs di terminal
2. Check database dengan psql
3. Verify .env configuration
4. Test API endpoints di /docs
5. Clear browser cache & localStorage

---

**Sistem sudah siap digunakan!** 🎉

Tinggal ikuti step-by-step di atas untuk running semuanya.
