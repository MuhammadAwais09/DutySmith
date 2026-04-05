// lib/services/chatbot_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../utils/constants.dart';

class ChatbotService {
  // Send message to chatbot API
  Future<Map<String, dynamic>> sendMessage(String message, String userId) async {
    try {
      final response = await http.post(
        Uri.parse(AppStrings.chatEndpoint),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode({
          'message': message,
          'user_id': userId,
        }),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get response from chatbot');
      }
    } catch (e) {
      // Return fallback response if API is unavailable
      return {
        'response': _getFallbackResponse(message),
        'intent': 'fallback',
        'confidence': 0.0,
        'model_active': false,
      };
    }
  }

  // Fallback responses when API is unavailable
  String _getFallbackResponse(String message) {
    final lowerMessage = message.toLowerCase();

    if (lowerMessage.contains('leave') && lowerMessage.contains('balance')) {
      return '📋 To check your leave balance, please go to the Leave section in the app. You can see your current balance and apply for new leaves there.';
    } else if (lowerMessage.contains('duty') || lowerMessage.contains('schedule')) {
      return '📅 To view your duty schedule, please check the Duties section. You\'ll find all your upcoming and past duties there.';
    } else if (lowerMessage.contains('attendance')) {
      return '✅ Your attendance records are available in the Attendance section. You can also check in and check out from there.';
    } else if (lowerMessage.contains('help')) {
      return '🤖 I can help you with:\n\n• Checking leave balance\n• Viewing duty schedules\n• Attendance information\n• General queries\n\nJust ask me anything!';
    } else if (lowerMessage.contains('hello') || lowerMessage.contains('hi')) {
      return 'Hello! 👋 How can I assist you today? You can ask me about your leaves, duties, or attendance.';
    } else {
      return 'I\'m here to help! You can ask me about:\n\n• Leave balance and requests\n• Duty schedules\n• Attendance records\n\nPlease try rephrasing your question or use the app navigation for more options.';
    }
  }

  // Check chatbot status
  Future<bool> checkStatus() async {
    try {
      final response = await http.get(
        Uri.parse('${AppStrings.baseUrl}/api/chat/status'),
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['status'] == 'online';
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}