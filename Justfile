# ============================================================
# Edify Justfile — Command Shortcuts
# Usage: just <command>
# ============================================================

# Default: show available commands
default:
    @just --list

# ---- Docker ----

# Start all services
up:
    docker compose up -d

# Stop all services
down:
    docker compose down

# Rebuild and start
rebuild:
    docker compose up -d --build

# View logs
logs service="edify-api":
    docker compose logs -f {{service}}

# ---- Backend ----

# Run backend locally (outside Docker)
backend-dev:
    cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Run backend tests
backend-test:
    cd backend && python -m pytest tests/ -v

# Lint backend
backend-lint:
    cd backend && ruff check . && ruff format --check .

# Format backend
backend-format:
    cd backend && ruff format .

# ---- Database Migrations ----

# Create a new migration
migrate-create message:
    cd backend && alembic revision --autogenerate -m "{{message}}"

# Run migrations
migrate-up:
    cd backend && alembic upgrade head

# Rollback one migration
migrate-down:
    cd backend && alembic downgrade -1

# Show migration history
migrate-history:
    cd backend && alembic history

# ---- Admin Web ----

# Start admin web dev server
admin-dev:
    cd admin-web && npm run dev

# Install admin web dependencies
admin-install:
    cd admin-web && npm install

# Build admin web
admin-build:
    cd admin-web && npm run build

# ---- Flutter ----

# Run Flutter app
mobile-run:
    cd mobile && flutter run

# Build Flutter APK
mobile-build:
    cd mobile && flutter build apk

# ---- Utilities ----

# Reset everything (careful!)
reset:
    docker compose down -v
    docker compose up -d --build
