import 'package:flutter/material.dart';
import 'package:dutysmith_app/core/theme/app_colors.dart';

class ScheduleScreen extends StatelessWidget {
  const ScheduleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.white,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                'My Schedule',
                style: TextStyle(
                  color: AppColors.primaryDarkBlue,
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            Expanded(
              child: ListView.builder(
                itemCount: 7,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemBuilder: (context, index) {
                  return Card(
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    margin: const EdgeInsets.symmetric(vertical: 8),
                    elevation: 1,
                    child: ListTile(
                      leading: const Icon(Icons.access_time, color: AppColors.accentBrightBlue),
                      title: Text('Duty ${index + 1}: Shift ${8 + index}:00'),
                      subtitle: const Text('Location: Main Branch'),
                      trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 16),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}