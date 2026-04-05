// lib/services/auth_service.dart
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_database/firebase_database.dart';
import '../models/user_model.dart';

class AuthService {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final DatabaseReference _database = FirebaseDatabase.instance.ref();

  User? get currentUser => _auth.currentUser;
  Stream<User?> get authStateChanges => _auth.authStateChanges();

  Future<UserModel?> signIn(String email, String password) async {
    try {
      final UserCredential result = await _auth.signInWithEmailAndPassword(
        email: email.trim(),
        password: password,
      );

      if (result.user != null) {
        final snapshot = await _database.child('users/${result.user!.uid}').get();
        
        if (snapshot.exists) {
          final userData = Map<String, dynamic>.from(snapshot.value as Map);
          
          // Block admin accounts from mobile app
          if (userData['type'] == 'Admin') {
            await _auth.signOut();
            throw Exception('Admin accounts cannot access the mobile app. Please use the web portal.');
          }
          
          return UserModel.fromMap(userData, result.user!.uid);
        }
      }
      return null;
    } on FirebaseAuthException catch (e) {
      throw _handleAuthException(e);
    }
  }

  Future<void> sendPasswordResetEmail(String email) async {
    try {
      await _auth.sendPasswordResetEmail(email: email.trim());
    } on FirebaseAuthException catch (e) {
      throw _handleAuthException(e);
    }
  }

  Future<void> signOut() async {
    await _auth.signOut();
  }

  Future<UserModel?> getCurrentUserData() async {
    if (currentUser == null) return null;

    final snapshot = await _database.child('users/${currentUser!.uid}').get();
    
    if (snapshot.exists) {
      final userData = Map<String, dynamic>.from(snapshot.value as Map);
      return UserModel.fromMap(userData, currentUser!.uid);
    }
    return null;
  }

  String _handleAuthException(FirebaseAuthException e) {
    switch (e.code) {
      case 'user-not-found':
        return 'No user found with this email address.';
      case 'wrong-password':
        return 'Incorrect password. Please try again.';
      case 'invalid-email':
        return 'The email address is invalid.';
      case 'user-disabled':
        return 'This account has been disabled.';
      case 'too-many-requests':
        return 'Too many attempts. Please try again later.';
      case 'invalid-credential':
        return 'Invalid email or password.';
      default:
        return e.message ?? 'An error occurred. Please try again.';
    }
  }
}