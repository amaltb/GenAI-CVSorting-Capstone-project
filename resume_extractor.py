import json
import re
import pdfplumber

from llm_client import LLMClient
from model import ResumeSchema


def extract_text_from_pdf(pdf_path):
    """
    Extract raw text from a resume PDF file using pdfplumber.

    Args:
        pdf_path (str): Path to resume PDF.

    Returns:
        str: Extracted text from the resume.
    """

    print("Extracting text from resume pdf file.")

    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text



def extract_resume_information(resume_text):
    """
    This methid uses LLM (Llama3:8b model) to extract structured resume
    information.

    Args:
        resume_text (str): Raw resume text.

    Returns:
        dict: Structured resume data.
    """

    print("Extracting structured information from resume text.")

    llm = LLMClient(model="llama3:8b")

    prompt = f"""
        You are a resume information extraction system.

        Extract the information and return ONLY valid JSON.
            
        Rules:
        - Output must be valid JSON
        - Do NOT add explanations
        - Do NOT add text before or after JSON
        - Return JSON only
            
        JSON format:
            
        {{
            "name": "",
            "email": "",
            "phone": "",
            "skills": ["", ""],
            "education": [
               {{
                 "degree": "",
                 "institution": "",
                 "year": ""
               }}
             ],
             "experience": [
               {{
                 "role": "",
                 "company": "",
                 "duration": "",
                 "description": ""
               }}
             ],
            "projects": [
               {{
                 "name": "",
                 "description": ""
               }}
             ],
            "awards": ["", ""]
        }}
            
        Resume text:
        {resume_text}
        """
    response = llm.generate(prompt)
    data = extract_json_from_response(response)

    if data:
        validated = ResumeSchema(**data)
        return validated.model_dump()
    return {
        "error": "Invalid JSON from model",
        "raw_output": response
        }


def extract_json_from_response(response):
    """
    Extract JSON object from LLM response safely.
    """

    try:
        # Direct parse first
        return json.loads(response)
    except:
        pass

    # Find JSON inside text
    match = re.search(r'\{.*\}', response, re.DOTALL)

    if match:
        json_str = match.group()

        try:
            return json.loads(json_str)
        except:
            pass

    return None


def process_resume(pdf_path):
    """
    Complete resume processing pipeline.

    Args:
        pdf_path (str): Path to resume file.

    Returns:
        dict: Extracted structured resume information.
    """

    resume_text = extract_text_from_pdf(pdf_path)

    structured_data = extract_resume_information(resume_text)

    return structured_data
