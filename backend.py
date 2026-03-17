from fastapi import FastAPI
from pydantic import BaseModel
import razorpay
import os

app = FastAPI()

client = razorpay.Client(auth=("YOUR_KEY_ID", "YOUR_SECRET"))

@app.get("/")
def home():
    return {"message": "Backend running 🚀"}

# 👉 CREATE ORDER
@app.post("/create_order")
def create_order():
    order = client.order.create({
        "amount": 7900,  # ₹79 (in paise)
        "currency": "INR",
        "payment_capture": 1
    })
    return order
