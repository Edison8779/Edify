import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/config/api_config.dart';
import '../auth/auth_provider.dart';
import '../music/providers/music_provider.dart';
import '../player/audio_player_handler.dart';
import '../player/player_screen.dart';
import '../search/search_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final songsAsync = ref.watch(songsProvider);
    final playerState = ref.watch(playerProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      body: SafeArea(
        child: Column(
          children: [
            // Top Bar
            Padding(
              padding: const EdgeInsets.all(20.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Good day, ${authState.user?.firstName ?? 'Listener'}',
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      const SizedBox(height: 2),
                      const Text('Explore your Edify catalog', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13)),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.logout, color: Color(0xFF94A3B8)),
                    onPressed: () {
                      ref.read(authProvider.notifier).logout();
                    },
                  ),
                ],
              ),
            ),

            // Content Body
            Expanded(
              child: IndexedStack(
                index: _currentIndex,
                children: [
                  // Home Catalog
                  songsAsync.when(
                    data: (songs) => songs.isEmpty
                        ? const Center(child: Text('No songs in catalog yet.', style: TextStyle(color: Color(0xFF94A3B8))))
                        : ListView.builder(
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            itemCount: songs.length,
                            itemBuilder: (context, idx) {
                              final song = songs[idx];
                              return ListTile(
                                  leading: Container(
                                    width: 48,
                                    height: 48,
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF1E293B),
                                      borderRadius: BorderRadius.circular(10),
                                      image: song.album?.coverUrl != null
                                          ? DecorationImage(
                                              image: NetworkImage('${ApiConfig.baseUrl}/media/${song.album!.coverUrl}'),
                                              fit: BoxFit.cover,
                                            )
                                          : null,
                                    ),
                                    child: song.album?.coverUrl == null
                                        ? const Icon(Icons.music_note, color: Colors.purpleAccent)
                                        : null,
                                  ),
                                title: Text(song.title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                subtitle: Text(song.artist?.name ?? 'Artist', style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                                trailing: IconButton(
                                  icon: const Icon(Icons.play_circle_fill, color: Colors.purpleAccent, size: 36),
                                  onPressed: () {
                                    ref.read(playerProvider.notifier).playSong(song, playlist: songs);
                                  },
                                ),
                              );
                            },
                          ),
                    loading: () => const Center(child: CircularProgressIndicator(color: Colors.purpleAccent)),
                    error: (err, stack) => Center(child: Text('Error loading songs: $err', style: const TextStyle(color: Colors.redAccent))),
                  ),
                  // Search View
                  const SearchScreen(),
                ],
              ),
            ),

            // Mini Player Bar
            if (playerState.currentSong != null)
              GestureDetector(
                onTap: () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => const PlayerScreen()));
                },
                child: Container(
                  height: 64,
                  margin: const EdgeInsets.all(12),
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.purple.withValues(alpha: 0.3)),
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: const Color(0xFF1E293B),
                          borderRadius: BorderRadius.circular(8),
                          image: playerState.currentSong?.album?.coverUrl != null
                              ? DecorationImage(
                                  image: NetworkImage('${ApiConfig.baseUrl}/media/${playerState.currentSong!.album!.coverUrl}'),
                                  fit: BoxFit.cover,
                                )
                              : null,
                        ),
                        child: playerState.currentSong?.album?.coverUrl == null
                            ? const Icon(Icons.music_note, color: Colors.purpleAccent, size: 20)
                            : null,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(playerState.currentSong!.title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                            Text(playerState.currentSong!.artist?.name ?? 'Artist', style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: Icon(playerState.isPlaying ? Icons.pause : Icons.play_arrow, color: Colors.white),
                        onPressed: () {
                          ref.read(playerProvider.notifier).togglePlayPause();
                        },
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (idx) => setState(() => _currentIndex = idx),
        backgroundColor: const Color(0xFF0F172A),
        selectedItemColor: Colors.purpleAccent,
        unselectedItemColor: const Color(0xFF94A3B8),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.search), label: 'Search'),
        ],
      ),
    );
  }
}
