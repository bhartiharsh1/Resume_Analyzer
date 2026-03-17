SKILLS_DB = [
    "python", "sql", "machine learning", "excel",
    "power bi", "tableau", "statistics", "java",
    "c++", "data analysis", "deep learning"
]

def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in SKILLS_DB:
        if skill in text:
            found_skills.append(skill)

    return found_skills


ROLE_SKILLS = {
    "data analyst": ["python", "sql", "excel", "power bi", "statistics"],
    "data scientist": ["python", "machine learning", "statistics", "deep learning"]
}

def skill_gap(user_skills, role):
    required = ROLE_SKILLS.get(role.lower(), [])
    missing = [skill for skill in required if skill not in user_skills]

    return missing