Now Edify becomes a proper 3-part system rather than just an Android music player:

                         🎵 EDIFY
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
       📱 Android       ⚙️ Backend      🖥️ Admin Web
          App             API             Dashboard
             │              │              │
             └──────────────┼──────────────┘
                            │
                   ┌────────┴────────┐
                   │                 │
              PostgreSQL          Storage
                   │                 │
                   │            1000+ songs
                   │
                Audit Logs

The Android app is for listening.
The website is your administration/control panel.
The FastAPI backend is the brain connecting everything.

And since you want this to be ₹0 from your side, we'll design it around free/open-source software and your own machine/storage.

## What Changed
- **Multi-Quality Audio Transcoding**: Added FFmpeg-based transcoding subsystem to generate 64k, 128k, and 256k variants from a master upload.
- **Storage Architecture**: Moved to UUID-based paths with `original/` and `variants/`.
- **Database Schema**: Introduced `song_audio_variants` to track transcoding status.
- **Upload Flow**: Made uploads async. The API queues Redis jobs for FFmpeg.
- **Streaming API**: Added `quality` query parameter to the streaming endpoint.

🎵 EDIFY — Complete Project Plan
1. Final product

Edify will have three applications:

1️⃣ Edify Android App

For:

Login
Browse music
Search
Play music
Like songs
Create playlists
Queue
Recently played
Listening history
Profile
Settings
Background playback
2️⃣ Edify Admin Website

For you as the owner:

Login
Dashboard
Upload music
Upload album artwork
Manage songs
Manage artists
Manage albums
Manage genres
Create/edit playlists
Manage users
See listening statistics
See audit logs
Manage storage
Monitor server
Enable/disable songs/users
Delete/restore content
3️⃣ Edify Backend

FastAPI will provide:

Authentication
Music
Streaming
Users
Playlists
Search
Library
Analytics
Audit logging
Admin
Storage
2. High-level architecture
                         INTERNET / LAN
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
       📱 Android App                    🖥️ Admin Website
       Kotlin + Compose                  React / Next.js
              │                                 │
              │ HTTPS                           │ HTTPS
              │                                 │
              └───────────────┬─────────────────┘
                              ▼
                     ┌──────────────────┐
                     │      Caddy       │
                     │ Reverse Proxy    │
                     │ HTTPS             │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │     FastAPI      │
                     │     Backend      │
                     └────────┬─────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                 ▼             ▼             ▼
           PostgreSQL       Redis       File Storage
                 │             │             │
                 │             │          Originals
                 │             │          Variants
                 │             │
                 └─────────────┼─────────────┘
                               ▼
                   ┌───────────────────────┐
                   │ FFmpeg Worker (Redis) │
                   └───────────────────────┘
                               │
                               ▼
                          Audit Logs
3. Technology stack
Android
Kotlin
Jetpack Compose
Media3 / ExoPlayer
Retrofit
Room
Hilt
DataStore
Backend
Python
FastAPI
SQLAlchemy 2.x
PostgreSQL
Redis
Alembic
Pydantic
JWT
Argon2
Admin website

I recommend:

Next.js
TypeScript
Tailwind CSS
TanStack Query

You could use plain React, but Next.js gives you a better foundation for a serious web application.

Infrastructure
Docker
Docker Compose
Caddy
Git

Everything is free/open-source.

4. Authentication architecture

We previously decided on:

Google
   +
Email/password

No paid SMS provider.

Your authentication system:

                   Authentication
                         │
              ┌──────────┴──────────┐
              │                     │
           Google              Email/Password
              │                     │
              └──────────┬──────────┘
                         ▼
                       User
                         │
                         ▼
                 Edify JWT Session
5. User roles

This is important because you have an admin website.

Define:

USER
ADMIN

Potentially later:

SUPER_ADMIN
EDITOR

For now:

USER
 └── Android access

ADMIN
 ├── Android access
 └── Admin website access
6. Database architecture

Core tables:

users
auth_identities
refresh_tokens

artists
albums
songs
song_audio_variants
genres

playlists
playlist_songs

liked_songs
play_history

audit_logs

uploads
storage_objects

Later:

user_sessions
notifications
lyrics
song_analytics
7. User model
users
────────────────────────
id
email
username
display_name
avatar_url

role

is_active
is_verified

created_at
updated_at
last_login_at
8. Authentication identities
auth_identities
────────────────────────
id
user_id

provider
provider_user_id

created_at

Examples:

user_id = 1

provider = google
provider_user_id = xyz

provider = password
provider_user_id = user@example.com
9. Music data model
Artist
artists
────────────────
id
name
bio
image_path
created_at
updated_at
Album
albums
────────────────
id
artist_id
title
cover_path
release_date
created_at
updated_at
Song
songs
────────────────────────
id
album_id
artist_id
genre_id

title
track_number

duration

song_audio_variants
────────────────────────
id
song_id
quality (original, 64k, 128k, 256k)
codec
bitrate
format
storage_key
file_size
status (PENDING, PROCESSING, READY, FAILED)
created_at
updated_at

is_active

created_at
updated_at
10. Music storage

Don't store MP3 files inside PostgreSQL.

Use:

PostgreSQL
      │
      │ metadata
      ▼
File Storage
      │
      ├── songs/
      ├── albums/
      └── artists/

Example:

storage/
└── songs/
    └── {song_uuid}/
        ├── original/
        │   └── master.flac
        ├── variants/
        │   ├── 64k/
        │   │   └── audio.mp3
        │   ├── 128k/
        │   │   └── audio.mp3
        │   └── 256k/
        │       └── audio.mp3
        ├── cover/
        │   └── cover.jpg
        └── temp/

10b. Audio Transcoding

We use FFmpeg via a Redis-backed background worker to generate variants.
- FastAPI accepts upload, stores in `original/`, and creates `song_audio_variants` DB records with `PENDING`.
- FastAPI enqueues jobs to Redis and returns `201 Created` immediately.
- Background worker processes FFmpeg tasks inside `temp/`.
- Worker updates DB status to `PROCESSING`, then `READY` (on success) or `FAILED` (on error).
11. Admin music upload

This will be one of the most important website features.

Website:

Upload Music

You select:

┌──────────────────────────────┐
│ Upload Music                 │
│                              │
│ Audio File                   │
│ [ Choose File ]              │
│                              │
│ Song Title                   │
│ [________________________]   │
│                              │
│ Artist                       │
│ [________________________]   │
│                              │
│ Album                        │
│ [________________________]   │
│                              │
│ Genre                        │
│ [________________________]   │
│                              │
│ Cover                        │
│ [ Choose Image ]             │
│                              │
│       [ Upload Song ]        │
└──────────────────────────────┘

Backend:

POST /admin/songs

Flow:

Website
   │
   │ multipart upload
   ▼
FastAPI
   │
   ├── Validate file
   ├── Validate metadata
   ├── Generate ID
   ├── Save file to `original/`
   ├── Create DB records (`song` and `variants`)
   ├── Queue transcoding job to Redis
   ├── Audit event
   └── Return Response (Async Processing)
12. Automatic metadata extraction

This is a feature I'd definitely add.

If your MP3 already contains:

Title
Artist
Album
Genre
Track number
Album art

Edify can read those tags during upload.

So instead of manually entering everything:

song.mp3
    │
    ▼
Metadata extraction
    │
    ├── Title
    ├── Artist
    ├── Album
    ├── Genre
    ├── Track
    └── Cover

Then the admin just verifies the information.

13. Music streaming

API:

GET /api/v1/songs/{song_id}/stream?quality=128k

Flow:

Android
   │
   │ Authorization
   ▼
FastAPI
   │
   ├── Verify JWT
   ├── Check song
   └── Check access
          │
          ▼
      File Storage
          │
          ▼
       Audio stream
          │
          ▼
       Media3
          │
          ▼
          🔊

Implement:

HTTP Range Requests
206 Partial Content
Content-Length
Content-Range
Accept-Ranges
Content-Type

This will give you proper seeking.

14. Android music player

Use Media3.

Player features:

Play
Pause
Quality Selection (Auto, Low, Med, High, Original)
Next
Previous
Seek
Shuffle
Repeat
Queue
Volume
Background playback
Notification controls

Architecture:

UI
 │
 ▼
ViewModel
 │
 ▼
MusicRepository
 │
 ├── API
 │
 └── Media3
       │
       ▼
 MusicPlayerService
       │
       ▼
    Android
15. Persistent player

The music should continue playing when:

User leaves Edify
User locks phone
User opens another app
Screen turns off

So use:

MediaSession
+
Foreground Service
+
Media3
16. Android screens
Authentication
Splash
   ↓
Login
 ├── Google
 └── Email
       │
       └── Register
Main
Home
Search
Library
Profile
Player
Mini Player
     ↓
Full Player
17. Home page
EDIFY

Good morning 👋

Recently Played
────────────────

[Album] [Album] [Album]

Your Favorites
────────────────

🎵 Song
🎵 Song
🎵 Song

Made For You
────────────────

[Album] [Album]

Backend:

GET /api/v1/home
18. Search
GET /api/v1/search?q=...

Return:

{
  "songs": [],
  "artists": [],
  "albums": [],
  "playlists": []
}
19. Library
Library
│
├── Liked Songs
├── Playlists
├── Albums
├── Artists
└── Recently Played
20. Playlists

Database:

playlists
playlist_songs

API:

POST   /playlists
GET    /playlists
GET    /playlists/{id}

POST   /playlists/{id}/songs
DELETE /playlists/{id}/songs/{song_id}

PATCH  /playlists/{id}
DELETE /playlists/{id}
21. Listening history

Whenever a user plays a song:

POST /history

Store:

user_id
song_id
started_at
ended_at
duration_played
completed

This will later power recommendations.

22. ⭐ Audit tracking

This is the part you specifically requested.

Every important administrative action should create an audit event.

For example:

Admin uploaded song
Admin deleted song
Admin edited album
Admin changed user role
User logged in
User created playlist
User liked song
User deleted playlist

Database:

audit_logs
────────────────────────────
id

actor_user_id
action

entity_type
entity_id

old_values
new_values

ip_address
user_agent

created_at

Example:

ID: 1928

Actor:
admin@example.com

Action:
SONG_UPDATED

Entity:
Song #127

Old:
{
  "title": "Old Name"
}

New:
{
  "title": "New Name"
}

Time:
2026-09-11 11:30
23. Admin Audit Dashboard

Website:

┌─────────────────────────────────────────────────┐
│ Audit Logs                                      │
├─────────────────────────────────────────────────┤
│ Actor       Action       Entity      Time       │
│                                                 │
│ Edison      UPLOAD       Song #123   10:21      │
│ Edison      UPDATE       Song #124   10:25      │
│ Edison      DELETE       Song #125   10:32      │
│ Edison      LOGIN        User        10:40      │
│                                                 │
└─────────────────────────────────────────────────┘

Filters:

Actor
Action
Entity
Date
User

Search:

Search audit logs...
24. Admin Dashboard

Your main dashboard could show:

┌─────────────────────────────────────────┐
│ EDIFY ADMIN                             │
│                                         │
│ Songs          1,024                    │
│ Albums           123                    │
│ Artists           87                    │
│ Users              3                    │
│ Playlists         24                    │
│                                         │
│ Storage       18.4 GB                   │
│                                         │
├─────────────────────────────────────────┤
│ Recent Activity                         │
│                                         │
│ 🎵 Uploaded Song                        │
│ ✏️ Updated Album                        │
│ ❤️ User liked Song                      │
│ 🗑️ Deleted Playlist                     │
└─────────────────────────────────────────┘
25. Admin website pages
/admin

├── Dashboard
│
├── Music
│   ├── Songs
│   ├── Artists
│   ├── Albums
│   └── Genres
│
├── Playlists
│
├── Users
│
├── Analytics
│
├── Audit Logs
│
├── Storage
│
└── Settings
26. Song management

Admin should be able to:

View songs
Search songs
Filter songs
Upload
Edit
Delete
Restore
Activate
Deactivate

Example:

Songs

[Search...................]

Title        Artist       Album       Status

Song 1       Artist 1     Album 1     Active
Song 2       Artist 2     Album 2     Active
Song 3       Artist 1     Album 3     Disabled
27. Soft deletion

Don't immediately destroy records.

Instead:

deleted_at

or:

is_deleted

Then:

Delete
   ↓
Soft Delete
   ↓
Audit Log

You can later:

Restore

This is much safer.

28. Storage management

Admin dashboard:

Storage

Total:
20 GB

Used:
14.2 GB

Available:
5.8 GB

Show:

Music        12.4 GB
Cover art     1.2 GB
Backups       0.6 GB
Other         0.0 GB
29. Analytics

Don't overcomplicate it initially.

Track:

Total plays
Most played songs
Most played artists
Most played albums
Listening time
Daily plays
Weekly plays
Monthly plays

Dashboard:

         Plays
          │
    █     │
    █     │       █
    █  █  │       █
 █  █  █  │   █   █
────────────────────
Mon Tue Wed Thu Fri
30. Recommendation system

Version 1:

Most Played
+
Liked Songs
+
Recently Played

Version 2:

Artist preferences
Album preferences
Genre preferences

Version 3:

Recommendation algorithm

You don't need ML initially.

31. Backend API structure

Use versioned APIs:

/api/v1
Auth
POST /auth/register
POST /auth/login
POST /auth/google
POST /auth/refresh
POST /auth/logout
GET  /auth/me
Users
GET   /users/me
PATCH /users/me
Songs
GET    /songs
GET    /songs/{id}
GET    /songs/{id}/stream
POST   /admin/songs
PATCH  /admin/songs/{id}
DELETE /admin/songs/{id}
Artists
GET /artists
GET /artists/{id}
POST /admin/artists
PATCH /admin/artists/{id}
DELETE /admin/artists/{id}
Albums
GET /albums
GET /albums/{id}
POST /admin/albums
PATCH /admin/albums/{id}
DELETE /admin/albums/{id}
Playlists
GET    /playlists
POST   /playlists
GET    /playlists/{id}
PATCH  /playlists/{id}
DELETE /playlists/{id}
POST   /playlists/{id}/songs
DELETE /playlists/{id}/songs/{song_id}
Library
POST   /songs/{id}/like
DELETE /songs/{id}/like
GET    /library/liked
GET    /library/recent
History
POST /history
GET  /history
Admin
GET /admin/dashboard
GET /admin/users
GET /admin/audit-logs
GET /admin/storage
32. Backend folder structure

I'd use:

edify/
│
├── backend/
│   │
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── logging.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── auth_identity.py
│   │   │   ├── refresh_token.py
│   │   │   ├── artist.py
│   │   │   ├── album.py
│   │   │   ├── song.py
│   │   │   ├── genre.py
│   │   │   ├── playlist.py
│   │   │   ├── history.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── schemas/
│   │   │
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── songs.py
│   │   │   ├── artists.py
│   │   │   ├── albums.py
│   │   │   ├── playlists.py
│   │   │   ├── library.py
│   │   │   ├── history.py
│   │   │   └── admin.py
│   │   │
│   │   ├── services/
│   │   │   ├── auth.py
│   │   │   ├── google.py
│   │   │   ├── music.py
│   │   │   ├── streaming.py
│   │   │   ├── storage.py
│   │   │   ├── playlist.py
│   │   │   ├── analytics.py
│   │   │   └── audit.py
│   │   │
│   │   └── dependencies/
│   │       ├── auth.py
│   │       └── permissions.py
│   │
│   ├── migrations/
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
│
├── android/
│
├── admin-web/
│
├── docker-compose.yml
└── README.md
33. Admin website structure
admin-web/
│
├── app/
│   ├── login/
│   ├── dashboard/
│   ├── songs/
│   ├── artists/
│   ├── albums/
│   ├── playlists/
│   ├── users/
│   ├── analytics/
│   ├── audit-logs/
│   ├── storage/
│   └── settings/
│
├── components/
│   ├── Sidebar
│   ├── Header
│   ├── DataTable
│   ├── MusicUploader
│   ├── AudioPreview
│   └── ConfirmDialog
│
├── lib/
│   ├── api.ts
│   ├── auth.ts
│   └── utils.ts
│
└── types/
34. Development phases

Now the important part: how you actually build it.

Don't try to build Android + backend + website simultaneously.

Phase 0 — Project setup
Day 1

☐ Create Git repository
☐ Backend repository structure
☐ Android project
☐ Admin web project
☐ Docker Compose
☐ PostgreSQL
☐ Redis
☐ Environment variables

At the end:

docker compose up

FastAPI       ✅
PostgreSQL    ✅
Redis         ✅
Admin Web     ✅
Phase 1 — Backend foundation
Day 2

☐ FastAPI architecture
☐ PostgreSQL connection
☐ SQLAlchemy 2.x
☐ Alembic
☐ Base model
☐ UUID IDs
☐ Error handling
☐ Logging
Phase 2 — Authentication
Day 3–4

☐ User model
☐ Email registration
☐ Password hashing
☐ Login
☐ JWT
☐ Refresh tokens
☐ Logout
☐ Google authentication
☐ User roles
☐ Authorization

Test:

Register
   ↓
Login
   ↓
Access Token
   ↓
Protected API
Phase 3 — Music database
Day 5–6

☐ Artist
☐ Album
☐ Genre
☐ Song
☐ Relationships
☐ CRUD APIs
☐ Database constraints
☐ Pagination
Phase 4 — Storage + Upload
Day 7–8

☐ File storage
☐ Upload API
☐ File validation
☐ Metadata extraction
☐ Cover extraction
☐ File naming
☐ Storage service
☐ Upload records
Phase 5 — Streaming
Day 9–10

☐ Streaming endpoint
☐ Authentication
☐ Range requests
☐ HTTP 206
☐ Seek support
☐ Error handling
☐ Large file handling

This is a particularly important backend phase.

Phase 6 — Admin website
Day 11–15

☐ Admin login
☐ Dashboard
☐ Song management
☐ Upload music
☐ Artist management
☐ Album management
☐ Genre management
☐ User management
☐ Storage dashboard
Phase 7 — Audit system
Day 16

☐ Audit model
☐ Audit service
☐ Record admin actions
☐ Record authentication events
☐ Audit API
☐ Audit dashboard
☐ Filters
☐ Search
Phase 8 — Android authentication
Day 17–18

☐ Android project architecture
☐ Login
☐ Registration
☐ Google login
☐ Token management
☐ Secure local storage
☐ Logout
Phase 9 — Android music
Day 19–23

☐ Home
☐ Songs
☐ Albums
☐ Artists
☐ Search
☐ Music details
☐ Media3
☐ Play
☐ Pause
☐ Seek
☐ Next
☐ Previous
Phase 10 — Background player
Day 24–25

☐ MediaSession
☐ Foreground service
☐ Notification
☐ Lock screen controls
☐ Queue
☐ Shuffle
☐ Repeat
Phase 11 — User features
Day 26–28

☐ Like songs
☐ Playlists
☐ Recently played
☐ History
☐ Library
☐ Profile
Phase 12 — Analytics
Day 29–30

☐ Play tracking
☐ Listening time
☐ Most played
☐ Top artists
☐ Top albums
☐ Daily statistics
Phase 13 — Recommendations
Day 31+

☐ Favorite artists
☐ Favorite genres
☐ Most played
☐ Similar songs
☐ Recommendation algorithm

ML can come much later.

35. Testing strategy

Don't leave testing until the end.

Backend:

pytest

Test:

Authentication
Permissions
Songs
Uploads
Streaming
Playlists
History
Audit logs

Example:

test_register()
test_login()
test_refresh_token()
test_google_login()
test_upload_song()
test_stream_song()
test_unauthorized_stream()
test_admin_delete_song()
test_audit_log_created()

Android:

Unit tests
Repository tests
ViewModel tests

Admin:

Component tests
API integration tests
36. Security architecture

Because this server exposes your personal music, security matters.

Implement:

HTTPS
JWT
Refresh-token rotation
Argon2 password hashing
RBAC
Rate limiting
File validation
Maximum upload size
Path traversal protection
CORS
Secure cookies where applicable
Input validation
Audit logs

Especially:

Never allow the client to submit an arbitrary filesystem path.

Bad:

{
  "file_path": "../../../secret.txt"
}

Instead, your backend generates the storage path.

37. ₹0 infrastructure

For your initial version:

Your PC
│
├── Docker
│
├── FastAPI
├── PostgreSQL
├── Redis
├── Caddy
│
└── Edify storage
      └── 1000 songs

Android / Public Access:

                     Internet (Cloudflare Tunnel / Tailscale)
PC (Localhost) ──────────────────────────────────────────────────► Friends' Phones

You can securely expose your local Caddy server to the internet for free using Cloudflare Tunnels or Tailscale. This allows your friends to install the Android app, log in, and stream music from anywhere without changing any core business logic.

You don't need:

AWS
Azure
GCP
Firebase
Supabase
Vercel Pro
Paid VPS
Paid database
Paid storage
SMS provider

for the initial personal system.

38. Backup strategy

This is important because your music files are valuable.

Have:

Primary
   │
   ├── Database
   └── Music

and:

Backup
   │
   ├── PostgreSQL backup
   └── Music backup

At minimum:

PostgreSQL
      ↓
pg_dump
      ↓
backup/

You can automate this later.

39. Final Edify architecture

After everything is complete:

                           🎵 EDIFY
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        📱 Android        ⚙️ FastAPI       🖥️ Admin
          App               Backend           Web
             │                │                │
             │                │                │
             └────────────────┼────────────────┘
                              │
                  ┌───────────┼───────────┐
                  │           │           │
                  ▼           ▼           ▼
             PostgreSQL     Redis       Storage
                  │                       │
                  │                       │
             ┌────┴─────┐             1000+
             │          │             Songs
          Users       Music
             │          │
             │          └── Artists
             │          └── Albums
             │          └── Songs
             │          └── Genres
             │
             ├── Playlists
             ├── Likes
             ├── History
             └── Audit Logs
🎯 The MVP I want you to build first

Don't start with recommendations, analytics, or a fancy dashboard.

Your first milestone should be:

                EDIFY V1
                   │
        ┌──────────┼──────────┐
        │          │          │
     Android    Backend     Admin
        │          │          │
      Login      Auth       Login
        │          │          │
       Home      Songs      Upload
        │          │          │
     Search     Storage    Manage
        │          │          │
      Player   Streaming   Audit
        │          │          │
        └──────────┼──────────┘
                   │
               PostgreSQL
                   │
              1000 Songs

Once that works end-to-end:

V2 → Likes + Playlists + History
V3 → Analytics + Audit improvements
V4 → Recommendations
V5 → Offline playback + advanced player

This is a substantial project, but it's very achievable if we build it incrementally. More importantly, it will teach you real backend concepts: authentication, authorization, file handling, HTTP streaming, database relationships, transactions, audit logging, background processing, caching, Docker, and Android API integration—all in one project.
