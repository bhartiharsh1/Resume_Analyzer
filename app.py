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

BACKEND_URL = "https://resume-analyzer-qamg.onrender.com"

# Upload
uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type="pdf")

# Role selection
job_role = st.selectbox("🎯 Select Job Role", ["Data Analyst", "Data Scientist"])
job_desc = {
    "Data Analyst": "python sql excel power bi statistics data analysis",
    "Data Scientist": "python machine learning statistics deep learning"
}

# Initialize session state
if "missing" not in st.session_state:
    st.session_state.missing = []

# 🔥 MAIN BLOCK
if uploaded_file:
    with st.spinner("Analyzing your resume..."):
        text = extract_text_from_pdf(uploaded_file)
        score = calculate_ats_score(text, job_desc[job_role])
        user_skills = extract_skills(text)
        missing = skill_gap(user_skills, job_role)
        st.session_state.missing = missing

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

# 👤 USER EMAIL
email = st.text_input("Enter your email (required for payment)")

# 🔒 LOCKED SECTION
st.subheader("❌ Missing Skills")
st.markdown("### 🔓 Unlock Full Report (₹1)")
st.warning("⚡ 90% resumes get rejected due to missing skills")


# ✅ CHECK PAYMENT STATUS
def check_payment(email):
    try:
        res = requests.get(
            f"{BACKEND_URL}/check_payment?email={email}",
            timeout=15
        )
        res.raise_for_status()
        return res.json()
    except requests.exceptions.Timeout:
        st.warning("⏳ Backend is waking up, please wait 30 seconds and try again.")
        return {"status": "error"}
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Check if Render service is running.")
        return {"status": "error"}
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return {"status": "error"}


# ✅ GET PAYMENT LINK from backend
def get_payment_link(email):
    try:
        res = requests.get(
            f"{BACKEND_URL}/create_payment_link?email={email}",
            timeout=15
        )
        res.raise_for_status()
        data = res.json()
        if "error" in data:
            st.error(f"❌ Razorpay error: {data['error']}")
            return None
        return data.get("payment_url")
    except requests.exceptions.Timeout:
        st.warning("⏳ Backend is waking up, please wait 30 seconds and try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Check if Render service is running.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


if email:
    status = check_payment(email)

    if status.get("status") == "paid":
        # ✅ UNLOCKED — show missing skills
        st.success("🔓 Already Unlocked ✅")
        missing = st.session_state.missing
        st.write(", ".join(missing) if missing else "No major gaps 🎉")
        if missing:
            st.subheader("📌 Recommended to Learn")
            for skill in missing:
                st.write(f"👉 {skill}")

    elif status.get("status") == "not_paid":
        if st.button("💳 Pay Now - ₹1"):
            with st.spinner("Generating payment link..."):
                payment_url = get_payment_link(email)

            if payment_url:
                # ✅ Show a clickable link — works 100% in Streamlit, no popup needed
                st.success("✅ Payment link generated! Click below to pay:")
                st.markdown(
                    f"""
                    <a href="{payment_url}" target="_blank"
                    style="
                        display: inline-block;
                        background-color: #528FF0;
                        color: white;
                        padding: 12px 28px;
                        border-radius: 8px;
                        font-size: 18px;
                        font-weight: bold;
                        text-decoration: none;
                        margin-top: 10px;
                    ">
                    💳 Click Here to Pay ₹1
                    </a>
                    """,
                    unsafe_allow_html=True
                )
                st.info("ℹ️ After payment, come back here and refresh the page to unlock your report.")

else:
    st.warning("⚠️ Enter email to continue")
