import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:vatochito_chat/src/features/auth/data/models/user_model.dart';
import 'package:vatochito_chat/src/features/users/data/user_repository.dart';

part 'user_list_state.dart';

class UserListCubit extends Cubit<UserListState> {
  UserListCubit(this._repository) : super(const UserListState());

  final UserRepository _repository;

  Future<void> fetchUsers({String? query}) async {
    emit(state.copyWith(status: UserListStatus.loading));
    try {
      final users = await _repository.fetchUsers(query: query);
      emit(state.copyWith(status: UserListStatus.success, users: users));
    } catch (e) {
      emit(state.copyWith(
        status: UserListStatus.failure,
        errorMessage: e.toString(),
      ));
    }
  }
}
