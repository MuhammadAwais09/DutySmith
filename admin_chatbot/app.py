"""
Duty Smith Admin Portal
Version: 2.1.0

Complete Staff Appointment & Duty Management System
with Integrated AI-Powered Employee Assistance Chatbot
"""

# ==================== IMPORTS ====================

from flask import (
    Flask, render_template, request, redirect, 
    url_for, flash, jsonify, session, send_file, make_response
)
from flask_cors import CORS
from functools import wraps
from datetime import datetime, timedelta
import requests
import json
import os
import pickle
import random
import numpy as np
import csv
import io
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Import configurations
from config import Config
from firebase_config import FirebaseREST

# ==================== APP INITIALIZATION ====================

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config.from_object(Config)

CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # In production, replace with your Flutter app domain
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize Firebase
db = FirebaseREST()

@app.template_filter('strptime')
def strptime_filter(date_string, format='%Y-%m-%d'):
    """Convert string to datetime object"""
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, format)
    except (ValueError, TypeError):
        return None

@app.template_filter('strftime')
def strftime_filter(date_obj, format='%Y-%m-%d'):
    """Convert datetime object to formatted string"""
    if not date_obj:
        return ''
    try:
        if isinstance(date_obj, str):
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        return date_obj.strftime(format)
    except (ValueError, TypeError, AttributeError):
        return date_obj

@app.template_filter('days_between')
def days_between_filter(start_date, end_date):
    """Calculate days between two date strings"""
    if not start_date or not end_date:
        return '?'
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        return (end - start).days + 1
    except (ValueError, TypeError):
        return '?'

@app.template_filter('time_ago')
def time_ago_filter(date_string):
    """Convert datetime to 'time ago' format"""
    if not date_string:
        return ''
    try:
        if isinstance(date_string, str):
            date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            date_obj = date_string
        
        now = datetime.now()
        diff = now - date_obj
        
        if diff.days > 30:
            return date_obj.strftime('%b %d, %Y')
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    except:
        return date_string
# ==================== NLTK SETUP ====================

import nltk
from nltk.stem import WordNetLemmatizer

def setup_nltk():
    """Download required NLTK data packages"""
    packages = [
        ('tokenizers/punkt_tab', 'punkt_tab'),
        ('corpora/wordnet', 'wordnet')
    ]
    
    for path, package in packages:
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                nltk.download(package, quiet=True)
                print(f"✅ Downloaded NLTK package: {package}")
            except:
                print(f"⚠️ Could not download NLTK package: {package}")

setup_nltk()
lemmatizer = WordNetLemmatizer()

# ==================== CHATBOT INITIALIZATION ====================

CHATBOT_DIR = os.path.join(os.path.dirname(__file__), 'ml_chatbot')
chatbot_model = None
chatbot_words = []
chatbot_classes = []
chatbot_intents = {"intents": []}
CHATBOT_ENABLED = False

def load_chatbot_model():
    """Load the trained chatbot model and data files"""
    global chatbot_model, chatbot_words, chatbot_classes, chatbot_intents, CHATBOT_ENABLED
    
    try:
        from tensorflow.keras.models import load_model
        
        # Define file paths - support both .keras and .h5 formats
        model_path_keras = os.path.join(CHATBOT_DIR, 'chatbot_model.keras')
        model_path_h5 = os.path.join(CHATBOT_DIR, 'chatbot_model.h5')
        words_path = os.path.join(CHATBOT_DIR, 'words.pkl')
        classes_path = os.path.join(CHATBOT_DIR, 'classes.pkl')
        intents_path = os.path.join(CHATBOT_DIR, 'intents.json')
        
        # Determine which model file exists
        if os.path.exists(model_path_keras):
            model_path = model_path_keras
        elif os.path.exists(model_path_h5):
            model_path = model_path_h5
        else:
            print(f"⚠️ No model file found in {CHATBOT_DIR}")
            return False
        
        # Check required files
        if not os.path.exists(words_path):
            print(f"⚠️ Missing words.pkl")
            return False
            
        if not os.path.exists(intents_path):
            print(f"⚠️ Missing intents.json")
            return False
        
        # Load model
        chatbot_model = load_model(model_path)
        print(f"✅ Chatbot model loaded from {os.path.basename(model_path)}")
        
        # Load vocabulary
        with open(words_path, 'rb') as f:
            chatbot_words = pickle.load(f)
        print(f"✅ Loaded {len(chatbot_words)} vocabulary words")
        
        # Load intents
        with open(intents_path, 'r', encoding='utf-8') as f:
            chatbot_intents = json.load(f)
        print("✅ Loaded intents data")
        
        # Load or generate classes
        if os.path.exists(classes_path):
            with open(classes_path, 'rb') as f:
                chatbot_classes = pickle.load(f)
            print(f"✅ Loaded {len(chatbot_classes)} intent classes")
        else:
            # Extract classes from intents.json
            chatbot_classes = sorted(list(set([
                intent['tag'] for intent in chatbot_intents.get('intents', [])
            ])))
            print(f"✅ Generated {len(chatbot_classes)} intent classes from intents.json")
            
            # Save classes.pkl for future use
            try:
                with open(classes_path, 'wb') as f:
                    pickle.dump(chatbot_classes, f)
                print(f"✅ Saved classes.pkl for future use")
            except:
                pass
        
        CHATBOT_ENABLED = True
        return True
        
    except ImportError:
        print("⚠️ TensorFlow not installed - Chatbot in fallback mode")
        # Still load intents for fallback mode
        try:
            intents_path = os.path.join(CHATBOT_DIR, 'intents.json')
            if os.path.exists(intents_path):
                with open(intents_path, 'r', encoding='utf-8') as f:
                    chatbot_intents = json.load(f)
                print("✅ Loaded intents for fallback mode")
        except:
            pass
        return False
    except Exception as e:
        print(f"⚠️ Error loading chatbot: {e}")
        return False

# Load chatbot on startup
load_chatbot_model()

# ==================== CHATBOT NLP FUNCTIONS ====================

def clean_sentence(sentence):
    """Tokenize and lemmatize input sentence"""
    if not sentence:
        return []
    try:
        tokens = nltk.word_tokenize(sentence)
        return [lemmatizer.lemmatize(w.lower()) for w in tokens]
    except Exception:
        return sentence.lower().split()

def bag_of_words(sentence):
    """Convert sentence to bag of words vector"""
    sentence_words = clean_sentence(sentence)
    bag = [1 if word in sentence_words else 0 for word in chatbot_words]
    return np.array(bag, dtype=np.float32)

def predict_intent(sentence, threshold=0.25):
    """Predict intent from user message"""
    if not CHATBOT_ENABLED or chatbot_model is None:
        return [{"intent": "fallback", "probability": 1.0}]
    
    try:
        bow = bag_of_words(sentence)
        preds = chatbot_model.predict(np.array([bow]), verbose=0)[0]
        
        results = [
            {"intent": chatbot_classes[i], "probability": float(preds[i])}
            for i in range(len(preds))
            if preds[i] > threshold
        ]
        
        results.sort(key=lambda x: x["probability"], reverse=True)
        return results if results else [{"intent": "unknown", "probability": 0.0}]
    except Exception as e:
        print(f"Prediction error: {e}")
        return [{"intent": "error", "probability": 0.0}]

def get_static_response(intents_list):
    """Get response based on predicted intent"""
    if not intents_list or intents_list[0]["intent"] in ["unknown", "error", "fallback"]:
        return "Sorry, I didn't understand that. You can ask about duties, leave balance, or attendance."
    
    tag = intents_list[0]["intent"]
    
    for intent in chatbot_intents.get("intents", []):
        if intent["tag"] == tag:
            return random.choice(intent["responses"])
    
    return "I understand your question, but I need more context."

# Fallback responses when ML model is not available
FALLBACK_RESPONSES = {
    "greeting": ["Hello! How can I help you today?", "Hi there! What can I assist you with?"],
    "leave": ["To check leave balance, please specify the employee name or use the employee selector."],
    "duty": ["For duty schedules, please check the Duties section or ask about a specific employee."],
    "attendance": ["Attendance records are available. Please specify the employee or date range."],
    "help": ["I can help with:\n• Leave balance\n• Duty schedules\n• Attendance\n• Employee info\n• Performance reports"],
    "goodbye": ["Goodbye! Have a great day!", "See you later!"],
    "default": ["I'm here to help! Ask about duties, leave, or attendance for any employee."]
}

def get_fallback_response(message):
    """Keyword-based fallback when ML model unavailable"""
    message_lower = message.lower()
    
    if any(w in message_lower for w in ['hi', 'hello', 'hey', 'good morning', 'good evening']):
        return random.choice(FALLBACK_RESPONSES["greeting"]), [{"intent": "greeting", "probability": 0.9}]
    
    if any(w in message_lower for w in ['leave', 'vacation', 'day off', 'holiday', 'balance']):
        return random.choice(FALLBACK_RESPONSES["leave"]), [{"intent": "leave_balance", "probability": 0.8}]
    
    if any(w in message_lower for w in ['duty', 'schedule', 'shift', 'assignment', 'upcoming']):
        return random.choice(FALLBACK_RESPONSES["duty"]), [{"intent": "duty_schedule", "probability": 0.8}]
    
    if any(w in message_lower for w in ['attendance', 'present', 'absent', 'check in', 'report']):
        return random.choice(FALLBACK_RESPONSES["attendance"]), [{"intent": "attendance", "probability": 0.8}]
    
    if any(w in message_lower for w in ['help', 'what can you do', 'commands', 'options']):
        return random.choice(FALLBACK_RESPONSES["help"]), [{"intent": "help", "probability": 0.9}]
    
    if any(w in message_lower for w in ['bye', 'goodbye', 'see you', 'thanks', 'thank you']):
        return random.choice(FALLBACK_RESPONSES["goodbye"]), [{"intent": "goodbye", "probability": 0.9}]
    
    return random.choice(FALLBACK_RESPONSES["default"]), [{"intent": "unknown", "probability": 0.5}]

def extract_employee_name_from_message(message, employees_cache):
    """Extract employee name from natural language query"""
    message_lower = message.lower()
    
    for emp in employees_cache:
        name_lower = emp.get('name', '').lower()
        if name_lower and name_lower in message_lower:
            return emp
        # Check first name
        first_name = name_lower.split()[0] if name_lower else ''
        if first_name and len(first_name) > 2 and first_name in message_lower:
            return emp
    
    return None

def get_admin_chatbot_response(message, employee_id=None):
    """
    Enhanced chatbot response for admin portal
    Handles employee-specific queries with Firebase data
    """
    
    # Get all employees for name extraction
    employees_cache = []
    try:
        users = db.get('users')
        if users and isinstance(users, dict):
            for uid, data in users.items():
                if isinstance(data, dict) and data.get('type') != 'Admin':
                    employees_cache.append({
                        'uid': uid,
                        'name': data.get('name', 'Unknown'),
                        'email': data.get('email', ''),
                        'type': data.get('type', 'Unknown'),
                        'department': data.get('department', 'N/A'),
                        'leaveBalance': data.get('leaveBalance', 0),
                        'phone': data.get('phone', 'N/A')
                    })
    except:
        pass
    
    # Try to extract employee from message if not provided
    target_employee = None
    if employee_id:
        target_employee = next((e for e in employees_cache if e['uid'] == employee_id), None)
    else:
        target_employee = extract_employee_name_from_message(message, employees_cache)
    
    # Get intent prediction
    if CHATBOT_ENABLED:
        intents_list = predict_intent(message)
    else:
        _, intents_list = get_fallback_response(message)
    
    if not intents_list:
        return "I'm having trouble understanding. Please try again.", [], None
    
    tag = intents_list[0]["intent"]
    message_lower = message.lower()
    
    # Handle different query types
    try:
        # Greetings
        if tag in ['greeting', 'greet'] or any(w in message_lower for w in ['hello', 'hi', 'hey']):
            return "👋 Hello! I'm your AI Admin Assistant. I can help you with:\n• Employee leave balances\n• Duty schedules\n• Attendance reports\n• Performance summaries\n\nSelect an employee or ask me anything!", intents_list, None
        
        # Help
        if tag == 'help' or 'help' in message_lower or 'what can you do' in message_lower:
            return """🤖 **AI Admin Assistant Help**

I can help you with:

📊 **Leave Management**
• "What is [Name]'s leave balance?"
• "Show pending leave requests"

📅 **Duty Schedules**
• "[Name]'s upcoming duties"
• "Today's duty assignments"

✅ **Attendance**
• "[Name]'s attendance this month"
• "Who was absent today?"

👥 **Employee Info**
• "[Name]'s contact info"
• "List all employees"

💡 **Tip:** Select an employee from the sidebar for faster queries!""", intents_list, None
        
        # Leave Balance Query
        if any(w in message_lower for w in ['leave', 'balance', 'vacation', 'day off', 'holiday']):
            if target_employee:
                leave_balance = target_employee.get('leaveBalance', 0)
                name = target_employee.get('name', 'Employee')
                
                # Get leave history
                leaves = db.get('leave_requests')
                pending = 0
                approved_this_month = 0
                
                if leaves and isinstance(leaves, dict):
                    for leave in leaves.values():
                        if isinstance(leave, dict) and leave.get('employeeId') == target_employee['uid']:
                            if leave.get('status') == 'pending':
                                pending += 1
                            elif leave.get('status') == 'approved':
                                try:
                                    start = datetime.fromisoformat(leave.get('startDate', ''))
                                    if start.month == datetime.now().month:
                                        end = datetime.fromisoformat(leave.get('endDate', ''))
                                        approved_this_month += (end - start).days + 1
                                except:
                                    pass
                
                response = f"""📋 **Leave Information for {name}**

🏖️ **Available Balance:** {leave_balance} days
⏳ **Pending Requests:** {pending}
📅 **Used This Month:** {approved_this_month} days

{'⚠️ Low balance alert!' if leave_balance < 5 else '✅ Balance looks good!'}"""
                return response, intents_list, target_employee
            else:
                return "Please select an employee or mention their name to check leave balance.\n\nExample: \"What is John's leave balance?\"", intents_list, None
        
        # Duty Schedule Query
        if any(w in message_lower for w in ['duty', 'duties', 'schedule', 'shift', 'assignment', 'upcoming']):
            duties = db.get('duties')
            today = datetime.now().strftime('%Y-%m-%d')
            
            if target_employee:
                name = target_employee.get('name', 'Employee')
                user_duties = []
                
                if duties and isinstance(duties, dict):
                    for d in duties.values():
                        if isinstance(d, dict) and d.get('employeeId') == target_employee['uid']:
                            duty_date = d.get('date', '')
                            if duty_date >= today:
                                user_duties.append(d)
                
                user_duties.sort(key=lambda x: x.get('date', ''))
                
                if user_duties:
                    response = f"📅 **Upcoming Duties for {name}**\n\n"
                    for i, duty in enumerate(user_duties[:5], 1):
                        status_icon = "🔵" if duty.get('status') == 'scheduled' else "✅"
                        response += f"{status_icon} **{duty.get('title')}**\n"
                        response += f"   📆 {duty.get('date')} | ⏰ {duty.get('startTime')} - {duty.get('endTime')}\n"
                        response += f"   📍 {duty.get('location', 'Main Branch')}\n\n"
                    
                    if len(user_duties) > 5:
                        response += f"_...and {len(user_duties) - 5} more duties_"
                    
                    return response, intents_list, target_employee
                else:
                    return f"✨ No upcoming duties scheduled for {name}.", intents_list, target_employee
            else:
                # Show today's all duties
                today_duties = []
                if duties and isinstance(duties, dict):
                    for d in duties.values():
                        if isinstance(d, dict) and d.get('date') == today:
                            emp = next((e for e in employees_cache if e['uid'] == d.get('employeeId')), None)
                            d['employeeName'] = emp.get('name', 'Unknown') if emp else 'Unknown'
                            today_duties.append(d)
                
                if today_duties:
                    response = f"📅 **Today's Duty Assignments** ({today})\n\n"
                    for duty in today_duties[:10]:
                        response += f"• **{duty.get('employeeName')}**: {duty.get('title')} ({duty.get('startTime')} - {duty.get('endTime')})\n"
                    return response, intents_list, None
                else:
                    return f"No duties scheduled for today ({today}).", intents_list, None
        
        # Attendance Query
        if any(w in message_lower for w in ['attendance', 'present', 'absent', 'check in', 'check out']):
            today = datetime.now().strftime('%Y-%m-%d')
            attendance_data = db.get('attendance')
            
            if target_employee:
                name = target_employee.get('name', 'Employee')
                uid = target_employee['uid']
                
                # Get this month's attendance
                month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
                present_days = 0
                absent_days = 0
                late_days = 0
                today_status = None
                
                if attendance_data and isinstance(attendance_data, dict) and uid in attendance_data:
                    user_attendance = attendance_data[uid]
                    if isinstance(user_attendance, dict):
                        for date_str, record in user_attendance.items():
                            if isinstance(record, dict):
                                if date_str == today:
                                    today_status = record
                                if date_str >= month_start:
                                    status = record.get('status', '')
                                    if status == 'present':
                                        present_days += 1
                                    elif status == 'absent':
                                        absent_days += 1
                                    elif status == 'late':
                                        late_days += 1
                
                response = f"📊 **Attendance Report for {name}**\n\n"
                
                if today_status:
                    response += f"**Today ({today}):**\n"
                    response += f"• Status: {today_status.get('status', 'N/A').title()}\n"
                    response += f"• Check-in: {today_status.get('checkIn', 'N/A')}\n"
                    response += f"• Check-out: {today_status.get('checkOut', 'Not yet')}\n\n"
                else:
                    response += f"**Today ({today}):** No record yet\n\n"
                
                total = present_days + absent_days + late_days
                rate = round((present_days / total * 100), 1) if total > 0 else 0
                
                response += f"**This Month Summary:**\n"
                response += f"✅ Present: {present_days} days\n"
                response += f"❌ Absent: {absent_days} days\n"
                response += f"⏰ Late: {late_days} days\n"
                response += f"📈 Attendance Rate: {rate}%"
                
                return response, intents_list, target_employee
            else:
                # Show today's attendance summary
                present_count = 0
                absent_count = 0
                not_recorded = 0
                
                for emp in employees_cache:
                    uid = emp['uid']
                    if attendance_data and isinstance(attendance_data, dict) and uid in attendance_data:
                        user_att = attendance_data[uid]
                        if isinstance(user_att, dict) and today in user_att:
                            if user_att[today].get('status') == 'present':
                                present_count += 1
                            else:
                                absent_count += 1
                        else:
                            not_recorded += 1
                    else:
                        not_recorded += 1
                
                response = f"📊 **Today's Attendance Summary** ({today})\n\n"
                response += f"✅ Present: {present_count}\n"
                response += f"❌ Absent/Late: {absent_count}\n"
                response += f"❓ Not Recorded: {not_recorded}\n"
                response += f"👥 Total Employees: {len(employees_cache)}"
                
                return response, intents_list, None
        
        # Contact/Employee Info Query
        if any(w in message_lower for w in ['contact', 'info', 'email', 'phone', 'details', 'information']):
            if target_employee:
                name = target_employee.get('name', 'Unknown')
                response = f"""👤 **Employee Information**

**Name:** {name}
**Email:** {target_employee.get('email', 'N/A')}
**Phone:** {target_employee.get('phone', 'N/A')}
**Type:** {target_employee.get('type', 'N/A')}
**Department:** {target_employee.get('department', 'N/A')}
**Leave Balance:** {target_employee.get('leaveBalance', 0)} days"""
                return response, intents_list, target_employee
            else:
                return "Please select an employee or mention their name to see their contact information.", intents_list, None
        
        # Performance Query
        if any(w in message_lower for w in ['performance', 'summary', 'report', 'stats', 'statistics']):
            if target_employee:
                name = target_employee.get('name', 'Employee')
                uid = target_employee['uid']
                
                # Calculate performance metrics
                attendance_data = db.get('attendance')
                duties_data = db.get('duties')
                
                month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
                today = datetime.now().strftime('%Y-%m-%d')
                
                present_days = 0
                total_work_days = 0
                
                if attendance_data and isinstance(attendance_data, dict) and uid in attendance_data:
                    user_att = attendance_data[uid]
                    if isinstance(user_att, dict):
                        for date_str, record in user_att.items():
                            if date_str >= month_start and isinstance(record, dict):
                                total_work_days += 1
                                if record.get('status') == 'present':
                                    present_days += 1
                
                total_duties = 0
                completed_duties = 0
                
                if duties_data and isinstance(duties_data, dict):
                    for duty in duties_data.values():
                        if isinstance(duty, dict) and duty.get('employeeId') == uid:
                            duty_date = duty.get('date', '')
                            if duty_date >= month_start and duty_date <= today:
                                total_duties += 1
                                if duty.get('status') == 'completed':
                                    completed_duties += 1
                
                att_rate = round((present_days / total_work_days * 100), 1) if total_work_days > 0 else 0
                duty_rate = round((completed_duties / total_duties * 100), 1) if total_duties > 0 else 0
                
                # Overall score
                overall = round((att_rate * 0.6 + duty_rate * 0.4), 1)
                
                response = f"""📈 **Performance Summary for {name}**

**This Month:**

✅ **Attendance Rate:** {att_rate}%
   • Present: {present_days}/{total_work_days} days

📋 **Duty Completion:** {duty_rate}%
   • Completed: {completed_duties}/{total_duties} duties

🏆 **Overall Score:** {overall}%
   {"⭐ Excellent performance!" if overall >= 90 else "👍 Good performance!" if overall >= 70 else "⚠️ Needs improvement"}"""
                
                return response, intents_list, target_employee
            else:
                return "Please select an employee to view their performance summary.", intents_list, None
        
        # List employees
        if any(w in message_lower for w in ['list employee', 'all employee', 'show employee', 'employees']):
            if employees_cache:
                response = f"👥 **Employee Directory** ({len(employees_cache)} total)\n\n"
                
                # Group by department
                by_dept = {}
                for emp in employees_cache:
                    dept = emp.get('department', 'Other')
                    if dept not in by_dept:
                        by_dept[dept] = []
                    by_dept[dept].append(emp)
                
                for dept, emps in sorted(by_dept.items()):
                    response += f"**{dept}:**\n"
                    for emp in emps:
                        response += f"• {emp.get('name')} ({emp.get('type')})\n"
                    response += "\n"
                
                return response, intents_list, None
            else:
                return "No employees found in the system.", intents_list, None
        
        # Pending leave requests
        if 'pending' in message_lower and 'leave' in message_lower:
            leaves = db.get('leave_requests')
            pending_list = []
            
            if leaves and isinstance(leaves, dict):
                for req_id, leave in leaves.items():
                    if isinstance(leave, dict) and leave.get('status') == 'pending':
                        emp = next((e for e in employees_cache if e['uid'] == leave.get('employeeId')), None)
                        leave['employeeName'] = emp.get('name', 'Unknown') if emp else 'Unknown'
                        leave['id'] = req_id
                        pending_list.append(leave)
            
            if pending_list:
                response = f"📝 **Pending Leave Requests** ({len(pending_list)})\n\n"
                for leave in pending_list[:10]:
                    response += f"• **{leave.get('employeeName')}**\n"
                    response += f"  📅 {leave.get('startDate')} to {leave.get('endDate')}\n"
                    response += f"  📝 {leave.get('reason', 'No reason')[:50]}\n\n"
                return response, intents_list, None
            else:
                return "✅ No pending leave requests!", intents_list, None
        
        # Goodbye
        if tag == 'goodbye' or any(w in message_lower for w in ['bye', 'goodbye', 'thanks', 'thank you']):
            return "👋 Goodbye! Have a great day! Feel free to ask me anything anytime.", intents_list, None
        
        # Default - try to get static response from intents
        response = get_static_response(intents_list)
        return response, intents_list, target_employee
        
    except Exception as e:
        print(f"Admin chatbot error: {e}")
        return f"Sorry, I encountered an error processing your request. Please try again.", intents_list, None

def get_employee_chatbot_response(message, user_id=None):
    """
    Chatbot response for mobile app employees
    Provides personalized responses based on user's own data
    """
    
    # Get intent prediction
    if CHATBOT_ENABLED:
        intents_list = predict_intent(message)
    else:
        _, intents_list = get_fallback_response(message)
    
    if not intents_list:
        return "I'm having trouble understanding. Please try again.", []
    
    tag = intents_list[0]["intent"]
    message_lower = message.lower()
    response = get_static_response(intents_list)
    
    # Personalize with Firebase data if user_id provided
    if user_id:
        try:
            # Leave balance query
            if any(w in message_lower for w in ['leave', 'balance', 'vacation', 'holiday']) or tag in ['CheckLeaveBalance', 'leave_balance']:
                user_data = db.get(f'users/{user_id}')
                if user_data and isinstance(user_data, dict):
                    leave_balance = user_data.get('leaveBalance', 0)
                    name = user_data.get('name', 'there')
                    response = f"Hello {name}! 🏖️\n\nYou have **{leave_balance} days** of leave remaining.\n\n"
                    
                    # Check pending requests
                    leaves = db.get('leave_requests')
                    pending = 0
                    if leaves and isinstance(leaves, dict):
                        for leave in leaves.values():
                            if isinstance(leave, dict) and leave.get('employeeId') == user_id and leave.get('status') == 'pending':
                                pending += 1
                    
                    if pending > 0:
                        response += f"📝 You have {pending} pending leave request(s)."
                    else:
                        response += "✅ No pending leave requests."
            
            # Duty schedule query
            elif any(w in message_lower for w in ['duty', 'schedule', 'shift', 'assignment']) or tag in ['GetDutySchedule', 'duty_schedule']:
                today = datetime.now().strftime('%Y-%m-%d')
                duties = db.get('duties')
                
                if duties and isinstance(duties, dict):
                    user_duties = [
                        d for d in duties.values()
                        if isinstance(d, dict) and d.get('employeeId') == user_id and d.get('date') >= today
                    ]
                    user_duties.sort(key=lambda x: x.get('date', ''))
                    
                    if user_duties:
                        response = "📅 **Your Upcoming Duties:**\n\n"
                        for duty in user_duties[:5]:
                            response += f"• **{duty.get('title')}**\n"
                            response += f"  📆 {duty.get('date')} | ⏰ {duty.get('startTime')} - {duty.get('endTime')}\n"
                            response += f"  📍 {duty.get('location', 'Main Branch')}\n\n"
                    else:
                        response = "✨ No upcoming duties scheduled for you."
            
            # Attendance query
            elif any(w in message_lower for w in ['attendance', 'present', 'absent', 'check']) or tag in ['ShowAttendance', 'attendance']:
                today = datetime.now().strftime('%Y-%m-%d')
                attendance = db.get(f'attendance/{user_id}/{today}')
                
                if attendance and isinstance(attendance, dict):
                    response = f"📊 **Today's Attendance** ({today}):\n\n"
                    response += f"• Status: **{attendance.get('status', 'N/A').title()}**\n"
                    response += f"• Check-in: {attendance.get('checkIn', 'N/A')}\n"
                    response += f"• Check-out: {attendance.get('checkOut', 'Not yet')}\n"
                    
                    if attendance.get('location'):
                        response += f"• Location: {attendance.get('location')}"
                else:
                    response = f"No attendance record for today ({today}) yet.\n\nDon't forget to check in! 📲"
                    
        except Exception as e:
            print(f"Employee chatbot personalization error: {e}")
    
    return response, intents_list

# ==================== DECORATORS ====================

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_uid' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== TEMPLATE CONTEXT ====================

@app.context_processor
def inject_globals():
    """Inject global variables into all templates"""
    return {
        'datetime': datetime,
        'chatbot_enabled': CHATBOT_ENABLED,
        'app_name': Config.APP_NAME,
        'app_version': Config.APP_VERSION
    }

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    return render_template('500.html'), 500

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Root URL - redirect based on auth status"""
    if 'admin_uid' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if 'admin_uid' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter email and password', 'danger')
            return render_template('login.html')
        
        try:
            # Firebase Auth REST API
            sign_in_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={Config.FIREBASE_API_KEY}"
            
            response = requests.post(sign_in_url, json={
                "email": email,
                "password": password,
                "returnSecureToken": True
            }, timeout=10)
            
            data = response.json()
            
            if 'error' in data:
                error_msg = data['error'].get('message', 'Unknown error')
                if 'INVALID_LOGIN_CREDENTIALS' in error_msg:
                    flash('Invalid email or password', 'danger')
                elif 'TOO_MANY_ATTEMPTS' in error_msg:
                    flash('Too many attempts. Please try again later.', 'danger')
                else:
                    flash(f'Login failed: {error_msg}', 'danger')
                return render_template('login.html')
            
            # Verify admin role
            uid = data['localId']
            user_data = db.get(f'users/{uid}')
            
            if not user_data:
                flash('User account not found in database', 'danger')
                return render_template('login.html')
            
            if user_data.get('type') != 'Admin':
                flash('Access denied. Admin privileges required.', 'danger')
                return render_template('login.html')
            
            # Set session
            session.permanent = True
            session['admin_uid'] = uid
            session['admin_email'] = email
            session['admin_name'] = user_data.get('name', 'Admin')
            session['id_token'] = data['idToken']
            
            flash(f'Welcome back, {session["admin_name"]}!', 'success')
            return redirect(url_for('dashboard'))
            
        except requests.exceptions.Timeout:
            flash('Connection timeout. Please try again.', 'danger')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
    
    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if 'admin_uid' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please enter your email address', 'danger')
            return render_template('forgot_password.html')
        
        try:
            reset_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={Config.FIREBASE_API_KEY}"
            
            response = requests.post(reset_url, json={
                "requestType": "PASSWORD_RESET",
                "email": email
            }, timeout=10)
            
            data = response.json()
            
            if 'error' in data:
                error_msg = data['error'].get('message', 'Unknown error')
                if 'EMAIL_NOT_FOUND' not in error_msg:
                    flash(f'Error: {error_msg}', 'danger')
                    return render_template('forgot_password.html')
            
            flash('Password reset link has been sent to your email address. Please check your inbox.', 'success')
            return redirect(url_for('login'))
            
        except requests.exceptions.Timeout:
            flash('Connection timeout. Please try again.', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    stats = {
        'total_employees': 0,
        'total_duties': 0,
        'pending_leaves': 0,
        'today_attendance': 0
    }
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        employees = db.get('users')
        if employees and isinstance(employees, dict):
            stats['total_employees'] = len([
                e for e in employees.values() 
                if isinstance(e, dict) and e.get('type') != 'Admin'
            ])
        
        duties = db.get('duties')
        if duties and isinstance(duties, dict):
            stats['total_duties'] = len([
                d for d in duties.values() 
                if isinstance(d, dict) and d.get('date') == today
            ])
        
        leaves = db.get('leave_requests')
        if leaves and isinstance(leaves, dict):
            stats['pending_leaves'] = len([
                l for l in leaves.values() 
                if isinstance(l, dict) and l.get('status') == 'pending'
            ])
        
        attendance = db.get('attendance')
        if attendance and isinstance(attendance, dict):
            for uid, dates in attendance.items():
                if isinstance(dates, dict) and today in dates:
                    record = dates[today]
                    if isinstance(record, dict) and record.get('status') == 'present':
                        stats['today_attendance'] += 1
                        
    except Exception as e:
        flash(f'Error loading dashboard stats: {str(e)}', 'warning')
    
    return render_template('dashboard.html', stats=stats, activities=[])

# ==================== EMPLOYEE MANAGEMENT ====================

@app.route('/employees')
@login_required
def employees():
    """Employee management page"""
    employees_list = []
    
    try:
        users = db.get('users')
        if users and isinstance(users, dict):
            for uid, data in users.items():
                if not isinstance(data, dict) or data.get('type') == 'Admin':
                    continue
                
                employees_list.append({
                    'uid': uid,
                    'name': data.get('name', 'Unknown'),
                    'email': data.get('email', ''),
                    'type': data.get('type', 'Unknown'),
                    'department': data.get('department', 'N/A'),
                    'createdAt': data.get('createdAt', ''),
                    'leaveBalance': data.get('leaveBalance', 0)
                })
                
    except Exception as e:
        flash(f'Error loading employees: {str(e)}', 'danger')
    
    return render_template('employees.html', employees=employees_list)

@app.route('/api/employees', methods=['GET', 'POST'])
@login_required
def api_employees():
    """API for employee operations"""
    
    if request.method == 'GET':
        try:
            users = db.get('users')
            employees = []
            
            if users and isinstance(users, dict):
                for uid, data in users.items():
                    if isinstance(data, dict) and data.get('type') != 'Admin':
                        employees.append({
                            'uid': uid,
                            'name': data.get('name', 'Unknown'),
                            'type': data.get('type', 'Unknown')
                        })
            
            return jsonify({'success': True, 'employees': employees})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # POST - Create new employee
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        user_type = data.get('type', 'Student')
        department = data.get('department', '').strip()
        
        if not all([email, password, name]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
        
        sign_up_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={Config.FIREBASE_API_KEY}"
        
        auth_response = requests.post(sign_up_url, json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        }, timeout=10)
        
        auth_data = auth_response.json()
        
        if 'error' in auth_data:
            return jsonify({'success': False, 'error': auth_data['error']['message']}), 400
        
        uid = auth_data['localId']
        
        user_data = {
            'uid': uid,
            'name': name,
            'email': email,
            'type': user_type,
            'department': department,
            'leaveBalance': 20,
            'createdAt': datetime.now().isoformat(),
            'createdBy': session['admin_uid']
        }
        
        db.put(f'users/{uid}', user_data)
        
        return jsonify({'success': True, 'uid': uid})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/employees/<uid>', methods=['DELETE'])
@login_required
def delete_employee(uid):
    """Delete employee"""
    try:
        db.delete(f'users/{uid}')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== DUTY MANAGEMENT ====================

@app.route('/duties')
@login_required
def duties():
    """Duty schedule page"""
    duties_list = []
    employees = {}
    
    try:
        users = db.get('users')
        if users and isinstance(users, dict):
            for uid, data in users.items():
                if isinstance(data, dict) and data.get('type') != 'Admin':
                    employees[uid] = data.get('name', 'Unknown')
        
        duties_data = db.get('duties')
        if duties_data and isinstance(duties_data, dict):
            for duty_id, data in duties_data.items():
                if not isinstance(data, dict):
                    continue
                
                duties_list.append({
                    'id': duty_id,
                    'employeeId': data.get('employeeId', ''),
                    'employeeName': employees.get(data.get('employeeId', ''), 'Unknown'),
                    'title': data.get('title', ''),
                    'date': data.get('date', ''),
                    'startTime': data.get('startTime', ''),
                    'endTime': data.get('endTime', ''),
                    'location': data.get('location', 'N/A'),
                    'status': data.get('status', 'scheduled')
                })
            
            duties_list.sort(key=lambda x: x['date'], reverse=True)
            
    except Exception as e:
        flash(f'Error loading duties: {str(e)}', 'danger')
    
    return render_template('duties.html', duties=duties_list, employees=employees)

@app.route('/api/duties', methods=['POST'])
@login_required
def create_duty():
    """Create new duty"""
    try:
        data = request.json
        
        required = ['employeeId', 'title', 'date', 'startTime', 'endTime']
        if not all(data.get(f) for f in required):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        duty_data = {
            'employeeId': data['employeeId'],
            'title': data['title'],
            'date': data['date'],
            'startTime': data['startTime'],
            'endTime': data['endTime'],
            'location': data.get('location', 'Main Branch'),
            'status': 'scheduled',
            'createdBy': session['admin_uid'],
            'createdAt': datetime.now().isoformat()
        }
        
        result = db.post('duties', duty_data)
        
        if result and 'name' in result:
            notification = {
                'userId': data['employeeId'],
                'title': 'New Duty Assigned',
                'message': f"You have been assigned: {data['title']} on {data['date']}",
                'type': 'duty_assigned',
                'read': False,
                'createdAt': datetime.now().isoformat()
            }
            db.post('notifications', notification)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/duties/<duty_id>', methods=['DELETE'])
@login_required
def delete_duty(duty_id):
    """Delete duty"""
    try:
        db.delete(f'duties/{duty_id}')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ATTENDANCE ====================

@app.route('/attendance')
@login_required
def attendance():
    """Attendance tracking page"""
    attendance_list = []
    date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    all_employees = []
    
    # Summary counts
    summary = {
        'present': 0,
        'late': 0,
        'absent': 0,
        'total': 0
    }
    
    try:
        # Get all employees for the dropdown
        users = db.get('users')
        if users and isinstance(users, dict):
            for uid, data in users.items():
                if isinstance(data, dict) and data.get('type') != 'Admin':
                    all_employees.append({
                        'uid': uid,
                        'name': data.get('name', 'Unknown'),
                        'type': data.get('type', 'Unknown')
                    })
            all_employees.sort(key=lambda x: x['name'])
        
        # Get attendance data
        attendance_data = db.get('attendance')
        
        if attendance_data and isinstance(attendance_data, dict):
            for uid, dates in attendance_data.items():
                if not isinstance(dates, dict) or date_filter not in dates:
                    continue
                
                record = dates[date_filter]
                if not isinstance(record, dict):
                    continue
                
                user_data = db.get(f'users/{uid}')
                employee_name = user_data.get('name', 'Unknown') if isinstance(user_data, dict) else 'Unknown'
                
                status = record.get('status', 'unknown')
                if status == 'present':
                    summary['present'] += 1
                elif status == 'late':
                    summary['late'] += 1
                elif status == 'absent':
                    summary['absent'] += 1
                summary['total'] += 1
                
                attendance_list.append({
                    'uid': uid,
                    'employeeName': employee_name,
                    'date': date_filter,
                    'checkIn': record.get('checkIn', '-'),
                    'checkOut': record.get('checkOut', '-'),
                    'status': status,
                    'location': record.get('location', '-')
                })
                
    except Exception as e:
        flash(f'Error loading attendance: {str(e)}', 'danger')
    
    return render_template('attendance.html', attendance=attendance_list, 
                           selected_date=date_filter, all_employees=all_employees,
                           summary=summary)
@app.route('/api/attendance', methods=['POST', 'PUT'])
@login_required
def api_attendance():
    """Create or update attendance record"""
    try:
        data = request.json
        
        employee_id = data.get('employeeId')
        date = data.get('date')
        check_in = data.get('checkIn')
        check_out = data.get('checkOut', '')
        status = data.get('status', 'present')
        location = data.get('location', 'Main Office')
        
        if not employee_id or not date or not check_in:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Build attendance data
        attendance_data = {
            'checkIn': check_in,
            'checkOut': check_out,
            'status': status,
            'location': location,
            'markedBy': session['admin_uid'],
            'markedAt': datetime.now().isoformat()
        }
        
        # Store in Firebase under attendance/{employeeId}/{date}
        db.put(f'attendance/{employee_id}/{date}', attendance_data)
        
        return jsonify({'success': True, 'message': 'Attendance recorded successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/attendance/<employee_id>/<date>', methods=['DELETE'])
@login_required
def delete_attendance(employee_id, date):
    """Delete attendance record"""
    try:
        db.delete(f'attendance/{employee_id}/{date}')
        return jsonify({'success': True, 'message': 'Attendance record deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/attendance/export', methods=['GET'])
@login_required
def export_attendance():
    """Export attendance to CSV"""
    try:
        date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        attendance_data = db.get('attendance')
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Employee Name', 'Date', 'Check In', 'Check Out', 'Status', 'Location'])
        
        if attendance_data and isinstance(attendance_data, dict):
            for uid, dates in attendance_data.items():
                if isinstance(dates, dict) and date_filter in dates:
                    record = dates[date_filter]
                    if isinstance(record, dict):
                        user_data = db.get(f'users/{uid}')
                        employee_name = user_data.get('name', 'Unknown') if isinstance(user_data, dict) else 'Unknown'
                        
                        writer.writerow([
                            employee_name,
                            date_filter,
                            record.get('checkIn', '-'),
                            record.get('checkOut', '-'),
                            record.get('status', '-'),
                            record.get('location', '-')
                        ])
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=attendance_{date_filter}.csv'
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
# ==================== LEAVE REQUESTS ====================

@app.route('/leave-requests')
@login_required
def leave_requests():
    """Leave requests page"""
    requests_list = []
    
    try:
        leaves = db.get('leave_requests')
        if leaves and isinstance(leaves, dict):
            for req_id, data in leaves.items():
                if not isinstance(data, dict):
                    continue
                
                user_data = db.get(f"users/{data.get('employeeId', '')}")
                employee_name = user_data.get('name', 'Unknown') if isinstance(user_data, dict) else 'Unknown'
                
                requests_list.append({
                    'id': req_id,
                    'employeeId': data.get('employeeId', ''),
                    'employeeName': employee_name,
                    'startDate': data.get('startDate', ''),
                    'endDate': data.get('endDate', ''),
                    'reason': data.get('reason', ''),
                    'status': data.get('status', 'pending'),
                    'requestedAt': data.get('requestedAt', ''),
                    'approvedBy': data.get('approvedBy', ''),
                    'approvedAt': data.get('approvedAt', '')
                })
            
            requests_list.sort(
                key=lambda x: (0 if x['status'] == 'pending' else 1, x['requestedAt']), 
                reverse=True
            )
            
    except Exception as e:
        flash(f'Error loading leave requests: {str(e)}', 'danger')
    
    return render_template('leave_requests.html', requests=requests_list)

@app.route('/api/leave-requests/<req_id>/approve', methods=['POST'])
@login_required
def approve_leave(req_id):
    """Approve leave request"""
    try:
        updates = {
            'status': 'approved',
            'approvedBy': session['admin_uid'],
            'approvedAt': datetime.now().isoformat()
        }
        db.patch(f'leave_requests/{req_id}', updates)
        
        leave_data = db.get(f'leave_requests/{req_id}')
        if leave_data and isinstance(leave_data, dict):
            employee_id = leave_data.get('employeeId')
            user_data = db.get(f'users/{employee_id}')
            
            if user_data and isinstance(user_data, dict):
                try:
                    start = datetime.fromisoformat(leave_data.get('startDate', ''))
                    end = datetime.fromisoformat(leave_data.get('endDate', ''))
                    days = (end - start).days + 1
                    current_balance = user_data.get('leaveBalance', 0)
                    db.patch(f'users/{employee_id}', {
                        'leaveBalance': max(0, current_balance - days)
                    })
                except ValueError:
                    pass
            
            notification = {
                'userId': employee_id,
                'title': 'Leave Approved',
                'message': f"Your leave request from {leave_data.get('startDate')} to {leave_data.get('endDate')} has been approved.",
                'type': 'leave_approved',
                'read': False,
                'createdAt': datetime.now().isoformat()
            }
            db.post('notifications', notification)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/leave-requests/<req_id>/reject', methods=['POST'])
@login_required
def reject_leave(req_id):
    """Reject leave request"""
    try:
        updates = {
            'status': 'rejected',
            'approvedBy': session['admin_uid'],
            'approvedAt': datetime.now().isoformat()
        }
        db.patch(f'leave_requests/{req_id}', updates)
        
        leave_data = db.get(f'leave_requests/{req_id}')
        if leave_data and isinstance(leave_data, dict):
            notification = {
                'userId': leave_data.get('employeeId'),
                'title': 'Leave Rejected',
                'message': f"Your leave request has been rejected.",
                'type': 'leave_rejected',
                'read': False,
                'createdAt': datetime.now().isoformat()
            }
            db.post('notifications', notification)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== NOTIFICATIONS ====================

@app.route('/notifications')
@login_required
def notifications():
    """Notifications management page"""
    return render_template('notifications.html')

@app.route('/api/notifications/send', methods=['POST'])
@login_required
def send_notification():
    """Send notification to employees"""
    try:
        data = request.json
        title = data.get('title', '').strip()
        message = data.get('message', '').strip()
        notification_type = data.get('type', 'general')
        user_ids = data.get('userIds', [])
        
        if not title or not message:
            return jsonify({'success': False, 'error': 'Title and message required'}), 400
        
        if not user_ids:
            users = db.get('users')
            if users and isinstance(users, dict):
                user_ids = [
                    uid for uid, u in users.items() 
                    if isinstance(u, dict) and u.get('type') != 'Admin'
                ]
        
        count = 0
        for uid in user_ids:
            notification_data = {
                'userId': uid,
                'title': title,
                'message': message,
                'type': notification_type,
                'read': False,
                'createdAt': datetime.now().isoformat(),
                'createdBy': session['admin_uid']
            }
            result = db.post('notifications', notification_data)
            if result:
                count += 1
        
        return jsonify({'success': True, 'count': count})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== REPORTS & ANALYTICS ====================

@app.route('/reports')
@login_required
def reports():
    """Reports and Analytics page"""
    return render_template('reports.html')

@app.route('/api/reports/attendance', methods=['GET'])
@login_required
def api_attendance_report():
    """Generate attendance report"""
    try:
        report_type = request.args.get('type', 'daily')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        employee_id = request.args.get('employee_id')
        download = request.args.get('download', 'false').lower() == 'true'
        format_type = request.args.get('format', 'csv')
        
        today = datetime.now()
        if report_type == 'daily':
            start = today.replace(hour=0, minute=0, second=0, microsecond=0)
            end = today
        elif report_type == 'weekly':
            start = today - timedelta(days=today.weekday())
            end = today
        elif report_type == 'monthly':
            start = today.replace(day=1)
            end = today
        else:
            if start_date and end_date:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                start = today - timedelta(days=30)
                end = today
        
        attendance_data = db.get('attendance')
        users = db.get('users')
        
        report_data = []
        
        if attendance_data and isinstance(attendance_data, dict):
            for uid, dates in attendance_data.items():
                if not isinstance(dates, dict):
                    continue
                
                if employee_id and uid != employee_id:
                    continue
                
                user_data = users.get(uid, {}) if users else {}
                employee_name = user_data.get('name', 'Unknown') if isinstance(user_data, dict) else 'Unknown'
                department = user_data.get('department', 'N/A') if isinstance(user_data, dict) else 'N/A'
                
                for date_str, record in dates.items():
                    if not isinstance(record, dict):
                        continue
                    
                    try:
                        record_date = datetime.strptime(date_str, '%Y-%m-%d')
                        if start.date() <= record_date.date() <= end.date():
                            report_data.append({
                                'employee_id': uid,
                                'employee_name': employee_name,
                                'department': department,
                                'date': date_str,
                                'status': record.get('status', 'unknown'),
                                'check_in': record.get('checkIn', '-'),
                                'check_out': record.get('checkOut', '-'),
                                'location': record.get('location', '-'),
                                'duration': calculate_duration(record.get('checkIn'), record.get('checkOut'))
                            })
                    except ValueError:
                        continue
        
        report_data.sort(key=lambda x: x['date'], reverse=True)
        
        if download:
            if format_type == 'pdf':
                return generate_pdf_report('Attendance Report', report_data, 
                                         ['Employee', 'Department', 'Date', 'Status', 'Check In', 'Check Out', 'Duration'])
            else:
                return generate_csv_report(report_data, 
                                         ['employee_name', 'department', 'date', 'status', 'check_in', 'check_out', 'duration'],
                                         'attendance_report')
        
        return jsonify({
            'success': True,
            'report_type': report_type,
            'start_date': start.strftime('%Y-%m-%d'),
            'end_date': end.strftime('%Y-%m-%d'),
            'total_records': len(report_data),
            'data': report_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/duties', methods=['GET'])
@login_required
def api_duty_report():
    """Generate duty schedule report"""
    try:
        employee_id = request.args.get('employee_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        download = request.args.get('download', 'false').lower() == 'true'
        format_type = request.args.get('format', 'csv')
        
        today = datetime.now()
        if not start_date:
            start = today
            start_date = start.strftime('%Y-%m-%d')
        else:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            
        if not end_date:
            end = today + timedelta(days=30)
            end_date = end.strftime('%Y-%m-%d')
        else:
            end = datetime.strptime(end_date, '%Y-%m-%d')
        
        duties_data = db.get('duties')
        users = db.get('users')
        
        report_data = []
        
        if duties_data and isinstance(duties_data, dict):
            for duty_id, data in duties_data.items():
                if not isinstance(data, dict):
                    continue
                
                if employee_id and data.get('employeeId') != employee_id:
                    continue
                
                if status and data.get('status') != status:
                    continue
                
                try:
                    duty_date = datetime.strptime(data.get('date', ''), '%Y-%m-%d')
                    if not (start.date() <= duty_date.date() <= end.date()):
                        continue
                except ValueError:
                    continue
                
                user_data = users.get(data.get('employeeId', ''), {}) if users else {}
                employee_name = user_data.get('name', 'Unknown') if isinstance(user_data, dict) else 'Unknown'
                
                report_data.append({
                    'duty_id': duty_id,
                    'employee_id': data.get('employeeId', ''),
                    'employee_name': employee_name,
                    'title': data.get('title', ''),
                    'date': data.get('date', ''),
                    'start_time': data.get('startTime', ''),
                    'end_time': data.get('endTime', ''),
                    'location': data.get('location', 'N/A'),
                    'status': data.get('status', 'scheduled')
                })
        
        report_data.sort(key=lambda x: x['date'])
        
        if download:
            if format_type == 'pdf':
                return generate_pdf_report('Duty Schedule Report', report_data,
                                         ['Employee', 'Title', 'Date', 'Start Time', 'End Time', 'Location', 'Status'])
            else:
                return generate_csv_report(report_data,
                                         ['employee_name', 'title', 'date', 'start_time', 'end_time', 'location', 'status'],
                                         'duty_schedule_report')
        
        return jsonify({
            'success': True,
            'start_date': start_date,
            'end_date': end_date,
            'total_records': len(report_data),
            'data': report_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/leaves', methods=['GET'])
@login_required
def api_leave_report():
    """Generate leave report"""
    try:
        status_filter = request.args.get('status')
        employee_id = request.args.get('employee_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        download = request.args.get('download', 'false').lower() == 'true'
        format_type = request.args.get('format', 'csv')
        
        leaves_data = db.get('leave_requests')
        users = db.get('users')
        
        report_data = []
        
        if leaves_data and isinstance(leaves_data, dict):
            for req_id, data in leaves_data.items():
                if not isinstance(data, dict):
                    continue
                
                if status_filter and data.get('status') != status_filter:
                    continue
                
                if employee_id and data.get('employeeId') != employee_id:
                    continue
                
                if start_date and end_date:
                    try:
                        req_start = datetime.strptime(data.get('startDate', ''), '%Y-%m-%d')
                        filter_start = datetime.strptime(start_date, '%Y-%m-%d')
                        filter_end = datetime.strptime(end_date, '%Y-%m-%d')
                        if not (filter_start.date() <= req_start.date() <= filter_end.date()):
                            continue
                    except ValueError:
                        continue
                
                user_data = users.get(data.get('employeeId', ''), {}) if users else {}
                employee_name = user_data.get('name', 'Unknown') if isinstance(user_data, dict) else 'Unknown'
                
                try:
                    start = datetime.strptime(data.get('startDate', ''), '%Y-%m-%d')
                    end = datetime.strptime(data.get('endDate', ''), '%Y-%m-%d')
                    days = (end - start).days + 1
                except:
                    days = 0
                
                report_data.append({
                    'request_id': req_id,
                    'employee_id': data.get('employeeId', ''),
                    'employee_name': employee_name,
                    'start_date': data.get('startDate', ''),
                    'end_date': data.get('endDate', ''),
                    'days': days,
                    'reason': data.get('reason', ''),
                    'status': data.get('status', 'pending'),
                    'requested_at': data.get('requestedAt', ''),
                    'approved_by': data.get('approvedBy', ''),
                    'approved_at': data.get('approvedAt', '')
                })
        
        report_data.sort(key=lambda x: x['requested_at'], reverse=True)
        
        summary = {
            'total_requests': len(report_data),
            'pending': len([r for r in report_data if r['status'] == 'pending']),
            'approved': len([r for r in report_data if r['status'] == 'approved']),
            'rejected': len([r for r in report_data if r['status'] == 'rejected']),
            'total_days': sum(r['days'] for r in report_data if r['status'] == 'approved')
        }
        
        if download:
            if format_type == 'pdf':
                return generate_pdf_report('Leave Report', report_data,
                                         ['Employee', 'Start Date', 'End Date', 'Days', 'Reason', 'Status', 'Requested At'])
            else:
                return generate_csv_report(report_data,
                                         ['employee_name', 'start_date', 'end_date', 'days', 'reason', 'status', 'requested_at'],
                                         'leave_report')
        
        return jsonify({
            'success': True,
            'summary': summary,
            'data': report_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/employees', methods=['GET'])
@login_required
def api_employee_report():
    """Generate employee directory report"""
    try:
        department = request.args.get('department')
        employee_type = request.args.get('type')
        download = request.args.get('download', 'false').lower() == 'true'
        format_type = request.args.get('format', 'csv')
        
        users = db.get('users')
        
        report_data = []
        
        if users and isinstance(users, dict):
            for uid, data in users.items():
                if not isinstance(data, dict) or data.get('type') == 'Admin':
                    continue
                
                if department and data.get('department') != department:
                    continue
                
                if employee_type and data.get('type') != employee_type:
                    continue
                
                report_data.append({
                    'employee_id': uid,
                    'name': data.get('name', 'Unknown'),
                    'email': data.get('email', ''),
                    'type': data.get('type', 'Unknown'),
                    'department': data.get('department', 'N/A'),
                    'phone': data.get('phone', 'N/A'),
                    'join_date': data.get('createdAt', ''),
                    'leave_balance': data.get('leaveBalance', 0),
                    'status': 'Active'
                })
        
        report_data.sort(key=lambda x: x['name'])
        
        if download:
            if format_type == 'pdf':
                return generate_pdf_report('Employee Directory Report', report_data,
                                         ['Name', 'Email', 'Type', 'Department', 'Phone', 'Join Date', 'Leave Balance', 'Status'])
            else:
                return generate_csv_report(report_data,
                                         ['name', 'email', 'type', 'department', 'phone', 'join_date', 'leave_balance', 'status'],
                                         'employee_directory_report')
        
        return jsonify({
            'success': True,
            'total_employees': len(report_data),
            'data': report_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== REPORT GENERATION HELPERS ====================

def calculate_duration(check_in, check_out):
    """Calculate duration between check-in and check-out"""
    if not check_in or not check_out or check_out == 'Not yet':
        return '-'
    try:
        fmt = '%H:%M:%S'
        t1 = datetime.strptime(check_in, fmt)
        t2 = datetime.strptime(check_out, fmt)
        diff = t2 - t1
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    except:
        return '-'

def generate_csv_report(data, headers, filename):
    """Generate CSV file from report data"""
    if not data:
        return jsonify({'success': False, 'error': 'No data to export'}), 400
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    
    for row in data:
        filtered_row = {k: row.get(k, '') for k in headers}
        writer.writerow(filtered_row)
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return response

def generate_pdf_report(title, data, headers):
    """Generate PDF file from report data"""
    if not data:
        return jsonify({'success': False, 'error': 'No data to export'}), 400
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), 
                           rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))
    
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey
    )
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", info_style))
    elements.append(Spacer(1, 20))
    
    table_data = [headers]
    
    key_mapping = {
        'Employee': 'employee_name',
        'Name': 'name',
        'Department': 'department',
        'Date': 'date',
        'Status': 'status',
        'Check In': 'check_in',
        'Check Out': 'check_out',
        'Duration': 'duration',
        'Title': 'title',
        'Start Time': 'start_time',
        'End Time': 'end_time',
        'Location': 'location',
        'Start Date': 'start_date',
        'End Date': 'end_date',
        'Days': 'days',
        'Reason': 'reason',
        'Requested At': 'requested_at',
        'Email': 'email',
        'Type': 'type',
        'Phone': 'phone',
        'Join Date': 'join_date',
        'Leave Balance': 'leave_balance',
        'Month': 'month',
        'Present': 'present_days',
        'Absent': 'absent_days',
        'Late': 'late_days',
        'Attendance %': 'attendance_rate',
        'Avg Check-in': 'avg_check_in',
        'Duties': 'total_duties',
        'Completed': 'completed_duties'
    }
    
    for row in data:
        table_row = []
        for header in headers:
            key = key_mapping.get(header, header.lower().replace(' ', '_'))
            value = row.get(key, '-')
            table_row.append(str(value))
        table_data.append(table_row)
    
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F8FF4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={title.replace(" ", "_").lower()}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    return response

# ==================== SETTINGS ====================

@app.route('/settings')
@login_required
def settings():
    """Settings page"""
    return render_template('settings.html')

# ==================== ADMIN CHATBOT ROUTES ====================

@app.route('/chatbot')
@login_required
def chatbot_admin():
    """Admin AI Assistant Interface"""
    return render_template('chatbot_admin.html')

@app.route('/api/chatbot/employees', methods=['GET'])
@login_required
def chatbot_employees():
    """Get employee list for chatbot sidebar"""
    try:
        users = db.get('users')
        employees = []
        
        if users and isinstance(users, dict):
            for uid, data in users.items():
                if isinstance(data, dict) and data.get('type') != 'Admin':
                    employees.append({
                        'uid': uid,
                        'name': data.get('name', 'Unknown'),
                        'email': data.get('email', ''),
                        'type': data.get('type', 'Unknown'),
                        'department': data.get('department', 'N/A'),
                        'leaveBalance': data.get('leaveBalance', 0)
                    })
        
        # Sort by name
        employees.sort(key=lambda x: x['name'])
        
        return jsonify({'success': True, 'employees': employees})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chatbot/chat', methods=['POST'])
@login_required
def chatbot_chat():
    """
    Admin Chatbot API endpoint
    Handles admin queries about employees, duties, attendance, etc.
    
    Request:
        POST /api/chatbot/chat
        Content-Type: application/json
        {"message": "What is John's leave balance?", "employee_id": "optional_uid"}
    
    Response:
        {
            "success": true,
            "response": "John has 15 days of leave remaining...",
            "intents": [...],
            "employee": {...} or null
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        message = data.get('message', '').strip()
        employee_id = data.get('employee_id')
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Get response from admin chatbot
        response, intents_list, matched_employee = get_admin_chatbot_response(message, employee_id)
        
        # Log chat for analytics
        try:
            chat_log = {
                'message': message,
                'response': response[:500],  # Truncate for storage
                'adminId': session.get('admin_uid'),
                'employeeId': employee_id or (matched_employee['uid'] if matched_employee else None),
                'intent': intents_list[0]['intent'] if intents_list else 'unknown',
                'confidence': intents_list[0]['probability'] if intents_list else 0,
                'timestamp': datetime.now().isoformat(),
                'model_active': CHATBOT_ENABLED
            }
            db.post('admin_chat_logs', chat_log)
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': message,
            'response': response,
            'intents': intents_list,
            'employee': matched_employee,
            'timestamp': datetime.now().isoformat(),
            'model_active': CHATBOT_ENABLED
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== MOBILE APP CHATBOT API ====================

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """
    Public chatbot API endpoint for Flutter mobile app
    
    Request:
        POST /api/chat
        Content-Type: application/json
        {"message": "Hello", "userId": "user_uid"}
    
    Response:
        {
            "success": true,
            "message": "Hello",
            "response": "Hi! How can I help you?",
            "intents": [{"intent": "greeting", "probability": 0.95}],
            "model_active": true
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        message = data.get('message', '').strip()
        user_id = data.get('userId')
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Get response for employee
        response, intents_list = get_employee_chatbot_response(message, user_id)
        
        # Log chat
        try:
            chat_log = {
                'message': message,
                'response': response[:500],
                'userId': user_id,
                'intent': intents_list[0]['intent'] if intents_list else 'unknown',
                'confidence': intents_list[0]['probability'] if intents_list else 0,
                'timestamp': datetime.now().isoformat(),
                'model_active': CHATBOT_ENABLED,
                'source': 'mobile_app'
            }
            db.post('chat_logs', chat_log)
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': message,
            'response': response,
            'intents': intents_list,
            'timestamp': datetime.now().isoformat(),
            'model_active': CHATBOT_ENABLED
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/status', methods=['GET'])
def chatbot_status():
    """Get chatbot status - public endpoint"""
    return jsonify({
        'success': True,
        'chatbot_enabled': CHATBOT_ENABLED,
        'model_loaded': chatbot_model is not None,
        'vocabulary_size': len(chatbot_words),
        'num_intents': len(chatbot_classes),
        'intents': chatbot_classes,
        'version': Config.APP_VERSION
    })

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 DUTY SMITH ADMIN PORTAL")
    print("=" * 60)
    print(f"📌 Version: {Config.APP_VERSION}")
    print(f"🔥 Firebase: {Config.FIREBASE_DATABASE_URL}")
    print(f"🤖 Chatbot: {'✅ Active (ML Model)' if CHATBOT_ENABLED else '⚠️ Fallback Mode (Keyword-based)'}")
    if CHATBOT_ENABLED:
        print(f"   └─ Vocabulary: {len(chatbot_words)} words")
        print(f"   └─ Intents: {len(chatbot_classes)} classes")
    print("=" * 60)
    print("📍 Endpoints:")
    print("   • Admin Portal: http://localhost:5000")
    print("   • Admin Chatbot: http://localhost:5000/chatbot")
    print("   • Mobile API: POST http://localhost:5000/api/chat")
    print("   • Chatbot Status: GET http://localhost:5000/api/chat/status")
    print("=" * 60 + "\n")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )