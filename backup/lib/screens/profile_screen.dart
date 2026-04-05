import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_database/firebase_database.dart';
import 'package:flutter/material.dart';
import 'package:dutysmith_app/core/theme/app_colors.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _userData;
  bool _loading = true;
  String? _errorText;
  final _auth = FirebaseAuth.instance;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final user = _auth.currentUser;
      if (user == null) {
        setState(() {
          _errorText = 'No authenticated user.';
          _loading = false;
        });
        return;
      }

      final dbRef = FirebaseDatabase.instance.ref('users/${user.uid}');
      final snapshot = await dbRef.get();
      if (snapshot.exists) {
        final data = Map<String, dynamic>.from(snapshot.value as Map);
        setState(() {
          _userData = data;
          _loading = false;
        });
      } else {
        setState(() {
          _errorText = 'User profile not found.';
          _loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorText = 'Failed to load profile.';
        _loading = false;
      });
    }
  }

  Future<void> _sendPasswordReset() async {
    final user = _auth.currentUser;
    if (user == null || user.email == null) return;

    try {
      await _auth.sendPasswordResetEmail(email: user.email!);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Password reset link sent to your email.'),
          backgroundColor: Colors.green,
        ),
      );
    } on FirebaseAuthException catch (e) {
      final msg = e.code == 'user-not-found'
          ? 'No user found for this email.'
          : e.message ?? 'Failed to send password reset email.';
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(msg),
          backgroundColor: Colors.redAccent,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentUser = _auth.currentUser;

    return Scaffold(
      backgroundColor: AppColors.white,
      appBar: AppBar(
        backgroundColor: AppColors.primaryDarkBlue,
        foregroundColor: AppColors.white,
        title: const Text('My Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Reload',
            onPressed: _loadProfile,
          )
        ],
      ),
      body: SafeArea(
        child: _loading
            ? const Center(
                child: CircularProgressIndicator(color: AppColors.accentBrightBlue),
              )
            : _errorText != null
                ? Center(child: Text(_errorText!))
                : _userData == null
                    ? const Center(child: Text('No user data found.'))
                    : Padding(
                        padding: const EdgeInsets.all(16),
                        child: ListView(
                          children: [
                            // ---- Profile header ----
                            ListTile(
                              leading: const CircleAvatar(
                                backgroundColor: AppColors.accentBrightBlue,
                                radius: 28,
                                child:
                                    Icon(Icons.person, color: AppColors.white, size: 30),
                              ),
                              title: Text(
                                _userData?['name'] ?? currentUser?.displayName ?? 'Unknown',
                                style: const TextStyle(
                                    fontWeight: FontWeight.bold, fontSize: 18),
                              ),
                              subtitle: Text(
                                _userData?['type'] ?? 'Employee',
                                style: const TextStyle(color: AppColors.darkGrey),
                              ),
                            ),
                            const Divider(),
                            ListTile(
                              leading: const Icon(Icons.email_outlined,
                                  color: AppColors.darkGrey),
                              title: Text(_userData?['email'] ?? currentUser?.email ?? ''),
                            ),
                            if (_userData?['type'] != null)
                              ListTile(
                                leading: const Icon(Icons.badge_outlined,
                                    color: AppColors.darkGrey),
                                title: Text('User Type: ${_userData!['type']}'),
                              ),
                            if (_userData?['department'] != null)
                              ListTile(
                                leading: const Icon(Icons.business_outlined,
                                    color: AppColors.darkGrey),
                                title:
                                    Text('Department: ${_userData!['department']}'),
                              ),
                            const SizedBox(height: 8),
                            // ---- Reset password section ----
                            const Divider(),
                            ListTile(
                              leading: const Icon(Icons.lock_reset_rounded,
                                  color: AppColors.accentBrightBlue),
                              title: const Text('Reset Password'),
                              subtitle: const Text(
                                  'Send reset email to your registered address'),
                              onTap: _sendPasswordReset,
                            ),
                            const Divider(),
                            const SizedBox(height: 20),
                            Text(
                              'Account Info',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                    color: AppColors.primaryDarkBlue,
                                    fontWeight: FontWeight.bold,
                                  ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'UID: ${currentUser?.uid ?? 'Unknown'}',
                              style: const TextStyle(fontSize: 13, color: AppColors.darkGrey),
                            ),
                            if (_userData?['createdAt'] != null)
                              Text(
                                'Created: ${_userData!['createdAt'].toString()}',
                                style: const TextStyle(
                                    fontSize: 13, color: AppColors.darkGrey),
                              ),
                          ],
                        ),
                      ),
      ),
    );
  }
}