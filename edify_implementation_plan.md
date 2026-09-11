# Edify Ecosystem Implementation Plan

This plan details the phase-wise implementation of the complete Edify ecosystem, comprising the FastAPI backend, the React/Next.js Admin Dashboard, and the Android (Kotlin/Compose) mobile application. The approach breaks down the architecture into manageable, incremental phases, prioritizing a functional Minimum Viable Product (MVP) before layering on advanced features.

> [!IMPORTANT]
> ## User Review Required
> Please review the phased breakdown below. If you approve, we will begin execution with **Phase 0** and **Phase 1**, focusing on setting up the project infrastructure and the backend foundation. 

> [!NOTE]
> ## Open Questions
> 1. **Repository Structure**: Would you prefer a monorepo approach (all three projects in one folder, e.g., `d:\Edify\`) or separate repositories for the Backend, Admin Web, and Android App? A monorepo is often easier to manage for solo projects.
> 2. **Authentication Flow**: Should we start with standard Email/Password first and add Google OAuth in a later sub-phase, or tackle both simultaneously during Phase 1?

---

## Proposed Implementation Phases

### Phase 0: Project Setup & Infrastructure
*Establishing the foundational environment.*
- **Version Control**: Initialize Git repository.
- **Project Structure**: Scaffold folders for `backend`, `admin-web`, and `android`.
- **Infrastructure**: Create `docker-compose.yml` to spin up PostgreSQL and Redis.
- **Environment**: Define `.env` templates for configuration variables.

### Phase 1: Backend Foundation & Authentication
*Building the core FastAPI server and secure access.*
- **Core setup**: FastAPI app, CORS, error handling, logging.
- **Database setup**: SQLAlchemy 2.x, Alembic migrations, PostgreSQL connection.
- **Models**: Implement `User`, `AuthIdentity`, `RefreshToken`.
- **APIs**: Registration, Login, JWT issuing, Refresh Tokens, Logout.

### Phase 2: Music Database & Storage 
*Handling the core entities: artists, albums, and songs.*
- **Models**: Implement `Artist`, `Album`, `Song`, and `Genre` models.
- **Storage**: Set up local file storage structure for MP3/FLAC and cover art.
- **APIs**: Implement CRUD endpoints for music metadata.
- **Upload Flow**: Build the secure upload API, including file validation and automatic ID3 metadata extraction.

### Phase 3: Admin Website Foundation
*Creating the control panel.*
- **Setup**: Initialize Next.js with Tailwind CSS and TypeScript.
- **Auth**: Implement Admin Login and secure routing.
- **Dashboard**: Create the main dashboard layout and sidebar.
- **Music Management**: Build the "Upload Music" interface and basic data tables to list songs/artists/albums.

### Phase 4: Streaming & Core Android App
*Getting the music to play.*
- **Backend**: Implement HTTP Range Requests (206 Partial Content) streaming endpoint for smooth seeking.
- **Android Setup**: Scaffold Android project with Jetpack Compose, Hilt, Retrofit.
- **Android Auth**: Implement login screens and token storage.
- **Android Player**: Integrate `Media3/ExoPlayer` and build the basic UI for browsing and playing music.

### Phase 5: Persistent Background Player
*Ensuring uninterrupted playback on Android.*
- **Android Services**: Implement `MediaSession` and Foreground Services.
- **System Integration**: Handle notification controls, lock screen widgets, and audio focus.
- **Player Features**: Implement queue, shuffle, and repeat functionalities.

### Phase 6: User Engagement & Library Features
*Personalizing the experience.*
- **Models & APIs**: Implement `Playlist`, `PlaylistSong`, `LikedSong`, and `PlayHistory` in the backend.
- **Android UI**: Build the "Library" section, enabling users to like songs, create playlists, and view recently played tracks.
- **Admin**: Add playlist and user management to the Admin Dashboard.

### Phase 7: Audit System & Analytics
*Tracking and reporting.*
- **Audit Logging**: Implement the `AuditLog` model and middleware to capture all admin and critical user actions.
- **Admin Audit UI**: Build the Audit Logs viewer in the Admin Dashboard with filters.
- **Analytics**: Track listening time, most played songs, and aggregate statistics.
- **Admin Stats UI**: Enhance the main dashboard with analytics charts.

### Phase 8: Recommendations & Polish
*Advanced features and final touch-ups.*
- **Recommendations**: Implement a basic recommendation algorithm (V1: most played + liked + recent) via a new `/home` endpoint.
- **Android Home Screen**: Display personalized recommendations.
- **Optimization**: Final performance reviews, query optimizations, and final UI/UX polish across the web and mobile apps.

---

## Verification Plan

### Automated Tests
- **Backend**: We will write `pytest` suites for each endpoint as we build them, ensuring authentication, permissions, streaming integrity, and database operations function correctly.

### Manual Verification
- We will test the `docker compose` setup to ensure all containers start cleanly.
- After completing Phase 4, we will manually test the end-to-end flow: Uploading a song via the Admin panel -> Logging into the Android app -> Streaming the song.
