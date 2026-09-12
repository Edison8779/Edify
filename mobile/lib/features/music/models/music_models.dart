class User {
  final String id;
  final String email;
  final String? firstName;
  final String? lastName;
  final bool isAdmin;

  User({required this.id, required this.email, this.firstName, this.lastName, required this.isAdmin});

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      email: json['email'] ?? '',
      firstName: json['first_name'],
      lastName: json['last_name'],
      isAdmin: json['is_admin'] ?? false,
    );
  }
}

class Genre {
  final String id;
  final String name;
  final String slug;

  Genre({required this.id, required this.name, required this.slug});

  factory Genre.fromJson(Map<String, dynamic> json) {
    return Genre(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      slug: json['slug'] ?? '',
    );
  }
}

class Artist {
  final String id;
  final String name;
  final String? bio;
  final String? avatarUrl;

  Artist({required this.id, required this.name, this.bio, this.avatarUrl});

  factory Artist.fromJson(Map<String, dynamic> json) {
    return Artist(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      bio: json['bio'],
      avatarUrl: json['avatar_url'],
    );
  }
}

class Album {
  final String id;
  final String title;
  final String? coverUrl;
  final int? releaseYear;

  Album({required this.id, required this.title, this.coverUrl, this.releaseYear});

  factory Album.fromJson(Map<String, dynamic> json) {
    return Album(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      coverUrl: json['cover_url'],
      releaseYear: json['release_year'],
    );
  }
}

class SongVariant {
  final String id;
  final String quality;
  final String status;

  SongVariant({required this.id, required this.quality, required this.status});

  factory SongVariant.fromJson(Map<String, dynamic> json) {
    return SongVariant(
      id: json['id'] ?? '',
      quality: json['quality'] ?? '',
      status: json['status'] ?? '',
    );
  }
}

class Song {
  final String id;
  final String title;
  final Artist? artist;
  final Album? album;
  final Genre? genre;
  final int durationSeconds;
  final List<SongVariant> variants;

  Song({
    required this.id,
    required this.title,
    this.artist,
    this.album,
    this.genre,
    required this.durationSeconds,
    required this.variants,
  });

  factory Song.fromJson(Map<String, dynamic> json) {
    return Song(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      artist: json['artist'] != null ? Artist.fromJson(json['artist']) : null,
      album: json['album'] != null ? Album.fromJson(json['album']) : null,
      genre: json['genre'] != null ? Genre.fromJson(json['genre']) : null,
      durationSeconds: json['duration_seconds'] ?? 0,
      variants: (json['variants'] as List<dynamic>?)?.map((v) => SongVariant.fromJson(v)).toList() ?? [],
    );
  }
}
