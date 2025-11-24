import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class ChatProvider with ChangeNotifier {
  List<dynamic> _conversations = [];
  List<dynamic> _messages = [];
  bool _isLoading = false;

  List<dynamic> get conversations => _conversations;
  List<dynamic> get messages => _messages;
  bool get isLoading => _isLoading;

  // Use 10.0.2.2 for Android Emulator, localhost for iOS/Web
  final String baseUrl = 'http://localhost:8000/api/chat';

  Future<void> getConversations(String token) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/conversations/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        _conversations = json.decode(response.body);
      } else {
        throw Exception('Failed to load conversations');
      }
    } catch (e) {
      debugPrint('Error fetching conversations: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> getMessages(String token, int conversationId) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/conversations/$conversationId/messages/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        // Handle pagination if needed, for now assume list or results
        if (data is Map && data.containsKey('results')) {
          _messages = data['results'];
        } else if (data is List) {
          _messages = data;
        }
        // Reverse to show newest at bottom if needed, but usually API returns newest first or last?
        // Typically chat UIs want newest at bottom.
        // If API returns newest first (descending), we might need to reverse.
      } else {
        throw Exception('Failed to load messages');
      }
    } catch (e) {
      debugPrint('Error fetching messages: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> sendMessage(
      String token, int conversationId, String content) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/conversations/$conversationId/messages/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode({'content': content}),
      );

      if (response.statusCode == 201) {
        final newMessage = json.decode(response.body);
        _messages.insert(0,
            newMessage); // Assuming list is displayed reversed or we add to top
        notifyListeners();
      } else {
        throw Exception('Failed to send message');
      }
    } catch (e) {
      debugPrint('Error sending message: $e');
      rethrow;
    }
  }

  void addMessage(dynamic message) {
    _messages.insert(0, message);
    notifyListeners();
  }
}
