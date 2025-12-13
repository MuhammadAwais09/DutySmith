import 'package:flutter/material.dart';
import 'package:dutysmith_app/core/theme/app_colors.dart';

class AttendanceScreen extends StatelessWidget {
  const AttendanceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text(
              'Attendance Records',
              style: TextStyle(
                  color: AppColors.primaryDarkBlue,
                  fontSize: 22,
                  fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: ListView.builder(
                itemCount: 10,
                itemBuilder: (context, i) {
                  final status = i % 3 == 0
                      ? 'Absent'
                      : i % 2 == 0
                          ? 'Late'
                          : 'Present';
                  final color = status == 'Present'
                      ? Colors.green
                      : status == 'Late'
                          ? Colors.orange
                          : Colors.red;
                  return Card(
                    margin: const EdgeInsets.symmetric(vertical: 6),
                    child: ListTile(
                      leading: Icon(Icons.calendar_today, color: AppColors.accentBrightBlue),
                      title: Text('Date: 2025-12-${10 + i}'),
                      trailing: Text(status, style: TextStyle(color: color, fontWeight: FontWeight.bold)),
                    ),
                  );
                },
              ),
            )
          ]),
        ),
      ),
    );
  }
}