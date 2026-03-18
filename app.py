import streamlit as st
import streamlit.components.v1 as components
import requests
from parser import extract_text_from_pdf
from ats import calculate_ats_score
from skills import extract_skills, skill_gap

# ─── CONFIG ───────────────────────────────────────────────
BACKEND_URL = " "https://resume-analyzer-qamg.onrender.com""    # change when deployed
RZP_KEY_ID  = "rzp_test_SSRER7EFytYsML" # must match backend

st.set_page_config(page_title="AI Resume Analyzer", layout="centered")

st.markdown("""
# 🚀 AI Resume Analyzer
This tool helps students:
- Check ATS score
- Identify missing skills
- Improve placement chances
""")

# ─── UPLOAD & ROLE ────────────────────────────────────────
uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type="pdf")

job_role = st.selectbox("🎯 Select Job Role", ["Data Analyst", "Data Scientist"])
job_desc = {
    "Data Analyst":   "python sql excel power bi statistics data analysis",
    "Data Scientist": "python machine learning statistics deep learning"
}

# ─── PHONE INPUT ──────────────────────────────────────────
phone = st.text_input(
    "📱 Enter your 10-digit mobile number",
    placeholder="9876543210",
    max_chars=10
)

phone_valid = phone.isdigit() and len(phone) == 10

if phone and not phone_valid:
    st.error("⚠️ Please enter a valid 10-digit mobile number")

# ─── HANDLE PAYMENT CALLBACK (Razorpay redirects here with query params) ──
params = st.query_params

if (
    "payment_id" in params
    and "phone" in params
    and not st.session_state.get("payment_verified")
):
    cb_phone = params["phone"]
    cb_pid   = params["payment_id"]

    with st.spinner("🔒 Verifying your payment with Razorpay..."):
        try:
            resp = requests.post(f"{BACKEND_URL}/save_payment", json={
                "phone":      cb_phone,
                "payment_id": cb_pid
            })
            result = resp.json()

            if result.get("status") == "success":
                st.session_state["payment_verified"] = True
                st.session_state["verified_phone"]   = cb_phone
                st.query_params.clear()
                st.rerun()
            else:
                reason = result.get("reason") or result.get("error", "Unknown error")
                st.error(f"❌ Payment verification failed: {reason}")
                st.query_params.clear()

        except Exception as e:
            st.error(f"Backend error during verification: {e}")

# ─── MAIN ANALYSIS ────────────────────────────────────────
if uploaded_file:
    with st.spinner("Analyzing your resume..."):
        text        = extract_text_from_pdf(uploaded_file)
        score       = calculate_ats_score(text, job_desc[job_role])
        user_skills = extract_skills(text)
        missing     = skill_gap(user_skills, job_role)

    st.divider()

    # ATS Score
    st.subheader(f"📊 ATS Score: {score}%")
    if score < 50:
        st.error("❌ Low chances — improve your resume")
    elif score < 75:
        st.warning("⚠️ Moderate chances")
    else:
        st.success("✅ High chances — strong profile!")

    st.divider()

    # Detected Skills (FREE)
    st.subheader("✅ Your Skills")
    st.write(", ".join(user_skills) if user_skills else "No skills detected")

    st.divider()

    # ─── LOCKED SECTION ───────────────────────────────────
    st.subheader("❌ Missing Skills")

    # Check if already paid (session cache first, then DB)
    already_paid = st.session_state.get("payment_verified", False)

    if not already_paid and phone_valid:
        try:
            chk = requests.get(
                f"{BACKEND_URL}/check_payment",
                params={"phone": phone}
            )
            if chk.json().get("status") == "paid":
                already_paid = True
                st.session_state["payment_verified"] = True
                st.session_state["verified_phone"]   = phone
        except Exception:
            pass  # backend unreachable — stay locked

    # ── UNLOCKED ──────────────────────────────────────────
    if already_paid:
        st.success("✅ Payment verified — full report unlocked!")
        st.write(", ".join(missing) if missing else "No major gaps 🎉")
        if missing:
            st.subheader("📌 Recommended to Learn")
            for skill in missing:
                st.write(f"👉 {skill}")

    # ── PAYMENT GATE ──────────────────────────────────────
    else:
        st.markdown("### 🔓 Unlock Full Report — ₹1 only")
        st.warning("⚡ 90% resumes get rejected due to missing skills")

        if not phone_valid:
            st.info("👆 Enter your valid 10-digit mobile number above to pay")
        else:
            # Create order from backend
            try:
                order_resp = requests.post(f"{BACKEND_URL}/create_order")
                order      = order_resp.json()
                order_id   = order.get("id")

                if not order_id:
                    st.error("❌ Could not create payment order. Is the backend running?")
                else:
                    # Razorpay inline checkout
                    # On success → redirects to this page with ?payment_id=...&phone=...
                    checkout_html = f"""
                    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>

                    <button id="pay-btn" style="
                        background: #6c63ff;
                        color: white;
                        padding: 14px 32px;
                        border: none;
                        border-radius: 8px;
                        font-size: 17px;
                        font-family: sans-serif;
                        cursor: pointer;
                        box-shadow: 0 4px 14px rgba(108,99,255,0.4);
                    ">
                        💳 Pay ₹1 &amp; Unlock Report
                    </button>

                    <p id="status-msg" style="
                        font-family: sans-serif;
                        font-size: 13px;
                        color: #888;
                        margin-top: 10px;
                    "></p>

                    <script>
                    document.getElementById('pay-btn').onclick = function() {{
                        var options = {{
                            key:         '{RZP_KEY_ID}',
                            amount:      100,
                            currency:    'INR',
                            order_id:    '{order_id}',
                            name:        'AI Resume Analyzer',
                            description: 'Unlock Missing Skills Report',
                            prefill: {{
                                contact: '91{phone}'
                            }},
                            theme: {{ color: '#6c63ff' }},
                            modal: {{
                                ondismiss: function() {{
                                    document.getElementById('status-msg').innerText =
                                        'Payment cancelled. Click above to try again.';
                                }}
                            }},
                            handler: function(response) {{
                                document.getElementById('status-msg').innerText =
                                    '✅ Payment done! Verifying...';
                                // Redirect back with payment_id + phone in URL
                                var base = window.top.location.href.split('?')[0];
                                var qs   = '?payment_id=' + response.razorpay_payment_id
                                         + '&phone={phone}';
                                window.top.location.href = base + qs;
                            }}
                        }};
                        var rzp = new Razorpay(options);
                        rzp.open();
                    }};
                    </script>
                    """
                    components.html(checkout_html, height=120)

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot reach backend. Make sure FastAPI is running on port 8000.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

else:
    if not uploaded_file:
        st.info("👆 Upload your resume PDF to get started")
