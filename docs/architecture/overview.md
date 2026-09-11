# Edify — System Architecture

## Overview

Edify is a three-part music platform ecosystem:

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
                           REST
                            │
                            ▼
                     ┌─────────────┐
                     │   FastAPI   │
                     └──────┬──────┘
                            │
               ┌────────────┼────────────┐
               ▼            ▼            ▼
          PostgreSQL      Redis       Storage
                                        │
                                   🎵 Music
```

## Components

### 📱 Flutter Mobile App
- **Purpose**: User-facing music listening experience
- **Stack**: Flutter + Dart, Riverpod, Dio, GoRouter, just_audio, audio_service
- **Features**: Login, browse, search, play, playlists, likes, offline playback

### 🖥️ React Admin Dashboard
- **Purpose**: Administrative management interface
- **Stack**: React + TypeScript (Vite), TanStack Query, React Router, Tailwind CSS
- **Features**: Music upload, catalog management, user management, analytics, audit logs

### ⚙️ FastAPI Backend
- **Purpose**: Central API serving both clients
- **Stack**: FastAPI, SQLAlchemy 2.x (async), PostgreSQL, Redis, Alembic
- **Architecture**: Modular monolith (Router → Service → Repository → Database)

## Infrastructure
- **Proxy**: Caddy (HTTPS, reverse proxy)
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Storage**: Self-hosted filesystem
- **Deployment**: Docker Compose
