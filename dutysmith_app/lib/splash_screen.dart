import 'dart:async';
import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';

import 'core/theme/app_colors.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  double _opacity = 0;

  StreamSubscription<User?>? _sub;
  bool _navigated = false;

  @override
  void initState() {
    super.initState();

    // Fade in
    Timer(const Duration(milliseconds: 120), () {
      if (mounted) setState(() => _opacity = 1);
    });

    // Ensure splash shows at least 2 seconds
    final minSplash = Future<void>.delayed(const Duration(seconds: 2));

    _sub = FirebaseAuth.instance.authStateChanges().listen((user) async {
      // Wait for minimum splash duration
      await minSplash;

      if (!mounted || _navigated) return;
      _navigated = true;

      final route = (user == null) ? '/login' : '/home';
      Navigator.of(context).pushReplacementNamed(route);
    });
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.white,
      body: SafeArea(
        child: Center(
          child: AnimatedOpacity(
            opacity: _opacity,
            duration: const Duration(milliseconds: 800),
            curve: Curves.easeOut,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                LayoutBuilder(
                  builder: (context, constraints) {
                    final double logoSize =
                        (constraints.maxWidth * 0.65).clamp(220.0, 360.0);

                    return Image.asset(
                      'assets/images/logo.png',
                      width: logoSize,
                      fit: BoxFit.contain,
                      filterQuality: FilterQuality.high,
                      errorBuilder: (context, error, stackTrace) {
                        return Icon(
                          Icons.image_not_supported,
                          size: logoSize * 0.5,
                          color: AppColors.darkGrey,
                        );
                      },
                    );
                  },
                ),
                const SizedBox(height: 18),
                Text(
                  'DutySmith',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w800,
                        color: AppColors.primaryDarkBlue,
                      ),
                ),
                const SizedBox(height: 22),
                SizedBox(
                  width: 220,
                  child: LinearProgressIndicator(
                    minHeight: 4,
                    backgroundColor:
                        AppColors.primaryDarkBlue.withValues(alpha: 38),
                    valueColor: const AlwaysStoppedAnimation<Color>(
                      AppColors.accentBrightBlue,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}