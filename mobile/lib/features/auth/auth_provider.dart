import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/legacy.dart';
import '../../core/network/api_client.dart';
import '../music/models/music_models.dart';

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

class AuthState {
  final User? user;
  final String? token;
  final bool isLoading;
  final String? error;
  final bool isGuest;

  AuthState({this.user, this.token, this.isLoading = false, this.error, this.isGuest = false});

  bool get isAuthenticated => (token != null && user != null) || isGuest;
}

class AuthNotifier extends StateNotifier<AuthState> {
  final ApiClient _apiClient;

  AuthNotifier(this._apiClient) : super(AuthState());

  Future<void> login(String email, String password) async {
    state = AuthState(isLoading: true);
    try {
      final res = await _apiClient.dio.post('/auth/login', data: {'email': email, 'password': password});
      final data = res.data['data'];
      final user = User.fromJson(data['user']);
      final token = data['tokens']['access_token'];

      _apiClient.setAuthToken(token);
      state = AuthState(user: user, token: token);
    } catch (e) {
      state = AuthState(error: 'Authentication failed. Please check credentials.');
    }
  }

  Future<void> register(String email, String password, String firstName) async {
    state = AuthState(isLoading: true);
    try {
      final res = await _apiClient.dio.post('/auth/register', data: {
        'email': email,
        'password': password,
        'first_name': firstName,
      });
      final data = res.data['data'];
      final user = User.fromJson(data['user']);
      final token = data['tokens']['access_token'];

      _apiClient.setAuthToken(token);
      state = AuthState(user: user, token: token);
    } catch (e) {
      state = AuthState(error: 'Registration failed. Try a different email.');
    }
  }

  void skipAuth() {
    _apiClient.setAuthToken(null);
    state = AuthState(
      user: User(
        id: 'guest',
        email: 'guest@edify.local',
        firstName: 'Guest',
        lastName: 'User',
        isAdmin: false,
      ),
      isGuest: true,
    );
  }

  void logout() {
    _apiClient.setAuthToken(null);
    state = AuthState();
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return AuthNotifier(apiClient);
});
