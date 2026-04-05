// lib/utils/helpers.dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import 'app_colors.dart'; // ✅ FIXED
import 'constants.dart';  // (keep if you use strings/assets later)

class Helpers {
  static String formatDate(String date) {
    try {
      final DateTime parsed = DateTime.parse(date);
      return DateFormat('MMM dd, yyyy').format(parsed);
    } catch (e) {
      return date;
    }
  }

  static String formatTime(String time) {
    try {
      final parts = time.split(':');
      final hour = int.parse(parts[0]);
      final minute = parts[1];
      final period = hour >= 12 ? 'PM' : 'AM';
      final displayHour = hour > 12 ? hour - 12 : (hour == 0 ? 12 : hour);
      return '$displayHour:$minute $period';
    } catch (e) {
      return time;
    }
  }

  static String formatDateTime(String dateTime) {
    try {
      final DateTime parsed = DateTime.parse(dateTime);
      return DateFormat('MMM dd, yyyy - hh:mm a').format(parsed);
    } catch (e) {
      return dateTime;
    }
  }

  static Color getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'present':
      case 'approved':
      case 'completed':
        return AppColors.success;
      case 'absent':
      case 'rejected':
      case 'cancelled':
        return AppColors.danger;
      case 'late':
      case 'pending':
      case 'scheduled':
        return AppColors.warning;
      default:
        return AppColors.info;
    }
  }

  static IconData getStatusIcon(String status) {
    switch (status.toLowerCase()) {
      case 'present':
      case 'approved':
      case 'completed':
        return Icons.check_circle;
      case 'absent':
      case 'rejected':
      case 'cancelled':
        return Icons.cancel;
      case 'late':
        return Icons.access_time;
      case 'pending':
      case 'scheduled':
        return Icons.pending;
      default:
        return Icons.info;
    }
  }

  static void showSnackBar(
    BuildContext context,
    String message, {
    bool isError = false,
  }) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? AppColors.danger : AppColors.success,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  static String getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) {
      return 'Good Morning';
    } else if (hour < 17) {
      return 'Good Afternoon';
    } else {
      return 'Good Evening';
    }
  }
}