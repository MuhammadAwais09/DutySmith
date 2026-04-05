// lib/models/user_model.dart
class UserModel {
  final String uid;
  final String name;
  final String email;
  final String type;
  final String? department;
  final int leaveBalance;
  final String? phone;
  final String? status;
  final String? createdAt;
  final String? createdBy;

  UserModel({
    required this.uid,
    required this.name,
    required this.email,
    required this.type,
    this.department,
    this.leaveBalance = 20,
    this.phone,
    this.status,
    this.createdAt,
    this.createdBy,
  });

  factory UserModel.fromMap(Map<String, dynamic> map, String uid) {
    return UserModel(
      uid: uid,
      name: map['name'] ?? '',
      email: map['email'] ?? '',
      type: map['type'] ?? 'Employee',
      department: map['department'],
      leaveBalance: map['leaveBalance'] ?? 20,
      phone: map['phone'],
      status: map['status'],
      createdAt: map['createdAt'],
      createdBy: map['createdBy'],
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'uid': uid,
      'name': name,
      'email': email,
      'type': type,
      'department': department,
      'leaveBalance': leaveBalance,
      'phone': phone,
      'status': status,
      'createdAt': createdAt,
      'createdBy': createdBy,
    };
  }

  String get initials {
    if (name.isEmpty) return 'U';
    final parts = name.trim().split(' ');
    if (parts.length == 1) {
      return parts[0][0].toUpperCase();
    } else {
      return '${parts[0][0]}${parts[parts.length - 1][0]}'.toUpperCase();
    }
  }

  String get firstName {
    if (name.isEmpty) return 'User';
    final parts = name.trim().split(' ');
    return parts[0];
  }

  bool get isAdmin => type.toLowerCase() == 'admin';
  bool get isStudent => type.toLowerCase() == 'student';
  bool get isTeacher => type.toLowerCase() == 'teacher';
  bool get isStaff => type.toLowerCase() == 'staff';
  bool get isActive => status?.toLowerCase() == 'active' || status == null;
}