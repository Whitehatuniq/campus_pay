from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from models.schemas import CreateEventFeeRequest, AdminStatsResponse
from config.firebase import get_db
from middleware.auth_middleware import require_admin
from datetime import datetime
import uuid

router = APIRouter()


# ─── DASHBOARD STATS ─────────────────────────────────────────
@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(admin: dict = Depends(require_admin)):
    db = get_db()

    users = db.collection("users").get()
    transactions = db.collection("transactions").get()

    txn_list = [doc.to_dict() for doc in transactions]
    total_amount = sum(t["amount"] for t in txn_list if t.get("status") == "success")
    pending = sum(1 for t in txn_list if t.get("status") == "pending")

    return AdminStatsResponse(
        total_users=len(users),
        total_transactions=len(txn_list),
        total_amount_processed=total_amount,
        pending_payments=pending
    )


# ─── USER MANAGEMENT ─────────────────────────────────────────
@router.get("/users", response_model=List[dict])
async def get_all_users(
    role: Optional[str] = None,
    admin: dict = Depends(require_admin)
):
    db = get_db()
    query = db.collection("users")

    if role:
        query = query.where("role", "==", role)

    users = query.get()
    result = []
    for doc in users:
        user = doc.to_dict()
        user.pop("password", None)   # Never expose passwords
        result.append(user)

    return result


@router.patch("/users/{uid}/deactivate", response_model=dict)
async def deactivate_user(uid: str, admin: dict = Depends(require_admin)):
    db = get_db()

    doc = db.collection("users").document(uid).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    db.collection("users").document(uid).update({"is_active": False})
    db.collection("wallets").document(uid).update({"is_active": False})

    return {"message": f"User {uid} deactivated successfully"}


@router.patch("/users/{uid}/activate", response_model=dict)
async def activate_user(uid: str, admin: dict = Depends(require_admin)):
    db = get_db()

    db.collection("users").document(uid).update({"is_active": True})
    db.collection("wallets").document(uid).update({"is_active": True})

    return {"message": f"User {uid} activated successfully"}


# ─── EVENT FEE MANAGEMENT ────────────────────────────────────
@router.post("/events/create", response_model=dict)
async def create_event_fee(
    data: CreateEventFeeRequest,
    admin: dict = Depends(require_admin)
):
    db = get_db()

    # Get admin's wallet UPI for receiving payments
    admin_wallet = db.collection("wallets").document(admin["sub"]).get().to_dict()

    event_id = str(uuid.uuid4())
    event_data = {
        "event_id": event_id,
        "event_name": data.event_name,
        "amount": data.amount,
        "due_date": data.due_date,
        "description": data.description,
        "target_role": data.target_role,
        "receiver_upi": admin_wallet["upi_id"],
        "created_by": admin["sub"],
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True
    }

    db.collection("events").document(event_id).set(event_data)
    return {"message": "Event fee created", "event_id": event_id}


@router.get("/events", response_model=List[dict])
async def get_all_events(admin: dict = Depends(require_admin)):
    db = get_db()
    events = db.collection("events").get()
    return [doc.to_dict() for doc in events]


# ─── FEE CONFIG (exam/back fees) ─────────────────────────────
@router.post("/fee-config/set", response_model=dict)
async def set_fee_config(
    fee_type: str,     # "regular" or "back"
    amount: float,
    description: str,
    admin: dict = Depends(require_admin)
):
    db = get_db()
    admin_wallet = db.collection("wallets").document(admin["sub"]).get().to_dict()

    db.collection("fee_config").document(fee_type).set({
        "fee_type": fee_type,
        "amount": amount,
        "description": description,
        "receiver_upi": admin_wallet["upi_id"],
        "updated_at": datetime.utcnow().isoformat(),
        "updated_by": admin["sub"]
    })

    return {"message": f"{fee_type} fee config updated to ₹{amount}"}


# ─── ALL TRANSACTIONS (ADMIN VIEW) ────────────────────────────
@router.get("/transactions", response_model=List[dict])
async def get_all_transactions(
    payment_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    admin: dict = Depends(require_admin)
):
    db = get_db()
    query = db.collection("transactions")

    if payment_type:
        query = query.where("payment_type", "==", payment_type)

    txns = query.get()
    result = [doc.to_dict() for doc in txns]
    result.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    return result[:limit]
