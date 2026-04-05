// lib/services/database_service.dart
import 'package:firebase_database/firebase_database.dart';
import '../models/duty_model.dart';
import '../models/attendance_model.dart';
import '../models/leave_model.dart';
import '../models/notification_model.dart';

class DatabaseService {
  final DatabaseReference _database = FirebaseDatabase.instance.ref();

  // ==================== DUTIES ====================

  Stream<List<DutyModel>> getDutiesStream(String employeeId) {
    return _database
        .child('duties')
        .orderByChild('employeeId')
        .equalTo(employeeId)
        .onValue
        .map((event) {
      final List<DutyModel> duties = [];
      if (event.snapshot.exists) {
        final Map<dynamic, dynamic> data =
            event.snapshot.value as Map<dynamic, dynamic>;
        data.forEach((key, value) {
          duties.add(DutyModel.fromMap(Map<String, dynamic>.from(value), key));
        });
      }
      duties.sort((a, b) => b.date.compareTo(a.date));
      return duties;
    });
  }

  Future<List<DutyModel>> getUpcomingDuties(String employeeId) async {
    final today = DateTime.now().toIso8601String().split('T')[0];
    final snapshot = await _database
        .child('duties')
        .orderByChild('employeeId')
        .equalTo(employeeId)
        .get();

    final List<DutyModel> duties = [];
    if (snapshot.exists) {
      final Map<dynamic, dynamic> data =
          snapshot.value as Map<dynamic, dynamic>;
      data.forEach((key, value) {
        final duty = DutyModel.fromMap(Map<String, dynamic>.from(value), key);
        if (duty.date.compareTo(today) >= 0 && duty.status == 'scheduled') {
          duties.add(duty);
        }
      });
    }
    duties.sort((a, b) => a.date.compareTo(b.date));
    return duties;
  }

  // ==================== ATTENDANCE ====================

  Stream<List<AttendanceModel>> getAttendanceStream(String employeeId) {
    return _database
        .child('attendance/$employeeId')
        .onValue
        .map((event) {
      final List<AttendanceModel> attendance = [];
      if (event.snapshot.exists) {
        final Map<dynamic, dynamic> data =
            event.snapshot.value as Map<dynamic, dynamic>;
        data.forEach((date, value) {
          attendance.add(
              AttendanceModel.fromMap(Map<String, dynamic>.from(value), date));
        });
      }
      attendance.sort((a, b) => b.date.compareTo(a.date));
      return attendance;
    });
  }

  Future<AttendanceModel?> getTodayAttendance(String employeeId) async {
    final today = DateTime.now().toIso8601String().split('T')[0];
    final snapshot =
        await _database.child('attendance/$employeeId/$today').get();

    if (snapshot.exists) {
      return AttendanceModel.fromMap(
          Map<String, dynamic>.from(snapshot.value as Map), today);
    }
    return null;
  }

  Future<void> checkIn(String employeeId, String location) async {
    final today = DateTime.now().toIso8601String().split('T')[0];
    final now = DateTime.now();
    final timeString =
        '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';

    final status = now.hour >= 9 ? 'late' : 'present';

    await _database.child('attendance/$employeeId/$today').update({
      'checkIn': timeString,
      'status': status,
      'location': location,
      'markedAt': now.toIso8601String(),
      'markedBy': employeeId,
    });
  }

  Future<void> checkOut(String employeeId) async {
    final today = DateTime.now().toIso8601String().split('T')[0];
    final now = DateTime.now();
    final timeString =
        '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';

    await _database.child('attendance/$employeeId/$today').update({
      'checkOut': timeString,
    });
  }

  Future<Map<String, int>> getAttendanceSummary(String employeeId) async {
    final snapshot = await _database.child('attendance/$employeeId').get();
    
    int present = 0;
    int late = 0;
    int absent = 0;

    if (snapshot.exists) {
      final Map<dynamic, dynamic> data =
          snapshot.value as Map<dynamic, dynamic>;
      data.forEach((key, value) {
        final status = value['status'] ?? 'absent';
        switch (status) {
          case 'present':
            present++;
            break;
          case 'late':
            late++;
            break;
          case 'absent':
            absent++;
            break;
        }
      });
    }

    return {
      'present': present,
      'late': late,
      'absent': absent,
      'total': present + late + absent,
    };
  }

  // ==================== LEAVE REQUESTS ====================

  Stream<List<LeaveModel>> getLeaveRequestsStream(String employeeId) {
    return _database
        .child('leave_requests')
        .orderByChild('employeeId')
        .equalTo(employeeId)
        .onValue
        .map((event) {
      final List<LeaveModel> leaves = [];
      if (event.snapshot.exists) {
        final Map<dynamic, dynamic> data =
            event.snapshot.value as Map<dynamic, dynamic>;
        data.forEach((key, value) {
          leaves.add(LeaveModel.fromMap(Map<String, dynamic>.from(value), key));
        });
      }
      leaves.sort((a, b) => (b.requestedAt ?? '').compareTo(a.requestedAt ?? ''));
      return leaves;
    });
  }

  Future<void> submitLeaveRequest({
    required String employeeId,
    required String startDate,
    required String endDate,
    required String reason,
  }) async {
    final newRef = _database.child('leave_requests').push();
    await newRef.set({
      'employeeId': employeeId,
      'startDate': startDate,
      'endDate': endDate,
      'reason': reason,
      'status': 'pending',
      'requestedAt': DateTime.now().toIso8601String(),
    });
  }

  // ==================== NOTIFICATIONS ====================

  Stream<List<NotificationModel>> getNotificationsStream(String employeeId) {
    return _database
        .child('notifications')
        .orderByChild('userId')
        .equalTo(employeeId)
        .onValue
        .map((event) {
      final List<NotificationModel> notifications = [];
      if (event.snapshot.exists) {
        final Map<dynamic, dynamic> data =
            event.snapshot.value as Map<dynamic, dynamic>;
        data.forEach((key, value) {
          notifications.add(
              NotificationModel.fromMap(Map<String, dynamic>.from(value), key));
        });
      }
      notifications.sort(
          (a, b) => (b.createdAt ?? '').compareTo(a.createdAt ?? ''));
      return notifications;
    });
  }

  Future<void> markNotificationAsRead(String notificationId) async {
    await _database.child('notifications/$notificationId').update({
      'read': true,
    });
  }

  Future<int> getUnreadNotificationCount(String employeeId) async {
    final snapshot = await _database
        .child('notifications')
        .orderByChild('userId')
        .equalTo(employeeId)
        .get();

    int count = 0;
    if (snapshot.exists) {
      final Map<dynamic, dynamic> data =
          snapshot.value as Map<dynamic, dynamic>;
      data.forEach((key, value) {
        if (value['read'] == false) count++;
      });
    }
    return count;
  }

  // ==================== USER DATA ====================

  Future<int> getLeaveBalance(String employeeId) async {
    final snapshot = await _database.child('users/$employeeId/leaveBalance').get();
    if (snapshot.exists) {
      return snapshot.value as int;
    }
    return 20;
  }
}