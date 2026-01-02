# Agent List Feature - Update Summary

## Summary
Menambahkan fitur untuk menampilkan daftar semua agent beserta nomor telepon mereka di Admin Chat Window.

## Backend Changes

### 1. User Model
**File:** `backend-dashboard-python/backend-dashboard-python.backup/app/models/user.py`
- Menambahkan kolom `phone` ke model User

### 2. Routes
**File:** `backend-dashboard-python/backend-dashboard-python.backup/app/routes/users.py` (NEW)
- Endpoint baru: `GET /users/agents` - Mendapatkan daftar semua agent
- Endpoint baru: `GET /users/admins` - Mendapatkan daftar semua admin
- Endpoint baru: `GET /users/` - Mendapatkan daftar semua users

### 3. Controller
**File:** `backend-dashboard-python/backend-dashboard-python.backup/app/controller/users_controller.py` (NEW)
- `get_all_agents()` - Query semua user dengan role agent
- `get_all_admins()` - Query semua user dengan role admin
- `get_all_users()` - Query semua user

### 4. Main App
**File:** `backend-dashboard-python/backend-dashboard-python.backup/app/main.py`
- Mendaftarkan router users ke aplikasi FastAPI

### 5. Auth Schema & Controller
**Files:**
- `app/schemas/auth_schema.py` - Menambahkan field phone
- `app/controller/auth_controller.py` - Menyimpan dan mengembalikan phone di register/login

### 6. Database Migration
**File:** `alembic/versions/ee001a086c5c_add_phone_to_users.py`
- Migration untuk menambahkan kolom phone ke tabel users

## Frontend Changes

### 1. API Client
**File:** `dashboard-message-center/lib/api.ts`
- Menambahkan interface `AgentUser`
- Menambahkan function `getAgentList(token)` untuk fetch daftar agent dari backend
- Mock data fallback jika backend belum tersedia

### 2. Admin Chat Window
**File:** `dashboard-message-center/components/chat/admin-chat-window.tsx`
- Menambahkan state `showAgentList` dan `agentList`
- Menambahkan useEffect untuk load daftar agent
- Menambahkan tombol "List Agent" di header
- Menambahkan UI section untuk menampilkan daftar agent dengan:
  - Avatar dengan initial nama (background hijau)
  - Nama agent dan status online
  - Username
  - Email
  - Nomor telepon (jika ada)

## Features

### Agent List Display
- **Button:** "List Agent" dengan icon UserCog
- **Background:** Hijau untuk membedakan dari Admin List (biru)
- **Info Ditampilkan:**
  - Nama lengkap agent
  - Username (@username)
  - Email address
  - Nomor telepon (dengan emoji 📱)
  - Status online (dot hijau jika online)

### Agent Profile
- Menampilkan data agent yang sedang login
- Termasuk nomor telepon yang tersimpan di database

## API Endpoints

### Get Agent List
```
GET /users/agents
Authorization: Bearer {token}

Response:
[
  {
    "id": 2,
    "name": "Agent User",
    "email": "agent@example.com",
    "phone": "087731624016",
    "username": "agent",
    "role": "agent",
    "online": false
  }
]
```

### Get Admin List
```
GET /users/admins
Authorization: Bearer {token}

Response:
[
  {
    "id": 1,
    "name": "Admin Utama",
    "email": "admin@example.com",
    "phone": "087731624016",
    "username": "admin",
    "role": "admin",
    "online": false
  }
]
```

## How to Use

1. **Apply Database Migration:**
   ```bash
   cd backend-dashboard-python/backend-dashboard-python.backup
   python3 -m alembic upgrade head
   ```

2. **Start Backend:**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Frontend sudah siap:**
   - Tombol "List Agent" akan muncul di Admin Chat Window
   - Klik untuk melihat daftar semua agent beserta nomor teleponnya
   - Data akan diambil dari backend jika tersedia, atau menggunakan mock data

## Notes
- Status online saat ini masih hardcoded ke `false` (TODO: implement real-time online tracking)
- Nomor telepon akan muncul jika tersedia di database
- Existing users perlu update profil mereka untuk menambahkan nomor telepon
