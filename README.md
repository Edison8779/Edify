# 🎵 Edify

**A personal music platform ecosystem** — stream, manage, and discover your music library.

Edify is a three-part system: a **Flutter mobile app** for listening, a **React admin dashboard** for management, and a **FastAPI backend** connecting everything.

---

## Architecture

```
                         🎵 EDIFY
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
       📱 Flutter       🖥️ React Web    ⚙️ FastAPI
       Mobile App      Admin Dashboard     Backend
             │              │              │
             └──────────────┼──────────────┘
                            │
               ┌────────────┼────────────┐
               ▼            ▼            ▼
          PostgreSQL      Redis       Storage
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Mobile** | Flutter, Dart, Riverpod, Dio, GoRouter, just_audio |
| **Admin Web** | React, TypeScript, Vite, TanStack Query, Tailwind CSS |
| **Backend** | FastAPI, SQLAlchemy 2.x, PostgreSQL, Redis, Alembic |
| **Infrastructure** | Docker Compose, Caddy |

## Project Structure

```
edify/
├── backend/           # FastAPI REST API
│   ├── app/
│   │   ├── api/       # Route handlers
│   │   ├── core/      # Config, DB, logging, exceptions
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   └── repositories/  # Data access
│   ├── migrations/    # Alembic migrations
│   └── tests/
├── mobile/            # Flutter mobile app
├── admin-web/         # React admin dashboard
├── infrastructure/    # Docker, Caddy, scripts
├── docs/              # Documentation
├── docker-compose.yml
├── Justfile           # Command shortcuts
└── .env.example       # Environment template
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Flutter SDK 3.x
- Docker & Docker Compose

### Setup

```bash
# 1. Clone and configure
git clone <repository-url>
cd edify
cp .env.example .env

# 2. Start infrastructure
docker compose up -d

# 3. Verify
curl http://localhost:8000/health
# → {"status": "ok", "version": "0.1.0"}

# 4. Admin Web (separate terminal)
cd admin-web && npm install && npm run dev

# 5. Flutter App
cd mobile && flutter pub get && flutter run
```

### Useful Endpoints

| URL | Description |
|-----|-------------|
| `http://localhost:8000/health` | API health check |
| `http://localhost:8000/docs` | Swagger UI |
| `http://localhost:8000/redoc` | ReDoc |
| `http://localhost:5173` | Admin Web (dev) |

## Development

See [docs/development/setup.md](docs/development/setup.md) for detailed setup instructions.

## License

Private — All rights reserved.
