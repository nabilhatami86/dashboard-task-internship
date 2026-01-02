# Docker Setup Guide

Panduan lengkap untuk menjalankan Dashboard Message Center menggunakan Docker.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Port yang tersedia: 3000, 8000, 5432

## 🚀 Quick Start

### 1. Clone dan Setup Environment

```bash
cd /Users/mm/Desktop/Dashboard
```

### 2. Setup Backend Environment

```bash
# Copy environment template
cp backend-dashboard-python/backend-dashboard-python.backup/.env.example backend-dashboard-python/backend-dashboard-python.backup/.env

# Edit .env file dengan kredensial Anda
nano backend-dashboard-python/backend-dashboard-python.backup/.env
```

Isi minimal yang diperlukan:

```env
DB_HOST=db
DB_PORT=5432
DB_NAME=dashboard_db
DB_USER=postgres
DB_PASSWORD=123

SECRET_KEY=ganti-dengan-secret-key-yang-kuat
WHAPI_TOKEN=token-whapi-anda
```

### 3. Build dan Jalankan Semua Services

```bash
# Build images
docker-compose build

# Jalankan semua container
docker-compose up -d

# Atau build + run sekaligus
docker-compose up -d --build
```

### 4. Cek Status Container

```bash
docker-compose ps
```

Output yang diharapkan:

```
NAME                   STATUS          PORTS
dashboard-frontend     Up 2 minutes    0.0.0.0:3000->3000/tcp
dashboard-backend      Up 2 minutes    0.0.0.0:8000->8000/tcp
dashboard-postgres     Up 2 minutes    0.0.0.0:5432->5432/tcp
```

### 5. Akses Aplikasi

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Command Cheatsheet

### Container Management

```bash
# Stop semua services
docker-compose stop

# Start semua services
docker-compose start

# Restart semua services
docker-compose restart

# Stop dan hapus container
docker-compose down

# Stop dan hapus container + volumes (HATI-HATI: data akan hilang)
docker-compose down -v
```

### Logs & Debugging

```bash
# Lihat logs semua container
docker-compose logs

# Lihat logs service tertentu
docker-compose logs frontend
docker-compose logs backend
docker-compose logs db

# Follow logs (real-time)
docker-compose logs -f backend

# Lihat 100 baris terakhir
docker-compose logs --tail=100 backend
```

### Database Operations

```bash
# Akses PostgreSQL shell
docker exec -it dashboard-postgres psql -U postgres -d dashboard_db

# Backup database
docker exec dashboard-postgres pg_dump -U postgres dashboard_db > backup.sql

# Restore database
cat backup.sql | docker exec -i dashboard-postgres psql -U postgres dashboard_db

# Run migrations
docker exec dashboard-backend alembic upgrade head

# Create new migration
docker exec dashboard-backend alembic revision --autogenerate -m "description"
```

### Development Mode

```bash
# Jalankan backend dengan hot reload
docker-compose up backend

# Rebuild service tertentu
docker-compose build --no-cache frontend
docker-compose up -d frontend

# Exec into container untuk debugging
docker exec -it dashboard-backend sh
docker exec -it dashboard-frontend sh
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│   Next.js       │  Port 3000
│   (dashboard-   │
│    frontend)    │
└────────┬────────┘
         │
         │ HTTP
         ▼
┌─────────────────┐
│   Backend       │
│   FastAPI       │  Port 8000
│   (dashboard-   │
│    backend)     │
└────────┬────────┘
         │
         │ PostgreSQL
         ▼
┌─────────────────┐
│   Database      │
│   PostgreSQL 16 │  Port 5432
│   (dashboard-   │
│    postgres)    │
└─────────────────┘
```

## 📦 Services Detail

### Frontend (Next.js)

- **Container**: dashboard-frontend
- **Port**: 3000
- **Build**: Multi-stage dengan standalone output
- **Features**:
  - Production optimized
  - Automatic restarts
  - Smart refresh system

### Backend (FastAPI + Python)

- **Container**: dashboard-backend
- **Port**: 8000
- **Features**:
  - Auto migration on startup
  - Hot reload untuk development
  - Health check endpoint
  - WhatsApp API integration

### Database (PostgreSQL)

- **Container**: dashboard-postgres
- **Port**: 5432
- **Data**: Persistent volume `postgres_data`
- **Features**:
  - Health checks
  - Automatic backups (via volume)

## 🔐 Security Notes

1. **Ganti password default** di `.env`:

   ```env
   DB_PASSWORD=password-yang-kuat
   SECRET_KEY=secret-key-yang-panjang-dan-acak
   ```

2. **Untuk Production**, edit `docker-compose.yml`:

   - Hapus port mapping database (5432:5432)
   - Gunakan secrets untuk credentials
   - Enable SSL/TLS
   - Gunakan reverse proxy (nginx)

3. **Jangan commit** file `.env` ke Git

## 🐛 Troubleshooting

### Container tidak bisa start

```bash
# Cek logs untuk error
docker-compose logs backend

# Hapus dan rebuild
docker-compose down
docker-compose up -d --build
```

### Database connection error

```bash
# Pastikan database sudah ready
docker-compose logs db

# Restart backend setelah db ready
docker-compose restart backend
```

### Port sudah digunakan

```bash
# Cari process yang menggunakan port
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Kill process atau edit docker-compose.yml untuk ganti port
```

### Build error - cache issue

```bash
# Clean build tanpa cache
docker-compose build --no-cache

# Atau hapus semua dan rebuild
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

### Frontend tidak bisa connect ke backend

Pastikan environment variable sudah benar:

```yaml
# di docker-compose.yml
environment:
  - NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Production Deployment

Untuk production deployment, gunakan:

1. **Update docker-compose.yml**:

   - Set `NODE_ENV=production`
   - Remove volume mounts
   - Use secrets
   - Add nginx reverse proxy

2. **Database**:

   - Use managed database (Railway, Supabase, etc)
   - Regular backups
   - Connection pooling

3. **Monitoring**:
   - Add health checks
   - Container monitoring
   - Log aggregation

Lihat [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) untuk detail lengkap.

## 🔄 Update & Maintenance

```bash
# Pull latest code
git pull

# Rebuild dan restart
docker-compose down
docker-compose up -d --build

# Update database schema
docker exec dashboard-backend alembic upgrade head
```

## 💾 Data Persistence

Data PostgreSQL disimpan di Docker volume `postgres_data`. Data akan tetap ada meskipun container dihapus, kecuali Anda menggunakan `docker-compose down -v`.

### Backup Volume

```bash
# Backup
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

## 📚 Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Next.js Docker Deployment](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI in Containers](https://fastapi.tiangolo.com/deployment/docker/)
