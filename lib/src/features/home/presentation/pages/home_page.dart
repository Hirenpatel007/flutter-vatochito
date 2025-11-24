import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:vatochito_chat/src/features/auth/presentation/bloc/auth_bloc.dart';
import 'package:vatochito_chat/src/features/auth/presentation/bloc/auth_state.dart';
import 'package:vatochito_chat/src/features/chat/presentation/pages/chat_list_page.dart';
import 'package:vatochito_chat/src/features/users/presentation/pages/user_list_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _selectedIndex = 0;

  static const List<Widget> _widgetOptions = <Widget>[
    ChatListPage(),
    UserListPage(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Image.asset(
              'assets/images/logo.png',
              height: 32,
              width: 32,
            ),
            const SizedBox(width: 8),
            const Text('Vatochito'),
          ],
        ),
        actions: [
          BlocBuilder<AuthBloc, AuthState>(
            builder: (context, state) {
              if (state is AuthAuthenticated) {
                return IconButton(
                  icon: CircleAvatar(
                    radius: 14,
                    backgroundImage: state.user.avatar != null
                        ? NetworkImage(state.user.avatar!)
                        : null,
                    child: state.user.avatar == null
                        ? const Icon(Icons.person, size: 16)
                        : null,
                  ),
                  onPressed: () => context.push('/profile'),
                );
              }
              return const SizedBox.shrink();
            },
          ),
        ],
      ),
      body: Center(
        child: _widgetOptions.elementAt(_selectedIndex),
      ),
      bottomNavigationBar: BottomNavigationBar(
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.chat_bubble_outline),
            activeIcon: Icon(Icons.chat_bubble),
            label: 'Chats',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.people_outline),
            activeIcon: Icon(Icons.people),
            label: 'Users',
          ),
        ],
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
      ),
    );
  }
}
