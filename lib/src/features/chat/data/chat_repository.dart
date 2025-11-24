import 'package:dio/dio.dart';
import 'package:vatochito_chat/src/core/constants/app_endpoints.dart';
import 'package:vatochito_chat/src/core/network/api_client.dart';
import 'package:vatochito_chat/src/core/network/websocket_service.dart';
import 'package:vatochito_chat/src/features/chat/data/models/conversation_model.dart';
import 'package:vatochito_chat/src/features/chat/data/models/message_model.dart';

class ChatRepository {
  ChatRepository({
    required ApiClient apiClient,
    required this.websocketService,
  }) : _client = apiClient.client;

  final Dio _client;
  final WebsocketService websocketService;

  Future<List<ConversationModel>> fetchConversations() async {
    final response = await _client.get<dynamic>(AppEndpoints.conversations);
    final data = List<Map<String, dynamic>>.from(response.data as List);
    return data.map(ConversationModel.fromJson).toList();
  }

  Future<List<MessageModel>> fetchMessages(int conversationId) async {
    final response = await _client.get<dynamic>(
      AppEndpoints.conversationMessages(conversationId),
    );
    final data = List<Map<String, dynamic>>.from(response.data as List);
    return data.map(MessageModel.fromJson).toList();
  }

  Future<ConversationModel?> createConversation(int userId) async {
    try {
      final response = await _client.post<dynamic>(
        '${AppEndpoints.conversations}create-direct/',
        data: {'user_id': userId},
      );
      return ConversationModel.fromJson(
        Map<String, dynamic>.from(response.data as Map),
      );
    } catch (e) {
      return null;
    }
  }

  Future<MessageModel> sendMessage({
    required int conversationId,
    required String content,
  }) async {
    final response = await _client.post<dynamic>(
      AppEndpoints.conversationMessages(conversationId),
      data: {'content': content},
    );
    return MessageModel.fromJson(
      Map<String, dynamic>.from(response.data as Map),
    );
  }

  Future<MessageModel> editMessage({
    required int conversationId,
    required int messageId,
    required String content,
  }) async {
    final response = await _client.patch<dynamic>(
      AppEndpoints.messageEdit(conversationId, messageId),
      data: {'content': content},
    );
    return MessageModel.fromJson(
      Map<String, dynamic>.from(response.data as Map),
    );
  }

  Future<void> deleteMessage({
    required int conversationId,
    required int messageId,
  }) async {
    await _client.delete<dynamic>(
      AppEndpoints.messageDelete(conversationId, messageId),
    );
  }
}
