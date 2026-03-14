"""
Run this script once to seed fake fee data in Firestore.
Usage: python seed_fees.py
"""
import firebase_admin
from firebase_admin import credentials, firestore
import sys
import os

KEY_PATH = "serviceAccountKey.json"
if not os.path.exists(KEY_PATH):
    print("❌ serviceAccountKey.json not found!")
    sys.exit(1)

cred = credentials.Certificate(KEY_PATH)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ── University receiver UPI (admin account) ──────────────────
UNIVERSITY_UPI = "poornima.university@campuspay"

# ── Fee types available ───────────────────────────────────────
FEE_TYPES = [
    {
        "fee_id": "exam_sem4_2024",
        "fee_name": "Semester 4 Exam Fee",
        "fee_type": "exam_fee",
        "amount": 1500.0,
        "due_date": "2024-04-30",
        "description": "End semester examination fee for Semester 4",
        "receiver_upi": UNIVERSITY_UPI,
        "is_active": True
    },
    {
        "fee_id": "back_math_2024",
        "fee_name": "Back Paper - Mathematics",
        "fee_type": "back_fee",
        "amount": 500.0,
        "due_date": "2024-04-15",
        "description": "Back paper examination fee for Mathematics",
        "receiver_upi": UNIVERSITY_UPI,
        "is_active": True
    },
    {
        "fee_id": "back_physics_2024",
        "fee_name": "Back Paper - Physics",
        "fee_type": "back_fee",
        "amount": 500.0,
        "due_date": "2024-04-15",
        "description": "Back paper examination fee for Physics",
        "receiver_upi": UNIVERSITY_UPI,
        "is_active": True
    },
    {
        "fee_id": "library_fine_2024",
        "fee_name": "Library Fine",
        "fee_type": "library_fine",
        "amount": 150.0,
        "due_date": "2024-03-31",
        "description": "Overdue library book fine",
        "receiver_upi": UNIVERSITY_UPI,
        "is_active": True
    },
    {
        "fee_id": "sports_fee_2024",
        "fee_name": "Sports & Cultural Fee",
        "fee_type": "event_fee",
        "amount": 800.0,
        "due_date": "2024-05-01",
        "description": "Annual sports and cultural activities fee",
        "receiver_upi": UNIVERSITY_UPI,
        "is_active": True
    }
]

# ── Seed fee types ────────────────────────────────────────────
print("Seeding fee types...")
for fee in FEE_TYPES:
    db.collection("fee_types").document(fee["fee_id"]).set(fee)
    print(f"  ✅ Added: {fee['fee_name']}")

# ── Assign pending fees to a specific student ─────────────────
# Replace with real enrollment numbers when connecting real DB
STUDENT_PENDING_FEES = [
    {
        "enrollment_no": "2024BCA101",   # Eklavya's enrollment
        "pending_fees": [
            "exam_sem4_2024",
            "back_math_2024",
            "library_fine_2024"
        ]
    },
    {
        "enrollment_no": "2024BCA102",
        "pending_fees": [
            "exam_sem4_2024",
            "sports_fee_2024"
        ]
    }
]

print("\nSeeding student pending fees...")
for student in STUDENT_PENDING_FEES:
    db.collection("student_pending_fees").document(
        student["enrollment_no"]
    ).set({
        "enrollment_no": student["enrollment_no"],
        "pending_fee_ids": student["pending_fees"],
        "paid_fee_ids": []
    })
    print(f"  ✅ Added pending fees for: {student['enrollment_no']}")

# ── Create university wallet if not exists ────────────────────
print("\nSetting up university wallet...")
uni_wallet = db.collection("wallets").where("upi_id", "==", UNIVERSITY_UPI).get()
if not uni_wallet:
    db.collection("wallets").document("university").set({
        "user_id": "university",
        "balance": 0.0,
        "upi_id": UNIVERSITY_UPI,
        "upi_pin": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6ThtOf/SIhRFHAgLRMoTYSwDoBTT2",
        "is_active": True
    })
    print("  ✅ University wallet created")
else:
    print("  ✅ University wallet already exists")

print("\n🎉 Seeding complete!")
print(f"University UPI: {UNIVERSITY_UPI}")
