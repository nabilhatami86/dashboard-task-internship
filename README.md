# 🚀 Dashboard Message Center

Dashboard lengkap untuk mengelola pesan WhatsApp dengan fitur chatbot otomatis, internal chat, dan manajemen user.

![CI](https://github.com/username/repo/workflows/CI/badge.svg)
![Docker Build](https://github.com/username/repo/workflows/Docker%20Build%20%26%20Push/badge.svg)

## ✨ Features

### 🎯 Core Features
- ✅ **WhatsApp Integration** - Connect via Whapi.cloud API
- 🤖 **Automated Chatbot** - Auto-response untuk customer & internal chat
- 💬 **Real-time Messaging** - Smart refresh system (WhatsApp-style)
- 👥 **Multi-user Support** - Admin & Agent roles dengan sidebar navigation
- 🔐 **Authentication** - JWT-based dengan role management & auto-logout
- 📊 **Dashboard Analytics** - Monitoring dashboard dengan real-time stats
- 🎫 **Ticket Queue System** - FIFO ticket assignment untuk agent
- 🎨 **Multi-Theme System** - 6 pilihan tema dengan smooth transitions

### 💡 Advanced Features
- 🔄 **Smart Polling** - Adaptive refresh dengan exponential backoff
- 👁️ **Visibility API** - Auto-pause saat tab tidak aktif
- 📱 **Responsive Sidebar** - Collapsible sidebar dengan mobile support
- 🌈 **Dynamic Theming** - Default, Dark, Blue, Purple, Green, Ocean themes
- 🎯 **Agent Dashboard** - Expandable sidebar dengan theme switcher
- 📈 **Admin Monitoring** - Premium glassmorphism UI dengan progress bars
- 🐳 **Docker Ready** - Production-ready containerization
- 🚀 **CI/CD Pipeline** - Automated testing & deployment
- 🌐 **Custom Dev Server** - Menampilkan semua network interfaces

## 📁 Project Structure

```
Dashboard/
├── backend-dashboard-python/          # FastAPI Backend
│   └── backend-dashboard-python.backup/
│       ├── app/                       # Application code
│       │   ├── config/               # Database & settings
│       │   ├── controller/           # Business logic
│       │   ├── models/               # SQLAlchemy models
│       │   ├── routes/               # API endpoints
│       │   ├── services/             # Bot services
│       │   └── whapi/                # WhatsApp integration
│       ├── alembic/                  # Database migrations
│       ├── Dockerfile                # Backend container
│       └── requirements.txt          # Python dependencies
│
├── dashboard-message-center/          # Next.js Frontend
│   ├── app/                          # App router pages
│   │   ├── dashboard-admin/         # Admin dashboard
│   │   ├── dashboard-admin-monitoring/ # Monitoring dashboard
│   │   ├── dashboard-agent/         # Agent dashboard
│   │   ├── dashboard-agent-queue/   # Ticket queue
│   │   └── login/                   # Authentication
│   ├── components/                   # React components
│   │   ├── auth/                    # Auth components
│   │   ├── chat/                    # Chat UI
│   │   ├── customer/                # Customer details
│   │   ├── providers/               # Theme & auth providers
│   │   └── ui/                      # UI components
│   │       ├── agent-sidebar.tsx    # Agent sidebar
│   │       ├── app-sidebar.tsx      # Admin sidebar
│   │       └── theme-switcher.tsx   # Theme selector
│   ├── hooks/                        # Custom React hooks
│   │   └── useSmartRefresh.ts       # Adaptive polling
│   ├── lib/                          # Utilities & API
│   │   └── themes.ts                # Theme configurations
│   ├── store/                        # Zustand state management
│   │   ├── authStore.ts             # Authentication state
│   │   └── themeStore.ts            # Theme state
│   ├── server.js                     # Custom Next.js server
│   ├── Dockerfile                    # Frontend container
│   └── package.json                  # Node dependencies
│
├── .github/                          # GitHub Actions
│   ├── workflows/                    # CI/CD pipelines
│   │   ├── ci.yml                   # Testing & linting
│   │   ├── docker-build.yml         # Build & push images
│   │   ├── deploy.yml               # Production deployment
│   │   └── auto-merge-dependabot.yml
│   └── dependabot.yml               # Dependency updates
│
├── nginx/                            # Nginx configuration
│   └── nginx.conf                   # Reverse proxy config
│
├── scripts/                          # Helper scripts
│   ├── deploy.sh                    # Deployment script
│   ├── rollback.sh                  # Rollback script
│   ├── backup-db.sh                 # Database backup
│   └── restore-db.sh                # Database restore
│
├── docker-compose.yml                # Development compose
├── docker-compose.prod.yml           # Production compose
└── README.md                         # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Option 1: Docker (Recommended)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd Dashboard

# 2. Setup environment
cp backend-dashboard-python/backend-dashboard-python.backup/.env.example backend-dashboard-python/backend-dashboard-python.backup/.env

# Edit .env with your credentials
nano backend-dashboard-python/backend-dashboard-python.backup/.env

# 3. Build and run
docker-compose up -d --build

# 4. Access applications
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

**Backend:**
```bash
cd backend-dashboard-python/backend-dashboard-python.backup

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd dashboard-message-center

# Install dependencies
npm install

# Start dev server (with custom server & network info)
npm run dev

# Or use default Next.js dev server
npm run dev:default
```

## 🐳 Docker Setup

Detailed Docker documentation: [DOCKER_SETUP.md](./DOCKER_SETUP.md)

**Quick commands:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend

# Database backup
docker exec dashboard-postgres pg_dump -U postgres asmi_db > backup.sql
```

## 🔄 CI/CD Pipeline

Detailed CI/CD documentation: [CI_CD_SETUP.md](./CI_CD_SETUP.md)

### Automated Workflows

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Runs on every push and PR
   - Backend tests with PostgreSQL
   - Frontend linting and build
   - Automatic checks

2. **Docker Build** (`.github/workflows/docker-build.yml`)
   - Builds on push to `main`
   - Pushes images to GitHub Container Registry
   - Tagged releases

3. **Deployment** (`.github/workflows/deploy.yml`)
   - Triggered by version tags (`v*.*.*`)
   - SSH deployment to production server
   - Health checks after deployment

4. **Dependabot** (`.github/dependabot.yml`)
   - Automatic dependency updates
   - Auto-merge for patch/minor versions
   - Weekly schedule

### Deployment Process

```bash
# 1. Create a release tag
git tag v1.0.0
git push origin v1.0.0

# 2. GitHub Actions automatically:
#    - Runs tests
#    - Builds Docker images
#    - Deploys to production
#    - Runs health checks

# 3. Manual deployment (if needed)
./scripts/deploy.sh production
```

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

### Chats
- `GET /chats/` - List all chats
- `GET /chats/{chat_id}` - Get specific chat
- `POST /chats/{chat_id}/messages` - Send message
- `DELETE /chats/{chat_id}` - Delete chat

### Admin Chat
- `GET /admin-chat/{agent_id}` - Get admin-agent chat
- `POST /admin-chat/{agent_id}/messages` - Send admin message
- `PUT /admin-chat/{agent_id}/mode` - Change mode (bot/manual)

### Users
- `GET /users/` - List users (admin only)
- `GET /users/agents` - List agent users

### WhatsApp Webhook
- `POST /whapi/webhook` - Receive WhatsApp messages

Full API documentation: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dashboard_db
DB_USER=postgres
DB_PASSWORD=your_password

# JWT
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=160

# WhatsApp API
WHAPI_BASE_URL=https://gate.whapi.cloud
WHAPI_TOKEN=your_whapi_token
WHAPI_URL=https://gate.whapi.cloud
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Theme System

6 pre-configured themes tersedia:

1. **☀️ Default Light** - Clean white theme dengan blue accents
2. **🌙 Dark Mode** - Dark theme untuk low-light environments
3. **🌊 Ocean Blue** - Fresh blue theme dengan sky gradients
4. **💜 Purple Dream** - Elegant purple dengan pink accents
5. **🌲 Forest Green** - Natural green theme
6. **🐋 Deep Ocean** - Dark blue ocean-inspired theme

Themes menggunakan CSS custom properties dan tersimpan di localStorage via Zustand persist middleware.

### Startup Information Display

Saat development, aplikasi menampilkan informasi lengkap:

**Backend (FastAPI):**
- Database connection details (host, port, database name)
- Loaded models & tables
- All API routes dengan endpoints
- CORS configuration
- Environment variables (password/token masked)

**Frontend (Next.js):**
- All available network interfaces (Wi-Fi, Ethernet, VPN, Docker)
- Project info & working directory
- Enabled features & server actions
- Available pages & routes

### Smart Refresh Configuration

Edit in `hooks/useSmartRefresh.ts`:
```typescript
const { markActivity } = useSmartRefresh({
  onRefresh: loadChats,
  minInterval: 15000,  // 15s when active
  maxInterval: 60000,  // 60s when idle
  enabled: true
});
```

## 🎨 UI Components

### Sidebar Components

**AgentSidebar** (`components/ui/agent-sidebar.tsx`)
- Expandable/collapsible sidebar (w-20 collapsed, w-64 expanded)
- Mobile responsive dengan hamburger menu
- Menu items: Customer Chats, Admin Chat, Ticket Queue
- Theme switcher & logout button
- Tooltips untuk collapsed state
- Smooth transitions (300ms ease-in-out)

**AppSidebar** (`components/ui/app-sidebar.tsx`)
- Admin dashboard sidebar
- Filter options: All Tickets, Assigned, Unassigned
- Dashboard monitoring navigation
- Chat list dengan real-time counts
- Theme switcher integration

**ThemeSwitcher** (`components/ui/theme-switcher.tsx`)
- Dropdown list dengan 6 themes
- Color preview dots untuk setiap theme
- Active theme indicator dengan checkmark
- Bottom-positioned dropdown (agar tidak tertutup)
- Scrollable list untuk scalability

### Theme Provider

ThemeProvider (`components/providers/theme-provider.tsx`) automatically applies theme on mount dan sync dengan Zustand store.

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd backend-dashboard-python/backend-dashboard-python.backup
pytest tests/ -v

# Frontend linting
cd dashboard-message-center
npm run lint

# Frontend build test
npm run build
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Helper Scripts

```bash
# Deploy to production
./scripts/deploy.sh production

# Rollback deployment
./scripts/rollback.sh v1.0.0

# Backup database
./scripts/backup-db.sh

# Restore database
./scripts/restore-db.sh backups/database_backup_20240101_120000.sql.gz
```

## 🔐 Security

- ✅ JWT authentication with HTTP-only cookies
- ✅ CORS configuration
- ✅ Rate limiting (nginx)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS protection headers
- ✅ Non-root Docker containers
- ✅ Environment variable secrets

**Production checklist:**
- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall
- [ ] Regular security updates
- [ ] Enable monitoring

## 📈 Performance

### Smart Refresh Optimization
- **78% reduction** in network requests
- Exponential backoff (15s → 60s)
- Pauses when tab inactive
- Activity-based acceleration

### Caching Strategy
- Browser caching for static assets
- API response caching (planned)
- Database query optimization

## 🐛 Troubleshooting

### Common Issues

**Container won't start:**
```bash
docker-compose logs backend
docker-compose down -v
docker-compose up -d --build
```

**Database connection error:**
```bash
# Check database status
docker-compose ps db

# Restart backend after db is ready
docker-compose restart backend
```

**Port already in use:**
```bash
# Find process using port
lsof -i :3000
lsof -i :8000

# Kill process or change port in docker-compose.yml
```

**Smart refresh too fast/slow:**
- Check `useSmartRefresh` configuration
- Verify network tab in browser DevTools
- Check console for errors

**Theme dropdown tertutup sidebar:**
- Fixed: Dropdown sekarang muncul ke atas (`bottom-full mb-2`)
- Width disesuaikan agar tidak overflow

**ESLint errors:**
```bash
# Fix common errors
npm run lint

# Common fixes:
# - TypeScript 'any': Use proper type checking (instanceof Error)
# - setState in effect: Use useMemo for computed values
# - Impure functions: Move Date.now() ke useEffect
```

**Sidebar tidak bisa expand:**
- AgentSidebar: Default state `useState(true)` untuk open by default
- Toggle button di bagian bawah sidebar (desktop)
- Hamburger menu untuk mobile

**Network interfaces tidak muncul:**
- Pastikan menggunakan `npm run dev` (bukan `npm run dev:default`)
- Custom server akan menampilkan semua interfaces (Wi-Fi, VPN, Docker, etc)

## 🧰 Technology Stack

### Frontend
- **Framework**: Next.js 16.0.10 (App Router, Turbopack)
- **UI Library**: React 19.2.1
- **Styling**: Tailwind CSS v4, tailwindcss-animate
- **State Management**: Zustand 5.0.9 (with persist middleware)
- **Components**: Radix UI (Avatar, Dialog, Dropdown, ScrollArea, Separator, Slot, Tooltip)
- **Icons**: Lucide React 0.561.0
- **Animations**: Framer Motion 12.23.26
- **Utilities**: clsx, tailwind-merge, class-variance-authority
- **Language**: TypeScript 5

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (JSON Web Tokens)
- **API Integration**: WhatsApp via Whapi.cloud
- **Language**: Python 3.11+

### DevOps & Tools
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Reverse Proxy**: Nginx
- **Linting**: ESLint 9, eslint-config-next
- **Version Control**: Git

## 📚 Documentation

- [Docker Setup Guide](./DOCKER_SETUP.md) - Complete Docker configuration
- [CI/CD Setup Guide](./CI_CD_SETUP.md) - GitHub Actions pipelines
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Production deployment
- [API Documentation](http://localhost:8000/docs) - Swagger/OpenAPI docs

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is private and proprietary.

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python API framework
- [Whapi.cloud](https://whapi.cloud/) - WhatsApp API provider
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Docker](https://www.docker.com/) - Containerization
- [GitHub Actions](https://github.com/features/actions) - CI/CD

---

**Made with ❤️ for efficient customer communication**
