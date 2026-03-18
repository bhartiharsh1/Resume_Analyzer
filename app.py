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

  # 👤 USER EMAIL (IMPORTANT)
email = st.text_input("Enter your email (required for payment)")


st.markdown("### 🔓 Unlock Full Report (₹1)")
st.warning("⚡ 90% resumes get rejected due to missing skills")

# 👉 CHECK PAYMENT STATUS
def check_payment(email):
    res = requests.get(
        f"https://resume-analyzer-qamg.onrender.com/check_payment?email={email}"
    )
    return res.json()


if email:
    status = check_payment(email)

    if status["status"] == "paid":
        st.success("🔓 Already Unlocked ✅")

        st.write(", ".join(missing) if missing else "No major gaps 🎉")

        if missing:
            st.subheader("📌 Recommended to Learn")
            for skill in missing:
                st.write(f"👉 {skill}")

    else:
        # 💳 PAY BUTTON (AUTO SYSTEM)
        if st.button("💳 Pay Now"):

            order = requests.post(
                "https://resume-analyzer-qamg.onrender.com/create_order"
            ).json()

            st.markdown(f"""
            <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
            <script>
            var options = {{
                "key": "rzp_test_SSRER7EFytYsML",
                "amount": "{order['amount']}",
                "currency": "INR",
                "name": "Resume Analyzer",
                "description": "Unlock Full Report",
                "order_id": "{order['id']}",
                "handler": function (response){{
                    fetch("https://resume-analyzer-qamg.onrender.com/save_payment", {{
                        method: "POST",
                        headers: {{
                            "Content-Type": "application/json"
                        }},
                        body: JSON.stringify({{
                            email: "{email}",
                            payment_id: response.razorpay_payment_id
                        }})
                    }})
                    .then(res => res.json())
                    .then(data => {{
                        alert("Payment Successful ✅");
                        window.location.reload();
                    }});
                }}
            }};
            var rzp = new Razorpay(options);
            rzp.open();
            </script>
            """, unsafe_allow_html=True)

else:
    st.warning("⚠️ Enter email to continue")
