from resume_extractor import process_resume
from parse_job import parse_job_description
from generate_cv import generate_cv
from llm_client import LLMClient
from state import SessionState


def run_interactive_session():
    """
    Main interactive workflow using CLI.
    """

    state = SessionState()

    print("Welcome to AI CV Builder\n")

    # Step 1: Resume input choice
    choice = input("Do you want to upload a resume? (yes/no): ").strip().lower()

    if choice == "yes":

        pdf_path = input("Enter path to your resume PDF: ").strip()

        print("Extracting resume data...")
        state.resume_data = process_resume(pdf_path)

    else:
        state.resume_data = collect_manual_input()

    # Step 2: Job description
    print("\nEnter job description (paste below):")
    job_text = input()

    state.job_description = job_text

    print("Parsing job description...")
    state.job_data = parse_job_description(job_text)

    # Step 3: Generate CV
    print("Generating CV...")
    state.generated_cv = generate_cv(state.resume_data, state.job_data)

    print("\nGenerated CV:\n")
    print(state.generated_cv)

    # Step 4: Iterative refinement
    refine_loop(state)


def collect_manual_input():
    """
    Collect resume details manually from user.
    """

    data = {}

    data["name"] = input("Enter your name: ")
    data["email"] = input("Enter your email: ")
    data["phone"] = input("Enter your phone: ")

    skills = input("Enter skills (comma separated): ")
    data["skills"] = [s.strip() for s in skills.split(",")]

    education = input("Enter education details: ")
    data["education"] = [education]

    experience = input("Enter experience: ")
    data["experience"] = [experience]

    projects = input("Enter projects: ")
    data["projects"] = [projects]

    return data
