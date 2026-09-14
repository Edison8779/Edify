import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/config/api_config.dart';
import '../music/providers/music_provider.dart';
import '../player/audio_player_handler.dart';

class SearchScreen extends ConsumerWidget {
  const SearchScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final searchResultsAsync = ref.watch(searchResultsProvider);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: Column(
        children: [
          TextField(
            onChanged: (val) {
              ref.read(searchQueryProvider.notifier).state = val;
            },
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: 'Search songs, artists, albums...',
              hintStyle: const TextStyle(color: Color(0xFF94A3B8)),
              prefixIcon: const Icon(Icons.search, color: Colors.purpleAccent),
              filled: true,
              fillColor: const Color(0xFF1E293B),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide.none),
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: searchResultsAsync.when(
              data: (songs) => songs.isEmpty
                  ? const Center(child: Text('Type to search music catalog...', style: TextStyle(color: Color(0xFF94A3B8))))
                  : ListView.builder(
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
                          subtitle: Text(song.artist?.name ?? 'Artist', style: const TextStyle(color: Color(0xFF94A3B8))),
                          onTap: () {
                            ref.read(playerProvider.notifier).playSong(song, playlist: songs);
                          },
                        );
                      },
                    ),
              loading: () => const Center(child: CircularProgressIndicator(color: Colors.purpleAccent)),
              error: (err, stack) => Center(child: Text('Search error: $err', style: const TextStyle(color: Colors.redAccent))),
            ),
          ),
        ],
      ),
    );
  }
}
