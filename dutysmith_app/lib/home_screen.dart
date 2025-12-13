import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';

import 'core/theme/app_colors.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = FirebaseAuth.instance.currentUser;

    return WillPopScope(
      onWillPop: () async => false, // 🚫 disables Android back button
      child: Scaffold(
        appBar: AppBar(
          automaticallyImplyLeading: false, // 🚫 removes top-left back arrow
          title: const Text('Home'),
          backgroundColor: AppColors.primaryDarkBlue,
          foregroundColor: Colors.white,
          actions: [
            IconButton(
              tooltip: 'Logout',
              icon: const Icon(Icons.logout),
              onPressed: () async {
                await FirebaseAuth.instance.signOut();
                if (!context.mounted) return;
                Navigator.of(context).pushReplacementNamed('/login');
              },
            ),
          ],
        ),
        body: Center(
          child: Text(
            'Logged in as:\n${user?.email ?? 'Unknown'}',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 16),
          ),
        ),
      ),
    );
  }
}