import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';

import '../../../auth/data/models/user_model.dart';
import 'message_model.dart';

part 'conversation_model.g.dart';

@JsonSerializable()
class ConversationModel extends Equatable {
  const ConversationModel({
    required this.id,
    this.title,
    this.conversationType,
    this.avatar,
    required this.members,
    this.lastMessage,
  });

  factory ConversationModel.fromJson(Map<String, dynamic> json) =>
      _$ConversationModelFromJson(json);

  Map<String, dynamic> toJson() => _$ConversationModelToJson(this);

  final int id;
  final String? title;
  @JsonKey(name: 'conversation_type')
  final String? conversationType;
  final String? avatar;
  final List<UserModel> members;
  @JsonKey(name: 'last_message')
  final MessageModel? lastMessage;

  @override
  List<Object?> get props =>
      [id, title, conversationType, avatar, members, lastMessage];
}
