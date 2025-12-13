import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:provider/provider.dart';

import 'firebase_options.dart';
import 'splash_screen.dart';

class LanguageProvider with ChangeNotifier {
  bool _isUrdu = false;

  bool get isUrdu => _isUrdu;

  void setLanguage(bool isUrdu) {
    _isUrdu = isUrdu;
    notifyListeners();
  }

  Locale get locale =>
      _isUrdu ? const Locale('ur', 'PK') : const Locale('en', 'US');
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  runApp(
    ChangeNotifierProvider(
      create: (_) => LanguageProvider(),
      child: const MainApp(),
    ),
  );
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<LanguageProvider>(
      builder: (context, languageProvider, child) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          locale: languageProvider.locale,
          supportedLocales: const [
            Locale('en', 'US'),
            Locale('ur', 'PK'),
          ],
          theme: ThemeData(
            primaryColor: const Color(0xFF003366),
            scaffoldBackgroundColor: const Color(0xFFFFFFFF),
          ),
          home: const SplashScreen(),
        );
      },
    );
  }
}