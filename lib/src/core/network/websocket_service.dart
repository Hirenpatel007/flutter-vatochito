import 'package:vatochito_chat/src/core/storage/token_storage.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../constants/app_endpoints.dart';

class WebsocketService {
  WebsocketService({required this.tokenStorage});

  final TokenStorage tokenStorage;

  Future<WebSocketChannel> connect(int conversationId) async {
    final token = await tokenStorage.getAccessToken();
    final uri = Uri.parse(
      '${AppEndpoints.conversationSocket(conversationId)}?token=$token',
    );
    return WebSocketChannel.connect(uri);
  }
}
