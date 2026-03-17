import streamlit as st
from parser import extract_text_from_pdf
from ats import calculate_ats_score
from skills import extract_skills, skill_gap

st.set_page_config(page_title="AI Resume Analyzer", layout="centered")

# Header
st.markdown("## 🚀 AI Resume Analyzer")
st.markdown("### 💼 Boost Your Placement Chances")

# Upload
uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type="pdf")

# Role selection
job_role = st.selectbox("🎯 Select Job Role", ["Data Analyst", "Data Scientist"])

job_desc = {
    "Data Analyst": "python sql excel power bi statistics data analysis",
    "Data Scientist": "python machine learning statistics deep learning"
}

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

    st.subheader("❌ Missing Skills")
    st.write(", ".join(missing) if missing else "No major gaps 🎉")

    # Recommendations
    if missing:
        st.subheader("📌 Recommended to Learn")
        for skill in missing:
            st.write(f"👉 {skill}")