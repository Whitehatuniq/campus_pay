"""
Creates 5 dummy student accounts in Firebase.
Run: python create_dummy_users.py
"""
import firebase_admin
from firebase_admin import credentials, firestore
import sys, os, uuid
from datetime import datetime
import bcrypt

KEY_PATH = "serviceAccountKey.json"
if not os.path.exists(KEY_PATH):
    print("serviceAccountKey.json not found!")
    sys.exit(1)

cred = credentials.Certificate(KEY_PATH)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

STUDENTS = [
    {"name": "Arjun Sharma",   "email": "arjun.sharma@poornima.edu",   "enrollment_no": "2024BCA102", "phone": "9876543211"},
    {"name": "Priya Patel",    "email": "priya.patel@poornima.edu",    "enrollment_no": "2024BCA103", "phone": "9876543212"},
    {"name": "Rahul Verma",    "email": "rahul.verma@poornima.edu",    "enrollment_no": "2024BCA104", "phone": "9876543213"},
    {"name": "Sneha Gupta",    "email": "sneha.gupta@poornima.edu",    "enrollment_no": "2024BCA105", "phone": "9876543214"},
    {"name": "Amit Rajput",    "email": "amit.rajput@poornima.edu",    "enrollment_no": "2024BCA106", "phone": "9876543215"},
]

PASSWORD = "Campus@123"
UPI_PIN  = "1234"

print("\n" + "="*60)
print("Creating 5 dummy student accounts...")
print("="*60)

for student in STUDENTS:
    uid = str(uuid.uuid4())
    upi_id = f"{student['name'].split()[0].lower()}{uid[:4]}@campuspay"

    # Create user
    db.collection("users").document(uid).set({
        "uid": uid,
        "name": student["name"],
        "email": student["email"],
        "password": hash_password(PASSWORD),
        "role": "student",
        "enrollment_no": student["enrollment_no"],
        "phone": student["phone"],
        "avatar": "👨‍🎓",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    })

    # Create wallet with ₹500 balance
    db.collection("wallets").document(uid).set({
        "user_id": uid,
        "balance": 500.0,
        "upi_id": upi_id,
        "upi_pin": hash_password(UPI_PIN),
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    })

    # Add pending fees
    db.collection("student_pending_fees").document(student["enrollment_no"]).set({
        "enrollment_no": student["enrollment_no"],
        "pending_fee_ids": ["exam_sem4_2024", "back_math_2024"],
        "paid_fee_ids": []
    })

    print(f"  ✅ {student['name']}")
    print(f"     Email:    {student['email']}")
    print(f"     UPI ID:   {upi_id}")
    print(f"     Balance:  ₹500.00")
    print()

print("="*60)
print(f"Password for ALL accounts: {PASSWORD}")
print(f"UPI PIN for ALL accounts:  {UPI_PIN}")
print("="*60 + "\n")
