import 'dart:async';
import 'dart:convert';
import 'dart:developer' as developer;

import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:vatochito_chat/src/features/chat/data/chat_repository.dart';
import 'package:vatochito_chat/src/features/chat/data/models/message_model.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

part 'chat_room_state.dart';

class ChatRoomCubit extends Cubit<ChatRoomState> {
  ChatRoomCubit(this._repository, this._getUserId)
      : super(const ChatRoomState());

  final ChatRepository _repository;
  final Future<int?> Function() _getUserId;
  StreamSubscription<dynamic>? _channelSubscription;
  WebSocketChannel? _channel;

  Future<void> connect(int conversationId) async {
    emit(state.copyWith(status: ChatRoomStatus.loading));
    try {
      final messages = await _repository.fetchMessages(conversationId);
      emit(state.copyWith(messages: messages));

      _channel = await _repository.websocketService.connect(conversationId);
      _channelSubscription = _channel!.stream.listen(
        (data) {
          final jsonData = jsonDecode(data as String) as Map<String, dynamic>;
          if (jsonData['type'] == 'message.new') {
            final messageData = jsonData['data'] as Map<String, dynamic>;
            final message = MessageModel.fromJson(messageData);
            emit(state.copyWith(messages: [message, ...state.messages]));
          } else if (jsonData['type'] == 'message.edited') {
            final messageData = jsonData['data'] as Map<String, dynamic>;
            final updatedMessage = MessageModel.fromJson(messageData);
            final updatedMessages = state.messages.map((m) {
              return m.id == updatedMessage.id ? updatedMessage : m;
            }).toList();
            emit(state.copyWith(messages: updatedMessages));
          } else if (jsonData['type'] == 'message.deleted') {
            final messageId = jsonData['message_id'] as int;
            final updatedMessages = state.messages.map((m) {
              if (m.id == messageId) {
                return m.copyWith(
                    isDeleted: true, content: 'This message was deleted');
              }
              return m;
            }).toList();
            emit(state.copyWith(messages: updatedMessages));
          }
        },
        onError: (error) {
          emit(state.copyWith(
            status: ChatRoomStatus.failure,
            errorMessage: error.toString(),
          ));
        },
        onDone: () {
          emit(state.copyWith(status: ChatRoomStatus.success));
        },
      );
      emit(state.copyWith(status: ChatRoomStatus.success));
    } catch (e) {
      emit(
        state.copyWith(
          status: ChatRoomStatus.failure,
          errorMessage: e.toString(),
        ),
      );
    }
  }

  Future<void> sendMessage(String content, int conversationId) async {
    developer.log('ChatRoomCubit.sendMessage called', name: 'ChatRoomCubit');
    developer.log('Content: "$content"', name: 'ChatRoomCubit');
    developer.log('ConversationId: $conversationId', name: 'ChatRoomCubit');
    developer.log('ChatRoomCubit.sendMessage called', name: 'ChatRoomCubit');
    developer.log('Content: "$content"', name: 'ChatRoomCubit');
    developer.log('ConversationId: $conversationId', name: 'ChatRoomCubit');
    if (content.isEmpty) {
      developer.log('Content is empty, returning', name: 'ChatRoomCubit');
      developer.log('Content is empty, returning', name: 'ChatRoomCubit');
      return;
    }
    try {
      final userId = await _getUserId();
      developer.log('sendMessage - userId: $userId', name: 'ChatRoomCubit');
      developer.log('sendMessage - userId: $userId', name: 'ChatRoomCubit');
      if (userId == null) {
        developer.log('userId is null, emitting error', name: 'ChatRoomCubit');
        developer.log('userId is null, emitting error', name: 'ChatRoomCubit');
        emit(state.copyWith(errorMessage: 'User not authenticated'));
        return;
      }
      if (_channel == null) {
        developer.log('WebSocket channel is null, emitting error',
            name: 'ChatRoomCubit');
        developer.log('WebSocket channel is null, emitting error',
            name: 'ChatRoomCubit');
        emit(state.copyWith(errorMessage: 'Not connected to chat'));
        return;
      }
      final message = {
        'type': 'message.send',
        'content': content,
        'conversation_id': conversationId,
        'user_id': userId,
      };
      developer.log('Sending WebSocket message: $message',
          name: 'ChatRoomCubit');
      developer.log('Sending WebSocket message: $message',
          name: 'ChatRoomCubit');
      _channel?.sink.add(jsonEncode(message));
      developer.log('WebSocket message sent successfully',
          name: 'ChatRoomCubit');
      developer.log('WebSocket message sent successfully',
          name: 'ChatRoomCubit');
    } catch (e, stack) {
      developer.log('Error in sendMessage',
          error: e, stackTrace: stack, name: 'ChatRoomCubit');
      developer.log('Error in sendMessage',
          error: e, stackTrace: stack, name: 'ChatRoomCubit');
      emit(state.copyWith(errorMessage: 'Failed to send message'));
    }
  }

  Future<void> editMessage(
      int messageId, String content, int conversationId) async {
    try {
      await _repository.editMessage(
        conversationId: conversationId,
        messageId: messageId,
        content: content,
      );
    } catch (e) {
      emit(state.copyWith(errorMessage: 'Failed to edit message'));
    }
  }

  Future<void> deleteMessage(int messageId, int conversationId) async {
    try {
      await _repository.deleteMessage(
        conversationId: conversationId,
        messageId: messageId,
      );
    } catch (e) {
      emit(state.copyWith(errorMessage: 'Failed to delete message'));
    }
  }

  void clearError() {
    emit(state.copyWith(clearError: true));
  }

  @override
  Future<void> close() {
    _channelSubscription?.cancel();
    _channel?.sink.close();
    return super.close();
  }
}
