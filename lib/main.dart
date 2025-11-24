import 'package:flutter/material.dart';
import 'package:vatochito_chat/src/app/app_bootstrap.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final app = await AppBootstrap.create();
  runApp(app);
}
