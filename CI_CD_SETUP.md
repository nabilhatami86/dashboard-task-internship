# CI/CD Setup Guide

Panduan lengkap untuk setup Continuous Integration dan Continuous Deployment menggunakan GitHub Actions.

## 📋 Overview

Project ini menggunakan GitHub Actions untuk:

- ✅ **CI (Continuous Integration)**: Testing dan linting otomatis
- 🐳 **Docker Build**: Build dan push Docker images
- 🚀 **CD (Continuous Deployment)**: Deploy otomatis ke server
- 🔄 **Dependabot**: Auto-update dependencies

## 🏗️ Workflow Architecture

```
┌─────────────────┐
│  Push to Repo   │
└────────┬────────┘
         │
         ├──────────────────────────────────────┐
         │                                      │
         ▼                                      ▼
┌─────────────────┐                    ┌─────────────────┐
│   CI Workflow   │                    │ Docker Build    │
│                 │                    │   Workflow      │
│ - Test Backend  │                    │                 │
│ - Test Frontend │                    │ - Build Images  │
│ - Run Linter    │                    │ - Push to GHCR  │
│ - Build Check   │                    │                 │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         │                                      │
         └──────────────┬───────────────────────┘
                        │
                        ▼
                ┌───────────────┐
                │ All Checks ✓  │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ Deploy to     │
                │  Production   │
                └───────────────┘
```

## 🔧 Setup Instructions

### 1. Repository Secrets

Buka **Settings > Secrets and variables > Actions** di GitHub repo Anda, lalu tambahkan secrets berikut:

#### Untuk Deployment (Optional)

```
SSH_PRIVATE_KEY     = SSH private key untuk akses server
SERVER_HOST         = IP atau domain server (contoh: 192.168.1.100)
SERVER_USER         = Username SSH (contoh: ubuntu)
DEPLOY_PATH         = Path deployment di server (contoh: /home/ubuntu/dashboard)
APP_URL             = URL aplikasi untuk health check (contoh: https://yourdomain.com)
```

#### Untuk Docker Registry (Otomatis dari GITHUB_TOKEN)

GitHub Actions secara otomatis menyediakan `GITHUB_TOKEN` untuk push ke GitHub Container Registry.

### 2. Enable GitHub Container Registry

1. Buka **Settings > Packages** di GitHub repo
2. Enable "Package Creation"
3. Set package visibility (public/private)

### 3. Setup SSH Key (untuk Deployment)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github-actions

# Copy public key ke server
ssh-copy-id -i ~/.ssh/github-actions.pub user@server

# Copy private key dan simpan sebagai GitHub Secret
cat ~/.ssh/github-actions
```

### 4. Setup Environment Variables di Server

Di server production, buat file `.env.production`:

```bash
# Di server
cd /path/to/deploy
nano .env.production
```

Isi dengan:

```env
DB_HOST=db
DB_PORT=5432
DB_NAME=dashboard_db
DB_USER=postgres
DB_PASSWORD=your-strong-password

SECRET_KEY=your-production-secret-key
WHAPI_TOKEN=your-whapi-token

NODE_ENV=production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

## 📁 Workflow Files

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Trigger**: Push ke `main` atau `develop`, atau Pull Request

**Jobs**:

- `backend-test`: Test backend dengan PostgreSQL
- `frontend-test`: Lint dan build frontend
- `build-check`: Konfirmasi semua test passed

**Kapan berjalan**: Setiap push atau PR

### 2. Docker Build Workflow (`.github/workflows/docker-build.yml`)

**Trigger**: Push ke `main` atau tag `v*`

**Jobs**:

- `build-backend`: Build dan push backend image
- `build-frontend`: Build dan push frontend image

**Output**: Images di GitHub Container Registry

- `ghcr.io/username/repo/backend:main`
- `ghcr.io/username/repo/frontend:main`

### 3. Deploy Workflow (`.github/workflows/deploy.yml`)

**Trigger**:

- Tag baru `v*.*.*` (contoh: v1.0.0)
- Manual via workflow dispatch

**Jobs**:

- `deploy`: SSH ke server, pull code, rebuild containers
- Health check setelah deployment

### 4. Dependabot Auto-merge (`.github/workflows/auto-merge-dependabot.yml`)

**Trigger**: Dependabot PR

**Jobs**:

- Auto-approve patch dan minor updates
- Auto-merge jika tests passed

## 🚀 Usage

### Development Workflow

```bash
# 1. Buat feature branch
git checkout -b feature/new-feature

# 2. Commit changes
git add .
git commit -m "feat: add new feature"

# 3. Push ke GitHub
git push origin feature/new-feature
```

**Otomatis berjalan**:

- ✅ CI workflow (test & lint)
- 🐳 Docker build (jika merge ke main)

### Release Workflow

```bash
# 1. Update version
npm version patch  # atau minor, major

# 2. Create git tag
git tag v1.0.1

# 3. Push tag
git push origin v1.0.1
```

**Otomatis berjalan**:

- ✅ CI workflow
- 🐳 Docker build dengan tag v1.0.1
- 🚀 Deploy ke production

### Manual Deployment

1. Buka **Actions** di GitHub repo
2. Pilih **Deploy to Production**
3. Klik **Run workflow**
4. Pilih environment (production/staging)
5. Klik **Run workflow**

## 📊 Monitoring

### Cek Status Workflow

```bash
# Via GitHub CLI
gh workflow list
gh run list
gh run view <run-id>
```

### Cek Docker Images

```bash
# Login ke GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull image
docker pull ghcr.io/username/repo/backend:main
docker pull ghcr.io/username/repo/frontend:main
```

### Cek Deployment di Server

```bash
# SSH ke server
ssh user@server

# Cek container status
docker-compose ps

# Cek logs
docker-compose logs -f --tail=100
```

## 🔐 Security Best Practices

### 1. Secrets Management

❌ **JANGAN**:

- Commit `.env` files
- Hardcode credentials
- Share secrets di chat/email

✅ **LAKUKAN**:

- Gunakan GitHub Secrets
- Rotate secrets regularly
- Use environment-specific secrets

### 2. SSH Security

```bash
# Disable password authentication di server
sudo nano /etc/ssh/sshd_config

# Set
PasswordAuthentication no
PubkeyAuthentication yes

# Restart SSH
sudo systemctl restart sshd
```

### 3. Docker Security

- ✅ Use non-root users di Dockerfile
- ✅ Scan images untuk vulnerabilities
- ✅ Use specific image tags, bukan `latest`
- ✅ Keep dependencies updated (Dependabot)

## 🐛 Troubleshooting

### CI Workflow Gagal

```bash
# Cek logs di GitHub Actions tab

# Test locally
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Atau jalankan test manual
cd backend-dashboard-python/backend-dashboard-python.backup
pytest tests/
```

### Docker Build Gagal

```bash
# Build locally untuk debug
docker build -t test-backend ./backend-dashboard-python/backend-dashboard-python.backup
docker build -t test-frontend ./dashboard-message-center

# Cek build logs
docker logs <container-id>
```

### Deployment Gagal

```bash
# SSH ke server
ssh user@server

# Cek Docker
docker-compose ps
docker-compose logs

# Manual deploy
cd /path/to/deploy
git pull
docker-compose up -d --build
```

### Permission Error di GitHub Actions

```yaml
# Tambahkan permissions di workflow
permissions:
  contents: read
  packages: write
  pull-requests: write
```

## 📈 Advanced Configuration

### Multi-Environment Setup

Buat file compose terpisah:

- `docker-compose.yml` - Development
- `docker-compose.prod.yml` - Production
- `docker-compose.staging.yml` - Staging

```bash
# Deploy ke staging
docker-compose -f docker-compose.staging.yml up -d

# Deploy ke production
docker-compose -f docker-compose.prod.yml up -d
```

### Slack Notifications

Tambahkan ke workflow:

```yaml
- name: Slack notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: "Deployment ${{ job.status }}"
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

### Database Migrations

Tambahkan step di deploy workflow:

```yaml
- name: Run migrations
  run: |
    ssh $SERVER_USER@$SERVER_HOST << 'EOF'
      cd ${{ secrets.DEPLOY_PATH }}
      docker-compose exec -T backend alembic upgrade head
    EOF
```

### Rollback Strategy

```bash
# Di server, simpan backup sebelum deploy
docker tag backend:latest backend:backup
docker tag frontend:latest frontend:backup

# Rollback jika deployment gagal
docker-compose down
docker tag backend:backup backend:latest
docker tag frontend:backup frontend:latest
docker-compose up -d
```

## 🎯 Next Steps

1. **Setup monitoring**:

   - Sentry untuk error tracking
   - Prometheus + Grafana untuk metrics
   - Uptime monitoring (UptimeRobot, Pingdom)

2. **Add more tests**:

   - Unit tests (pytest, jest)
   - Integration tests
   - E2E tests (Playwright, Cypress)

3. **Performance optimization**:

   - Enable caching
   - CDN setup
   - Database indexing

4. **Security hardening**:
   - Enable HTTPS
   - Add rate limiting
   - Implement WAF

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Dependabot Configuration](https://docs.github.com/en/code-security/dependabot)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

---

## 🔄 Workflow Status Badges

Tambahkan di `README.md`:

```markdown
![CI](https://github.com/username/repo/workflows/CI/badge.svg)
![Docker Build](https://github.com/username/repo/workflows/Docker%20Build%20%26%20Push/badge.svg)
![Deploy](https://github.com/username/repo/workflows/Deploy%20to%20Production/badge.svg)
```
