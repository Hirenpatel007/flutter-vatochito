import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class WebSocketProvider with ChangeNotifier {
  WebSocketChannel? _channel;
  final List<dynamic> _messages = [];
  bool _isConnected = false;

  bool get isConnected => _isConnected;
  List<dynamic> get messages => _messages;

  void connect(String conversationId, String token) {
    if (_channel != null) {
      _channel!.sink.close();
    }

    // Use 10.0.2.2 for Android Emulator, localhost for iOS/Web
    final wsUrl =
        Uri.parse('ws://localhost:8000/ws/chat/$conversationId/?token=$token');
    _channel = WebSocketChannel.connect(wsUrl);
    _isConnected = true;
    notifyListeners();

    _channel!.stream.listen(
      (message) {
        final data = json.decode(message);
        _messages.add(data);
        notifyListeners();
      },
      onDone: () {
        _isConnected = false;
        notifyListeners();
      },
      onError: (error) {
        _isConnected = false;
        notifyListeners();
        debugPrint('WebSocket error: $error');
      },
    );
  }

  void sendMessage(String message) {
    if (_channel != null && _isConnected) {
      _channel!.sink.add(json.encode({
        'message': message,
      }));
    }
  }

  void disconnect() {
    if (_channel != null) {
      _channel!.sink.close();
      _channel = null;
      _isConnected = false;
      _messages.clear();
      notifyListeners();
    }
  }

  @override
  void dispose() {
    disconnect();
    super.dispose();
  }
}
