import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../providers/chat_provider.dart';

class ChatListScreen extends StatefulWidget {
  const ChatListScreen({super.key});

  @override
  State<ChatListScreen> createState() => _ChatListScreenState();
}

class _ChatListScreenState extends State<ChatListScreen> {
  @override
  void initState() {
    super.initState();
    _loadConversations();
  }

  Future<void> _loadConversations() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
    if (authProvider.token != null) {
      await chatProvider.getConversations(authProvider.token!);
    }
  }

  @override
  Widget build(BuildContext context) {
    final chatProvider = Provider.of<ChatProvider>(context);
    final authProvider = Provider.of<AuthProvider>(context, listen: false);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Chats'),
        actions: [
          IconButton(
            icon: const Icon(Icons.exit_to_app),
            onPressed: () {
              authProvider.logout();
              Navigator.of(context).pushReplacementNamed('/auth');
            },
          ),
        ],
      ),
      body: chatProvider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: chatProvider.conversations.length,
              itemBuilder: (context, index) {
                final conversation = chatProvider.conversations[index];
                // Assuming conversation object structure. Adjust based on actual API response.
                // Usually has 'id', 'name' or 'participants', 'last_message'
                final name =
                    conversation['name'] ?? 'Chat ${conversation['id']}';
                final lastMessage = conversation['last_message'] != null
                    ? conversation['last_message']['content']
                    : 'No messages yet';

                return ListTile(
                  leading: const CircleAvatar(child: Icon(Icons.person)),
                  title: Text(name),
                  subtitle: Text(lastMessage),
                  onTap: () {
                    Navigator.of(context).pushNamed(
                      '/chat',
                      arguments: {
                        'id': conversation['id'],
                        'name': name,
                      },
                    );
                  },
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // TODO: Implement new chat creation
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('New chat feature coming soon!')),
          );
        },
        child: const Icon(Icons.message),
      ),
    );
  }
}
