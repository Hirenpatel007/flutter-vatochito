import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';

part 'user_model.g.dart';

@JsonSerializable()
class UserModel extends Equatable {
  const UserModel({
    required this.id,
    required this.username,
    this.email,
    this.displayName,
    this.avatar,
    this.statusMessage,
    this.isOnline,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) =>
      _$UserModelFromJson(json);

  Map<String, dynamic> toJson() => _$UserModelToJson(this);

  final int id;
  final String username;
  final String? email;

  @JsonKey(name: 'display_name')
  final String? displayName;

  final String? avatar;

  @JsonKey(name: 'status_message')
  final String? statusMessage;

  @JsonKey(name: 'is_online')
  final bool? isOnline;

  @override
  List<Object?> get props => [
        id,
        username,
        email,
        displayName,
        avatar,
        statusMessage,
        isOnline,
      ];
}
