import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:vatochito_chat/src/core/storage/token_storage.dart';

import '../constants/app_endpoints.dart';

class ApiClient {
  ApiClient({required this.tokenStorage}) {
    _initialize();
  }

  final TokenStorage tokenStorage;
  late final Dio client;

  void _initialize() {
    client = Dio(
      BaseOptions(
        baseUrl: AppEndpoints.apiBaseUrl,
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8',
        },
      ),
    );

    client.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await tokenStorage.getAccessToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            try {
              final newAccessToken = await _refreshToken();
              if (newAccessToken != null) {
                // Retry the original request with the new token
                error.requestOptions.headers['Authorization'] =
                    'Bearer $newAccessToken';
                final response =
                    await client.fetch<dynamic>(error.requestOptions);
                return handler.resolve(response);
              }
            } catch (e) {
              // If refresh fails, pass the error
            }
          }
          return handler.next(error);
        },
      ),
    );

    if (kDebugMode) {
      client.interceptors.add(
        LogInterceptor(
          requestBody: true,
          responseBody: true,
        ),
      );
    }
  }

  Future<String?> _refreshToken() async {
    try {
      final refreshToken = await tokenStorage.getRefreshToken();
      if (refreshToken == null) return null;

      final response = await Dio().post<dynamic>(
        AppEndpoints.refreshToken,
        data: {'refresh': refreshToken},
      );

      if (response.statusCode == 200 && response.data != null) {
        final newAccessToken = response.data!['access'] as String;
        await tokenStorage.saveAccessToken(newAccessToken);
        return newAccessToken;
      }
    } catch (e) {
      // Clear tokens if refresh fails
      await tokenStorage.clearTokens();
    }
    return null;
  }
}
