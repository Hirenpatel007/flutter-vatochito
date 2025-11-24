import 'package:equatable/equatable.dart';
import 'package:vatochito_chat/src/features/auth/data/models/user_model.dart';

abstract class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object?> get props => [];
}

class AuthInitial extends AuthState {}

class AuthLoading extends AuthState {}

class AuthAuthenticated extends AuthState {
  const AuthAuthenticated({required this.user});
  final UserModel user;

  @override
  List<Object?> get props => [user];
}

class AuthUnauthenticated extends AuthState {
  const AuthUnauthenticated({this.error});
  final String? error;

  @override
  List<Object?> get props => [error];
}
