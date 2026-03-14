from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest, UserProfile
from config.firebase import get_db
from config.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from middleware.auth_middleware import get_current_user
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/register", response_model=dict, status_code=201)
async def register(data: RegisterRequest):
    db = get_db()

    # Check if email already exists
    existing = db.collection("users").where("email", "==", data.email).get()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    uid = str(uuid.uuid4())
    upi_id = f"{data.name.lower().replace(' ', '')}{uid[:4]}@campuspay"

    user_data = {
        "uid": uid,
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password),
        "role": data.role,
        "enrollment_no": data.enrollment_no,
        "phone": data.phone,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }

    # Save user to Firestore
    db.collection("users").document(uid).set(user_data)

    # Auto-create wallet for the user
    wallet_data = {
        "user_id": uid,
        "balance": 0.0,
        "upi_id": upi_id,
        "upi_pin": hash_password("1234"),   # Default PIN — user should change it
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    db.collection("wallets").document(uid).set(wallet_data)

    return {
        "message": "Registration successful",
        "user_id": uid,
        "upi_id": upi_id
    }


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    db = get_db()

    users = db.collection("users").where("email", "==", data.email).get()
    if not users:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = users[0].to_dict()

    if not user.get("is_active"):
        raise HTTPException(status_code=403, detail="Account is deactivated")

    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token_payload = {
        "sub": user["uid"],
        "email": user["email"],
        "role": user["role"],
        "name": user["name"]
    }

    return TokenResponse(
        access_token=create_access_token(token_payload),
        refresh_token=create_refresh_token(token_payload),
        user_id=user["uid"],
        role=user["role"]
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(data: RefreshTokenRequest):
    payload = decode_token(data.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = create_access_token({
        "sub": payload["sub"],
        "email": payload["email"],
        "role": payload["role"],
        "name": payload["name"]
    })

    return {"access_token": new_access, "token_type": "bearer"}


@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    db = get_db()
    uid = current_user["sub"]

    doc = db.collection("users").document(uid).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    user = doc.to_dict()
    user.pop("password", None)   # Never expose password
    return UserProfile(**user)


@router.post("/change-password", response_model=dict)
async def change_password(
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    uid = current_user["sub"]

    doc = db.collection("users").document(uid).get()
    user = doc.to_dict()

    if not verify_password(old_password, user["password"]):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    db.collection("users").document(uid).update({
        "password": hash_password(new_password)
    })

    return {"message": "Password changed successfully"}


@router.patch("/update-profile", response_model=dict)
async def update_profile(
    phone: str = None,
    avatar: str = None,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    uid = current_user["sub"]

    update_data = {}
    if phone: update_data["phone"] = phone
    if avatar: update_data["avatar"] = avatar

    if update_data:
        db.collection("users").document(uid).update(update_data)

    return {"message": "Profile updated successfully"}


@router.patch("/update-profile", response_model=dict)
async def update_profile(
    phone: str = None,
    avatar: str = None,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    uid = current_user["sub"]
    update_data = {}
    if phone: update_data["phone"] = phone
    if avatar: update_data["avatar"] = avatar
    if update_data:
        db.collection("users").document(uid).update(update_data)
    return {"message": "Profile updated successfully"}
