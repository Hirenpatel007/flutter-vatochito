// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'message_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

MessageModel _$MessageModelFromJson(Map<String, dynamic> json) => MessageModel(
      id: (json['id'] as num).toInt(),
      user: UserModel.fromJson(json['sender'] as Map<String, dynamic>),
      content: json['content'] as String,
      timestamp: DateTime.parse(json['created_at'] as String),
      isRead: json['is_read'] as bool?,
      isDeleted: json['is_deleted'] as bool? ?? false,
      editedAt: json['edited_at'] == null
          ? null
          : DateTime.parse(json['edited_at'] as String),
    );

Map<String, dynamic> _$MessageModelToJson(MessageModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'sender': instance.user,
      'content': instance.content,
      'created_at': instance.timestamp.toIso8601String(),
      'is_read': instance.isRead,
      'is_deleted': instance.isDeleted,
      'edited_at': instance.editedAt?.toIso8601String(),
    };
