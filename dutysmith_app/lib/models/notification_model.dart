// lib/models/notification_model.dart
import 'package:flutter/material.dart';

class NotificationModel {
  final String id;
  final String userId;
  final String title;
  final String message;
  final String type;
  final bool read;
  final String? createdAt;
  final String? createdBy;

  NotificationModel({
    required this.id,
    required this.userId,
    required this.title,
    required this.message,
    required this.type,
    required this.read,
    this.createdAt,
    this.createdBy,
  });

  factory NotificationModel.fromMap(Map<String, dynamic> map, String id) {
    return NotificationModel(
      id: id,
      userId: map['userId'] ?? '',
      title: map['title'] ?? '',
      message: map['message'] ?? '',
      type: map['type'] ?? 'general',
      read: map['read'] ?? false,
      createdAt: map['createdAt'],
      createdBy: map['createdBy'],
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'userId': userId,
      'title': title,
      'message': message,
      'type': type,
      'read': read,
      'createdAt': createdAt,
      'createdBy': createdBy,
    };
  }

  IconData get icon {
    switch (type) {
      case 'duty_assigned':
        return Icons.assignment;
      case 'leave_approved':
        return Icons.check_circle;
      case 'leave_rejected':
        return Icons.cancel;
      case 'urgent':
        return Icons.warning;
      default:
        return Icons.notifications;
    }
  }
}