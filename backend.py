from fastapi import FastAPI
from pydantic import BaseModel
import razorpay

app = FastAPI()

# 🔐 Razorpay keys (keep test for now)
client = razorpay.Client(auth=("rzp_test_SSRER7EFytYsML", "LaeSPK56HLqC3IIoXLE8aLp5"))

# ✅ Root route (VERY IMPORTANT for Render)
@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}

# ✅ Request body model
class Payment(BaseModel):
    payment_id: str
    order_id: str
    signature: str

# ✅ Payment verification route
@app.post("/verify_payment")
def verify_payment(data: Payment):
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data.order_id,
            "razorpay_payment_id": data.payment_id,
            "razorpay_signature": data.signature
        })
        return {"status": "success"}
    
    except Exception as e:
        print("Error:", e)   # 👈 helps debugging in Render logs
        return {"status": "failed"}
