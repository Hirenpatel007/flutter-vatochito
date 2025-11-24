import 'package:equatable/equatable.dart';

abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

class AuthAppStarted extends AuthEvent {
  const AuthAppStarted();
}

class AuthLoginRequested extends AuthEvent {
  const AuthLoginRequested({required this.username, required this.password});

  final String username;
  final String password;

  @override
  List<Object?> get props => [username, password];
}

class AuthRegisterRequested extends AuthEvent {
  const AuthRegisterRequested({
    required this.username,
    required this.password,
    this.email,
  });

  final String username;
  final String password;
  final String? email;

  @override
  List<Object?> get props => [username, password, email];
}

class AuthLogoutRequested extends AuthEvent {
  const AuthLogoutRequested();
}

class AuthUserUpdated extends AuthEvent {
  const AuthUserUpdated();
}
