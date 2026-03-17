import fitz  # PyMuPDF
from ats import calculate_ats_score
from skills import extract_skills, skill_gap

def extract_text_from_pdf(file):
    text = ""
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    
    for page in pdf:
        text += page.get_text()
    
    return text
