// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'conversation_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ConversationModel _$ConversationModelFromJson(Map<String, dynamic> json) =>
    ConversationModel(
      id: (json['id'] as num).toInt(),
      title: json['title'] as String?,
      conversationType: json['conversation_type'] as String?,
      avatar: json['avatar'] as String?,
      members: (json['members'] as List<dynamic>)
          .map((e) => UserModel.fromJson(e['user'] as Map<String, dynamic>))
          .toList(),
      lastMessage: json['last_message'] == null
          ? null
          : MessageModel.fromJson(json['last_message'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$ConversationModelToJson(ConversationModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'conversation_type': instance.conversationType,
      'avatar': instance.avatar,
      'members': instance.members,
      'last_message': instance.lastMessage,
    };
