"""
Run this to seed canteen menu data.
Usage: python seed_canteen.py
"""
import firebase_admin
from firebase_admin import credentials, firestore
import sys, os

KEY_PATH = "serviceAccountKey.json"
if not os.path.exists(KEY_PATH):
    print("serviceAccountKey.json not found!")
    sys.exit(1)

cred = credentials.Certificate(KEY_PATH)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

CANTEENS = [
    {
        "canteen_id": "pu_canteen",
        "name": "PU Canteen",
        "description": "Main university canteen",
        "location": "Ground Floor, Main Block",
        "timing": "8:00 AM - 8:00 PM",
        "upi_id": "pu.canteen@campuspay",
        "is_active": True
    },
    {
        "canteen_id": "cybrus_cafe",
        "name": "Cybrus Cafe",
        "description": "Trendy cafe near the CS block",
        "location": "Near Computer Science Block",
        "timing": "9:00 AM - 6:00 PM",
        "upi_id": "cybrus.cafe@campuspay",
        "is_active": True
    },
    {
        "canteen_id": "cafegram",
        "name": "Cafegram",
        "description": "Instagram-worthy cafe with great snacks",
        "location": "Student Activity Centre",
        "timing": "10:00 AM - 7:00 PM",
        "upi_id": "cafegram@campuspay",
        "is_active": True
    }
]

MENU_ITEMS = {
    "pu_canteen": [
        # Food
        {"item_id": "pu_01", "name": "Poha", "category": "Breakfast", "price": 20, "emoji": "🍚", "is_available": True},
        {"item_id": "pu_02", "name": "Samosa (2 pcs)", "category": "Snacks", "price": 15, "emoji": "🥟", "is_available": True},
        {"item_id": "pu_03", "name": "Aloo Paratha", "category": "Breakfast", "price": 30, "emoji": "🫓", "is_available": True},
        {"item_id": "pu_04", "name": "Dal Rice", "category": "Meals", "price": 50, "emoji": "🍛", "is_available": True},
        {"item_id": "pu_05", "name": "Rajma Chawal", "category": "Meals", "price": 55, "emoji": "🍛", "is_available": True},
        {"item_id": "pu_06", "name": "Veg Thali", "category": "Meals", "price": 70, "emoji": "🍽️", "is_available": True},
        {"item_id": "pu_07", "name": "Bread Omelette", "category": "Breakfast", "price": 35, "emoji": "🍳", "is_available": True},
        {"item_id": "pu_08", "name": "Pav Bhaji", "category": "Snacks", "price": 40, "emoji": "🥘", "is_available": True},
        {"item_id": "pu_09", "name": "Maggi", "category": "Snacks", "price": 25, "emoji": "🍜", "is_available": True},
        {"item_id": "pu_10", "name": "Kurkure Chaat", "category": "Snacks", "price": 20, "emoji": "🌶️", "is_available": True},
        {"item_id": "pu_11", "name": "Bhel Puri", "category": "Snacks", "price": 25, "emoji": "🥣", "is_available": True},
        {"item_id": "pu_12", "name": "Veg Sandwich", "category": "Snacks", "price": 30, "emoji": "🥪", "is_available": True},
        {"item_id": "pu_13", "name": "Paneer Sandwich", "category": "Snacks", "price": 40, "emoji": "🥪", "is_available": True},
        {"item_id": "pu_14", "name": "Chole Bhature", "category": "Meals", "price": 60, "emoji": "🫓", "is_available": True},
        {"item_id": "pu_15", "name": "Veg Burger", "category": "Snacks", "price": 45, "emoji": "🍔", "is_available": True},
        # Drinks
        {"item_id": "pu_16", "name": "Chai", "category": "Drinks", "price": 10, "emoji": "☕", "is_available": True},
        {"item_id": "pu_17", "name": "Cold Coffee", "category": "Drinks", "price": 30, "emoji": "☕", "is_available": True},
        {"item_id": "pu_18", "name": "Lassi", "category": "Drinks", "price": 25, "emoji": "🥛", "is_available": True},
        {"item_id": "pu_19", "name": "Nimbu Pani", "category": "Drinks", "price": 15, "emoji": "🍋", "is_available": True},
        {"item_id": "pu_20", "name": "Cold Drink (Can)", "category": "Drinks", "price": 30, "emoji": "🥤", "is_available": True},
        {"item_id": "pu_21", "name": "Water Bottle", "category": "Drinks", "price": 20, "emoji": "💧", "is_available": True},
        {"item_id": "pu_22", "name": "Mango Shake", "category": "Drinks", "price": 40, "emoji": "🥭", "is_available": True},
    ],
    "cybrus_cafe": [
        {"item_id": "cy_01", "name": "Espresso", "category": "Coffee", "price": 60, "emoji": "☕", "is_available": True},
        {"item_id": "cy_02", "name": "Cappuccino", "category": "Coffee", "price": 80, "emoji": "☕", "is_available": True},
        {"item_id": "cy_03", "name": "Cold Brew", "category": "Coffee", "price": 90, "emoji": "🧊", "is_available": True},
        {"item_id": "cy_04", "name": "Caramel Latte", "category": "Coffee", "price": 100, "emoji": "☕", "is_available": True},
        {"item_id": "cy_05", "name": "Chocolate Shake", "category": "Shakes", "price": 90, "emoji": "🍫", "is_available": True},
        {"item_id": "cy_06", "name": "Oreo Shake", "category": "Shakes", "price": 100, "emoji": "🍪", "is_available": True},
        {"item_id": "cy_07", "name": "Grilled Sandwich", "category": "Food", "price": 70, "emoji": "🥪", "is_available": True},
        {"item_id": "cy_08", "name": "Pasta", "category": "Food", "price": 90, "emoji": "🍝", "is_available": True},
        {"item_id": "cy_09", "name": "Pizza Slice", "category": "Food", "price": 80, "emoji": "🍕", "is_available": True},
        {"item_id": "cy_10", "name": "Brownie", "category": "Desserts", "price": 60, "emoji": "🍫", "is_available": True},
        {"item_id": "cy_11", "name": "Cheesecake Slice", "category": "Desserts", "price": 80, "emoji": "🍰", "is_available": True},
        {"item_id": "cy_12", "name": "French Fries", "category": "Food", "price": 60, "emoji": "🍟", "is_available": True},
    ],
    "cafegram": [
        {"item_id": "cg_01", "name": "Dalgona Coffee", "category": "Coffee", "price": 100, "emoji": "☕", "is_available": True},
        {"item_id": "cg_02", "name": "Rose Milk", "category": "Drinks", "price": 60, "emoji": "🌹", "is_available": True},
        {"item_id": "cg_03", "name": "Bubble Tea", "category": "Drinks", "price": 120, "emoji": "🧋", "is_available": True},
        {"item_id": "cg_04", "name": "Smoothie Bowl", "category": "Food", "price": 130, "emoji": "🍓", "is_available": True},
        {"item_id": "cg_05", "name": "Avocado Toast", "category": "Food", "price": 110, "emoji": "🥑", "is_available": True},
        {"item_id": "cg_06", "name": "Waffle", "category": "Desserts", "price": 100, "emoji": "🧇", "is_available": True},
        {"item_id": "cg_07", "name": "Pancakes", "category": "Food", "price": 90, "emoji": "🥞", "is_available": True},
        {"item_id": "cg_08", "name": "Nutella Sandwich", "category": "Food", "price": 70, "emoji": "🥜", "is_available": True},
        {"item_id": "cg_09", "name": "Iced Matcha", "category": "Coffee", "price": 110, "emoji": "🍵", "is_available": True},
        {"item_id": "cg_10", "name": "Fruit Platter", "category": "Food", "price": 80, "emoji": "🍱", "is_available": True},
        {"item_id": "cg_11", "name": "Nachos", "category": "Snacks", "price": 90, "emoji": "🌮", "is_available": True},
        {"item_id": "cg_12", "name": "Tiramisu", "category": "Desserts", "price": 120, "emoji": "🍮", "is_available": True},
    ]
}

# Seed canteens
print("Seeding canteens...")
for canteen in CANTEENS:
    db.collection("canteens").document(canteen["canteen_id"]).set(canteen)
    # Create wallet for each canteen
    existing = db.collection("wallets").where("upi_id", "==", canteen["upi_id"]).get()
    if not existing:
        db.collection("wallets").document(canteen["canteen_id"]).set({
            "user_id": canteen["canteen_id"],
            "balance": 0.0,
            "upi_id": canteen["upi_id"],
            "upi_pin": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6ThtOf/SIhRFHAgLRMoTYSwDoBTT2",
            "is_active": True
        })
    print(f"  ✅ {canteen['name']}")

# Seed menu items
print("\nSeeding menu items...")
for canteen_id, items in MENU_ITEMS.items():
    for item in items:
        item["canteen_id"] = canteen_id
        db.collection("menu_items").document(item["item_id"]).set(item)
    print(f"  ✅ {canteen_id}: {len(items)} items")

print("\n🎉 Canteen data seeded!")
