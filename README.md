# 🧩 Dashboard Backend API — Dokumentasi Lengkap

Backend API ini menyediakan fitur: Authentication, WhatsApp Bot Integration, dan User Management menggunakan `FastAPI`, `PostgreSQL`, dan `SQLAlchemy`.

Dokumentasi ini menjelaskan cara instalasi, konfigurasi, testing webhook, perintah admin, integrasi AI (opsional), dan tips deployment.

---

## Prasyarat

- Python 3.10+
- PostgreSQL (lokal atau via Docker)
- Virtual environment (disarankan)
- Jika ingin AI: akses OpenAI API key (opsional)

---

## Struktur Proyek (ringkasan)

Folder utama:

- `app/` — kode aplikasi (entry `app/main.py`)
- `app/config/` — konfigurasi dan variabel environment
- `app/whapi/` — client & webhook integrasi WhatsApp
- `app/services/` — service seperti `bot_service.py` (AI + admin handling)
- `alembic/` — migrasi database

Lihat `app/README.md` untuk detail tiap folder.

---

## Environment Variables (detail)

Letakkan file `.env` di root atau export environment variables.

Paling penting:

- `DATABASE_URL` atau `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD` — koneksi DB
- `SECRET_KEY` — JWT secret
- `ALGORITHM` — JWT algorithm (mis. `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` — durasi token
- `WHAPI_BASE_URL` — base URL provider WHAPI (mis. `https://gate.whapi.cloud`)
- `WHAPI_TOKEN` — token untuk mengirim pesan WHAPI
- `WHAPI_ADMINS` — (opsional) daftar nomor admin, contoh: `62811xxxx,62812xxxx`
- `OPENAI_API_KEY` — (opsional) kunci OpenAI jika mau pakai AI reply

Contoh `.env`:

```ini
DATABASE_URL=postgresql://user:pass@localhost:5432/asmi_db
SECRET_KEY=your-super-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60000
WHAPI_BASE_URL=https://gate.whapi.cloud
WHAPI_TOKEN=your-whapi-token
WHAPI_ADMINS=62811xxxx,62812xxxx
OPENAI_API_KEY=sk-xxx
```

---

## Instalasi & Menjalankan (singkat)

1. Clone repo dan aktifkan virtualenv:

```bash
git clone <repo-url>
cd backend-dashboard-python
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependency:

```bash
pip install -r requirements.txt
```

3. Jalankan database (Docker recommended) atau pastikan `DATABASE_URL` valid.

4. Jalankan migrasi:

```bash
alembic upgrade head
```

5. Jalankan server:

```bash
uvicorn app.main:app --reload
```

Endpoints:

- `http://127.0.0.1:8000` — API root
- `http://127.0.0.1:8000/docs` — Swagger UI

---

## Testing Webhook (lokal)

Anda bisa mensimulasikan incoming message dari provider dengan `curl`:

```bash
curl -X POST http://127.0.0.1:8000/webhook/whapi \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"from":"62811xxxx","text":{"body":"Halo saya butuh bantuan"}}]}'
```

Respon yang diharapkan:

```json
{ "status": "ok" }
```

Catatan teknis:

- Route webhook menggunakan `BackgroundTasks` sehingga pemanggilan `send_text` (synchronous) tidak memblokir event loop.
- Jika `send_text` gagal karena konfigurasi `WHAPI_BASE_URL`/`WHAPI_TOKEN` salah, periksa `.env` dan log aplikasi.

---

## Menguji pengiriman pesan manual

Contoh file `test_send.py` (bisa dibuat di root project):

```python
from app.whapi.client import send_text

if __name__ == '__main__':
    print(send_text('62811xxxx', 'Pesan test dari local'))
```

Jalankan:

```bash
python test_send.py
```

Jika `WHAPI_BASE_URL` dan `WHAPI_TOKEN` valid, Anda akan mendapatkan respon dict dari API provider.

---

## Admin & Human Handoff (fitur chat)

Konsep:

- `WHAPI_ADMINS` berisi nomor yang dianggap admin/operator.
- Admin dapat mengirim perintah lewat WhatsApp chat mereka sendiri (atau endpoint internal) untuk mengatur flow:
  - `assign <user>` — set target user ke mode `AGENT` (human)
  - `unassign <user>` — kembalikan target ke mode `BOT`
  - `reply <user> <message>` — admin mengirim balasan yang akan diteruskan ke `user`

Implementasi saat ini (`app/services/bot_service.py`):

- Menyimpan state sederhana di memori (`user_state`, `last_human_reply`). Untuk produksi, gunakan Redis/DB.
- Jika user di-mode `AGENT` atau `PAUSE`, bot otomatis tidak membalas.
- Jika admin mengirim `reply`, service mengembalikan token khusus yang perlu dideteksi oleh caller untuk meneruskan pesan ke target — saya bisa patch `app/whapi/webhook.py` agar mendeteksi token ini dan mengirim pesan secara otomatis.

Contoh panggilan admin (simulasi via webhook):

```bash
curl -X POST http://127.0.0.1:8000/webhook/whapi \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"from":"62811xxxx","text":{"body":"reply 62812xxxx Saya akan bantu sekarang"}}]}'
```

---

## AI Fallback (opsional)

Jika `OPENAI_API_KEY` diset, `app/services/bot_service.py` akan mencoba memanggil OpenAI ChatCompletion (default `gpt-3.5-turbo`) untuk menghasilkan balasan otomatis. Jika tidak tersedia, fungsi akan mengembalikan canned reply.

Catatan keamanan & biaya:

- Gunakan rate limiting dan cost monitoring saat memanggil OpenAI.
- Sanitasi prompt bila perlu (jangan kirim data sensitif tanpa kontrol).

---

## Rekomendasi Produksi

- Ubah `app/whapi/client.py` menjadi async menggunakan `httpx.AsyncClient` agar lebih efisien di bawah beban.
- Simpan `user_state` dan metadata di Redis atau DB (agar bersifat persist dan multi-instance).
- Tambahkan verifikasi signature HMAC untuk webhook jika provider mendukung, simpan `WHAPI_SECRET` di konfigurasi.
- Tambahkan monitoring/logging terpusat (Sentry/ELK) dan retry/backoff pada `send_text`.
- Proteksi endpoint admin (verifikasi nomor/otentikasi tambahan).

---

## Troubleshooting

- Jika webhook tidak menerima event: periksa URL webhook di provider dan pastikan server dapat diakses (ngrok untuk lokal).
- Jika `send_text` gagal: periksa `WHAPI_TOKEN`, `WHAPI_BASE_URL`, dan cek logs untuk error dari provider.

---

## Help / Next Steps saya bisa bantu

- Saya dapat:
  - Buatkan `test_send.py` otomatis dan endpoint admin helper.
  - Patch `app/whapi/webhook.py` untuk otomatis meng-handle `__ADMIN_REPLY__` token dari `bot_service`.
  - Konversi `client.py` ke `httpx.AsyncClient`.

Katakan mana yang mau saya kerjakan selanjutnya.

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
