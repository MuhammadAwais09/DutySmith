from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from datetime import datetime, timedelta
import requests
import json
import os

app = Flask(__name__)
app.secret_key = 'duty-smith-secret-key-change-in-production'

# Firebase Configuration
FIREBASE_DATABASE_URL = "https://dutysmith-25ccb-default-rtdb.firebaseio.com"
FIREBASE_API_KEY = "AIzaSyDdRS9eN2K6Hq39RS6eoYnyUWqkjseQwzY"

class FirebaseREST:
    def __init__(self):
        self.database_url = FIREBASE_DATABASE_URL
        self.api_key = FIREBASE_API_KEY
    
    def get(self, path):
        url = f"{self.database_url}/{path}.json"
        try:
            response = requests.get(url, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Firebase GET error: {e}")
            return None
    
    def put(self, path, data):
        url = f"{self.database_url}/{path}.json"
        try:
            response = requests.put(url, json=data, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Firebase PUT error: {e}")
            return None
    
    def post(self, path, data):
        url = f"{self.database_url}/{path}.json"
        try:
            response = requests.post(url, json=data, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Firebase POST error: {e}")
            return None
    
    def patch(self, path, data):
        url = f"{self.database_url}/{path}.json"
        try:
            response = requests.patch(url, json=data, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Firebase PATCH error: {e}")
            return None
    
    def delete(self, path):
        url = f"{self.database_url}/{path}.json"
        try:
            response = requests.delete(url, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Firebase DELETE error: {e}")
            return None

# Initialize Firebase
db = FirebaseREST()

# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_uid' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Root URL - redirect to login if not authenticated, else dashboard"""
    if 'admin_uid' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - no sidebar shown here"""
    # If already logged in, go to dashboard
    if 'admin_uid' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Firebase Auth REST API - Sign in
            sign_in_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
            
            response = requests.post(sign_in_url, json={
                "email": email,
                "password": password,
                "returnSecureToken": True
            })
            
            data = response.json()
            
            if 'error' in data:
                error_message = data['error']['message']
                if 'INVALID_LOGIN_CREDENTIALS' in error_message or 'INVALID_PASSWORD' in error_message:
                    flash('Invalid email or password', 'danger')
                else:
                    flash(f'Login failed: {error_message}', 'danger')
                return render_template('login.html')
            
            # Check if user is admin in database
            uid = data['localId']
            user_data = db.get(f'users/{uid}')
            
            if not user_data:
                flash('User data not found', 'danger')
                return render_template('login.html')
            
            if user_data.get('type') != 'Admin':
                flash('Access denied. Admin privileges required.', 'danger')
                return render_template('login.html')
            
            # Set session
            session['admin_uid'] = uid
            session['admin_email'] = email
            session['admin_name'] = user_data.get('name', 'Admin')
            session['id_token'] = data['idToken']
            
            flash(f'Welcome back, {session["admin_name"]}!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
    
    # Render login WITHOUT sidebar (no base.html extension)
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# All routes below require login and show sidebar (use base.html)

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with sidebar"""
    stats = {
        'total_employees': 0,
        'total_duties': 0,
        'pending_leaves': 0,
        'today_attendance': 0
    }
    
    try:
        # Count employees
        employees = db.get('users')
        if employees:
            stats['total_employees'] = len([e for e in employees.values() if isinstance(e, dict) and e.get('type') != 'Admin'])
        
        # Count today's duties
        today = datetime.now().strftime('%Y-%m-%d')
        duties = db.get('duties')
        if duties:
            stats['total_duties'] = len([d for d in duties.values() if isinstance(d, dict) and d.get('date') == today])
        
        # Count pending leaves
        leaves = db.get('leave_requests')
        if leaves:
            stats['pending_leaves'] = len([l for l in leaves.values() if isinstance(l, dict) and l.get('status') == 'pending'])
        
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'warning')
    
    recent_activities = []
    
    return render_template('dashboard.html', stats=stats, activities=recent_activities)

@app.route('/employees')
@login_required
def employees():
    """Employee management page"""
    employees_list = []
    try:
        users = db.get('users')
        if users and isinstance(users, dict):
            for uid, data in users.items():
                if not isinstance(data, dict):
                    continue
                if data.get('type') == 'Admin':
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

@app.route('/api/employees', methods=['POST'])
@login_required
def add_employee():
    """API to add new employee"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        user_type = data.get('type', 'Student')
        department = data.get('department', '')
        
        # Create user in Firebase Auth via REST API
        sign_up_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
        
        auth_response = requests.post(sign_up_url, json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        })
        
        auth_data = auth_response.json()
        
        if 'error' in auth_data:
            return jsonify({'success': False, 'error': auth_data['error']['message']}), 400
        
        uid = auth_data['localId']
        
        # Save to database
        user_data = {
            'uid': uid,
            'name': name,
            'email': email,
            'type': user_type,
            'department': department,
            'leaveBalance': 20,
            'createdAt': datetime.now().isoformat()
        }
        
        db.put(f'users/{uid}', user_data)
        
        return jsonify({'success': True, 'uid': uid})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/employees/<uid>', methods=['DELETE'])
@login_required
def delete_employee(uid):
    """API to delete employee"""
    try:
        db.delete(f'users/{uid}')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/duties')
@login_required
def duties():
    """Duty schedule page"""
    duties_list = []
    employees = {}
    
    try:
        # Get employees for dropdown
        users = db.get('users')
        if users and isinstance(users, dict):
            for uid, user_data in users.items():
                if isinstance(user_data, dict) and user_data.get('type') != 'Admin':
                    employees[uid] = user_data.get('name', 'Unknown')
        
        # Get duties
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
                    'location': data.get('location', ''),
                    'status': data.get('status', 'scheduled')
                })
            
            duties_list.sort(key=lambda x: x['date'], reverse=True)
            
    except Exception as e:
        flash(f'Error loading duties: {str(e)}', 'danger')
    
    return render_template('duties.html', duties=duties_list, employees=employees)

@app.route('/api/duties', methods=['POST'])
@login_required
def create_duty():
    """API to create new duty"""
    try:
        data = request.json
        
        duty_data = {
            'employeeId': data.get('employeeId'),
            'title': data.get('title'),
            'date': data.get('date'),
            'startTime': data.get('startTime'),
            'endTime': data.get('endTime'),
            'location': data.get('location', 'Main Branch'),
            'status': 'scheduled',
            'createdBy': session['admin_uid'],
            'createdAt': datetime.now().isoformat()
        }
        
        result = db.post('duties', duty_data)
        
        # Create notification for employee
        if result and 'name' in result:
            notification_data = {
                'userId': data.get('employeeId'),
                'title': 'New Duty Assigned',
                'message': f"You have been assigned to {data.get('title')} on {data.get('date')}",
                'type': 'duty_assigned',
                'read': False,
                'createdAt': datetime.now().isoformat(),
                'relatedId': result['name'].split('/')[-1] if 'name' in result else ''
            }
            db.post('notifications', notification_data)
        
        return jsonify({'success': True, 'dutyId': result.get('name', '').split('/')[-1] if result else ''})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/duties/<duty_id>', methods=['DELETE'])
@login_required
def delete_duty(duty_id):
    """API to delete duty"""
    try:
        db.delete(f'duties/{duty_id}')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/attendance')
@login_required
def attendance():
    """Attendance tracking page"""
    attendance_list = []
    date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        attendance_data = db.get('attendance')
        
        if attendance_data and isinstance(attendance_data, dict):
            for uid, dates in attendance_data.items():
                if not isinstance(dates, dict):
                    continue
                    
                if date_filter in dates:
                    record = dates[date_filter]
                    if not isinstance(record, dict):
                        continue
                        
                    user_data = db.get(f'users/{uid}')
                    
                    attendance_list.append({
                        'uid': uid,
                        'employeeName': user_data.get('name', 'Unknown') if isinstance(user_data, dict) else 'Unknown',
                        'date': date_filter,
                        'checkIn': record.get('checkIn', '-'),
                        'checkOut': record.get('checkOut', '-'),
                        'status': record.get('status', 'unknown'),
                        'location': record.get('location', '-')
                    })
    except Exception as e:
        flash(f'Error loading attendance: {str(e)}', 'danger')
    
    return render_template('attendance.html', attendance=attendance_list, selected_date=date_filter)

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
                
                requests_list.append({
                    'id': req_id,
                    'employeeId': data.get('employeeId', ''),
                    'employeeName': user_data.get('name', 'Unknown') if isinstance(user_data, dict) else 'Unknown',
                    'startDate': data.get('startDate', ''),
                    'endDate': data.get('endDate', ''),
                    'reason': data.get('reason', ''),
                    'status': data.get('status', 'pending'),
                    'requestedAt': data.get('requestedAt', ''),
                    'approvedBy': data.get('approvedBy', ''),
                    'approvedAt': data.get('approvedAt', '')
                })
            
            requests_list.sort(key=lambda x: (0 if x['status'] == 'pending' else 1, x['requestedAt']), reverse=True)
            
    except Exception as e:
        flash(f'Error loading leave requests: {str(e)}', 'danger')
    
    return render_template('leave_requests.html', requests=requests_list)

@app.route('/api/leave-requests/<req_id>/approve', methods=['POST'])
@login_required
def approve_leave(req_id):
    """API to approve leave request"""
    try:
        updates = {
            'status': 'approved',
            'approvedBy': session['admin_uid'],
            'approvedAt': datetime.now().isoformat()
        }
        
        db.patch(f'leave_requests/{req_id}', updates)
        
        # Update leave balance
        leave_data = db.get(f'leave_requests/{req_id}')
        if leave_data and isinstance(leave_data, dict):
            employee_id = leave_data.get('employeeId')
            user_data = db.get(f'users/{employee_id}')
            if user_data and isinstance(user_data, dict):
                current_balance = user_data.get('leaveBalance', 0)
                try:
                    start = datetime.fromisoformat(leave_data.get('startDate', ''))
                    end = datetime.fromisoformat(leave_data.get('endDate', ''))
                    days = (end - start).days + 1
                    db.patch(f'users/{employee_id}', {'leaveBalance': max(0, current_balance - days)})
                except:
                    pass
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/leave-requests/<req_id>/reject', methods=['POST'])
@login_required
def reject_leave(req_id):
    """API to reject leave request"""
    try:
        updates = {
            'status': 'rejected',
            'approvedBy': session['admin_uid'],
            'approvedAt': datetime.now().isoformat()
        }
        
        db.patch(f'leave_requests/{req_id}', updates)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/notifications')
@login_required
def notifications():
    """Notifications page"""
    return render_template('notifications.html')

@app.route('/api/notifications/send', methods=['POST'])
@login_required
def send_notification():
    """API to send notification"""
    try:
        data = request.json
        user_ids = data.get('userIds', [])
        title = data.get('title')
        message = data.get('message')
        notification_type = data.get('type', 'general')
        
        if not user_ids:
            users = db.get('users')
            if users and isinstance(users, dict):
                user_ids = [uid for uid, u in users.items() if isinstance(u, dict) and u.get('type') != 'Admin']
        
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
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/reports')
@login_required
def reports():
    """Reports page"""
    return render_template('reports.html')

@app.route('/settings')
@login_required
def settings():
    """Settings page"""
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)