import 'package:flutter/material.dart';
import 'package:dutysmith_app/core/theme/app_colors.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool darkMode = false;
  bool notifications = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Settings',
                  style: TextStyle(
                      color: AppColors.primaryDarkBlue,
                      fontWeight: FontWeight.bold,
                      fontSize: 22)),
              const SizedBox(height: 20),
              SwitchListTile(
                title: const Text('Enable App Notifications'),
                value: notifications,
                onChanged: (v) => setState(() => notifications = v),
                activeColor: AppColors.accentBrightBlue,
              ),
              SwitchListTile(
                title: const Text('Dark Mode'),
                value: darkMode,
                onChanged: (v) => setState(() => darkMode = v),
                activeColor: AppColors.accentBrightBlue,
              ),
              const Divider(),
              ListTile(
                leading: const Icon(Icons.info_outline, color: AppColors.darkGrey),
                title: const Text('App version 1.0.0'),
                onTap: () {},
              ),
            ],
          ),
        ),
      ),
    );
  }
}