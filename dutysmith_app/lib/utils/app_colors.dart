import 'package:flutter/material.dart';

class AppColors {
  // Primary Dark Blue (Deep Navy)
  static const Color primaryDarkBlue = Color(0xFF0A2A4E);

  // Accent Bright Blue
  static const Color primaryBlue = Color(0xFF1F8FF4);
  static const Color accentBlue = Color(0xFF3498DB);

  // White
  static const Color white = Color(0xFFFFFFFF);

  // Background
  static const Color background = Color(0xFFF5F7FA);
  static const Color cardBackground = Color(0xFFFFFFFF);

  // Status Colors
  static const Color success = Color(0xFF198754);
  static const Color warning = Color(0xFFFFC107);
  static const Color danger = Color(0xFFDC3545);
  static const Color info = Color(0xFF0DCAF0);

  // Text Colors
  static const Color textPrimary = Color(0xFF2C3E50);
  static const Color textSecondary = Color(0xFF6C757D);
  static const Color darkGrey = Color(0xFF1A1A1A);

  // User Type Colors
  static const Color studentColor = Color(0xFF9C27B0);
  static const Color teacherColor = Color(0xFF2196F3);
  static const Color staffColor = Color(0xFF4CAF50);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryDarkBlue, Color(0xFF05152A)],
  );

  static const LinearGradient accentGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryBlue, Color(0xFF0D6EFD)],
  );
}