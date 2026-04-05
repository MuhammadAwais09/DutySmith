"""
Create Admin User for DutySmith
Run this script once to set up admin credentials
"""

import requests
import json
from datetime import datetime

# ==================== CONFIGURATION ====================

FIREBASE_API_KEY = "AIzaSyDdRS9eN2K6Hq39RS6eoYnyUWqkjseQwzY"
FIREBASE_DATABASE_URL = "https://dutysmith-25ccb-default-rtdb.firebaseio.com"

# Admin Credentials - Change these as needed
ADMIN_EMAIL = "admin@dutysmith.com"
ADMIN_PASSWORD = "Admin@123456"
ADMIN_NAME = "System Administrator"
ADMIN_DEPARTMENT = "Administration"

# ==================== FUNCTIONS ====================

def create_firebase_auth_user(email, password):
    """Create user in Firebase Authentication"""
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if 'error' in data:
            return None, data['error']['message']
        
        return data['localId'], None  # Return UID
        
    except Exception as e:
        return None, str(e)


def add_user_to_database(uid, name, email, user_type, department):
    """Add user data to Firebase Realtime Database"""
    
    url = f"{FIREBASE_DATABASE_URL}/users/{uid}.json"
    
    user_data = {
        "uid": uid,
        "name": name,
        "email": email,
        "type": user_type,  # "Admin", "Teacher", "Student", "Staff"
        "department": department,
        "leaveBalance": 0 if user_type == "Admin" else 20,
        "createdAt": datetime.now().isoformat(),
        "status": "active"
    }
    
    try:
        response = requests.put(url, json=user_data, timeout=10)
        
        if response.status_code == 200:
            return True, None
        else:
            return False, response.text
            
    except Exception as e:
        return False, str(e)


def get_existing_user_uid(email, password):
    """Try to sign in and get UID if user already exists"""
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if 'error' in data:
            return None
        
        return data['localId']
        
    except:
        return None


def check_user_in_database(uid):
    """Check if user exists in database"""
    
    url = f"{FIREBASE_DATABASE_URL}/users/{uid}.json"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data is not None
    except:
        return False


def create_admin():
    """Main function to create admin user"""
    
    print("\n" + "=" * 60)
    print("🛠️  DUTYSMITH ADMIN USER SETUP")
    print("=" * 60)
    
    # Step 1: Try to create new user
    print(f"\n📧 Email: {ADMIN_EMAIL}")
    print(f"🔑 Password: {ADMIN_PASSWORD}")
    print(f"👤 Name: {ADMIN_NAME}")
    print(f"🏢 Department: {ADMIN_DEPARTMENT}")
    print(f"👑 Role: Admin")
    
    print("\n⏳ Creating Firebase Auth user...")
    
    uid, error = create_firebase_auth_user(ADMIN_EMAIL, ADMIN_PASSWORD)
    
    if error:
        if 'EMAIL_EXISTS' in error:
            print("ℹ️  Email already exists. Trying to get existing user...")
            uid = get_existing_user_uid(ADMIN_EMAIL, ADMIN_PASSWORD)
            
            if uid:
                print(f"✅ Found existing user: {uid}")
            else:
                print("❌ Could not retrieve existing user. Check password.")
                return False
        else:
            print(f"❌ Auth Error: {error}")
            return False
    else:
        print(f"✅ Created Auth user: {uid}")
    
    # Step 2: Add/Update user in database
    print("\n⏳ Adding user to Realtime Database...")
    
    success, db_error = add_user_to_database(
        uid=uid,
        name=ADMIN_NAME,
        email=ADMIN_EMAIL,
        user_type="Admin",  # This makes them an admin!
        department=ADMIN_DEPARTMENT
    )
    
    if success:
        print("✅ User added to database with Admin role!")
    else:
        print(f"❌ Database Error: {db_error}")
        return False
    
    # Success!
    print("\n" + "=" * 60)
    print("🎉 ADMIN USER CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"""
┌─────────────────────────────────────────┐
│         LOGIN CREDENTIALS               │
├─────────────────────────────────────────┤
│  📧 Email:    {ADMIN_EMAIL:<24} │
│  🔑 Password: {ADMIN_PASSWORD:<24} │
│  👑 Role:     Administrator             │
│  🆔 UID:      {uid:<24} │
└─────────────────────────────────────────┘

🌐 Login URL: http://localhost:5000/login
    """)
    
    return True


def create_test_users():
    """Create additional test users (optional)"""
    
    test_users = [
        {
            "email": "teacher@dutysmith.com",
            "password": "Teacher@123",
            "name": "John Teacher",
            "type": "Teacher",
            "department": "Computer Science"
        },
        {
            "email": "student@dutysmith.com",
            "password": "Student@123",
            "name": "Jane Student",
            "type": "Student",
            "department": "Computer Science"
        },
        {
            "email": "staff@dutysmith.com",
            "password": "Staff@123",
            "name": "Bob Staff",
            "type": "Staff",
            "department": "Administration"
        }
    ]
    
    print("\n" + "=" * 60)
    print("📝 CREATING TEST USERS")
    print("=" * 60)
    
    for user in test_users:
        print(f"\n⏳ Creating {user['type']}: {user['email']}...")
        
        uid, error = create_firebase_auth_user(user['email'], user['password'])
        
        if error and 'EMAIL_EXISTS' in error:
            uid = get_existing_user_uid(user['email'], user['password'])
            if not uid:
                print(f"  ⚠️  Skipped (exists with different password)")
                continue
        elif error:
            print(f"  ❌ Error: {error}")
            continue
        
        success, _ = add_user_to_database(
            uid=uid,
            name=user['name'],
            email=user['email'],
            user_type=user['type'],
            department=user['department']
        )
        
        if success:
            print(f"  ✅ Created: {user['email']} / {user['password']}")
        else:
            print(f"  ❌ Database error")
    
    print("\n" + "=" * 60)
    print("📋 ALL TEST USERS")
    print("=" * 60)
    print("""
┌────────────────────────────────────────────────────────┐
│  TYPE     │  EMAIL                  │  PASSWORD        │
├────────────────────────────────────────────────────────┤
│  Admin    │  admin@dutysmith.com    │  Admin@123456    │
│  Teacher  │  teacher@dutysmith.com  │  Teacher@123     │
│  Student  │  student@dutysmith.com  │  Student@123     │
│  Staff    │  staff@dutysmith.com    │  Staff@123       │
└────────────────────────────────────────────────────────┘
    """)


# ==================== MAIN ====================

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🛡️  DUTYSMITH ADMIN SETUP  🛡️                ║
║                                                           ║
║   This script will create admin credentials for login     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Create admin user
    admin_created = create_admin()
    
    if admin_created:
        # Ask if user wants to create test users
        print("\n" + "-" * 60)
        create_tests = input("Do you want to create test users? (y/n): ").strip().lower()
        
        if create_tests == 'y':
            create_test_users()
    
    print("\n✅ Setup complete! Run 'python app.py' to start the server.")
    print("=" * 60 + "\n")