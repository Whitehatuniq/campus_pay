from fastapi import APIRouter, HTTPException, Depends
from config.firebase import get_db
from config.security import verify_password
from middleware.auth_middleware import get_current_user
from datetime import datetime
import uuid

router = APIRouter()

UNIVERSITY_UPI = "poornima.university@campuspay"


@router.get("/pending")
async def get_pending_fees(current_user: dict = Depends(get_current_user)):
    """Get pending fees for the logged-in student only."""
    db = get_db()
    uid = current_user["sub"]

    # Get student's enrollment number
    user_doc = db.collection("users").document(uid).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    user = user_doc.to_dict()
    enrollment_no = user.get("enrollment_no")

    if not enrollment_no:
        raise HTTPException(status_code=400, detail="Enrollment number not set on your account")

    # Get student's pending fee IDs
    pending_doc = db.collection("student_pending_fees").document(enrollment_no).get()

    if not pending_doc.exists:
        return {"pending_fees": [], "paid_fees": [], "enrollment_no": enrollment_no}

    pending_data = pending_doc.to_dict()
    pending_ids = pending_data.get("pending_fee_ids", [])
    paid_ids = pending_data.get("paid_fee_ids", [])

    # Fetch fee details for each pending fee
    pending_fees = []
    for fee_id in pending_ids:
        fee_doc = db.collection("fee_types").document(fee_id).get()
        if fee_doc.exists:
            fee = fee_doc.to_dict()
            pending_fees.append(fee)

    # Fetch paid fee details
    paid_fees = []
    for fee_id in paid_ids:
        fee_doc = db.collection("fee_types").document(fee_id).get()
        if fee_doc.exists:
            fee = fee_doc.to_dict()
            paid_fees.append(fee)

    return {
        "enrollment_no": enrollment_no,
        "pending_fees": pending_fees,
        "paid_fees": paid_fees,
        "total_pending": sum(f["amount"] for f in pending_fees)
    }


@router.post("/pay/{fee_id}")
async def pay_fee(
    fee_id: str,
    upi_pin: str,
    current_user: dict = Depends(get_current_user)
):
    """Pay a specific pending fee."""
    db = get_db()
    uid = current_user["sub"]

    # Get student info
    user_doc = db.collection("users").document(uid).get()
    user = user_doc.to_dict()
    enrollment_no = user.get("enrollment_no")

    if not enrollment_no:
        raise HTTPException(status_code=400, detail="Enrollment number not set")

    # Check fee exists
    fee_doc = db.collection("fee_types").document(fee_id).get()
    if not fee_doc.exists:
        raise HTTPException(status_code=404, detail="Fee not found")
    fee = fee_doc.to_dict()

    # Check fee is actually pending for this student
    pending_doc = db.collection("student_pending_fees").document(enrollment_no).get()
    if not pending_doc.exists:
        raise HTTPException(status_code=400, detail="No pending fees found for your account")

    pending_data = pending_doc.to_dict()
    if fee_id not in pending_data.get("pending_fee_ids", []):
        raise HTTPException(status_code=400, detail="This fee is not pending for your account")

    # Get sender wallet
    sender_wallet_ref = db.collection("wallets").document(uid)
    sender_wallet = sender_wallet_ref.get().to_dict()

    if not sender_wallet:
        raise HTTPException(status_code=400, detail="Wallet not found")

    # Validate UPI PIN
    if not verify_password(upi_pin, sender_wallet["upi_pin"]):
        raise HTTPException(status_code=401, detail="Incorrect UPI PIN")

    # Check balance
    if sender_wallet["balance"] < fee["amount"]:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Required: ₹{fee['amount']}, Available: ₹{sender_wallet['balance']}"
        )

    # Find university wallet
    uni_wallets = db.collection("wallets").where("upi_id", "==", UNIVERSITY_UPI).get()
    if not uni_wallets:
        raise HTTPException(status_code=404, detail="University wallet not found")

    uni_wallet_ref = db.collection("wallets").document(uni_wallets[0].id)
    uni_wallet = uni_wallet_ref.get().to_dict()

    # Deduct from student, credit to university
    sender_wallet_ref.update({"balance": sender_wallet["balance"] - fee["amount"]})
    uni_wallet_ref.update({"balance": uni_wallet["balance"] + fee["amount"]})

    # Move fee from pending to paid
    updated_pending = [f for f in pending_data["pending_fee_ids"] if f != fee_id]
    updated_paid = pending_data.get("paid_fee_ids", []) + [fee_id]

    db.collection("student_pending_fees").document(enrollment_no).update({
        "pending_fee_ids": updated_pending,
        "paid_fee_ids": updated_paid
    })

    # Log transaction
    txn_id = str(uuid.uuid4())
    db.collection("transactions").document(txn_id).set({
        "transaction_id": txn_id,
        "sender_id": uid,
        "sender_upi": sender_wallet["upi_id"],
        "receiver_upi": UNIVERSITY_UPI,
        "amount": fee["amount"],
        "payment_type": fee["fee_type"],
        "description": f"{fee['fee_name']} - {enrollment_no}",
        "status": "success",
        "fee_id": fee_id,
        "enrollment_no": enrollment_no,
        "timestamp": datetime.utcnow().isoformat()
    })

    return {
        "message": f"₹{fee['amount']} paid successfully for {fee['fee_name']}",
        "transaction_id": txn_id,
        "fee_name": fee["fee_name"],
        "amount": fee["amount"],
        "remaining_pending": len(updated_pending)
    }
