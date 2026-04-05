// lib/models/leave_model.dart
class LeaveModel {
  final String id;
  final String employeeId;
  final String startDate;
  final String endDate;
  final String reason;
  final String status;
  final String? requestedAt;
  final String? approvedBy;
  final String? approvedAt;

  LeaveModel({
    required this.id,
    required this.employeeId,
    required this.startDate,
    required this.endDate,
    required this.reason,
    required this.status,
    this.requestedAt,
    this.approvedBy,
    this.approvedAt,
  });

  factory LeaveModel.fromMap(Map<String, dynamic> map, String id) {
    return LeaveModel(
      id: id,
      employeeId: map['employeeId'] ?? '',
      startDate: map['startDate'] ?? '',
      endDate: map['endDate'] ?? '',
      reason: map['reason'] ?? '',
      status: map['status'] ?? 'pending',
      requestedAt: map['requestedAt'],
      approvedBy: map['approvedBy'],
      approvedAt: map['approvedAt'],
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'employeeId': employeeId,
      'startDate': startDate,
      'endDate': endDate,
      'reason': reason,
      'status': status,
      'requestedAt': requestedAt,
      'approvedBy': approvedBy,
      'approvedAt': approvedAt,
    };
  }

  int get daysCount {
    try {
      final start = DateTime.parse(startDate);
      final end = DateTime.parse(endDate);
      return end.difference(start).inDays + 1;
    } catch (e) {
      return 1;
    }
  }
}