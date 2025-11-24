import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:vatochito_chat/src/core/network/websocket_service.dart';

import '../config/app_router.dart';
import '../core/network/api_client.dart';
import '../core/storage/token_storage.dart';
import '../features/auth/data/repositories/auth_repository.dart';
import '../features/auth/presentation/bloc/auth_bloc.dart';
import '../features/auth/presentation/bloc/auth_event.dart';
import '../features/auth/presentation/bloc/auth_state.dart';
import '../features/chat/data/chat_repository.dart';
import '../features/chat/presentation/bloc/chat_list_cubit.dart';
import '../features/chat/presentation/bloc/chat_room_cubit.dart';
import '../features/users/data/user_repository.dart';
import '../features/users/presentation/bloc/user_list_cubit.dart';
import 'app.dart';

class AppBootstrap {
  AppBootstrap._();

  static Future<Widget> create() async {
    const tokenStorage = TokenStorage(FlutterSecureStorage());
    final apiClient = ApiClient(tokenStorage: tokenStorage);
    final websocketService = WebsocketService(tokenStorage: tokenStorage);

    final authRepository = AuthRepository(
      apiClient: apiClient,
      tokenStorage: tokenStorage,
    );
    final chatRepository = ChatRepository(
      apiClient: apiClient,
      websocketService: websocketService,
    );
    final userRepository = UserRepository(apiClient: apiClient);
    final authBloc = AuthBloc(authRepository)..add(const AuthAppStarted());

    final appRouter = AppRouter(authBloc: authBloc);

    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider.value(value: authRepository),
        RepositoryProvider.value(value: chatRepository),
        RepositoryProvider.value(value: userRepository),
      ],
      child: MultiBlocProvider(
        providers: [
          BlocProvider<AuthBloc>.value(value: authBloc),
          BlocProvider(create: (_) => ChatListCubit(chatRepository)),
          BlocProvider(
              create: (context) => ChatRoomCubit(chatRepository, () async {
                    final state = context.read<AuthBloc>().state;
                    if (state is AuthAuthenticated) {
                      return state.user.id;
                    }
                    return authRepository.getUserId();
                  })),
          BlocProvider(create: (_) => UserListCubit(userRepository)),
        ],
        child: VatochitoApp(router: appRouter.router),
      ),
    );
  }
}
