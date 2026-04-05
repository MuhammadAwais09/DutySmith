// lib/models/attendance_model.dart
class AttendanceModel {
  final String date;
  final String? checkIn;
  final String? checkOut;
  final String status;
  final String? location;
  final String? markedBy;
  final String? markedAt;

  AttendanceModel({
    required this.date,
    this.checkIn,
    this.checkOut,
    required this.status,
    this.location,
    this.markedBy,
    this.markedAt,
  });

  factory AttendanceModel.fromMap(Map<String, dynamic> map, String date) {
    return AttendanceModel(
      date: date,
      checkIn: map['checkIn'],
      checkOut: map['checkOut'],
      status: map['status'] ?? 'absent',
      location: map['location'],
      markedBy: map['markedBy'],
      markedAt: map['markedAt'],
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'checkIn': checkIn,
      'checkOut': checkOut,
      'status': status,
      'location': location,
      'markedBy': markedBy,
      'markedAt': markedAt,
    };
  }
}