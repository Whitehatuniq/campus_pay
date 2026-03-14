from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from config.firebase import get_db
from config.security import verify_password
from middleware.auth_middleware import get_current_user
from datetime import datetime
import uuid

router = APIRouter()


class EventRegistration(BaseModel):
    event_id: str
    name: str
    branch: str
    year: str
    enrollment_no: str
    contact_no: str
    upi_pin: str


@router.get("/list")
async def get_events():
    """Get all active events — public endpoint."""
    db = get_db()
    events = db.collection("events").where("is_active", "==", True).get()
    return [doc.to_dict() for doc in events]


@router.get("/my-registrations")
async def get_my_registrations(current_user: dict = Depends(get_current_user)):
    """Get all events the logged-in student has registered for."""
    db = get_db()
    uid = current_user["sub"]
    regs = db.collection("event_registrations").where("user_id", "==", uid).get()
    return [doc.to_dict() for doc in regs]


@router.post("/register")
async def register_for_event(
    data: EventRegistration,
    current_user: dict = Depends(get_current_user)
):
    """Register for an event and pay the fee."""
    db = get_db()
    uid = current_user["sub"]

    # Check event exists
    event_doc = db.collection("events").document(data.event_id).get()
    if not event_doc.exists:
        raise HTTPException(status_code=404, detail="Event not found")
    event = event_doc.to_dict()

    if not event.get("is_active"):
        raise HTTPException(status_code=400, detail="Event registration is closed")

    # Check not already registered
    existing = db.collection("event_registrations")\
        .where("user_id", "==", uid)\
        .where("event_id", "==", data.event_id)\
        .get()
    if existing:
        raise HTTPException(status_code=400, detail="You are already registered for this event")

    # Get sender wallet
    sender_wallet_ref = db.collection("wallets").document(uid)
    sender_wallet = sender_wallet_ref.get().to_dict()

    if not sender_wallet:
        raise HTTPException(status_code=400, detail="Wallet not found")

    # Validate UPI PIN
    if not verify_password(data.upi_pin, sender_wallet["upi_pin"]):
        raise HTTPException(status_code=401, detail="Incorrect UPI PIN")

    # Check balance
    if sender_wallet["balance"] < event["fee"]:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Required: ₹{event['fee']}, Available: ₹{sender_wallet['balance']}"
        )

    # Find university wallet
    uni_wallets = db.collection("wallets").where("upi_id", "==", event["receiver_upi"]).get()
    if not uni_wallets:
        raise HTTPException(status_code=404, detail="University wallet not found")

    uni_wallet_ref = db.collection("wallets").document(uni_wallets[0].id)
    uni_wallet = uni_wallet_ref.get().to_dict()

    # Deduct from student, credit to university
    sender_wallet_ref.update({"balance": sender_wallet["balance"] - event["fee"]})
    uni_wallet_ref.update({"balance": uni_wallet["balance"] + event["fee"]})

    # Save registration
    reg_id = str(uuid.uuid4())
    db.collection("event_registrations").document(reg_id).set({
        "registration_id": reg_id,
        "user_id": uid,
        "event_id": data.event_id,
        "event_name": event["event_name"],
        "name": data.name,
        "branch": data.branch,
        "year": data.year,
        "enrollment_no": data.enrollment_no,
        "contact_no": data.contact_no,
        "amount_paid": event["fee"],
        "registered_at": datetime.utcnow().isoformat()
    })

    # Log transaction
    txn_id = str(uuid.uuid4())
    db.collection("transactions").document(txn_id).set({
        "transaction_id": txn_id,
        "sender_id": uid,
        "sender_upi": sender_wallet["upi_id"],
        "receiver_upi": event["receiver_upi"],
        "amount": event["fee"],
        "payment_type": "event_fee",
        "description": f"Event Registration: {event['event_name']} - {data.enrollment_no}",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    })

    return {
        "message": f"Successfully registered for {event['event_name']}!",
        "registration_id": reg_id,
        "transaction_id": txn_id,
        "event_name": event["event_name"],
        "amount_paid": event["fee"]
    }
