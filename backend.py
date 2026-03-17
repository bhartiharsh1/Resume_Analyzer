from fastapi import FastAPI
from pydantic import BaseModel
import razorpay

app = FastAPI()

client = razorpay.Client(auth=("rzp_test_SSRER7EFytYsML", "LaeSPK56HLqC3IIoXLE8aLp5"))

@app.get("/")
def home():
    return {"message": "Backend running 🚀"}


# 👉 CREATE ORDER
@app.post("/create_order")
def create_order():
    order = client.order.create({
        "amount": 100,  # ₹1 (in paise)
        "currency": "INR",
        "payment_capture": 1
    })
    return order


# 👉 ADD THIS (VERY IMPORTANT 🔥)
class Payment(BaseModel):
    payment_id: str
    order_id: str
    signature: str


@app.post("/verify_payment")
def verify_payment(data: Payment):
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': data.order_id,
            'razorpay_payment_id': data.payment_id,
            'razorpay_signature': data.signature
        })
        return {"status": "success"}

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
