import 'package:flutter/material.dart';
import 'package:vatochito_chat/src/features/chat/data/models/message_model.dart';

class MessageBubble extends StatelessWidget {
  const MessageBubble({
    super.key,
    required this.message,
    required this.isMe,
  });

  final MessageModel message;
  final bool isMe;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Align(
      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 14),
        decoration: BoxDecoration(
          color: isMe ? theme.primaryColor : theme.cardColor,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: isMe ? const Radius.circular(16) : Radius.zero,
            bottomRight: isMe ? Radius.zero : const Radius.circular(16),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 3,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment:
              isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            if (!isMe)
              Text(
                message.user.displayName ?? message.user.username,
                style: theme.textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: theme.primaryColor,
                ),
              ),
            Text(
              message.isDeleted ? 'This message was deleted' : message.content,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: isMe ? Colors.white : theme.textTheme.bodyLarge?.color,
                fontStyle:
                    message.isDeleted ? FontStyle.italic : FontStyle.normal,
              ),
            ),
            if (!message.isDeleted && message.editedAt != null)
              Padding(
                padding: const EdgeInsets.only(top: 2),
                child: Text(
                  '(edited)',
                  style: theme.textTheme.bodySmall?.copyWith(
                    fontSize: 10,
                    color: isMe ? Colors.white70 : Colors.grey,
                  ),
                ),
              ),
            const SizedBox(height: 4),
            Text(
              '${message.timestamp.hour}:${message.timestamp.minute.toString().padLeft(2, '0')}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: isMe
                    ? Colors.white70
                    : theme.textTheme.bodySmall?.color?.withOpacity(0.7),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
