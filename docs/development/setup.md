# Edify — Local Development Setup

## Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **Flutter SDK** 3.x
- **Docker** & Docker Compose
- **Git**

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd edify
```

### 2. Create environment file

```bash
cp .env.example .env
# Edit .env with your local settings (defaults are fine for development)
```

### 3. Start infrastructure

```bash
docker compose up -d
```

This starts:
- **PostgreSQL** on port `5432`
- **Redis** on port `6379`
- **FastAPI** on port `8000`

### 4. Verify services

```bash
# Check all services are healthy
docker compose ps

# Test API
curl http://localhost:8000/health

# View API docs
# Open http://localhost:8000/docs in your browser
```

### 5. Set up Admin Web (separate terminal)

```bash
cd admin-web
npm install
npm run dev
# Open http://localhost:5173 in your browser
```

### 6. Set up Flutter App

```bash
cd mobile
flutter pub get
flutter run
```

## Project Structure

```
edify/
├── backend/           # FastAPI application
├── mobile/            # Flutter application
├── admin-web/         # React admin dashboard
├── infrastructure/    # Docker, Caddy, scripts
├── docs/              # Documentation
├── docker-compose.yml
├── Justfile           # Command shortcuts
└── .env.example
```

## Useful Commands

| Command | Description |
|---------|-------------|
| `docker compose up -d` | Start all services |
| `docker compose down` | Stop all services |
| `docker compose logs -f edify-api` | View backend logs |
| `cd backend && alembic upgrade head` | Run database migrations |
| `cd backend && alembic revision --autogenerate -m "description"` | Create new migration |
| `cd admin-web && npm run dev` | Start admin web dev server |
| `cd mobile && flutter run` | Run Flutter app |
