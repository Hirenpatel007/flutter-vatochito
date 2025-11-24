import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:vatochito_chat/src/features/auth/presentation/bloc/auth_bloc.dart';
import 'package:vatochito_chat/src/features/auth/presentation/bloc/auth_state.dart';
import 'package:vatochito_chat/src/features/chat/presentation/bloc/chat_list_cubit.dart';

class ChatListPage extends StatefulWidget {
  const ChatListPage({super.key});

  @override
  State<ChatListPage> createState() => _ChatListPageState();
}

class _ChatListPageState extends State<ChatListPage> {
  @override
  void initState() {
    super.initState();
    context.read<ChatListCubit>().loadConversations();
  }

  @override
  Widget build(BuildContext context) {
    final authState = context.watch<AuthBloc>().state;
    if (authState is! AuthAuthenticated) {
      return const Center(child: Text('Not authenticated'));
    }
    final currentUser = authState.user;
    return Scaffold(
      body: BlocBuilder<ChatListCubit, ChatListState>(
        builder: (context, state) {
          if (state.status == ChatListStatus.loading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state.status == ChatListStatus.failure) {
            return Center(
              child: Text(state.errorMessage ?? 'Failed to load conversations'),
            );
          }
          final conversations = state.conversations;
          if (conversations.isEmpty) {
            return const Center(child: Text('No conversations yet.'));
          }
          return RefreshIndicator(
            onRefresh: () => context.read<ChatListCubit>().loadConversations(),
            child: ListView.builder(
              itemCount: conversations.length,
              itemBuilder: (context, index) {
                final conversation = conversations[index];
                final otherUser = conversation.members.firstWhere(
                  (member) => member.id != currentUser.id,
                  orElse: () => conversation.members.first,
                );
                return ListTile(
                  leading: CircleAvatar(
                    backgroundImage: otherUser.avatar != null
                        ? NetworkImage(otherUser.avatar!)
                        : null,
                    child: otherUser.avatar == null
                        ? Text(
                            (otherUser.displayName?.isNotEmpty ?? false)
                                ? otherUser.displayName!
                                    .substring(0, 1)
                                    .toUpperCase()
                                : (otherUser.username.isNotEmpty
                                    ? otherUser.username
                                        .substring(0, 1)
                                        .toUpperCase()
                                    : 'U'),
                          )
                        : null,
                  ),
                  title: Text(conversation.title ??
                      otherUser.displayName ??
                      otherUser.username),
                  subtitle: Text(conversation.lastMessage?.content ?? ''),
                  onTap: () {
                    context.goNamed(
                      'chat',
                      pathParameters: {'id': conversation.id.toString()},
                      extra: conversation,
                    );
                  },
                );
              },
            ),
          );
        },
      ),
    );
  }
}
