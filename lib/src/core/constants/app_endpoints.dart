import 'dart:io';

import 'package:flutter/foundation.dart';

class AppEndpoints {
  const AppEndpoints._();

  // Production mode flag - true for release, false for debug
  static const bool _isProduction = bool.fromEnvironment('dart.vm.product');

  static String get baseUrl {
    if (_isProduction) {
      // Production - Render backend URL
      return 'https://flutter-vatochito.onrender.com';
    }
    // Development - Local server
    if (kIsWeb) return 'http://localhost:8000';
    if (Platform.isAndroid) return 'http://10.0.2.2:8000';
    return 'http://localhost:8000';
  }

  static String get apiBaseUrl => '$baseUrl/api';

  static String get wsBaseUrl {
    if (_isProduction) {
      // Production - Secure WebSocket
      return 'wss://flutter-vatochito.onrender.com';
    }
    // Development - Local WebSocket
    if (kIsWeb) return 'ws://localhost:8000';
    if (Platform.isAndroid) return 'ws://10.0.2.2:8000';
    return 'ws://localhost:8000';
  }

  // Auth
  static const String login = '/auth/login/';
  static const String register = '/auth/register/';
  static const String refreshToken = '/auth/refresh/';
  static const String users = '/auth/users/';
  static const String profile = '/auth/profile/me/';

  // Chat
  static const String conversations = '/chat/conversations/';
  static const String searchUsers = '/chat/users/search/';

  static String conversationMessages(int id) =>
      '/chat/conversations/$id/messages/';
  static String messageDetail(int conversationId, int messageId) =>
      '/chat/conversations/$conversationId/messages/$messageId/';
  static String messageEdit(int conversationId, int messageId) =>
      '/chat/conversations/$conversationId/messages/$messageId/edit/';
  static String messageDelete(int conversationId, int messageId) =>
      '/chat/conversations/$conversationId/messages/$messageId/soft-delete/';
  static String conversationSocket(int id) => '$wsBaseUrl/ws/chat/$id/';
}
