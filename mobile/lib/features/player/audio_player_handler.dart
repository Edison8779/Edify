import 'dart:io';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/legacy.dart';
import 'package:just_audio/just_audio.dart';
import '../../core/config/api_config.dart';
import '../music/models/music_models.dart';

enum LoopModeState { off, all, one }

class PlayerStateModel {
  final Song? currentSong;
  final bool isPlaying;
  final String quality; // 'original', '256k', '128k', '64k'
  final Duration position;
  final Duration duration;
  final List<Song> playlist;
  final bool isShuffleMode;
  final LoopModeState loopMode;

  PlayerStateModel({
    this.currentSong,
    this.isPlaying = false,
    this.quality = '128k',
    this.position = Duration.zero,
    this.duration = Duration.zero,
    this.playlist = const [],
    this.isShuffleMode = false,
    this.loopMode = LoopModeState.off,
  });

  PlayerStateModel copyWith({
    Song? currentSong,
    bool? isPlaying,
    String? quality,
    Duration? position,
    Duration? duration,
    List<Song>? playlist,
    bool? isShuffleMode,
    LoopModeState? loopMode,
  }) {
    return PlayerStateModel(
      currentSong: currentSong ?? this.currentSong,
      isPlaying: isPlaying ?? this.isPlaying,
      quality: quality ?? this.quality,
      position: position ?? this.position,
      duration: duration ?? this.duration,
      playlist: playlist ?? this.playlist,
      isShuffleMode: isShuffleMode ?? this.isShuffleMode,
      loopMode: loopMode ?? this.loopMode,
    );
  }
}

class AudioPlayerNotifier extends StateNotifier<PlayerStateModel> {
  final AudioPlayer _player = AudioPlayer();
  final Random _random = Random();

  AudioPlayerNotifier() : super(PlayerStateModel()) {
    _player.playerStateStream.listen((stateData) {
      state = state.copyWith(isPlaying: stateData.playing);
      if (stateData.processingState == ProcessingState.completed) {
        if (state.loopMode == LoopModeState.one) {
          _player.seek(Duration.zero);
          _player.play();
        } else {
          playNext();
        }
      }
    });

    _player.positionStream.listen((pos) {
      state = state.copyWith(position: pos);
    });

    _player.durationStream.listen((dur) {
      if (dur != null) {
        state = state.copyWith(duration: dur);
      }
    });
  }

  Future<void> playSong(Song song, {String? quality, List<Song>? playlist}) async {
    final q = quality ?? state.quality;
    final pl = playlist ?? (state.playlist.isEmpty ? [song] : state.playlist);
    
    String baseUrl = ApiConfig.localUrl;
    if (!kIsWeb && Platform.isAndroid) {
      baseUrl = ApiConfig.baseUrl;
    }
    final streamUrl = '$baseUrl/songs/${song.id}/stream?quality=$q';

    state = state.copyWith(currentSong: song, quality: q, playlist: pl);

    try {
      await _player.setUrl(streamUrl);
      await _player.play();
    } catch (e) {
      debugPrint('Error playing song: $e');
    }
  }

  void playNext() {
    if (state.playlist.isEmpty || state.currentSong == null) return;
    
    if (state.isShuffleMode) {
      int nextIdx = _random.nextInt(state.playlist.length);
      playSong(state.playlist[nextIdx]);
      return;
    }

    int currentIdx = state.playlist.indexWhere((s) => s.id == state.currentSong!.id);
    if (currentIdx == -1) return;

    if (currentIdx + 1 < state.playlist.length) {
      playSong(state.playlist[currentIdx + 1]);
    } else if (state.loopMode == LoopModeState.all) {
      playSong(state.playlist.first);
    } else {
      _player.stop();
      _player.seek(Duration.zero);
    }
  }

  void playPrevious() {
    if (state.playlist.isEmpty || state.currentSong == null) return;

    if (state.position.inSeconds > 3) {
      _player.seek(Duration.zero);
      return;
    }

    if (state.isShuffleMode) {
      int nextIdx = _random.nextInt(state.playlist.length);
      playSong(state.playlist[nextIdx]);
      return;
    }

    int currentIdx = state.playlist.indexWhere((s) => s.id == state.currentSong!.id);
    if (currentIdx == -1) return;

    if (currentIdx - 1 >= 0) {
      playSong(state.playlist[currentIdx - 1]);
    } else if (state.loopMode == LoopModeState.all) {
      playSong(state.playlist.last);
    } else {
      _player.seek(Duration.zero);
    }
  }

  void toggleShuffle() {
    state = state.copyWith(isShuffleMode: !state.isShuffleMode);
  }

  void toggleLoopMode() {
    LoopModeState nextMode;
    if (state.loopMode == LoopModeState.off) {
      nextMode = LoopModeState.all;
    } else if (state.loopMode == LoopModeState.all) {
      nextMode = LoopModeState.one;
    } else {
      nextMode = LoopModeState.off;
    }
    state = state.copyWith(loopMode: nextMode);
  }

  void togglePlayPause() {
    if (_player.playing) {
      _player.pause();
    } else {
      _player.play();
    }
  }

  void seek(Duration position) {
    _player.seek(position);
  }

  void changeQuality(String quality) {
    if (state.currentSong != null) {
      playSong(state.currentSong!, quality: quality);
    } else {
      state = state.copyWith(quality: quality);
    }
  }

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }
}

final playerProvider = StateNotifierProvider<AudioPlayerNotifier, PlayerStateModel>((ref) {
  return AudioPlayerNotifier();
});
