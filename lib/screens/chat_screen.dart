import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../providers/chat_provider.dart';
import '../providers/websocket_provider.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _messageController = TextEditingController();
  int? _conversationId;
  String? _conversationName;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final args =
        ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;
    _conversationId = args['id'];
    _conversationName = args['name'];
    _initChat();
  }

  void _initChat() {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
    final wsProvider = Provider.of<WebSocketProvider>(context, listen: false);

    if (authProvider.token != null && _conversationId != null) {
      chatProvider.getMessages(authProvider.token!, _conversationId!);
      wsProvider.connect(_conversationId.toString(), authProvider.token!);
    }
  }

  @override
  void dispose() {
    _messageController.dispose();
    // We might want to disconnect WS here, but if we go back to list, maybe keep it?
    // Usually disconnect when leaving the screen.
    // Accessing provider in dispose is tricky if context is not valid, but usually ok for listen:false
    // But better to do it in deactivate or just rely on provider cleanup if it was scoped.
    // Here provider is global, so we should disconnect.
    // However, we can't access context easily in dispose if the widget is unmounted.
    // Let's do it in deactivate.
    super.dispose();
  }

  @override
  void deactivate() {
    final wsProvider = Provider.of<WebSocketProvider>(context, listen: false);
    wsProvider.disconnect();
    super.deactivate();
  }

  void _sendMessage() async {
    if (_messageController.text.trim().isEmpty) return;

    final content = _messageController.text;
    _messageController.clear();

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
    // final wsProvider = Provider.of<WebSocketProvider>(context, listen: false);

    // We can send via HTTP or WS. Usually HTTP for persistence and WS for real-time echo.
    // If backend handles WS message saving, we can use WS.
    // But ChatProvider uses HTTP. Let's stick to HTTP for sending and WS for receiving.

    try {
      await chatProvider.sendMessage(
          authProvider.token!, _conversationId!, content);
      if (!mounted) return;
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to send message: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final chatProvider = Provider.of<ChatProvider>(context);
    final wsProvider = Provider.of<WebSocketProvider>(context);
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final currentUserId =
        authProvider.user?['id']; // Assuming user object has id

    // Merge HTTP messages and WS messages if needed, or just rely on one source.
    // Ideally, WS updates the same list in ChatProvider or we listen to both.
    // For simplicity, let's assume ChatProvider manages the state and we might need to integrate WS updates there.
    // But here we have two lists.
    // Let's just display ChatProvider messages for now.
    // To make it real-time, WebSocketProvider should update ChatProvider or we merge them here.
    // A better architecture is WebSocketProvider updates ChatProvider.
    // But for now, let's just listen to WS and add to ChatProvider manually in the listener?
    // Or better: WebSocketProvider exposes a stream, and we listen to it in initState and add to ChatProvider.

    // Actually, let's just use a simple approach:
    // When WS receives a message, we add it to ChatProvider's list.
    // But ChatProvider is not listening to WebSocketProvider.
    // We can do this in the UI: listen to wsProvider.messages and if new one comes, add to chatProvider?
    // No, that causes loops.

    // Let's just display chatProvider.messages.
    // And in _initChat, we can set up a listener on WS stream to add to chatProvider.

    return Scaffold(
      appBar: AppBar(
        title: Text(_conversationName ?? 'Chat'),
        actions: [
          Icon(
            Icons.circle,
            color: wsProvider.isConnected ? Colors.green : Colors.red,
            size: 12,
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: chatProvider.isLoading
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    reverse: true, // Start from bottom
                    itemCount: chatProvider.messages.length,
                    itemBuilder: (context, index) {
                      final message = chatProvider.messages[index];
                      final isMe = message['sender'] == currentUserId ||
                          (message['sender'] is Map &&
                              message['sender']['id'] == currentUserId);

                      return Align(
                        alignment:
                            isMe ? Alignment.centerRight : Alignment.centerLeft,
                        child: Container(
                          margin: const EdgeInsets.symmetric(
                              vertical: 4, horizontal: 8),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: isMe ? Colors.blue : Colors.grey[300],
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            message['content'] ?? '',
                            style: TextStyle(
                                color: isMe ? Colors.white : Colors.black),
                          ),
                        ),
                      );
                    },
                  ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: const InputDecoration(
                      hintText: 'Type a message...',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: _sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
