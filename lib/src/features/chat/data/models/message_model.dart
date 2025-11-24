import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:vatochito_chat/src/features/auth/data/models/user_model.dart';

part 'message_model.g.dart';

@JsonSerializable()
class MessageModel extends Equatable {
  const MessageModel({
    required this.id,
    required this.user,
    required this.content,
    required this.timestamp,
    this.isRead,
    this.isDeleted = false,
    this.editedAt,
  });

  factory MessageModel.fromJson(Map<String, dynamic> json) =>
      _$MessageModelFromJson(json);

  Map<String, dynamic> toJson() => _$MessageModelToJson(this);

  final int id;
  @JsonKey(name: 'sender')
  final UserModel user;
  final String content;
  @JsonKey(name: 'created_at')
  final DateTime timestamp;
  @JsonKey(name: 'is_read')
  final bool? isRead;
  @JsonKey(name: 'is_deleted')
  final bool isDeleted;
  @JsonKey(name: 'edited_at')
  final DateTime? editedAt;

  MessageModel copyWith({
    int? id,
    UserModel? user,
    String? content,
    DateTime? timestamp,
    bool? isRead,
    bool? isDeleted,
    DateTime? editedAt,
  }) {
    return MessageModel(
      id: id ?? this.id,
      user: user ?? this.user,
      content: content ?? this.content,
      timestamp: timestamp ?? this.timestamp,
      isRead: isRead ?? this.isRead,
      isDeleted: isDeleted ?? this.isDeleted,
      editedAt: editedAt ?? this.editedAt,
    );
  }

  @override
  List<Object?> get props =>
      [id, user, content, timestamp, isRead, isDeleted, editedAt];
}
