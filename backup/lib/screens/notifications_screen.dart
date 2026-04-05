import 'package:flutter/material.dart';
import 'package:dutysmith_app/core/theme/app_colors.dart';

class NotificationsScreen extends StatelessWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final notifications = List.generate(
        5,
        (i) => 'Leave Request ${i + 1} has been ${i % 2 == 0 ? 'Approved' : 'Pending'}');

    return Scaffold(
      backgroundColor: AppColors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Notifications',
                  style: TextStyle(
                      color: AppColors.primaryDarkBlue,
                      fontWeight: FontWeight.bold,
                      fontSize: 22)),
              const SizedBox(height: 12),
              Expanded(
                child: ListView.builder(
                  itemCount: notifications.length,
                  itemBuilder: (context, index) {
                    final message = notifications[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(vertical: 6),
                      child: ListTile(
                        leading:
                            const Icon(Icons.notifications, color: AppColors.accentBrightBlue),
                        title: Text(message),
                        subtitle:
                            Text('Date: 2025-12-${index + 10}', style: const TextStyle(fontSize: 12)),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}