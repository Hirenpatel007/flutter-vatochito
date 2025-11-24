import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:vatochito_chat/src/core/constants/app_endpoints.dart';
import 'package:vatochito_chat/src/core/network/api_client.dart';
import 'package:vatochito_chat/src/core/storage/token_storage.dart';
import 'package:vatochito_chat/src/features/auth/data/models/user_model.dart';

class AuthRepository {
  AuthRepository({
    required ApiClient apiClient,
    required this.tokenStorage,
  }) : _client = apiClient.client;

  final Dio _client;
  final TokenStorage tokenStorage;

  Future<void> login(String username, String password) async {
    try {
      final response = await _client.post<dynamic>(
        AppEndpoints.login,
        data: {'username': username, 'password': password},
      );
      final accessToken = response.data!['access'] as String;
      final refreshToken = response.data!['refresh'] as String;
      await tokenStorage.saveTokens(
        accessToken: accessToken,
        refreshToken: refreshToken,
      );
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<void> register({
    required String username,
    required String password,
    String? email,
  }) async {
    try {
      await _client.post<dynamic>(
        AppEndpoints.register,
        data: {
          'username': username,
          'password': password,
          'password2': password,
          if (email != null) 'email': email,
        },
      );
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Exception _handleDioError(DioException e) {
    final data = e.response?.data;
    if (data != null && data is Map) {
      final messages = <String>[];
      for (final value in data.values) {
        if (value is List) {
          messages.addAll(value.map((v) => v.toString()));
        } else {
          messages.add(value.toString());
        }
      }
      if (messages.isNotEmpty) {
        return Exception(messages.join('\n'));
      }
    }
    return Exception(e.message ?? 'An error occurred');
  }

  Future<void> logout() async {
    await tokenStorage.clearTokens();
  }

  Future<UserModel?> getCurrentUser() async {
    try {
      final token = await tokenStorage.getAccessToken();
      if (token == null) return null;

      final response = await _client.get<dynamic>(AppEndpoints.profile);
      return UserModel.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      print('Error fetching current user: $e');
      return null;
    }
  }

  Future<UserModel?> uploadAvatar(String filePath) async {
    try {
      final formData = FormData.fromMap({
        'avatar': await MultipartFile.fromFile(filePath),
      });

      final response = await _client.post<dynamic>(
        '${AppEndpoints.profile}avatar/',
        data: formData,
      );
      return UserModel.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      print('Error uploading avatar: $e');
      return null;
    }
  }

  Future<bool> deleteAvatar() async {
    try {
      await _client.delete<dynamic>('${AppEndpoints.profile}avatar/');
      return true;
    } catch (e) {
      print('Error deleting avatar: $e');
      return false;
    }
  }

  Future<int?> getUserId() async {
    try {
      final token = await tokenStorage.getAccessToken();
      if (token == null) {
        print('DEBUG: getUserId - Token is null');
        return null;
      }
      final parts = token.split('.');
      if (parts.length != 3) {
        print('DEBUG: getUserId - Invalid token format');
        return null;
      }

      final normalized = base64Url.normalize(parts[1]);
      final payloadString = utf8.decode(base64Url.decode(normalized));
      final payload = json.decode(payloadString) as Map<String, dynamic>;

      final userId = payload['user_id'];
      print(
          'DEBUG: getUserId - Parsed userId: $userId (${userId.runtimeType})');

      if (userId is int) return userId;
      if (userId is String) return int.tryParse(userId);

      print('DEBUG: getUserId - Could not parse userId');
      return null;
    } catch (e, stack) {
      print('DEBUG: getUserId - Error: $e');
      print(stack);
      return null;
    }
  }
}
