import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:vatochito_chat/src/features/auth/data/models/user_model.dart';

import '../features/auth/presentation/bloc/auth_bloc.dart';
import '../features/auth/presentation/bloc/auth_state.dart';
import '../features/auth/presentation/pages/login_page.dart';
import '../features/auth/presentation/pages/profile_page.dart';
import '../features/auth/presentation/pages/register_page.dart';
import '../features/chat/data/models/conversation_model.dart';
import '../features/chat/presentation/pages/chat_room_page.dart';
import '../features/home/presentation/pages/home_page.dart';
import 'go_router_refresh_stream.dart';

class AppRouter {
  final AuthBloc authBloc;
  late final GoRouter router;

  AppRouter({required this.authBloc}) {
    router = GoRouter(
      initialLocation: '/login',
      refreshListenable: GoRouterRefreshStream(authBloc.stream),
      routes: [
        GoRoute(
          path: '/login',
          name: 'login',
          builder: (context, state) => const LoginPage(),
        ),
        GoRoute(
          path: '/register',
          name: 'register',
          builder: (context, state) => const RegisterPage(),
        ),
        GoRoute(
          path: '/profile',
          name: 'profile',
          builder: (context, state) => const ProfilePage(),
        ),
        GoRoute(
            path: '/',
            name: 'home',
            builder: (context, state) => const HomePage(),
            routes: [
              GoRoute(
                path: 'chat/:id',
                name: 'chat',
                builder: (context, state) {
                  final conversation = state.extra as ConversationModel?;
                  final conversationId =
                      int.tryParse(state.pathParameters['id'] ?? '');
                  if (conversationId == null) {
                    return const Text('Invalid chat ID');
                  }
                  final authState = context.read<AuthBloc>().state;
                  UserModel? currentUser;
                  if (authState is AuthAuthenticated) {
                    currentUser = authState.user;
                  }
                  return ChatRoomPage(
                    conversationId: conversationId,
                    title: conversation?.title,
                    currentUser: currentUser,
                  );
                },
              ),
            ]),
      ],
      redirect: (BuildContext context, GoRouterState state) {
        final authState = context.read<AuthBloc>().state;
        final onAuthRoutes = state.matchedLocation == '/login' ||
            state.matchedLocation == '/register';

        if (authState is! AuthAuthenticated && !onAuthRoutes) {
          return '/login';
        }

        if (authState is AuthAuthenticated && onAuthRoutes) {
          return '/';
        }

        return null;
      },
    );
  }
}
