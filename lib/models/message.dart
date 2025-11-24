class Message {
  final int id;
  final String content;
  final int senderId;
  final int chatRoomId;
  final DateTime timestamp;
  final String messageType;
  final bool isRead;
  final String? attachment;

  Message({
    required this.id,
    required this.content,
    required this.senderId,
    required this.chatRoomId,
    required this.timestamp,
    this.messageType = 'text',
    this.isRead = false,
    this.attachment,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      content: json['content'],
      senderId: json['sender'] is Map ? json['sender']['id'] : json['sender'],
      chatRoomId: json['conversation'],
      timestamp: DateTime.parse(json['created_at']),
      messageType: json['message_type'] ?? 'text',
      isRead: false, // Not in serializer fields explicitly, maybe in receipts?
      attachment: json['attachments'] != null &&
              (json['attachments'] as List).isNotEmpty
          ? json['attachments'][0]['file']
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'sender_id': senderId,
      'chat_room_id': chatRoomId,
      'timestamp': timestamp.toIso8601String(),
      'message_type': messageType,
      'is_read': isRead,
      'attachment': attachment,
    };
  }
}
