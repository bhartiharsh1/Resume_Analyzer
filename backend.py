from fastapi import FastAPI
import razorpay

app = FastAPI()

client = razorpay.Client(auth=("rzp_test_SSRER7EFytYsML", "LaeSPK56HLqC3IIoXLE8aLp5"))

@app.get("/")
def home():
    return {"message": "Backend running 🚀"}


# 🔐 VERIFY PAYMENT (FOR PAYMENT LINK)
@app.post("/verify_payment")
def verify_payment(data: dict):
    payment_id = data.get("payment_id")

    if not payment_id:
        return {"status": "failed", "error": "No payment_id provided"}

    try:
        # 🔥 Fetch payment from Razorpay
        payment = client.payment.fetch(payment_id)

        # Check if payment is successful
        if payment["status"] == "captured":
            return {"status": "success"}
        else:
            return {"status": "failed", "error": "Payment not completed"}

    except Exception as e:
        return {"status": "failed", "error": str(e)}
