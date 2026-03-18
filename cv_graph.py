from langgraph.graph import StateGraph, END

from constants import GENERIC_QUERY
from cv_input_collector import _collect_personal_info, _collect_education_experience, _collect_skills_projects_awards
from llm_client import LLMClient
from resume_extractor import process_resume
from state import AgentState
from util import _strip_code_blocks, _export_cv_to_pdf


def greeting_node(state: AgentState) -> dict:
    """
    This is a greeting node. First node in the langgraph. It simply greets the user.

    :param state:
    :return:
    """
    print("\nHi! I can help you create and tailor your CV.")
    return {}


def input_mode_node(state: AgentState) -> dict:
    """
    This node is responsible for selecting user input type. User can either
    submit their current CV or choose to manually enter all their details.
    User can choose from pdf or manual. If the user has a generic queries
    they can type help to post their query.

    :param state: The current agent state.
    :return: Dict with next_route in the graph based on user choice.
    """
    while True:
        choice = input("Would you like to upload your resume as a PDF or enter details manually? (pdf/manual/help): ").strip().lower()
        if choice == "pdf":
            return {"next_route": "resume_extraction"}
        elif choice == "manual":
            return {"next_route": "manual_resume_input"}
        elif choice == "help":
            llm = LLMClient()
            question = input(f"{GENERIC_QUERY}")
            print(llm.generate(question))
        else:
            print("Please type 'pdf', 'manual', or 'help'.")


def resume_extraction_node(state: AgentState) -> dict:
    """
    This node handles extracting resume data from a user-provided PDF file.
    It prompts the user for the file path and uses the resume extractor to parse
    the PDF into structured data. Resume extractor uses pdfplumber to convert pdf
    to text and makes LLM (llama3:8b model) call to extract structured data from
    pdf text. The user can type 'back' to return to the
    input mode selection. If extraction fails, the error is displayed and the
    user is prompted again.

    :param state: The current agent state.
    :return: Dict with extracted resume_data, or next_route to go back.
    """
    while True:
        path = input("Please provide the path to your PDF resume (or type 'back' to go back): ").strip()
        if path.lower() == "back":
            return {"next_route": "input_mode"}
        try:
            data = process_resume(path)
            return {"resume_data": data}
        except Exception as e:
            print(f"Error extracting resume: {e}")


def manual_resume_input_node(state: AgentState) -> dict:
    """
    This node handles collecting required details from the user for CV generation
    by grouping input into 3 queries:
      1. Personal Info (name, email, phone)
      2. Education & Experience
      3. Skills, Projects & Awards

    The user can type 'back' at any prompt to return to the input mode selection.

    :param state: The current agent state.
    :return: Dict with structured resume_data, or next_route to go back.
    """
    print("\nLet's collect your details for the CV. Type 'back' at any point to go back.\n")

    collectors = [_collect_personal_info, _collect_education_experience, _collect_skills_projects_awards]
    resume_data: dict = {}

    for collect in collectors:
        result = collect()
        if result is None:
            return {"next_route": "input_mode"}
        resume_data.update(result)

    print("\n✅ All details collected successfully!")
    return {"resume_data": resume_data}


def job_description_input_node(state: AgentState) -> dict:
    """
    This node collects the job description from the user and saves it in agent_state.

    :param state: The current agent state
    :return: Dict with job_description
    """
    while True:
        jd = input("Please paste the job description (or type 'help' for Q&A): ")
        if jd.strip().lower() == "help":
            llm = LLMClient()
            question = input(f"{GENERIC_QUERY}")
            print(llm.generate(question))
        else:
            return {"job_description": jd}


def job_parsing_node(state: AgentState) -> dict:
    """
    This node handles parsing the provided job description and extracting
    key details from it. It uses LLM (By default Gemma3:1b model) to extract
    the key details from the given job description. It then saves the extracted
    details in the agent state.

    :param state: The current agent state.
    :return:
    """
    print("Parsing job description...")
    llm = LLMClient()
    prompt = f"""
        Extract the key requirements, responsibilities, and keywords from the following job description. Return as JSON with keys: requirements, responsibilities, keywords.
        Job Description:
        {state['job_description']}
    """
    job_data = llm.generate(prompt)
    return {"job_data": job_data}


def cv_generation_node(state: AgentState) -> dict:
    """
    This node handles the CV generation task. It takes the given resume data
    and job description to generate a revised resume tailored to the given
    job description. It makes an LLM call (Gemma3:1b model) to generate the CV.

    :param state: Current agent state.
    :return: Dict with generated_cv.
    """
    print("Generating tailored CV...")
    llm = LLMClient()
    prompt = f"""
        You are a professional CV writer. Using the resume data and job description data below, generate a tailored, ATS-friendly CV.

        Rules:
        - Output ONLY the CV content in plain text
        - Do NOT add any explanations, notes, or commentary
        - Do NOT add text before or after the CV
        - Do NOT say things like "Here is the CV" or "I hope this helps"
        - Do NOT wrap the output in markdown code blocks like ```text or ```
        - Do NOT use any markdown formatting at all

        Resume Data: {state['resume_data']}
        Job Data: {state['job_data']}
    """
    cv = llm.generate(prompt)
    # Strip markdown code block wrappers if present
    cv = _strip_code_blocks(cv)
    print("CV generated:\n")
    print(cv)
    return {"generated_cv": cv}


def review_node(state: AgentState) -> dict:
    """
    This node handles collecting user feedback on the generated cv.
    If the user wants to refine the CV, it then collects user feedback
    to incorporate and route to cv refinement node.

    :param state: The current agent state.
    :return: Route to refinement_node or save the generated cv in pdf format
    or print the cv depending on user request.
    """
    while True:
        choice = input("Would you like to (view) the full CV, (refine) it, or (finish)? (view/refine/finish/help): ").strip().lower()
        if choice == "refine":
            return {"review_route": "refinement"}
        elif choice == "view":
            print("\n--- Full CV ---\n")
            print(state["generated_cv"])
            print("\n--- End of CV ---\n")
        elif choice == "help":
            llm = LLMClient()
            question = input(f"{GENERIC_QUERY}")
            print(llm.generate(question))
        elif choice in ("finish", "no"):
            # Export CV to PDF using Pandoc
            pdf_path = _export_cv_to_pdf(state["generated_cv"])
            if pdf_path.startswith("Error"):
                print(pdf_path)
            else:
                print(f"\nYour CV has been saved as PDF: {pdf_path}")
            return {"review_route": "end"}
        else:
            print("Please type 'view', 'refine', 'finish', or 'help'.")


def refinement_node(state: AgentState) -> dict:
    """
    This node handles cv refinement by incorporating user feedbacks.
    It refines the previously generated CV tailored to given job description
    and given user feedback using LLM (Gemma3:1b model) call. It prints the refined CV for user review.

    :param state: The current agent state.
    :return: Dict with updated cv.
    """
    feedback = input("Please provide your feedback for refinement: ")
    llm = LLMClient()
    prompt = f"""
        You are a professional CV writer. Here is the current CV:
        {state['generated_cv']}
        
        User feedback: {feedback}
        
        Job description: {state['job_data']}
        
        Update the CV accordingly and return the full revised CV.
        
        Rules:
        - Output ONLY the updated CV content in plain text
        - Do NOT add any explanations, notes, or commentary
        - Do NOT add text before or after the CV
        - Do NOT say things like "Here is the updated CV" or "I hope this helps"
        - Do NOT wrap the output in markdown code blocks like ```text or ```
        - Do NOT use any markdown formatting at all
    """
    updated_cv = llm.generate(prompt)
    updated_cv = _strip_code_blocks(updated_cv)
    print("CV refined.\n")
    print(updated_cv)
    return {"generated_cv": updated_cv}


# ── Router functions (return the name of the next node) ──────────────────────

def input_mode_router(state: AgentState) -> str:
    """
    Router method to get the next node name from agent state.

    :param state: The current agent state.
    :return: Next node name
    """
    return state.get("next_route", "resume_extraction")


def review_router(state: AgentState) -> str:
    """
    Method to check the end of graph after review node.

    :param state: The current agent state.
    :return: End of graph or the next node name.
    """
    route = state.get("review_route", "end")
    if route == "end":
        return END
    return route


# ── Build and run the graph ──────────────────────────────────────────────────

def run():
    """
    Method to compile the graph and run with initial agent state.

    :return:
    """
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("greeting", greeting_node)
    graph.add_node("input_mode", input_mode_node)
    graph.add_node("resume_extraction", resume_extraction_node)
    graph.add_node("manual_resume_input", manual_resume_input_node)
    graph.add_node("job_description_input", job_description_input_node)
    graph.add_node("job_parsing", job_parsing_node)
    graph.add_node("cv_generation", cv_generation_node)
    graph.add_node("review", review_node)
    graph.add_node("refinement", refinement_node)

    # Edges
    graph.set_entry_point("greeting")
    graph.add_edge("greeting", "input_mode")

    # Conditional: input_mode -> resume_extraction OR manual_resume_input
    graph.add_conditional_edges("input_mode", input_mode_router)

    graph.add_edge("resume_extraction", "job_description_input")
    graph.add_edge("manual_resume_input", "job_description_input")
    graph.add_edge("job_description_input", "job_parsing")
    graph.add_edge("job_parsing", "cv_generation")
    graph.add_edge("cv_generation", "review")

    # Conditional: review -> refinement OR END
    graph.add_conditional_edges("review", review_router)

    graph.add_edge("refinement", "review")

    # Compile & run
    app = graph.compile()
    initial_state: AgentState = {
        "resume_data": None,
        "job_description": None,
        "job_data": None,
        "generated_cv": None,
        "next_route": None,
        "review_route": None,
    }
    app.invoke(initial_state)
