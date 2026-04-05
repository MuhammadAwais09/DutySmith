// lib/screens/attendance_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';
import '../services/database_service.dart';
import '../models/attendance_model.dart';
import '../utils/constants.dart';
import '../utils/helpers.dart';
import '../utils/app_colors.dart'; // ✅ FIXED

class AttendanceScreen extends StatelessWidget {
  const AttendanceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = Provider.of<AppProvider>(context).currentUser;

    if (user == null) {
      return const Center(child: CircularProgressIndicator());
    }

    return StreamBuilder<List<AttendanceModel>>(
      stream: DatabaseService().getAttendanceStream(user.uid),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        final attendance = snapshot.data ?? [];

        if (attendance.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.fact_check_outlined,
                  size: 80,
                  color: Colors.grey.shade300,
                ),
                const SizedBox(height: 16),
                const Text(
                  'No attendance records yet',
                  style: TextStyle(
                    fontSize: 18,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: attendance.length,
          itemBuilder: (context, index) {
            final record = attendance[index];
            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Helpers.getStatusColor(record.status).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    Helpers.getStatusIcon(record.status),
                    color: Helpers.getStatusColor(record.status),
                  ),
                ),
                title: Text(
                  Helpers.formatDate(record.date),
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
                subtitle: Text(
                  '${record.checkIn != null ? Helpers.formatTime(record.checkIn!) : '--'} - '
                  '${record.checkOut != null ? Helpers.formatTime(record.checkOut!) : '--'}',
                ),
                trailing: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Helpers.getStatusColor(record.status).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    record.status.toUpperCase(),
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Helpers.getStatusColor(record.status),
                    ),
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }
}