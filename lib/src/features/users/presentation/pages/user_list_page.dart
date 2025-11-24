import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:vatochito_chat/src/features/chat/presentation/bloc/chat_list_cubit.dart';
import 'package:vatochito_chat/src/features/users/presentation/bloc/user_list_cubit.dart';

class UserListPage extends StatefulWidget {
  const UserListPage({super.key});

  @override
  State<UserListPage> createState() => _UserListPageState();
}

class _UserListPageState extends State<UserListPage> {
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    context.read<UserListCubit>().fetchUsers();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    context.read<UserListCubit>().fetchUsers(query: query);
  }

  void _onUserTap(int userId) {
    context
        .read<ChatListCubit>()
        .createConversation(userId)
        .then((conversation) {
      if (conversation != null && mounted) {
        context.goNamed(
          'chat',
          pathParameters: {'id': conversation.id.toString()},
          extra: conversation,
        );
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not start conversation')),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _searchController,
              decoration: const InputDecoration(
                labelText: 'Search users',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
              ),
              onChanged: _onSearchChanged,
            ),
          ),
          Expanded(
            child: BlocBuilder<UserListCubit, UserListState>(
              builder: (context, state) {
                if (state.status == UserListStatus.loading) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (state.status == UserListStatus.failure) {
                  return Center(
                      child:
                          Text(state.errorMessage ?? 'Failed to load users'));
                }
                if (state.users.isEmpty) {
                  return const Center(child: Text('No users found'));
                }
                return RefreshIndicator(
                  onRefresh: () => context
                      .read<UserListCubit>()
                      .fetchUsers(query: _searchController.text),
                  child: ListView.builder(
                    itemCount: state.users.length,
                    itemBuilder: (context, index) {
                      final user = state.users[index];
                      return ListTile(
                        leading: CircleAvatar(
                          backgroundImage: user.avatar != null
                              ? NetworkImage(user.avatar!)
                              : null,
                          child: user.avatar == null
                              ? Text(
                                  (user.displayName?.isNotEmpty ?? false)
                                      ? user.displayName!
                                          .substring(0, 1)
                                          .toUpperCase()
                                      : (user.username.isNotEmpty
                                          ? user.username
                                              .substring(0, 1)
                                              .toUpperCase()
                                          : 'U'),
                                )
                              : null,
                        ),
                        title: Text(user.displayName ?? user.username),
                        subtitle: Text(user.statusMessage ?? ''),
                        onTap: () => _onUserTap(user.id),
                      );
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
