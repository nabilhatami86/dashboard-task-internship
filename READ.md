# ASMI Dashboard API

Backend API untuk **Dashboard ASMI** menggunakan **FastAPI**. Project ini disusun dengan pendekatan **MVP (Minimum Viable Product)**: struktur sederhana, jelas, dan mudah dikembangkan ke tahap production.

---

## 🚀 Tech Stack

- Python 3.9+
- FastAPI
- Uvicorn

---

## 📁 Struktur Project

```text
project/
├── .venv/                # virtual environment
├── app/
│   ├── main.py           # entry point aplikasi
│   ├── routes/           # semua endpoint API
│   │   └── dashboard.py
│   ├── config/             # config & core utilities
│   │   └── config.py
│   └── __init__.py
├── .env                  # environment variables
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Environment

### 1️⃣ Buat Virtual Environment

```bash
python -m venv .venv
```

Aktifkan:

- Windows

```bash
.venv\Scripts\activate
```

- Mac / Linux

```bash
source .venv/bin/activate
```

---

### 2️⃣ Install Dependency

```bash
pip install -r requirements.txt
```

Isi `requirements.txt`:

```text
fastapi
uvicorn
python-dotenv
```

---

## ▶️ Menjalankan Aplikasi

```bash
uvicorn app.main:app --reload
```

Akses:

- API Base: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📌 Endpoint Dasar

### Health Check Dashboard

```http
GET /dashboard/health
```

Response:

```json
{
  "service": "ASMI Dashboard",
  "status": "ok"
}
```

---

## 🔧 Konfigurasi Environment

Buat file `.env` di root project:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
```

Digunakan di:

```python
app/core/config.py
```

---

## 🧠 Prinsip Arsitektur

- `main.py` → wiring aplikasi
- `routes/` → request & response API
- `core/` → config, database, security
- MVP friendly, no over-engineering

---

## 🔜 Rencana Pengembangan

- Statistik dashboard
- Summary penilaian
- Progress harian & total
- Auth (JWT)
- Database integration
- Docker support

---

## 👤 Target Penggunaan

- Internal Dashboard ASMI
- Backend untuk Frontend (Next.js / React)

---

## 📄 Lisensi

Internal Project – ASMI
