from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import razorpay
import sqlite3
import os
from contextlib import contextmanager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RAZORPAY_KEY_ID     = os.getenv("RAZORPAY_KEY_ID",     "rzp_test_SSRER7EFytYsML")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "LaeSPK56HLqC3IIoXLE8aLp5")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

DATABASE = "payments.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            phone          TEXT PRIMARY KEY,
            payment_status TEXT,
            payment_id     TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

@app.get("/")
def home():
    return {"message": "Backend running 🚀"}

# ── Create Razorpay order ──────────────────────────────────
@app.post("/create_order")
def create_order():
    try:
        order = client.order.create({
            "amount":          100,   # ₹1 = 100 paise
            "currency":        "INR",
            "payment_capture": 1
        })
        return order
    except Exception as e:
        return {"error": str(e)}

# ── Save & verify payment ──────────────────────────────────
class PaymentData(BaseModel):
    phone:      str
    payment_id: str

@app.post("/save_payment")
def save_payment(data: PaymentData):
    # Basic phone validation
    phone = data.phone.strip()
    if not phone.isdigit() or len(phone) != 10:
        return {"status": "failed", "reason": "Invalid phone number"}
    try:
        payment = client.payment.fetch(data.payment_id)
        if payment["status"] == "captured":
            with get_db() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO users (phone, payment_status, payment_id)
                    VALUES (?, ?, ?)
                """, (phone, "paid", data.payment_id))
                conn.commit()
            return {"status": "success"}
        return {"status": "failed", "reason": f"Payment status: {payment['status']}"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

# ── Check payment status ───────────────────────────────────
@app.get("/check_payment")
def check_payment(phone: str):
    phone = phone.strip()
    if not phone.isdigit() or len(phone) != 10:
        return {"status": "invalid", "reason": "Invalid phone number"}
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT payment_status FROM users WHERE phone=?", (phone,)
            )
            result = cursor.fetchone()
        if result and result[0] == "paid":
            return {"status": "paid"}
        return {"status": "not_paid"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
