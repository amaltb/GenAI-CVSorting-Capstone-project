from langchain.tools import tool
from resume_extractor import process_resume

def create_tools(state):

    @tool
    def extract_resume_tool(file_path: str) -> str:
        """
        Extract resume data from a PDF file and store it in memory.
        """

        data = process_resume(file_path)
        state.resume_data = data
        return f"Resume data extracted successfully: {data}"

    @tool
    def manual_input_tool(input_text: str) -> str:
        """
        Collect resume details manually from user input.
        """

        # Simple parsing (can improve later)
        state.resume_data = {
            "raw_input": input_text
        }

        return "Manual resume data stored."


    @tool
    def parse_job_tool(job_text: str) -> str:
        """
        Parse job description and store structured job data.
        """

        state.job_description = job_text
        job_data = parse_job_description(job_text)
        state.job_data = job_data
        return f"Job data extracted: {job_data}"


    @tool
    def generate_cv_tool(dummy_input: str) -> str:
        """
        Generate CV using stored resume and job data.
        """

        if not state.resume_data or not state.job_data:
            return "Missing resume or job data."

        cv = generate_cv(state.resume_data, state.job_data)
        state.generated_cv = cv
        return cv


    @tool
    def refine_cv_tool(feedback: str) -> str:
        """
        Refine the generated CV based on user feedback.
        """

        if not state.generated_cv:
            return "No CV generated yet."

        llm = LLMClient("gemma3:1b")

        prompt = f"""
            You are a resume editor.

            Current CV:
            {state.generated_cv}

            User feedback:
            {feedback}

            Update the CV accordingly.
            Return full updated CV.
            """

        updated_cv = llm.generate(prompt)
        state.generated_cv = updated_cv
        return updated_cv

    return [
        extract_resume_tool,
        manual_input_tool,
        parse_job_tool,
        generate_cv_tool,
        refine_cv_tool
    ]

