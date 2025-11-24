import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:vatochito_chat/src/features/chat/data/chat_repository.dart';
import 'package:vatochito_chat/src/features/chat/data/models/conversation_model.dart';

part 'chat_list_state.dart';

class ChatListCubit extends Cubit<ChatListState> {
  ChatListCubit(this._repository) : super(const ChatListState());

  final ChatRepository _repository;

  Future<void> loadConversations() async {
    emit(state.copyWith(status: ChatListStatus.loading));
    try {
      final conversations = await _repository.fetchConversations();
      emit(
        state.copyWith(
          status: ChatListStatus.success,
          conversations: conversations,
        ),
      );
    } catch (error) {
      emit(
        state.copyWith(
          status: ChatListStatus.failure,
          errorMessage: error.toString(),
        ),
      );
    }
  }

  Future<ConversationModel?> createConversation(int userId) async {
    try {
      final conversation = await _repository.createConversation(userId);
      if (conversation != null) {
        await loadConversations();
      }
      return conversation;
    } catch (e) {
      return null;
    }
  }
}
