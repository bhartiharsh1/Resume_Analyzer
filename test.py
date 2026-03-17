from parser import extract_text_from_pdf
from ats import calculate_ats_score
from skills import extract_skills, skill_gap

if __name__ == "__main__":
    with open("Resume4.pdf", "rb") as f:
        text = extract_text_from_pdf(f)

    print(text[:1000])

    job_desc = """
    Looking for a Data Analyst with skills in Python, SQL, Excel, Power BI, and Statistics.
    """

    score = calculate_ats_score(text, job_desc)
    print("ATS Score:", score)

    # Extract skills
    user_skills = extract_skills(text)

    # Find missing skills
    missing = skill_gap(user_skills, "data analyst")

    print("\nYour Skills:", user_skills)
    print("Missing Skills:", missing)