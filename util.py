import re
import subprocess
import tempfile
import os


def _strip_code_blocks(text: str) -> str:
    """
    Remove markdown code block wrappers and trailing LLM commentary from output.
    Cleans up common artifacts such as ```text blocks, **Note:** sections,
    disclaimers, revision notes, and horizontal rule separators that LLMs
    tend to append to generated content.

    :param text: Raw LLM output string potentially containing markdown artifacts.
    :return: Cleaned plain text with code blocks and trailing commentary removed.
    """
    # Remove opening ```<optional language tag> and closing ```
    text = re.sub(r'^```\w*\n?', '', text.strip())
    text = re.sub(r'\n?```$', '', text.strip())
    # Remove trailing notes/commentary added by LLM (e.g. **Note:**, Note:, ---\n, etc.)
    text = re.sub(r'\n\s*\*{0,2}Note\*{0,2}\s*:.*', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'\n\s*---\s*\n.*', '', text, flags=re.DOTALL)
    text = re.sub(r'\n\s*\*{0,2}Disclaimer\*{0,2}\s*:.*', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'\n\s*\*{0,2}Changes made\*{0,2}\s*:.*', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'\n\s*\*{0,2}Revision notes?\*{0,2}\s*:.*', '', text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()



def _export_cv_to_pdf(cv_text: str, output_path: str = "revised_cv.pdf") -> str:
    """
    Export CV plain text to a PDF file using Pandoc. Writes the CV content to a
    temporary markdown file, converts it to PDF via Pandoc with pdflatex as the
    default engine, and falls back to Pandoc's default engine if pdflatex fails.

    :param cv_text: The CV content in plain text or markdown format.
    :param output_path: The output PDF file path. Defaults to 'revised_cv.pdf'.
    :return: Absolute path to the generated PDF on success, or an error message string on failure.
    """
    try:
        # Write CV text to a temporary markdown file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
            tmp.write(cv_text)
            tmp_path = tmp.name

        # Use Pandoc to convert markdown to PDF
        result = subprocess.run(
            ["pandoc", tmp_path, "-o", output_path,
             "--pdf-engine=pdflatex",
             "-V", "geometry:margin=1in",
             "-V", "fontsize=11pt"],
            capture_output=True, text=True
        )

        # Clean up temp file
        os.unlink(tmp_path)

        if result.returncode != 0:
            # Fallback: try without pdflatex (use default engine)
            with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
                tmp.write(cv_text)
                tmp_path = tmp.name

            result = subprocess.run(
                ["pandoc", tmp_path, "-o", output_path],
                capture_output=True, text=True
            )
            os.unlink(tmp_path)

            if result.returncode != 0:
                return f"Error generating PDF: {result.stderr}"

        return os.path.abspath(output_path)
    except Exception as e:
        return f"Error generating PDF: {e}"


def _prompt(label: str) -> str | None:
    """
    Prompt the user for input with the given label. Returns None if the user
    types 'back', allowing callers to handle navigation to the previous step.

    :param label: The label to display before the input cursor (e.g., 'Full Name').
    :return: The user's input string, or None if the user typed 'back'.
    """
    value = input(f"{label}: ").strip()
    return None if value.lower() == "back" else value
