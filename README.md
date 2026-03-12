# 🎓 CampusPay Backend — FastAPI + Firebase

Campus payment system for Poornima University.  
Simulates a UPI-like payment flow for exam fees, back fees, event payments, and more.

---

## 📁 Project Structure

```
campus_pay/
├── main.py                    # FastAPI app entry point
├── requirements.txt
├── serviceAccountKey.json     # ⚠️ YOU ADD THIS (from Firebase Console)
├── config/
│   ├── firebase.py            # Firebase init + Firestore client
│   └── security.py            # JWT + bcrypt utilities
├── middleware/
│   └── auth_middleware.py     # JWT auth dependency (get_current_user)
├── models/
│   └── schemas.py             # All Pydantic request/response models
└── routers/
    ├── auth.py                # Register, Login, Refresh, Profile
    ├── wallet.py              # Balance, Add Money, Change PIN
    ├── payment.py             # Pay, Pay Event Fee, Pay Exam Fee
    ├── transaction.py         # History, Detail, Monthly Summary
    └── admin.py               # Stats, Users, Events, Fee Config
```

---

## ⚙️ Setup Instructions

### 1. Clone & install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Firebase
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a project → Enable **Firestore Database**
3. Go to **Project Settings → Service Accounts → Generate new private key**
4. Download it and rename to `serviceAccountKey.json`
5. Place it in the root `campus_pay/` folder

### 3. Run the server
```bash
uvicorn main:app --reload
```

### 4. Open API docs
```
http://127.0.0.1:8000/docs
```

---

## 🔐 Authentication Flow

```
POST /api/auth/register   → Get user_id + upi_id
POST /api/auth/login      → Get access_token + refresh_token
GET  /api/auth/me         → View profile (requires Bearer token)
POST /api/auth/refresh    → Get new access_token
```

**Use the access_token as:** `Authorization: Bearer <token>`

---

## 💸 Payment Flow (like UPI)

```
1. Student registers   → wallet auto-created with UPI ID
2. Student adds money  → POST /api/wallet/add-money
3. Student pays fee    → POST /api/payment/pay
                          { receiver_upi, amount, payment_type, upi_pin }
4. Transaction logged  → GET /api/transaction/history
```

---

## 🗃️ Firestore Collections

| Collection     | Description                          |
|---------------|--------------------------------------|
| `users`        | User accounts (students + admins)    |
| `wallets`      | Wallet balance + UPI ID + PIN hash   |
| `transactions` | All payment records                  |
| `events`       | Campus events with fee details       |
| `fee_config`   | Exam/back fee configuration          |

---

## 🧑‍💼 Admin APIs

```
GET  /api/admin/stats                    → Dashboard numbers
GET  /api/admin/users                    → All users
POST /api/admin/events/create            → Create event fee
POST /api/admin/fee-config/set           → Set exam/back fee amount
GET  /api/admin/transactions             → All transactions
```
> Admin role is set during registration: `"role": "admin"`

---

## 📦 Payment Types Supported

| Type           | Description              |
|---------------|--------------------------|
| `exam_fee`     | Regular semester exam    |
| `back_fee`     | Back paper / due exam    |
| `event_fee`    | Campus events            |
| `canteen`      | Canteen payments         |
| `library_fine` | Library overdue fine     |
| `other`        | Miscellaneous            |

---

## 🔒 Security Notes
- Passwords are hashed with **bcrypt**
- UPI PINs are **never stored in plain text**
- JWT tokens expire in **60 minutes** (access) / **7 days** (refresh)
- Admin routes are protected by **role-based middleware**
- Passwords are never returned in any API response
