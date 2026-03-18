import streamlit as st
import streamlit.components.v1 as components
from parser import extract_text_from_pdf
from ats import calculate_ats_score
from skills import extract_skills, skill_gap
import requests

st.set_page_config(page_title="AI Resume Analyzer", layout="centered")

st.markdown("""
# 🚀 AI Resume Analyzer

This tool helps students:
- Check ATS score
- Identify missing skills
- Improve placement chances
""")

# Upload
uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type="pdf")

# Role selection
job_role = st.selectbox("🎯 Select Job Role", ["Data Analyst", "Data Scientist"])

job_desc = {
    "Data Analyst": "python sql excel power bi statistics data analysis",
    "Data Scientist": "python machine learning statistics deep learning"
}

# MAIN BLOCK
if uploaded_file:

    with st.spinner("Analyzing your resume..."):
        text = extract_text_from_pdf(uploaded_file)
        score = calculate_ats_score(text, job_desc[job_role])
        user_skills = extract_skills(text)
        missing = skill_gap(user_skills, job_role)

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

    # Skills
    st.subheader("✅ Your Skills")
    st.write(", ".join(user_skills) if user_skills else "No skills detected")

    st.divider()

    # LOCKED SECTION
    st.subheader("❌ Missing Skills")

    st.markdown("### 🔓 Unlock Full Report (₹79)")
    st.warning("⚡ 90% resumes get rejected due to missing skills")

    # 💳 PAY BUTTON
    if st.button("💳 Pay Now"):

        try:
            response = requests.post(
                "https://resume-analyzer-qamg.onrender.com/create_order"
            )
            order = response.json()

            st.session_state["order_id"] = order["id"]

            # 🔥 Razorpay HTML
            payment_html = f"""
            <html>
            <head>
                <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
            </head>
            <body>
                <script>
                    var options = {{
                        "key": "rzp_test_SSRER7EFytYsML",
                        "amount": "{order['amount']}",
                        "currency": "INR",
                        "name": "Resume Analyzer",
                        "description": "Unlock Full Report",
                        "order_id": "{order['id']}",
                        "handler": function (response){{
                            alert("Payment Successful!");
                        }},
                        "theme": {{
                            "color": "#3399cc"
                        }}
                    }};
                    var rzp = new Razorpay(options);
                    rzp.open();
                </script>
            </body>
            </html>
            """

            components.html(payment_html, height=600)

        except Exception as e:
            st.error(f"Payment Error: {e}")

    st.divider()

    # 🔐 VERIFY PAYMENT (Manual for now)
    st.subheader("🔐 Verify Payment")

    payment_id = st.text_input("Enter Payment ID")
    signature = st.text_input("Enter Signature")

    if st.button("Verify Payment"):
        try:
            response = requests.post(
                "https://resume-analyzer-qamg.onrender.com/verify_payment",
                json={
                    "payment_id": payment_id,
                    "order_id": st.session_state.get("order_id"),
                    "signature": signature
                }
            )

            result = response.json()

            if result["status"] == "success":
                st.success("Payment Verified ✅")

                # 🔓 UNLOCK DATA
                st.subheader("📌 Missing Skills")
                st.write(", ".join(missing) if missing else "No major gaps 🎉")

                if missing:
                    st.subheader("📚 Recommended to Learn")
                    for skill in missing:
                        st.write(f"👉 {skill}")

            else:
                st.error("Payment Failed ❌")

        except Exception as e:
            st.error(f"Error: {e}")
