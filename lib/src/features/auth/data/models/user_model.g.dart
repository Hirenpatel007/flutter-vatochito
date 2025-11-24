// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UserModel _$UserModelFromJson(Map<String, dynamic> json) => UserModel(
      id: (json['id'] as num).toInt(),
      username: json['username'] as String,
      email: json['email'] as String?,
      displayName: json['display_name'] as String?,
      avatar: json['avatar'] as String?,
      statusMessage: json['status_message'] as String?,
      isOnline: json['is_online'] as bool?,
    );

Map<String, dynamic> _$UserModelToJson(UserModel instance) => <String, dynamic>{
      'id': instance.id,
      'username': instance.username,
      'email': instance.email,
      'display_name': instance.displayName,
      'avatar': instance.avatar,
      'status_message': instance.statusMessage,
      'is_online': instance.isOnline,
    };
