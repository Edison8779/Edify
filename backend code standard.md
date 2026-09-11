For Edify, I would establish the engineering standard before writing the actual features. That prevents the project from becoming a collection of endpoints that are difficult to maintain later.

Below is the standard I recommend for a production-grade Edify system.

🎵 Edify — Production Engineering Standard
1. System Architecture

Edify has three clients/components:

                         EDIFY SYSTEM
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        📱 Android       🖥️ Admin Web      ⚙️ Backend
          Client            Client           FastAPI
             │                │                │
             └────────────────┼────────────────┘
                              │
                           HTTPS
                              │
                              ▼
                       ┌─────────────┐
                       │   Caddy     │
                       │ Reverse     │
                       │ Proxy       │
                       └──────┬──────┘
                              │
                              ▼
                       ┌─────────────┐
                       │   FastAPI   │
                       │     API     │
                       └──────┬──────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        PostgreSQL          Redis          File Storage
             │                │                │
             │                │             Music
             │                │             Covers
             │                │
             └────────────────┴────────────────┐
                                               │
                                         Background Jobs

The backend should not become responsible for everything.

Keep responsibilities separated.

2. Backend Architecture

Use a modular monolith first.

Do not start with microservices.

FastAPI
   │
   ├── Auth
   ├── Users
   ├── Music
   ├── Albums
   ├── Artists
   ├── Playlists
   ├── Library
   ├── Streaming
   ├── Analytics
   └── Admin

This gives you production-quality separation without the complexity of distributed systems.

3. Recommended Folder Structure
backend/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   │
│   ├── api/
│   │   ├── router.py
│   │   │
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── songs.py
│   │       ├── artists.py
│   │       ├── albums.py
│   │       ├── playlists.py
│   │       ├── library.py
│   │       ├── history.py
│   │       ├── search.py
│   │       └── admin.py
│   │
│   ├── models/
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── auth_identity.py
│   │   ├── refresh_token.py
│   │   ├── song.py
│   │   ├── artist.py
│   │   ├── album.py
│   │   ├── genre.py
│   │   ├── playlist.py
│   │   ├── history.py
│   │   └── audit_log.py
│   │
│   ├── schemas/
│   │   ├── common.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── song.py
│   │   ├── artist.py
│   │   ├── album.py
│   │   ├── playlist.py
│   │   └── admin.py
│   │
│   ├── services/
│   │   ├── auth/
│   │   │   ├── service.py
│   │   │   ├── google.py
│   │   │   └── password.py
│   │   │
│   │   ├── music/
│   │   │   ├── service.py
│   │   │   ├── metadata.py
│   │   │   └── storage.py
│   │   │
│   │   ├── streaming/
│   │   │   └── service.py
│   │   │
│   │   ├── playlist/
│   │   │   └── service.py
│   │   │
│   │   ├── analytics/
│   │   │   └── service.py
│   │   │
│   │   └── audit/
│   │       └── service.py
│   │
│   ├── repositories/
│   │   ├── user.py
│   │   ├── song.py
│   │   ├── album.py
│   │   ├── artist.py
│   │   ├── playlist.py
│   │   └── audit.py
│   │
│   ├── dependencies/
│   │   ├── auth.py
│   │   ├── database.py
│   │   └── permissions.py
│   │
│   └── utils/
│       ├── pagination.py
│       ├── files.py
│       └── datetime.py
│
├── migrations/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── api/
│
├── scripts/
│
├── docker/
│
├── .env.example
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
4. Layer Responsibilities

This is extremely important.

Router

Router handles:

HTTP
 ↓
Validation
 ↓
Authentication
 ↓
Call service
 ↓
Return response

Router should not contain business logic.

Bad:

@router.post("/songs")
async def create_song(...):
    # 100 lines of business logic

Good:

@router.post(...)
async def create_song(
    data: SongCreate,
    service: SongService = Depends(get_song_service),
):
    return await service.create_song(data)
5. Service Layer

The service contains business rules.

Example:

SongRouter
    ↓
SongService
    ↓
SongRepository
    ↓
PostgreSQL

Service:

Create song
    │
    ├── Validate metadata
    ├── Validate permissions
    ├── Save file
    ├── Create DB record
    └── Create audit event
6. Repository Layer

Repositories deal with persistence.

Repository
    ↓
SQLAlchemy
    ↓
PostgreSQL

Don't put business rules inside repositories.

Bad:

SongRepository.create()
   ├── check admin
   ├── send email
   ├── upload file
   └── create audit log

Repository should primarily deal with database operations.

7. API Design Standard

Use:

/api/v1/...

Example:

/api/v1/auth/login
/api/v1/songs
/api/v1/songs/{song_id}
/api/v1/albums
/api/v1/artists
/api/v1/playlists

Admin:

/api/v1/admin/songs
/api/v1/admin/users
/api/v1/admin/audit-logs
8. HTTP Methods

Use HTTP semantics properly.

GET

Retrieve:

GET /api/v1/songs
POST

Create:

POST /api/v1/playlists
PATCH

Partial update:

PATCH /api/v1/songs/{id}
DELETE

Delete:

DELETE /api/v1/playlists/{id}

Don't use:

POST /deleteSong
POST /updateSong
9. Resource Naming

Use plural nouns.

Good:

/songs
/artists
/albums
/playlists
/users

Not:

/getSongs
/getArtist
/createPlaylist
/deleteUser
10. API Response Standard

Don't randomly return different formats.

Use a predictable structure.

Success:

{
  "data": {
    "id": "..."
  }
}

List:

{
  "data": [],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 120
  }
}
11. Pagination

Never return thousands of records by default.

Use:

GET /api/v1/songs?page=1&page_size=20

Response:

{
  "data": [],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 1000,
    "total_pages": 50
  }
}

Set a maximum:

page_size <= 100
12. Filtering

Example:

GET /api/v1/songs?artist_id=123

Multiple:

GET /api/v1/songs?artist_id=123&album_id=456

Sorting:

GET /api/v1/songs?sort=-created_at
13. Search
GET /api/v1/search?q=believer

Response:

{
  "data": {
    "songs": [],
    "artists": [],
    "albums": []
  }
}
14. Error Handling

This is one of the most important production standards.

Never return random errors like:

{
  "error": "something went wrong"
}

Use a standard error format.

{
  "error": {
    "code": "SONG_NOT_FOUND",
    "message": "The requested song does not exist.",
    "request_id": "req_01..."
  }
}
15. Error Codes

Create application-level error codes.

Example:

AUTH_INVALID_CREDENTIALS
AUTH_TOKEN_EXPIRED
AUTH_TOKEN_INVALID
AUTH_ACCOUNT_DISABLED

USER_NOT_FOUND
USER_ALREADY_EXISTS

SONG_NOT_FOUND
SONG_ALREADY_EXISTS
SONG_INACTIVE

ALBUM_NOT_FOUND
ARTIST_NOT_FOUND

PLAYLIST_NOT_FOUND
PLAYLIST_SONG_ALREADY_EXISTS

FILE_TOO_LARGE
INVALID_FILE_TYPE
UPLOAD_FAILED

PERMISSION_DENIED

INTERNAL_SERVER_ERROR

These codes are useful for both Android and Admin Web.

16. HTTP Status Codes

Use them correctly.

200 OK
201 Created
204 No Content

400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
429 Too Many Requests

500 Internal Server Error
503 Service Unavailable

Example:

Wrong password:

401
AUTH_INVALID_CREDENTIALS

User authenticated but isn't admin:

403
PERMISSION_DENIED

Song doesn't exist:

404
SONG_NOT_FOUND

Duplicate email:

409
USER_ALREADY_EXISTS
17. Global Exception Handler

Don't write:

try:
    ...
except Exception:
    return {"error": "..."}

inside every endpoint.

Instead:

Application
     │
     ▼
Exception
     │
     ▼
Global Exception Handler
     │
     ├── Log
     ├── Generate request ID
     └── Standard response
18. Never expose internal errors

Bad:

{
  "error": "psycopg2.errors.UniqueViolation: ..."
}

The client should never see:

SQL queries
database errors
stack traces
filesystem paths
internal service details

Production:

{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred.",
    "request_id": "req_123"
  }
}

The actual exception goes into your server logs.

19. Request ID

Every request gets a unique ID.

Request
   ↓
req_8f2a91
   ↓
Router
   ↓
Service
   ↓
Database

Log:

[req_8f2a91] POST /songs
[req_8f2a91] user=123
[req_8f2a91] song created
[req_8f2a91] 201

If something breaks, you can search:

req_8f2a91

and find the entire request lifecycle.

20. Logging Standard

Use structured logs.

Instead of:

print("song uploaded")

use logging.

Conceptually:

{
  "level": "INFO",
  "event": "song_uploaded",
  "user_id": "...",
  "song_id": "...",
  "request_id": "...",
  "timestamp": "..."
}

Never log:

passwords
access tokens
refresh tokens
Google tokens
private information
21. Authentication Standard

Edify:

Google OAuth
+
Email/password

Password:

Password
   ↓
Argon2id
   ↓
Hash

Never store plaintext passwords.

22. JWT Standard

Use:

Access Token
+
Refresh Token

Access token:

short-lived

Refresh token:

long-lived

And store refresh-token state server-side so you can revoke sessions.

23. Authorization

Create dependencies:

get_current_user()
require_authenticated_user()
require_admin()

Example:

GET /songs
     ↓
Authenticated user

POST /admin/songs
     ↓
Authenticated user
     ↓
ADMIN?
     ↓
YES → continue
NO  → 403
24. File Upload Security

This is extremely important for Edify.

Never trust:

filename
extension
MIME type
client-provided size

Validate:

File size
Actual file type
Audio format
Filename
Metadata

Allow only what you need:

.mp3
.flac
.m4a

for example.

Set:

MAX_UPLOAD_SIZE
25. Never use the original filename as storage path

Bad:

/music/{filename}

Better:

/music/{song_uuid}.{extension}

Example:

music/
    0193d1e3-....mp3

Database:

song_id
storage_key
26. Streaming Architecture

Streaming gets its own service.

Android
   │
   ▼
StreamingRouter
   │
   ▼
StreamingService
   │
   ├── authenticate
   ├── authorize
   ├── resolve storage
   └── stream
          │
          ▼
      File Storage

Support:

Range
206 Partial Content
Content-Length
Content-Type
Accept-Ranges
Content-Range

This is essential for seeking.

27. Database Transactions

Whenever multiple database changes must succeed together:

Transaction

Example:

Create playlist
      │
      ├── playlist row
      └── audit row

Either:

both succeed

or:

both rollback

Don't leave partially completed operations.

28. Audit System

Every important action should produce an audit event.

Admin
 │
 ▼
Upload song
 │
 ├── DB operation
 │
 └── Audit event

Audit model:

audit_logs
──────────────────────────
id
actor_user_id

action
entity_type
entity_id

old_values
new_values

request_id
ip_address
user_agent

created_at

Example:

{
  "action": "SONG_UPDATED",
  "entity_type": "song",
  "entity_id": "...",
  "old_values": {
    "title": "Old Title"
  },
  "new_values": {
    "title": "New Title"
  }
}

Audit logs should be append-only.

Admins shouldn't casually modify historical audit records.

29. Soft Delete

For important entities:

deleted_at

Instead of:

DELETE FROM songs;

immediately.

Flow:

Delete
 ↓
deleted_at = now()
 ↓
Audit
 ↓
Hidden from normal queries

Then admin can:

Restore
30. Database Standard

Use modern SQLAlchemy 2.x style.

For example:

class Song(Base):
    __tablename__ = "songs"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

Avoid old-style patterns.

Use:

Mapped[]
mapped_column()
relationship()
31. Database Constraints

Don't rely only on Python validation.

Database should also protect integrity.

Examples:

email UNIQUE
username UNIQUE
foreign keys
NOT NULL
CHECK constraints
indexes
32. Indexes

Index fields used frequently for:

Search
Foreign keys
Sorting
Filtering
Authentication

For example:

users.email
users.username

songs.artist_id
songs.album_id

play_history.user_id
play_history.played_at

audit_logs.actor_user_id
audit_logs.created_at

Don't blindly index every column.

33. Redis

Don't introduce Redis everywhere.

Use it for things such as:

Rate limiting
Caching
Temporary OTP/session data if needed
Frequently accessed metadata

Example:

GET /home
     ↓
Redis cache
     │
 ┌───┴───┐
 │       │
Hit     Miss
 │       │
 ▼       ▼
Return  PostgreSQL
34. Background Jobs

Some operations shouldn't block HTTP requests.

For example:

Upload song
    ↓
Save file
    ↓
Return
    ↓
Background processing
    ├── Extract metadata
    ├── Generate waveform
    ├── Generate thumbnails
    └── Analyze audio

For V1, keep this simple. You can add a proper worker system once you actually need it.

35. Configuration

Never hard-code secrets.

Bad:

SECRET_KEY = "abc123"

Use environment variables:

DATABASE_URL
REDIS_URL
JWT_SECRET_KEY
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
STORAGE_PATH

.env:

DATABASE_URL=...
REDIS_URL=...
JWT_SECRET_KEY=...

Commit only:

.env.example

Never:

.env
36. API Versioning

Start:

/api/v1

Later:

/api/v2

Don't break Android clients unexpectedly.

37. Documentation

FastAPI automatically gives you OpenAPI documentation.

Maintain:

/api/docs
/api/redoc

But documentation should also explain:

Authentication
Error codes
Pagination
Rate limits
Streaming
Admin permissions
38. Android API contract

Android should never depend on backend implementation details.

It only knows:

HTTP API
JSON
HTTP status
error code

Example:

{
  "error": {
    "code": "SONG_NOT_FOUND",
    "message": "Song not found.",
    "request_id": "req_123"
  }
}

Android can map:

SONG_NOT_FOUND
    ↓
"Song is no longer available"
39. Admin Web API contract

Same API.

Admin Web
    ↓
FastAPI

Don't create separate backend logic for Android and Web.

Use:

Same domain services
Same database
Different permissions
40. Testing Standard

Minimum:

Unit tests
Integration tests
API tests
Unit
Password hashing
JWT
Playlist logic
Metadata parsing
Pagination
Integration
PostgreSQL
Repositories
Transactions
Storage
API
POST /auth/login
GET /songs
POST /admin/songs
GET /songs/{id}/stream
41. Test Pyramid
              /\
             /  \
            / E2E\
           /------\
          / API    \
         /----------\
        / Integration\
       /--------------\
      /   Unit Tests   \
     /__________________\

Most tests should be unit tests.

42. Docker

Development:

docker compose up

Services:

edify-api
postgres
redis
caddy

Later:

edify-worker
43. Deployment

Your initial deployment:

Your PC / Home Server
        │
        ├── Docker
        │
        ├── Caddy
        │
        ├── FastAPI
        │
        ├── PostgreSQL
        │
        ├── Redis
        │
        └── Music Storage

For local network:

Phone
  │
 Wi-Fi
  │
Home Server

No cloud required.

44. Git Standards

Branches:

main
develop
feature/auth
feature/music-upload
feature/streaming
feature/playlists
fix/streaming-range

Commit messages:

feat: add Google authentication
feat: implement song upload
feat: add range-based streaming

fix: handle expired refresh tokens
fix: prevent duplicate playlist songs

refactor: extract streaming service

test: add playlist service tests
docs: update API authentication docs
45. Code Quality

Use:

Ruff
Pyright
pytest
pre-commit

Keep:

Type hints
Small functions
Explicit dependencies
Meaningful names
No unnecessary abstractions

Avoid:

God classes
God services
1000-line routers
Global mutable state
Hidden database queries
Business logic in schemas
Business logic in routers
46. Important architectural rule

The flow should generally look like:

HTTP Request
     │
     ▼
Router
     │
     ▼
Schema validation
     │
     ▼
Authentication / Authorization
     │
     ▼
Service
     │
     ▼
Repository
     │
     ▼
Database

For storage:

Service
   │
   ▼
Storage abstraction
   │
   ▼
Filesystem / Object Storage

For external providers:

Service
   │
   ▼
Provider abstraction
   │
   ├── Google
   └── Future provider

This prevents vendor-specific code from spreading everywhere.

47. Edify API domains

I'd officially define these domains:

AUTH
USER
MUSIC
ARTIST
ALBUM
PLAYLIST
LIBRARY
SEARCH
STREAMING
HISTORY
ANALYTICS
ADMIN
AUDIT
STORAGE
48. Production request flow

Example: user plays a song.

Android
   │
   │ GET /api/v1/songs/{id}/stream
   ▼
Caddy
   │
   ▼
FastAPI
   │
   ├── Request ID
   ├── JWT validation
   ├── User authorization
   ├── Song lookup
   └── Streaming service
              │
              ▼
          File Storage
              │
              ▼
        HTTP 206 stream
              │
              ▼
            Media3
              │
              ▼
             🔊
49. Production upload flow
Admin Web
   │
   │ multipart/form-data
   ▼
FastAPI
   │
   ├── Authenticate
   ├── Check ADMIN
   ├── Validate file
   ├── Generate storage key
   ├── Save file
   ├── Extract metadata
   ├── DB transaction
   ├── Audit event
   └── Response
50. Production error flow
                 Exception
                     │
             ┌───────┴────────┐
             │                │
        Expected          Unexpected
             │                │
             ▼                ▼
      App Exception      Internal Error
             │                │
             └───────┬────────┘
                     ▼
              Global Handler
                     │
             ┌───────┴────────┐
             ▼                ▼
           Logs          API Response
                              │
                              ▼
                    Standard Error JSON
51. The most important rule for Edify

Don't prematurely make it a distributed system.

❌ Don't do this initially:
Auth Microservice
Music Microservice
Streaming Microservice
Playlist Microservice
Analytics Microservice
User Microservice
Search Microservice

That's unnecessary for your project.

✅ Do this:
              FastAPI
                 │
       ┌─────────┼─────────┐
       │         │         │
      Auth     Music    Playlists
       │         │         │
       └─────────┼─────────┘
                 │
             PostgreSQL

Modular monolith now → split services only when there is a real reason.

52. Edify development order

This is the order I'd follow strictly:

01. Project foundation
        ↓
02. Database
        ↓
03. Authentication
        ↓
04. Authorization/Roles
        ↓
05. Music catalog
        ↓
06. File storage
        ↓
07. Admin upload
        ↓
08. Streaming
        ↓
09. Android authentication
        ↓
10. Android music browsing
        ↓
11. Android Media3 player
        ↓
12. Playlists
        ↓
13. Likes + Library
        ↓
14. History
        ↓
15. Audit system
        ↓
16. Analytics
        ↓
17. Search improvements
        ↓
18. Recommendations
        ↓
19. Production hardening
53. Definition of "production grade" for Edify

Before we call Edify V1 production-ready, every feature should satisfy:

☐ Type hints
☐ Input validation
☐ Authentication
☐ Authorization
☐ Proper HTTP status codes
☐ Standard error response
☐ Request ID
☐ Structured logging
☐ Database transaction where needed
☐ Audit event where appropriate
☐ Unit tests
☐ Integration tests
☐ API tests
☐ Documentation
☐ No secrets in source code
☐ No sensitive data in logs
☐ Proper database constraints
☐ Pagination
☐ Rate limiting where needed
☐ Graceful failure
