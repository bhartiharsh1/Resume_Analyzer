import streamlit as st
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

# 🔥 MAIN BLOCK
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

    # 🔒 LOCKED SECTION
    st.subheader("❌ Missing Skills")

    st.markdown("### 🔓 Unlock Full Report (₹1)")
    st.warning("⚡ 90% resumes get rejected due to missing skills")

    # ✅ PAYMENT LINK (REPLACED BUTTON)
    st.markdown("[💳 Pay Now](https://rzp.io/rzp/Ir3XL5cl)")

    st.info("After payment, enter your details below 👇")

    # 🔐 VERIFY PAYMENT
    st.subheader("🔐 Verify Payment")

    payment_id = st.text_input("Enter Payment ID")
    signature = st.text_input("Enter Signature")

    if st.button("Verify Payment"):
        try:
            response = requests.post(
                "https://resume-analyzer-qamg.onrender.com/verify_payment",
                json={
                    "payment_id": payment_id,
                    "order_id": "",  # no order id with link
                    "signature": signature
                }
            )

            result = response.json()

            if result.get("status") == "success":
                st.success("Payment Verified ✅")

                # 🔓 UNLOCK DATA
                st.write(", ".join(missing) if missing else "No major gaps 🎉")

                if missing:
                    st.subheader("📌 Recommended to Learn")
                    for skill in missing:
                        st.write(f"👉 {skill}")

            else:
                st.error("Payment Failed ❌")

        except Exception as e:
            st.error(f"Error: {e}")
