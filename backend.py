from fastapi import FastAPI
from pydantic import BaseModel
import razorpay

app = FastAPI()

client = razorpay.Client(auth=("rzp_test_SSRER7EFytYsML", "LaeSPK56HLqC3IIoXLE8aLp5"))

# 👇 DEFINE INPUT STRUCTURE
class Payment(BaseModel):
    payment_id: str
    order_id: str
    signature: str

# 👇 USE MODEL HERE
@app.post("/verify_payment")
def verify_payment(data: Payment):
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': data.order_id,
            'razorpay_payment_id': data.payment_id,
            'razorpay_signature': data.signature
        })
        return {"status": "success"}
    except:
        return {"status": "failed"}
