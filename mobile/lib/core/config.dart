/// Edify — Core configuration.
///
/// App-wide constants, API URLs, and environment-specific settings.

class AppConfig {
  AppConfig._();

  static const String appName = 'Edify';
  static const String apiBaseUrl = 'http://10.0.2.2:8000'; // Android emulator → host
  static const String apiPrefix = '/api/v1';

  static String get apiUrl => '$apiBaseUrl$apiPrefix';
}
