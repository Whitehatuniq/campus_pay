from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from config.firebase import get_db
from config.security import verify_password
from middleware.auth_middleware import get_current_user
from datetime import datetime
import uuid

router = APIRouter()

class OrderItem(BaseModel):
    item_id: str
    quantity: int

class PlaceOrder(BaseModel):
    canteen_id: str
    items: List[OrderItem]
    upi_pin: str

@router.get("/list")
async def get_canteens():
    db = get_db()
    canteens = db.collection("canteens").where("is_active", "==", True).get()
    return [doc.to_dict() for doc in canteens]

@router.get("/{canteen_id}/menu")
async def get_menu(canteen_id: str):
    db = get_db()
    items = db.collection("menu_items").where("canteen_id", "==", canteen_id).get()
    menu = [doc.to_dict() for doc in items]
    # Group by category
    categories = {}
    for item in menu:
        cat = item.get("category", "Other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    return {"canteen_id": canteen_id, "categories": categories, "all_items": menu}

@router.post("/order")
async def place_order(
    data: PlaceOrder,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    uid = current_user["sub"]

    # Get canteen
    canteen_doc = db.collection("canteens").document(data.canteen_id).get()
    if not canteen_doc.exists:
        raise HTTPException(status_code=404, detail="Canteen not found")
    canteen = canteen_doc.to_dict()

    # Calculate total
    total = 0.0
    order_items = []
    for order_item in data.items:
        item_doc = db.collection("menu_items").document(order_item.item_id).get()
        if not item_doc.exists:
            raise HTTPException(status_code=404, detail=f"Item {order_item.item_id} not found")
        item = item_doc.to_dict()
        subtotal = item["price"] * order_item.quantity
        total += subtotal
        order_items.append({
            "item_id": item["item_id"],
            "name": item["name"],
            "price": item["price"],
            "quantity": order_item.quantity,
            "subtotal": subtotal,
            "emoji": item.get("emoji", "🍽️")
        })

    # Get sender wallet
    sender_wallet_ref = db.collection("wallets").document(uid)
    sender_wallet = sender_wallet_ref.get().to_dict()

    if not sender_wallet:
        raise HTTPException(status_code=400, detail="Wallet not found")

    # Validate PIN
    if not verify_password(data.upi_pin, sender_wallet["upi_pin"]):
        raise HTTPException(status_code=401, detail="Incorrect UPI PIN")

    # Check balance
    if sender_wallet["balance"] < total:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Required: ₹{total:.2f}, Available: ₹{sender_wallet['balance']:.2f}"
        )

    # Get canteen wallet
    canteen_wallets = db.collection("wallets").where("upi_id", "==", canteen["upi_id"]).get()
    if not canteen_wallets:
        raise HTTPException(status_code=404, detail="Canteen wallet not found")

    canteen_wallet_ref = db.collection("wallets").document(canteen_wallets[0].id)
    canteen_wallet = canteen_wallet_ref.get().to_dict()

    # Transfer money
    sender_wallet_ref.update({"balance": sender_wallet["balance"] - total})
    canteen_wallet_ref.update({"balance": canteen_wallet["balance"] + total})

    # Save order
    order_id = str(uuid.uuid4())
    order_no = f"ORD{order_id[:6].upper()}"
    db.collection("orders").document(order_id).set({
        "order_id": order_id,
        "order_no": order_no,
        "user_id": uid,
        "canteen_id": data.canteen_id,
        "canteen_name": canteen["name"],
        "items": order_items,
        "total": total,
        "status": "confirmed",
        "timestamp": datetime.utcnow().isoformat()
    })

    # Log transaction
    txn_id = str(uuid.uuid4())
    db.collection("transactions").document(txn_id).set({
        "transaction_id": txn_id,
        "sender_id": uid,
        "sender_upi": sender_wallet["upi_id"],
        "receiver_upi": canteen["upi_id"],
        "amount": total,
        "payment_type": "canteen",
        "description": f"Order {order_no} at {canteen['name']}",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    })

    return {
        "message": f"Order placed successfully at {canteen['name']}!",
        "order_no": order_no,
        "order_id": order_id,
        "items": order_items,
        "total": total,
        "transaction_id": txn_id
    }

@router.get("/my-orders")
async def get_my_orders(current_user: dict = Depends(get_current_user)):
    db = get_db()
    uid = current_user["sub"]
    orders = db.collection("orders").where("user_id", "==", uid).get()
    result = [doc.to_dict() for doc in orders]
    result.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return result
