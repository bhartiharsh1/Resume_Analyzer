import streamlit as st
import streamlit.components.v1 as components
import requests
from parser import extract_text_from_pdf
from ats import calculate_ats_score
from skills import extract_skills, skill_gap

# ─── CONFIG ───────────────────────────────────────────────
BACKEND_URL    = "http://localhost:8000"   # change to your deployed backend URL
RZP_KEY_ID     = "rzp_test_SSRER7EFytYsML"  # must match backend

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
    "Data Analyst":  "python sql excel power bi statistics data analysis",
    "Data Scientist": "python machine learning statistics deep learning"
}

# ─── EMAIL (needed to track payment per user) ─────────────
email = st.text_input("📧 Enter your email to unlock report", placeholder="you@example.com")

# ─── HANDLE PAYMENT CALLBACK (query params set by Razorpay JS) ────────────
params = st.query_params

if (
    "payment_id" in params
    and "email" in params
    and not st.session_state.get("payment_verified")
):
    with st.spinner("🔒 Verifying your payment..."):
        try:
            resp = requests.post(f"{BACKEND_URL}/save_payment", json={
                "email":      params["email"],
                "payment_id": params["payment_id"]
            })
            if resp.json().get("status") == "success":
                st.session_state["payment_verified"] = True
                st.session_state["verified_email"]   = params["email"]
                # Clean URL
                st.query_params.clear()
                st.rerun()
            else:
                st.error("❌ Payment could not be verified. Contact support.")
        except Exception as e:
            st.error(f"Verification error: {e}")

# ─── MAIN ANALYSIS BLOCK ──────────────────────────────────
if uploaded_file:
    with st.spinner("Analyzing your resume..."):
        text       = extract_text_from_pdf(uploaded_file)
        score      = calculate_ats_score(text, job_desc[job_role])
        user_skills = extract_skills(text)
        missing    = skill_gap(user_skills, job_role)

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

    # Detected Skills
    st.subheader("✅ Your Skills")
    st.write(", ".join(user_skills) if user_skills else "No skills detected")

    st.divider()

    # ─── LOCKED SECTION ───────────────────────────────────
    st.subheader("❌ Missing Skills")

    # ── Determine if this user has already paid ──
    already_paid = st.session_state.get("payment_verified", False)

    if not already_paid and email:
        try:
            chk = requests.get(f"{BACKEND_URL}/check_payment", params={"email": email})
            if chk.json().get("status") == "paid":
                already_paid = True
                st.session_state["payment_verified"] = True
                st.session_state["verified_email"]   = email
        except Exception:
            pass  # backend unreachable — stay locked

    # ── SHOW UNLOCKED CONTENT ──
    if already_paid:
        st.success("✅ Payment verified — full report unlocked!")
        st.write(", ".join(missing) if missing else "No major gaps 🎉")
        if missing:
            st.subheader("📌 Recommended to Learn")
            for skill in missing:
                st.write(f"👉 {skill}")

    # ── SHOW PAYMENT GATE ──
    else:
        st.markdown("### 🔓 Unlock Full Report — ₹1 only")
        st.warning("⚡ 90% resumes get rejected due to missing skills")

        if not email:
            st.info("👆 Enter your email above to proceed with payment")
        else:
            # Create a fresh Razorpay order from backend
            try:
                order_resp = requests.post(f"{BACKEND_URL}/create_order")
                order      = order_resp.json()
                order_id   = order.get("id")

                if not order_id:
                    st.error("Could not create payment order. Try again.")
                else:
                    # Inline Razorpay checkout — on success, redirects back
                    # with ?payment_id=...&email=... so Streamlit can verify
                    checkout_html = f"""
                    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
                    <button
                        id="pay-btn"
                        style="
                            background: #6c63ff;
                            color: white;
                            padding: 12px 28px;
                            border: none;
                            border-radius: 8px;
                            font-size: 16px;
                            cursor: pointer;
                            font-family: sans-serif;
                        "
                    >
                        💳 Pay ₹1 &amp; Unlock Report
                    </button>

                    <script>
                    document.getElementById('pay-btn').onclick = function() {{
                        var options = {{
                            key:         '{RZP_KEY_ID}',
                            amount:      100,
                            currency:    'INR',
                            order_id:    '{order_id}',
                            name:        'AI Resume Analyzer',
                            description: 'Unlock Missing Skills Report',
                            prefill:     {{ email: '{email}' }},
                            theme:       {{ color: '#6c63ff' }},
                            handler: function(response) {{
                                // Redirect back to this page with payment details in URL
                                var base = window.top.location.href.split('?')[0];
                                var qs   = '?payment_id=' + response.razorpay_payment_id
                                         + '&email={email}';
                                window.top.location.href = base + qs;
                            }}
                        }};
                        var rzp = new Razorpay(options);
                        rzp.open();
                    }};
                    </script>
                    """
                    components.html(checkout_html, height=80)

            except Exception as e:
                st.error(f"Backend connection error: {e}")
                st.markdown("[💳 Pay directly via link](https://rzp.io/rzp/Ir3XL5cl)")
