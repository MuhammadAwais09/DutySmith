// lib/models/duty_model.dart
class DutyModel {
  final String id;
  final String employeeId;
  final String title;
  final String date;
  final String startTime;
  final String endTime;
  final String location;
  final String status;
  final String? createdBy;
  final String? createdAt;

  DutyModel({
    required this.id,
    required this.employeeId,
    required this.title,
    required this.date,
    required this.startTime,
    required this.endTime,
    required this.location,
    required this.status,
    this.createdBy,
    this.createdAt,
  });

  factory DutyModel.fromMap(Map<String, dynamic> map, String id) {
    return DutyModel(
      id: id,
      employeeId: map['employeeId'] ?? '',
      title: map['title'] ?? '',
      date: map['date'] ?? '',
      startTime: map['startTime'] ?? '',
      endTime: map['endTime'] ?? '',
      location: map['location'] ?? '',
      status: map['status'] ?? 'scheduled',
      createdBy: map['createdBy'],
      createdAt: map['createdAt'],
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'employeeId': employeeId,
      'title': title,
      'date': date,
      'startTime': startTime,
      'endTime': endTime,
      'location': location,
      'status': status,
      'createdBy': createdBy,
      'createdAt': createdAt,
    };
  }
}