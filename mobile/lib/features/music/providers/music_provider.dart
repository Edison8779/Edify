import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/legacy.dart';
import '../../auth/auth_provider.dart';
import '../models/music_models.dart';

final songsProvider = FutureProvider<List<Song>>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  final res = await apiClient.dio.get('/songs');
  final List items = res.data['data'];
  return items.map((json) => Song.fromJson(json)).toList();
});

final artistsProvider = FutureProvider<List<Artist>>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  final res = await apiClient.dio.get('/artists');
  final List items = res.data['data'];
  return items.map((json) => Artist.fromJson(json)).toList();
});

class SearchQueryNotifier extends StateNotifier<String> {
  SearchQueryNotifier() : super('');

  @override
  set state(String value) => super.state = value;
}

final searchQueryProvider = StateNotifierProvider<SearchQueryNotifier, String>((ref) {
  return SearchQueryNotifier();
});

final searchResultsProvider = FutureProvider<List<Song>>((ref) async {
  final query = ref.watch(searchQueryProvider);
  if (query.trim().isEmpty) return [];

  final apiClient = ref.watch(apiClientProvider);
  final res = await apiClient.dio.get('/search', queryParameters: {'q': query});
  final List songsList = res.data['data']['songs'] ?? [];
  return songsList.map((json) => Song.fromJson(json)).toList();
});
