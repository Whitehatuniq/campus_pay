from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from config.firebase import get_db
from middleware.auth_middleware import require_admin
from datetime import datetime

router = APIRouter()

# ─── CANTEEN MENU MANAGEMENT ─────────────────────────────────

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    emoji: Optional[str] = None
    is_available: Optional[bool] = None

class NewMenuItem(BaseModel):
    item_id: str
    name: str
    category: str
    price: float
    emoji: str = "🍽️"
    canteen_id: str
    is_available: bool = True

@router.get("/canteen/menu/{canteen_id}")
async def admin_get_menu(canteen_id: str, admin=Depends(require_admin)):
    db = get_db()
    items = db.collection("menu_items").where("canteen_id", "==", canteen_id).get()
    return [doc.to_dict() for doc in items]

@router.post("/canteen/menu/add")
async def admin_add_menu_item(data: NewMenuItem, admin=Depends(require_admin)):
    db = get_db()
    existing = db.collection("menu_items").document(data.item_id).get()
    if existing.exists:
        raise HTTPException(status_code=400, detail="Item ID already exists")
    db.collection("menu_items").document(data.item_id).set(data.dict())
    return {"message": f"Menu item '{data.name}' added successfully"}

@router.patch("/canteen/menu/{item_id}")
async def admin_update_menu_item(item_id: str, data: MenuItemUpdate, admin=Depends(require_admin)):
    db = get_db()
    doc = db.collection("menu_items").document(item_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Menu item not found")
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    db.collection("menu_items").document(item_id).update(update_data)
    return {"message": "Menu item updated successfully"}

@router.delete("/canteen/menu/{item_id}")
async def admin_delete_menu_item(item_id: str, admin=Depends(require_admin)):
    db = get_db()
    db.collection("menu_items").document(item_id).delete()
    return {"message": "Menu item deleted successfully"}

@router.patch("/canteen/menu/{item_id}/toggle")
async def admin_toggle_item_availability(item_id: str, admin=Depends(require_admin)):
    db = get_db()
    doc = db.collection("menu_items").document(item_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Item not found")
    current = doc.to_dict().get("is_available", True)
    db.collection("menu_items").document(item_id).update({"is_available": not current})
    return {"message": f"Item {'disabled' if current else 'enabled'} successfully", "is_available": not current}


# ─── EXAM FEE MANAGEMENT ─────────────────────────────────────

class FeeUpdate(BaseModel):
    fee_name: Optional[str] = None
    amount: Optional[float] = None
    due_date: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class NewFee(BaseModel):
    fee_id: str
    fee_name: str
    fee_type: str
    amount: float
    due_date: str
    description: str = ""
    receiver_upi: str = "poornima.university@campuspay"
    is_active: bool = True

@router.get("/fees/list")
async def admin_get_fees(admin=Depends(require_admin)):
    db = get_db()
    fees = db.collection("fee_types").get()
    return [doc.to_dict() for doc in fees]

@router.post("/fees/add")
async def admin_add_fee(data: NewFee, admin=Depends(require_admin)):
    db = get_db()
    db.collection("fee_types").document(data.fee_id).set(data.dict())
    return {"message": f"Fee '{data.fee_name}' added successfully"}

@router.patch("/fees/{fee_id}")
async def admin_update_fee(fee_id: str, data: FeeUpdate, admin=Depends(require_admin)):
    db = get_db()
    doc = db.collection("fee_types").document(fee_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Fee not found")
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    db.collection("fee_types").document(fee_id).update(update_data)
    return {"message": "Fee updated successfully"}

@router.delete("/fees/{fee_id}")
async def admin_delete_fee(fee_id: str, admin=Depends(require_admin)):
    db = get_db()
    db.collection("fee_types").document(fee_id).delete()
    return {"message": "Fee deleted successfully"}


# ─── EVENT MANAGEMENT ────────────────────────────────────────

class EventUpdate(BaseModel):
    event_name: Optional[str] = None
    description: Optional[str] = None
    fee: Optional[float] = None
    date: Optional[str] = None
    last_date: Optional[str] = None
    venue: Optional[str] = None
    is_active: Optional[bool] = None

class NewEvent(BaseModel):
    event_id: str
    event_name: str
    description: str
    fee: float
    date: str
    last_date: str
    venue: str
    receiver_upi: str = "poornima.university@campuspay"
    is_active: bool = True

@router.get("/events/list")
async def admin_get_events(admin=Depends(require_admin)):
    db = get_db()
    events = db.collection("events").get()
    return [doc.to_dict() for doc in events]

@router.post("/events/add")
async def admin_add_event(data: NewEvent, admin=Depends(require_admin)):
    db = get_db()
    db.collection("events").document(data.event_id).set(data.dict())
    return {"message": f"Event '{data.event_name}' added successfully"}

@router.patch("/events/{event_id}")
async def admin_update_event(event_id: str, data: EventUpdate, admin=Depends(require_admin)):
    db = get_db()
    doc = db.collection("events").document(event_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Event not found")
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    db.collection("events").document(event_id).update(update_data)
    return {"message": "Event updated successfully"}

@router.delete("/events/{event_id}")
async def admin_delete_event(event_id: str, admin=Depends(require_admin)):
    db = get_db()
    db.collection("events").document(event_id).delete()
    return {"message": "Event deleted successfully"}

@router.patch("/events/{event_id}/toggle")
async def admin_toggle_event(event_id: str, admin=Depends(require_admin)):
    db = get_db()
    doc = db.collection("events").document(event_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Event not found")
    current = doc.to_dict().get("is_active", True)
    db.collection("events").document(event_id).update({"is_active": not current})
    return {"message": f"Event {'disabled' if current else 'enabled'}", "is_active": not current}
