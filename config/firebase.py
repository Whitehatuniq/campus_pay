import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import sys
import json

KEY_PATH = "serviceAccountKey.json"

if not firebase_admin._apps:
    google_creds = os.getenv("GOOGLE_CREDENTIALS")

    if google_creds:
        cred_dict = json.loads(google_creds)
        cred = credentials.Certificate(cred_dict)
    elif os.path.exists(KEY_PATH):
        cred = credentials.Certificate(KEY_PATH)
    else:
        print("❌ FIREBASE SETUP REQUIRED - add serviceAccountKey.json or GOOGLE_CREDENTIALS env var")
        sys.exit(1)

    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_db():
    return db

def get_auth():
    return auth
