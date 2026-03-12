from fastapi import APIRouter, HTTPException, Depends
from models.schemas import WalletResponse, AddMoneyRequest
from config.firebase import get_db
from config.security import verify_password, hash_password
from middleware.auth_middleware import get_current_user
from datetime import datetime
import uuid

router = APIRouter()


@router.get("/balance", response_model=WalletResponse)
async def get_balance(current_user: dict = Depends(get_current_user)):
    db = get_db()
    uid = current_user["sub"]

    doc = db.collection("wallets").document(uid).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Wallet not found")

    wallet = doc.to_dict()
    wallet.pop("upi_pin", None)   # Never expose PIN
    return WalletResponse(**wallet)


@router.post("/add-money", response_model=dict)
async def add_money(
    data: AddMoneyRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Mock money addition — simulates a UPI/card top-up.
    In production, integrate Razorpay/PayU payment gateway here.
    """
    db = get_db()
    uid = current_user["sub"]

    wallet_ref = db.collection("wallets").document(uid)
    wallet = wallet_ref.get().to_dict()

    new_balance = wallet["balance"] + data.amount
    wallet_ref.update({"balance": new_balance})

    # Log the top-up as a transaction
    txn_id = str(uuid.uuid4())
    db.collection("transactions").document(txn_id).set({
        "transaction_id": txn_id,
        "sender_id": "MOCK_GATEWAY",
        "receiver_upi": wallet["upi_id"],
        "amount": data.amount,
        "payment_type": "wallet_topup",
        "description": f"Wallet top-up via {data.method}",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    })

    return {
        "message": f"₹{data.amount} added successfully",
        "new_balance": new_balance,
        "transaction_id": txn_id
    }


@router.post("/change-pin", response_model=dict)
async def change_upi_pin(
    old_pin: str,
    new_pin: str,
    current_user: dict = Depends(get_current_user)
):
    if len(new_pin) not in [4, 6] or not new_pin.isdigit():
        raise HTTPException(status_code=400, detail="PIN must be 4 or 6 digits")

    db = get_db()
    uid = current_user["sub"]

    wallet_ref = db.collection("wallets").document(uid)
    wallet = wallet_ref.get().to_dict()

    if not verify_password(old_pin, wallet["upi_pin"]):
        raise HTTPException(status_code=400, detail="Old PIN is incorrect")

    wallet_ref.update({"upi_pin": hash_password(new_pin)})
    return {"message": "UPI PIN changed successfully"}


@router.get("/upi-id", response_model=dict)
async def get_upi_id(current_user: dict = Depends(get_current_user)):
    db = get_db()
    uid = current_user["sub"]

    doc = db.collection("wallets").document(uid).get()
    wallet = doc.to_dict()
    return {"upi_id": wallet["upi_id"]}
