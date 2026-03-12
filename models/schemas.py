from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime


# ─── AUTH MODELS ─────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["student", "admin"] = "student"
    enrollment_no: Optional[str] = None   # For students
    phone: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    role: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ─── USER MODEL ──────────────────────────────────────────────
class UserProfile(BaseModel):
    uid: str
    name: str
    email: str
    role: str
    enrollment_no: Optional[str]
    phone: Optional[str]
    is_active: bool = True
    created_at: Optional[str]


# ─── WALLET MODELS ───────────────────────────────────────────
class WalletResponse(BaseModel):
    user_id: str
    balance: float
    upi_id: str             # e.g. eklavya@campuspay
    is_active: bool

class AddMoneyRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be positive")
    method: Literal["mock_upi", "mock_card"] = "mock_upi"


# ─── PAYMENT MODELS ──────────────────────────────────────────
class PaymentType(str):
    EXAM_FEE     = "exam_fee"
    BACK_FEE     = "back_fee"
    EVENT_FEE    = "event_fee"
    CANTEEN      = "canteen"
    LIBRARY_FINE = "library_fine"
    OTHER        = "other"

class PaymentRequest(BaseModel):
    receiver_upi: str                    # Who receives the payment
    amount: float = Field(..., gt=0)
    payment_type: Literal[
        "exam_fee", "back_fee", "event_fee",
        "canteen", "library_fine", "other"
    ]
    description: Optional[str] = None
    upi_pin: str                         # Mock PIN validation (4-6 digits)

class PaymentResponse(BaseModel):
    transaction_id: str
    status: Literal["success", "failed", "pending"]
    amount: float
    receiver_upi: str
    payment_type: str
    timestamp: str
    message: str


# ─── TRANSACTION MODELS ──────────────────────────────────────
class TransactionRecord(BaseModel):
    transaction_id: str
    sender_id: str
    receiver_upi: str
    amount: float
    payment_type: str
    description: Optional[str]
    status: str
    timestamp: str


# ─── ADMIN MODELS ────────────────────────────────────────────
class CreateEventFeeRequest(BaseModel):
    event_name: str
    amount: float
    due_date: str
    description: Optional[str] = None
    target_role: Literal["student", "all"] = "student"

class AdminStatsResponse(BaseModel):
    total_users: int
    total_transactions: int
    total_amount_processed: float
    pending_payments: int
