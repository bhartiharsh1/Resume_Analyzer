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
if "payment_done" not in st.session_state:
    st.session_state.payment_done = False

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


# ✅ CHECK PAYMENT STATUS — with timeout + proper error messages
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


# ✅ CREATE ORDER — with timeout + proper error messages
def create_order():
    try:
        res = requests.post(
            f"{BACKEND_URL}/create_order",
            timeout=15
        )
        res.raise_for_status()
        data = res.json()
        if "error" in data:
            st.error(f"❌ Razorpay error: {data['error']}")
            return None
        return data
    except requests.exceptions.Timeout:
        st.warning("⏳ Backend is waking up, please wait 30 seconds and try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Check if Render service is running.")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None


if email:
    status = check_payment(email)

    if status.get("status") == "paid" or st.session_state.payment_done:
        st.success("🔓 Already Unlocked ✅")
        missing = st.session_state.missing
        st.write(", ".join(missing) if missing else "No major gaps 🎉")
        if missing:
            st.subheader("📌 Recommended to Learn")
            for skill in missing:
                st.write(f"👉 {skill}")

    else:
        if st.button("💳 Pay Now"):
            with st.spinner("Connecting to payment gateway..."):
                order = create_order()

            if order and "id" in order:
                # ✅ components.html() runs JS — st.markdown() does NOT
                razorpay_html = f"""
                <html>
                <body>
                <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
                <script>
                    var options = {{
                        "key": "rzp_test_SSRER7EFytYsML",
                        "amount": "{order['amount']}",
                        "currency": "INR",
                        "name": "Resume Analyzer",
                        "description": "Unlock Full Report",
                        "order_id": "{order['id']}",
                        "prefill": {{
                            "email": "{email}"
                        }},
                        "handler": function (response) {{
                            fetch("{BACKEND_URL}/save_payment", {{
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
                                if (data.status === "success") {{
                                    alert("✅ Payment Successful! Refreshing...");
                                    window.parent.location.reload();
                                }} else {{
                                    alert("❌ Payment verification failed. Contact support.");
                                }}
                            }})
                            .catch(err => {{
                                alert("❌ Error saving payment: " + err);
                            }});
                        }},
                        "modal": {{
                            "ondismiss": function() {{
                                alert("⚠️ Payment cancelled.");
                            }}
                        }}
                    }};
                    var rzp = new Razorpay(options);
                    rzp.open();
                </script>
                </body>
                </html>
                """
                components.html(razorpay_html, height=1)

else:
    st.warning("⚠️ Enter email to continue")
