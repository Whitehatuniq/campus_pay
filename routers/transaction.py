from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from models.schemas import TransactionRecord
from config.firebase import get_db
from middleware.auth_middleware import get_current_user

router = APIRouter()


@router.get("/history", response_model=List[dict])
async def get_transaction_history(
    limit: int = Query(20, ge=1, le=100),
    payment_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all transactions for the logged-in user (sent + received)."""
    db = get_db()
    uid = current_user["sub"]

    # Get user's UPI ID first
    wallet = db.collection("wallets").document(uid).get().to_dict()
    user_upi = wallet["upi_id"]

    # Fetch sent transactions
    sent_query = db.collection("transactions").where("sender_id", "==", uid)
    received_query = db.collection("transactions").where("receiver_upi", "==", user_upi)

    sent_txns = [doc.to_dict() for doc in sent_query.get()]
    received_txns = [doc.to_dict() for doc in received_query.get()]

    # Tag direction
    for txn in sent_txns:
        txn["direction"] = "debit"
    for txn in received_txns:
        txn["direction"] = "credit"

    all_txns = sent_txns + received_txns

    # Filter by payment type if provided
    if payment_type:
        all_txns = [t for t in all_txns if t.get("payment_type") == payment_type]

    # Sort by timestamp descending
    all_txns.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    return all_txns[:limit]


@router.get("/{transaction_id}", response_model=dict)
async def get_transaction_detail(
    transaction_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get details of a specific transaction."""
    db = get_db()
    uid = current_user["sub"]

    doc = db.collection("transactions").document(transaction_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Transaction not found")

    txn = doc.to_dict()

    # Security: only sender or receiver can view
    wallet = db.collection("wallets").document(uid).get().to_dict()
    if txn["sender_id"] != uid and txn["receiver_upi"] != wallet["upi_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return txn


@router.get("/summary/monthly", response_model=dict)
async def get_monthly_summary(
    current_user: dict = Depends(get_current_user)
):
    """Get total spent/received grouped by payment type this month."""
    db = get_db()
    uid = current_user["sub"]

    wallet = db.collection("wallets").document(uid).get().to_dict()
    user_upi = wallet["upi_id"]

    sent = db.collection("transactions").where("sender_id", "==", uid).get()
    received = db.collection("transactions").where("receiver_upi", "==", user_upi).get()

    total_spent = sum(doc.to_dict()["amount"] for doc in sent)
    total_received = sum(doc.to_dict()["amount"] for doc in received)

    # Breakdown by type
    breakdown = {}
    for doc in sent:
        t = doc.to_dict()
        ptype = t.get("payment_type", "other")
        breakdown[ptype] = breakdown.get(ptype, 0) + t["amount"]

    return {
        "total_spent": total_spent,
        "total_received": total_received,
        "breakdown_by_type": breakdown,
        "current_balance": wallet["balance"]
    }
