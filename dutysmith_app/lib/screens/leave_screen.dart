import 'package:flutter/material.dart';
import 'package:dutysmith_app/core/theme/app_colors.dart';

class LeaveScreen extends StatefulWidget {
  const LeaveScreen({super.key});

  @override
  State<LeaveScreen> createState() => _LeaveScreenState();
}

class _LeaveScreenState extends State<LeaveScreen> {
  DateTime? startDate;
  DateTime? endDate;
  final TextEditingController _reasonController = TextEditingController();

  Future<void> _selectDate(bool isStart) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2023),
      lastDate: DateTime(2030),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(primary: AppColors.accentBrightBlue),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() {
        if (isStart) {
          startDate = picked;
        } else {
          endDate = picked;
        }
      });
    }
  }

  void _submitLeave() {
    if (startDate == null || endDate == null || _reasonController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill all fields')),
      );
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Leave request submitted!')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Apply for Leave',
                style: TextStyle(
                    fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.primaryDarkBlue),
              ),
              const SizedBox(height: 16),
              TextField(
                readOnly: true,
                decoration: InputDecoration(
                  labelText: 'Start Date',
                  suffixIcon: const Icon(Icons.calendar_today),
                ),
                onTap: () => _selectDate(true),
                controller: TextEditingController(
                    text: startDate == null ? '' : startDate.toString().split(' ')[0]),
              ),
              const SizedBox(height: 12),
              TextField(
                readOnly: true,
                decoration: InputDecoration(
                  labelText: 'End Date',
                  suffixIcon: const Icon(Icons.calendar_today),
                ),
                onTap: () => _selectDate(false),
                controller: TextEditingController(
                    text: endDate == null ? '' : endDate.toString().split(' ')[0]),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _reasonController,
                decoration: const InputDecoration(
                    labelText: 'Reason', border: OutlineInputBorder(), alignLabelWithHint: true),
                maxLines: 3,
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.accentBrightBlue,
                    minimumSize: const Size(double.infinity, 48)),
                onPressed: _submitLeave,
                child: const Text('Submit Request', style: TextStyle(color: AppColors.white)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}