import 'package:flutter/material.dart';
import 'package:dutysmith_app/core/theme/app_colors.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('My Profile',
                style: TextStyle(
                    color: AppColors.primaryDarkBlue,
                    fontSize: 22,
                    fontWeight: FontWeight.bold)),
            const SizedBox(height: 20),
            ListTile(
              leading: const CircleAvatar(
                backgroundColor: AppColors.accentBrightBlue,
                radius: 28,
                child: Icon(Icons.person, color: AppColors.white, size: 30),
              ),
              title: const Text('John Doe',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
              subtitle: const Text('Software Engineer'),
              trailing:
                  IconButton(onPressed: () {}, icon: const Icon(Icons.edit, color: AppColors.accentBrightBlue)),
            ),
            const Divider(),
            const ListTile(
              leading: Icon(Icons.email_outlined, color: AppColors.darkGrey),
              title: Text('john.doe@dutysmith.io'),
            ),
            const ListTile(
              leading: Icon(Icons.phone, color: AppColors.darkGrey),
              title: Text('+92 300 123 4567'),
            ),
            const ListTile(
              leading: Icon(Icons.business_outlined, color: AppColors.darkGrey),
              title: Text('Department: HR & Admin'),
            ),
          ]),
        ),
      ),
    );
  }
}