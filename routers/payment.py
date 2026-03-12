from fastapi import APIRouter, HTTPException, Depends
from models.schemas import PaymentRequest, PaymentResponse
from config.firebase import get_db
from config.security import verify_password
from middleware.auth_middleware import get_current_user
from datetime import datetime
import uuid

router = APIRouter()


@router.post("/pay", response_model=PaymentResponse)
async def make_payment(
    data: PaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Core payment endpoint — works like UPI Send Money.
    Deducts from sender wallet, credits receiver wallet.
    """
    db = get_db()
    uid = current_user["sub"]

    # ── 1. Get sender wallet ──────────────────────────────────
    sender_wallet_ref = db.collection("wallets").document(uid)
    sender_wallet = sender_wallet_ref.get().to_dict()

    if not sender_wallet or not sender_wallet.get("is_active"):
        raise HTTPException(status_code=400, detail="Sender wallet not found or inactive")

    # ── 2. Validate UPI PIN ───────────────────────────────────
    if not verify_password(data.upi_pin, sender_wallet["upi_pin"]):
        raise HTTPException(status_code=401, detail="Incorrect UPI PIN")

    # ── 3. Check balance ──────────────────────────────────────
    if sender_wallet["balance"] < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    # ── 4. Find receiver by UPI ID ────────────────────────────
    receivers = db.collection("wallets").where("upi_id", "==", data.receiver_upi).get()
    if not receivers:
        raise HTTPException(status_code=404, detail=f"UPI ID '{data.receiver_upi}' not found")

    receiver_wallet_ref = db.collection("wallets").document(receivers[0].id)
    receiver_wallet = receiver_wallet_ref.get().to_dict()

    if not receiver_wallet.get("is_active"):
        raise HTTPException(status_code=400, detail="Receiver wallet is inactive")

    # ── 5. Transfer (debit sender, credit receiver) ───────────
    sender_wallet_ref.update({"balance": sender_wallet["balance"] - data.amount})
    receiver_wallet_ref.update({"balance": receiver_wallet["balance"] + data.amount})

    # ── 6. Log transaction ────────────────────────────────────
    txn_id = str(uuid.uuid4())
    txn_data = {
        "transaction_id": txn_id,
        "sender_id": uid,
        "sender_upi": sender_wallet["upi_id"],
        "receiver_upi": data.receiver_upi,
        "amount": data.amount,
        "payment_type": data.payment_type,
        "description": data.description or f"{data.payment_type} payment",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }
    db.collection("transactions").document(txn_id).set(txn_data)

    return PaymentResponse(
        transaction_id=txn_id,
        status="success",
        amount=data.amount,
        receiver_upi=data.receiver_upi,
        payment_type=data.payment_type,
        timestamp=txn_data["timestamp"],
        message=f"₹{data.amount} paid successfully to {data.receiver_upi}"
    )


@router.post("/pay-event-fee", response_model=PaymentResponse)
async def pay_event_fee(
    event_id: str,
    upi_pin: str,
    current_user: dict = Depends(get_current_user)
):
    """Pay a specific campus event fee using event ID."""
    db = get_db()

    # Fetch event details
    event_doc = db.collection("events").document(event_id).get()
    if not event_doc.exists:
        raise HTTPException(status_code=404, detail="Event not found")

    event = event_doc.to_dict()

    # Reuse core payment logic by building a PaymentRequest
    payment_data = PaymentRequest(
        receiver_upi=event["receiver_upi"],
        amount=event["amount"],
        payment_type="event_fee",
        description=f"Event fee: {event['event_name']}",
        upi_pin=upi_pin
    )

    return await make_payment(payment_data, current_user)


@router.post("/pay-exam-fee", response_model=PaymentResponse)
async def pay_exam_fee(
    fee_type: str,   # "regular" or "back"
    upi_pin: str,
    current_user: dict = Depends(get_current_user)
):
    """Pay exam or back/due fees."""
    db = get_db()
    uid = current_user["sub"]

    # Fetch fee structure from config collection
    fee_doc = db.collection("fee_config").document(fee_type).get()
    if not fee_doc.exists:
        raise HTTPException(status_code=404, detail=f"Fee type '{fee_type}' not found")

    fee = fee_doc.to_dict()

    payment_data = PaymentRequest(
        receiver_upi=fee["receiver_upi"],
        amount=fee["amount"],
        payment_type="back_fee" if fee_type == "back" else "exam_fee",
        description=fee.get("description", f"{fee_type} exam fee"),
        upi_pin=upi_pin
    )

    return await make_payment(payment_data, current_user)
