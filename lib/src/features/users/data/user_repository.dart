import 'package:dio/dio.dart';
import 'package:vatochito_chat/src/core/constants/app_endpoints.dart';
import 'package:vatochito_chat/src/core/network/api_client.dart';
import 'package:vatochito_chat/src/features/auth/data/models/user_model.dart';

class UserRepository {
  UserRepository({required ApiClient apiClient}) : _client = apiClient.client;

  final Dio _client;

  Future<List<UserModel>> fetchUsers({String? query}) async {
    final endpoint = query != null && query.isNotEmpty
        ? AppEndpoints.searchUsers
        : AppEndpoints.users;

    final queryParams = query != null && query.isNotEmpty ? {'q': query} : null;

    final response = await _client.get<dynamic>(
      endpoint,
      queryParameters: queryParams,
    );
    // Handle pagination if needed, assuming list for now
    final results = response.data is List
        ? response.data as List
        : (response.data['results'] as List);

    final data = List<Map<String, dynamic>>.from(results);
    return data.map(UserModel.fromJson).toList();
  }
}
