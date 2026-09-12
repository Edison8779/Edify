export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  avatar_url?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface Genre {
  id: string;
  name: string;
  slug: string;
  description?: string;
}

export interface Artist {
  id: string;
  name: string;
  bio?: string;
  avatar_url?: string;
  created_at: string;
}

export interface Album {
  id: string;
  title: string;
  artist_id: string;
  artist?: Artist;
  cover_url?: string;
  release_year?: number;
  created_at: string;
}

export interface SongVariant {
  id: string;
  song_id: string;
  quality: string;
  file_path: string;
  bitrate: number;
  codec: string;
  file_size_bytes: number;
  status: 'pending' | 'processing' | 'ready' | 'failed';
}

export interface Song {
  id: string;
  title: string;
  artist_id: string;
  album_id?: string;
  genre_id?: string;
  artist?: Artist;
  album?: Album;
  genre?: Genre;
  duration_seconds: number;
  track_number?: number;
  file_path: string;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  is_active: boolean;
  play_count: number;
  variants: SongVariant[];
  created_at: string;
}

export interface AdminStats {
  total_users: number;
  total_songs: number;
  total_artists: number;
  total_albums: number;
  total_genres: number;
  total_storage_bytes: number;
}

export interface AuditLog {
  id: string;
  actor_id?: string;
  action: string;
  target_type?: string;
  target_id?: string;
  ip_address?: string;
  user_agent?: string;
  status: string;
  details?: Record<string, any>;
  created_at: string;
}
