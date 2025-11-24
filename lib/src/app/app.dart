import 'package:flutter/material.dart';

class VatochitoApp extends StatelessWidget {
  const VatochitoApp({
    required this.router,
    super.key,
  });

  final RouterConfig<Object> router;

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Vatochito',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      routerConfig: router,
    );
  }
}
