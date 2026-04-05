// ignore_for_file: library_private_types_in_public_api

import 'package:flutter/material.dart';
import 'package:dutysmith_app/core/theme/app_colors.dart';
import 'package:dutysmith_app/home_screen.dart';
import 'package:dutysmith_app/screens/schedule_screen.dart';
import 'package:dutysmith_app/screens/leave_screen.dart';
import 'package:dutysmith_app/screens/attendance_screen.dart';
import 'package:dutysmith_app/screens/chatbot_screen.dart';
import 'package:dutysmith_app/screens/notifications_screen.dart';
import 'package:dutysmith_app/screens/profile_screen.dart';
import 'package:dutysmith_app/screens/settings_screen.dart';
import 'package:dutysmith_app/login_screen.dart';

class MenuScreen extends StatefulWidget {
  const MenuScreen({super.key});

  @override
  _MenuScreenState createState() => _MenuScreenState();
}

class _MenuScreenState extends State<MenuScreen> with SingleTickerProviderStateMixin {
  int _selectedIndex = 0;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  // All main pages for navigation
  final List<Widget> _screens = const [
    HomeScreen(),
    ScheduleScreen(),
    LeaveScreen(),
    AttendanceScreen(),
    ChatbotScreen(),
    NotificationsScreen(),
    ProfileScreen(),
    SettingsScreen(),
  ];

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 250),
      value: 1.0,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0)
        .animate(CurvedAnimation(parent: _animationController, curve: Curves.easeInOut));
    _animationController.forward();
  }

  void _logout() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const LoginScreen()),
    );
  }

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
      _animationController.forward(from: 0.0);
    });
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.white,
      appBar: AppBar(
        title: const Text('DutySmith'),
        backgroundColor: AppColors.primaryDarkBlue,
        foregroundColor: AppColors.white,
        elevation: 0,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(bottom: Radius.circular(14)),
        ),
      ),
      drawer: Drawer(
        child: Container(
          color: AppColors.white,
          child: ListView(
            padding: EdgeInsets.zero,
            children: [
              DrawerHeader(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      AppColors.primaryDarkBlue,
                      AppColors.accentBrightBlue,
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: const Align(
                  alignment: Alignment.bottomLeft,
                  child: Text(
                    'Employee Portal',
                    style: TextStyle(
                      color: AppColors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ),
              _buildDrawerItem(Icons.dashboard, 'Dashboard', 0),
              _buildDrawerItem(Icons.calendar_month, 'My Schedule', 1),
              _buildDrawerItem(Icons.beach_access, 'Apply for Leave', 2),
              _buildDrawerItem(Icons.check_circle, 'Attendance', 3),
              _buildDrawerItem(Icons.chat, 'Chatbot Assistant', 4),
              _buildDrawerItem(Icons.notifications, 'Notifications', 5),
              _buildDrawerItem(Icons.person, 'Profile', 6),
              _buildDrawerItem(Icons.settings, 'Settings', 7),
              const Divider(),
              ListTile(
                leading: const Icon(Icons.logout, color: Colors.redAccent),
                title: const Text(
                  'Logout',
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
                onTap: () {
                  Navigator.pop(context);
                  _logout();
                },
              ),
            ],
          ),
        ),
      ),

      // Animated Screen
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: IndexedStack(
          index: _selectedIndex,
          children: _screens,
        ),
      ),

      // Bottom Nav for primary sections
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex < 4 ? _selectedIndex : 0,
        onTap: _onItemTapped,
        backgroundColor: AppColors.primaryDarkBlue,
        selectedItemColor: AppColors.accentBrightBlue,
        unselectedItemColor: AppColors.white.withOpacity(0.6),
        type: BottomNavigationBarType.fixed,
        selectedFontSize: 14,
        unselectedFontSize: 12,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.calendar_month),
            label: 'Schedule',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.beach_access),
            label: 'Leave',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.check_circle),
            label: 'Attendance',
          ),
        ],
      ),
    );
  }

  Widget _buildDrawerItem(IconData icon, String title, int index) {
    final bool isSelected = _selectedIndex == index;

    return ListTile(
      leading: Icon(
        icon,
        color: isSelected ? AppColors.accentBrightBlue : AppColors.darkGrey,
      ),
      title: Text(
        title,
        style: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w500,
          color: isSelected ? AppColors.accentBrightBlue : AppColors.darkGrey,
        ),
      ),
      selected: isSelected,
      selectedTileColor: AppColors.accentBrightBlue.withOpacity(0.1),
      onTap: () {
        setState(() {
          _selectedIndex = index;
          _animationController.forward(from: 0.0);
        });
        Navigator.pop(context);
      },
    );
  }
}