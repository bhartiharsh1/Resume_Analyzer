from fastapi import FastAPI
from pydantic import BaseModel
import razorpay
import sqlite3

app = FastAPI()

# 🔐 Razorpay client
client = razorpay.Client(auth=("rzp_test_SSRER7EFytYsML", "LaeSPK56HLqC3IIoXLE8aLp5"))

# 🗄️ DATABASE
conn = sqlite3.connect("payments.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    payment_status TEXT,
    payment_id TEXT
)
""")
conn.commit()


@app.get("/")
def home():
    return {"message": "Backend running 🚀"}


# 👉 CREATE ORDER
@app.post("/create_order")
def create_order():
    order = client.order.create({
        "amount": 100,  # ₹1
        "currency": "INR",
        "payment_capture": 1
    })
    return order


# 👉 SAVE PAYMENT (AUTO VERIFY)
class PaymentData(BaseModel):
    email: str
    payment_id: str


@app.post("/save_payment")
def save_payment(data: PaymentData):
    try:
        payment = client.payment.fetch(data.payment_id)

        if payment["status"] == "captured":

            cursor.execute("""
            INSERT OR REPLACE INTO users (email, payment_status, payment_id)
            VALUES (?, ?, ?)
            """, (data.email, "paid", data.payment_id))

            conn.commit()

            return {"status": "success"}

        return {"status": "failed"}

    except Exception as e:
        return {"status": "failed", "error": str(e)}


# 👉 CHECK PAYMENT STATUS
@app.get("/check_payment")
def check_payment(email: str):
    cursor.execute("SELECT payment_status FROM users WHERE email=?", (email,))
    result = cursor.fetchone()

    if result and result[0] == "paid":
        return {"status": "paid"}

    return {"status": "not_paid"}
