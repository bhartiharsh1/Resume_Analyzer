from fastapi import FastAPI, Request
import razorpay
import os

app = FastAPI()

client = razorpay.Client(auth=("rzp_test_SSRER7EFytYsML", "LaeSPK56HLqC3IIoXLE8aLp5"))

@app.post("/verify_payment")
async def verify_payment(request: Request):
    data = await request.json()

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': data['order_id'],
            'razorpay_payment_id': data['payment_id'],
            'razorpay_signature': data['signature']
        })
        return {"status": "success"}
    except:
        return {"status": "failed"}