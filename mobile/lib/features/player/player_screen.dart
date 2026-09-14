import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/config/api_config.dart';
import '../player/audio_player_handler.dart';

class PlayerScreen extends ConsumerWidget {
  const PlayerScreen({super.key});

  String _formatDuration(Duration d) {
    final minutes = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final playerState = ref.watch(playerProvider);
    final song = playerState.currentSong;

    if (song == null) {
      return Scaffold(
        backgroundColor: const Color(0xFF0F172A),
        appBar: AppBar(backgroundColor: Colors.transparent, elevation: 0),
        body: const Center(child: Text('No song selected', style: TextStyle(color: Colors.white))),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.keyboard_arrow_down, color: Colors.white, size: 32),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text('Now Playing', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
        centerTitle: true,
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.high_quality, color: Colors.purpleAccent),
            color: const Color(0xFF1E293B),
            onSelected: (quality) {
              ref.read(playerProvider.notifier).changeQuality(quality);
            },
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'original', child: Text('Original Master', style: TextStyle(color: Colors.white))),
              const PopupMenuItem(value: '256k', child: Text('High (256 kbps)', style: TextStyle(color: Colors.white))),
              const PopupMenuItem(value: '128k', child: Text('Medium (128 kbps)', style: TextStyle(color: Colors.white))),
              const PopupMenuItem(value: '64k', child: Text('Low (64 kbps)', style: TextStyle(color: Colors.white))),
            ],
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16),
          child: Column(
            children: [
              const Spacer(),
              // Cover Artwork
              Container(
                width: 280,
                height: 280,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(24),
                  color: const Color(0xFF1E293B),
                  image: song.album?.coverUrl != null
                      ? DecorationImage(
                          image: NetworkImage('${ApiConfig.baseUrl}/media/${song.album!.coverUrl}'),
                          fit: BoxFit.cover,
                        )
                      : null,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.purple.withValues(alpha: 0.3),
                      blurRadius: 30,
                      spreadRadius: 5,
                    ),
                  ],
                ),
                child: song.album?.coverUrl == null
                    ? const Center(
                        child: Icon(Icons.music_note, size: 100, color: Colors.purpleAccent),
                      )
                    : null,
              ),
              const Spacer(),
              // Song Info & Quality Badge
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          song.title,
                          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          song.artist?.name ?? 'Unknown Artist',
                          style: const TextStyle(fontSize: 16, color: Color(0xFF94A3B8)),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.purple.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.purple.withValues(alpha: 0.4)),
                    ),
                    child: Text(
                      playerState.quality.toUpperCase(),
                      style: const TextStyle(color: Colors.purpleAccent, fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              // Seek Slider
              SliderTheme(
                data: SliderThemeData(
                  trackHeight: 4,
                  activeTrackColor: Colors.purpleAccent,
                  inactiveTrackColor: const Color(0xFF334155),
                  thumbColor: Colors.purpleAccent,
                  overlayColor: Colors.purple.withValues(alpha: 0.2),
                ),
                child: Slider(
                  value: playerState.position.inSeconds.toDouble().clamp(0, playerState.duration.inSeconds.toDouble()),
                  max: playerState.duration.inSeconds.toDouble() > 0 ? playerState.duration.inSeconds.toDouble() : 1.0,
                  onChanged: (val) {
                    ref.read(playerProvider.notifier).seek(Duration(seconds: val.toInt()));
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 6),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(_formatDuration(playerState.position), style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                    Text(_formatDuration(playerState.duration), style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              // Playback Controls
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  IconButton(
                    icon: Icon(
                      Icons.shuffle,
                      size: 28,
                      color: playerState.isShuffleMode ? Colors.purpleAccent : Colors.white54,
                    ),
                    onPressed: () {
                      ref.read(playerProvider.notifier).toggleShuffle();
                    },
                  ),
                  IconButton(
                    icon: const Icon(Icons.skip_previous, size: 36, color: Colors.white),
                    onPressed: () {
                      ref.read(playerProvider.notifier).playPrevious();
                    },
                  ),
                  GestureDetector(
                    onTap: () {
                      ref.read(playerProvider.notifier).togglePlayPause();
                    },
                    child: Container(
                      width: 72,
                      height: 72,
                      decoration: const BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: LinearGradient(colors: [Color(0xFF9333EA), Color(0xFF6366F1)]),
                      ),
                      child: Icon(
                        playerState.isPlaying ? Icons.pause : Icons.play_arrow,
                        size: 40,
                        color: Colors.white,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.skip_next, size: 36, color: Colors.white),
                    onPressed: () {
                      ref.read(playerProvider.notifier).playNext();
                    },
                  ),
                  IconButton(
                    icon: Icon(
                      playerState.loopMode == LoopModeState.one ? Icons.repeat_one : Icons.repeat,
                      size: 28,
                      color: playerState.loopMode != LoopModeState.off ? Colors.purpleAccent : Colors.white54,
                    ),
                    onPressed: () {
                      ref.read(playerProvider.notifier).toggleLoopMode();
                    },
                  ),
                ],
              ),
              const Spacer(),
            ],
          ),
        ),
      ),
    );
  }
}
