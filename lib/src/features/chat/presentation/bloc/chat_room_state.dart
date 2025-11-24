part of 'chat_room_cubit.dart';

enum ChatRoomStatus { initial, loading, success, failure }

class ChatRoomState extends Equatable {
  const ChatRoomState({
    this.status = ChatRoomStatus.initial,
    this.messages = const [],
    this.errorMessage,
  });

  final ChatRoomStatus status;
  final List<MessageModel> messages;
  final String? errorMessage;

  ChatRoomState copyWith({
    ChatRoomStatus? status,
    List<MessageModel>? messages,
    String? errorMessage,
    bool clearError = false,
  }) {
    return ChatRoomState(
      status: status ?? this.status,
      messages: messages ?? this.messages,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
    );
  }

  @override
  List<Object?> get props => [status, messages, errorMessage];
}
