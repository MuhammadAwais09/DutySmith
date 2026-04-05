// lib/providers/app_provider.dart
import 'package:flutter/material.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';
import '../services/database_service.dart';

class AppProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();
  final DatabaseService _databaseService = DatabaseService();

  UserModel? _currentUser;
  bool _isLoading = false;
  int _unreadNotifications = 0;

  UserModel? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  int get unreadNotifications => _unreadNotifications;
  bool get isLoggedIn => _currentUser != null;

  Future<bool> initialize() async {
    _isLoading = true;
    notifyListeners();

    try {
      _currentUser = await _authService.getCurrentUserData();
      if (_currentUser != null) {
        await _loadUnreadNotifications();
      }
      _isLoading = false;
      notifyListeners();
      return _currentUser != null;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<String?> login(String email, String password) async {
    _isLoading = true;
    notifyListeners();

    try {
      _currentUser = await _authService.signIn(email, password);
      if (_currentUser != null) {
        await _loadUnreadNotifications();
      }
      _isLoading = false;
      notifyListeners();
      return null;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return e.toString().replaceAll('Exception: ', '');
    }
  }

  Future<String?> forgotPassword(String email) async {
    _isLoading = true;
    notifyListeners();

    try {
      await _authService.sendPasswordResetEmail(email);
      _isLoading = false;
      notifyListeners();
      return null;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return e.toString().replaceAll('Exception: ', '');
    }
  }

  Future<void> logout() async {
    await _authService.signOut();
    _currentUser = null;
    _unreadNotifications = 0;
    notifyListeners();
  }

  Future<void> _loadUnreadNotifications() async {
    if (_currentUser != null) {
      _unreadNotifications =
          await _databaseService.getUnreadNotificationCount(_currentUser!.uid);
      notifyListeners();
    }
  }

  Future<void> refreshNotificationCount() async {
    await _loadUnreadNotifications();
  }

  Future<void> refreshUserData() async {
    _currentUser = await _authService.getCurrentUserData();
    notifyListeners();
  }
}