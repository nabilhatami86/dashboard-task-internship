# 🧩 Dashboard Backend API

Backend API untuk **Dashboard** dengan fitur **Authentication**, **WhatsApp Bot Integration**, dan **User Management** menggunakan **FastAPI**, **PostgreSQL**, dan **SQLAlchemy**.

---

## 🚀 Tech Stack

- **Python 3.10+**
- **FastAPI** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Alembic** - Database migration
- **JWT** - Authentication
- **Passlib + Bcrypt** - Password hashing
- **WhatsApp API (Whapi.cloud)** - Bot integration
- **Uvicorn** - ASGI server

---

## 📁 Project Structure

```bash
backend-dashboard/
│
├── app/
│   ├── main.py                    # Application entry point
│   │
│   ├── config/
│   │   ├── config.py              # App configuration
│   │   ├── database.py            # Database connection
│   │   ├── deps.py                # Dependencies (get_db)
│   │   └── confiq_whapi.py        # WhatsApp API config
│   │
│   ├── models/
│   │   └── user.py                # User model
│   │
│   ├── schemas/
│   │   └── auth_schema.py         # Auth validation schemas
│   │
│   ├── routes/
│   │   └── auth.py                # Auth endpoints
│   │
│   ├── controller/
│   │   └── auth_controller.py     # Auth business logic
│   │
│   ├── services/
│   │   └── bot_service.py         # WhatsApp bot logic
│   │
│   ├── whapi/
│   │   ├── client.py              # WhatsApp API client
│   │   └── webhook.py             # WhatsApp webhook handler
│   │
│   └── utils/
│       ├── security.py            # Password hashing
│       └── jwt.py                 # JWT token handler
│
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
├── docker-compose.yml             # Docker configuration
└── README.md
```

---

## ⚙️ Environment Variables

Buat file `.env` di root project:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=asmi_db
DB_USER=postgres
DB_PASSWORD=your_password

# JWT
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60000

# WhatsApp API
WHAPI_BASE_URL=https://gate.whapi.cloud
WHAPI_TOKEN=your-whapi-token-here
```

---

## 📦 Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd backend-dashboard
```

### 2. Setup Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

```bash
# Menggunakan Docker (Recommended)
docker-compose up -d

# Atau install PostgreSQL manual dan buat database
createdb asmi_db
```

### 5. Run Migrations

```bash
alembic upgrade head
```

---

## ▶️ Run Application

```bash
uvicorn app.main:app --reload
```

Server akan berjalan di:

- **API**: `http://127.0.0.1:8000`
- **Swagger Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## 📡 API Endpoints

### ✅ Health Check

#### `GET /`

Cek status aplikasi

**Response:**

```json
{
  "status": "ok"
}
```

#### `GET /db-connect`

Cek koneksi database

**Response:**

```json
{
  "database": "postgresql",
  "status": "connected"
}
```

---

### 🔐 Authentication

#### `POST /auth/register`

Register user baru

**Request Body:**

```json
{
  "name": "Admin User",
  "email": "admin@example.com",
  "username": "admin",
  "password": "password123",
  "role": "admin"
}
```

**Available Roles:**

- `admin` - Administrator
- `karyawan` - Karyawan/Staff

**Response:**

```json
{
  "message": "Register success",
  "data": {
    "id": 1,
    "name": "Admin User",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "created_at": "2025-01-01T10:00:00"
  }
}
```

**Validasi:**

- Password minimal 6 karakter
- Password maksimal 72 karakter
- Email harus valid
- Username dan email harus unik

---

#### `POST /auth/login`

Login dengan username atau email

**Request Body:**

```json
{
  "identifier": "admin",
  "password": "password123"
}
```

> **Note:** `identifier` bisa berupa **username** atau **email**

**Response:**

```json
{
  "message": "Login success",
  "data": {
    "id": 1,
    "name": "Admin User",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 🔑 Authorization (JWT)

Untuk endpoint yang memerlukan autentikasi, tambahkan header:

```
Authorization: Bearer <access_token>
```

**JWT Payload:**

```json
{
  "sub": "1",
  "role": "admin",
  "exp": 1735689600
}
```

---

### 💬 WhatsApp Bot Webhook

#### `POST /webhook/whapi`

Webhook untuk menerima pesan WhatsApp dari Whapi.cloud

**Request Body (dari Whapi.cloud):**

```json
{
  "messages": [
    {
      "from": "62812345678@s.whatsapp.net",
      "text": {
        "body": "Halo"
      }
    }
  ]
}
```

**Bot Commands:**

- `admin` - Alihkan ke admin (mode manual)
- `pause` - Pause bot sementara
- `bot` - Aktifkan bot kembali
- Pesan lain - Tampilkan menu bot otomatis

**Bot Response Example:**

```
Halo 👋
Silakan pilih:
1️⃣ Info
2️⃣ Bantuan

Ketik *agent* untuk berbicara dengan manusia.
```

**Response:**

```json
{
  "status": "ok"
}
```

---

## 🤖 Bot Service Logic

Bot memiliki **3 state** untuk setiap user:

| State   | Deskripsi                     |
| ------- | ----------------------------- |
| `BOT`   | Bot aktif, balas otomatis     |
| `AGENT` | Mode manual, admin yang balas |
| `PAUSE` | Bot di-pause sementara        |

**File:** `app/services/bot_service.py`

```python
user_state = {}

def handle_bot(user: str, message: str):
    # Logic untuk handle pesan dari user
    # Return None jika tidak perlu balas (mode AGENT/PAUSE)
    # Return text untuk auto-reply
```

---

## 📱 WhatsApp API Integration

### Setup WhatsApp API

1. Daftar di [Whapi.cloud](https://whapi.cloud)
2. Dapatkan API token
3. Set webhook URL ke `https://your-domain.com/webhook/whapi`
4. Tambahkan `WHAPI_TOKEN` ke file `.env`

### Send Message Programmatically

**File:** `app/whapi/client.py`

```python
from app.whapi.client import send_text

# Kirim pesan WhatsApp
send_text("62812345678@s.whatsapp.net", "Halo dari bot!")
```

---

## 🗄️ Database Models

### User Model

**File:** `app/models/user.py`

```python
class User(Base):
    __tablename__ = "users"

    id: int                    # Primary key
    name: str                  # Full name
    email: str                 # Email (unique)
    username: str              # Username (unique)
    password: str              # Hashed password
    role: UserRole             # admin | agent
    created_at: datetime       # Timestamp
```

---

## 🔒 Security Features

- ✅ Password di-hash dengan **bcrypt**
- ✅ JWT token dengan expiry time
- ✅ Role-based access control (admin/karyawan)
- ✅ Email validation
- ✅ Password strength validation (min 6, max 72 karakter)
- ✅ Unique constraint untuk username dan email

---

## 🧪 Development

### Run dengan Auto-Reload

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Buat migration baru
alembic revision --autogenerate -m "description"

# Jalankan migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Testing dengan Swagger UI

Akses `http://localhost:8000/docs` untuk testing API interaktif.

---

## 🚀 Deployment

### Menggunakan Docker

```bash
docker-compose up -d
```

### Environment Production

Pastikan update nilai berikut di `.env`:

- `SECRET_KEY` - Generate key yang kuat (gunakan `openssl rand -hex 32`)
- `DB_PASSWORD` - Password database yang aman
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Sesuaikan dengan kebutuhan
- `WHAPI_TOKEN` - Token production dari Whapi.cloud

---

## 🛠️ Troubleshooting

### Database Connection Error

```bash
# Cek status PostgreSQL
docker-compose ps

# Restart database
docker-compose restart db

# Lihat logs
docker-compose logs db
```

### Import Error

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### WhatsApp Webhook Tidak Menerima Pesan

1. Pastikan webhook URL sudah diset di Whapi.cloud
2. Cek `WHAPI_TOKEN` di `.env` sudah benar
3. Pastikan server bisa diakses dari internet (gunakan ngrok untuk testing lokal)

---

## 📚 Future Improvements

- [ ] Refresh token mechanism
- [ ] User profile endpoint (`/auth/me`)
- [ ] Role-based middleware decorator
- [ ] Message history database
- [ ] WhatsApp media support (image, document, video)
- [ ] Admin dashboard untuk kelola bot
- [ ] Logging & monitoring (Sentry, LogRocket)
- [ ] Rate limiting
- [ ] API key authentication
- [ ] Unit tests & integration tests
- [ ] CI/CD pipeline

---

## 📖 Tech Documentation

- **FastAPI**: https://fastapi.tiangolo.com
- **SQLAlchemy**: https://docs.sqlalchemy.org
- **Whapi.cloud**: https://whapi.cloud/docs
- **Alembic**: https://alembic.sqlalchemy.org

---

## 📄 License

MIT License

---

## 👨‍💻 Author

ASMI Dashboard Team
