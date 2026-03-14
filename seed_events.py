"""
Run this script once to seed fake events in Firestore.
Usage: python seed_events.py
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

UNIVERSITY_UPI = "poornima.university@campuspay"

EVENTS = [
    {
        "event_id": "techfest_2024",
        "event_name": "TechFest 2024",
        "description": "Annual technical festival with coding, robotics and more",
        "fee": 200.0,
        "date": "2024-05-15",
        "last_date": "2024-05-10",
        "venue": "Main Auditorium",
        "receiver_upi": UNIVERSITY_UPI,
        "is_active": True
    },
    {
        "event_id": "sports_day_2024",
        "event_name": "Annual Sports Day",
        "description": "Inter-college sports competition",
        "fee": 150.0,
        "date": "2024-05-20",
        "last_date": "2024-05-15",
        "venue": "Sports Ground",
        "receiver_upi": UNIVERSITY_UPI,
        "is_active": True
    },
    {
        "event_id": "cultural_fest_2024",
        "event_name": "Cultural Fest 2024",
        "description": "Music, dance and drama performances",
        "fee": 100.0,
        "date": "2024-06-01",
        "last_date": "2024-05-25",
        "venue": "Open Air Theatre",
        "receiver_upi": UNIVERSITY_UPI,
        "is_active": True
    },
    {
        "event_id": "hackathon_2024",
        "event_name": "24Hr Hackathon",
        "description": "24 hour coding competition with prizes",
        "fee": 250.0,
        "date": "2024-05-18",
        "last_date": "2024-05-12",
        "venue": "Computer Lab",
        "receiver_upi": UNIVERSITY_UPI,
        "is_active": True
    }
]

print("Seeding events...")
for event in EVENTS:
    db.collection("events").document(event["event_id"]).set(event)
    print(f"  ✅ Added: {event['event_name']} - ₹{event['fee']}")

print("\n🎉 Events seeded successfully!")
