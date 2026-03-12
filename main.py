from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, wallet, payment, transaction, admin

app = FastAPI(
    title="CampusPay API",
    description="Campus Payment System - UPI-like payment backend for Poornima University",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router,        prefix="/api/auth",        tags=["Authentication"])
app.include_router(wallet.router,      prefix="/api/wallet",      tags=["Wallet"])
app.include_router(payment.router,     prefix="/api/payment",     tags=["Payment"])
app.include_router(transaction.router, prefix="/api/transaction",  tags=["Transactions"])
app.include_router(admin.router,       prefix="/api/admin",       tags=["Admin"])

@app.get("/")
def root():
    return {"message": "Welcome to CampusPay API 🎓", "status": "running"}
