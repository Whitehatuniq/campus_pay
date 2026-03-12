import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

# Initialize Firebase Admin SDK
# Download your serviceAccountKey.json from Firebase Console >
# Project Settings > Service Accounts > Generate new private key

cred = credentials.Certificate("serviceAccountKey.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_db():
    return db

def get_auth():
    return auth
