from util import _prompt


def _parse_education(raw: str) -> list[dict]:
    """
    Parse semicolon-separated education entries into a list of dicts.
    Each entry is expected in the format: 'Degree, Institution, Year'.

    :param raw: Raw user input string with entries separated by semicolons.
    :return: List of dicts with keys: degree, institution, year.
    """
    entries = []
    for entry in raw.split(";"):
        parts = [p.strip() for p in entry.strip().split(",")]
        entries.append({
            "degree": parts[0] if len(parts) > 0 else "",
            "institution": parts[1] if len(parts) > 1 else "",
            "year": parts[2] if len(parts) > 2 else "",
        })
    return entries


def _parse_experience(raw: str) -> list[dict]:
    """
    Parse semicolon-separated work experience entries into a list of dicts.
    Each entry is expected in the format: 'Role, Company, Duration, Description'.

    :param raw: Raw user input string with entries separated by semicolons.
    :return: List of dicts with keys: role, company, duration, description.
    """
    entries = []
    for entry in raw.split(";"):
        parts = [p.strip() for p in entry.strip().split(",")]
        entries.append({
            "role": parts[0] if len(parts) > 0 else "",
            "company": parts[1] if len(parts) > 1 else "",
            "duration": parts[2] if len(parts) > 2 else "",
            "description": ", ".join(parts[3:]) if len(parts) > 3 else "",
        })
    return entries


def _parse_projects(raw: str) -> list[dict]:
    """
    Parse semicolon-separated project entries into a list of dicts.
    Each entry is expected in the format: 'Name - Description'.

    :param raw: Raw user input string with entries separated by semicolons.
    :return: List of dicts with keys: name, description.
    """
    entries = []
    for entry in raw.split(";"):
        parts = [p.strip() for p in entry.strip().split("-", 1)]
        entries.append({
            "name": parts[0] if len(parts) > 0 else "",
            "description": parts[1] if len(parts) > 1 else "",
        })
    return entries



def _collect_personal_info() -> dict | None:
    """
    Collect personal information (name, email, phone) from the user.
    Returns None if the user types 'back' at any prompt.

    :return: Dict with keys name, email, phone, or None to go back.
    """
    print("── Step 1/3: Personal Information ──")
    name = _prompt("Full Name")
    if name is None: return None
    email = _prompt("Email")
    if email is None: return None
    phone = _prompt("Phone")
    if phone is None: return None
    return {"name": name, "email": email, "phone": phone}


def _collect_education_experience() -> dict | None:
    """
    Collect education and work experience details from the user.
    Guides the user with example formats and parses the input into
    structured lists. Returns None if the user types 'back' at any prompt.

    :return: Dict with keys education and experience, or None to go back.
    """
    print("\n── Step 2/3: Education & Work Experience ──")
    print("Enter education (e.g., 'B.Tech in CS, XYZ University, 2020'). Separate multiple with ;")
    edu_input = _prompt("Education")
    if edu_input is None: return None

    print("\nEnter experience (e.g., 'Software Engineer, Google, 2020-2023, Built microservices'). Separate multiple with ;")
    exp_input = _prompt("Experience")
    if exp_input is None: return None

    return {"education": _parse_education(edu_input), "experience": _parse_experience(exp_input)}


def _collect_skills_projects_awards() -> dict | None:
    """
    Collect skills, projects, and awards from the user. Skills are
    comma-separated, projects and awards are semicolon-separated.
    Returns None if the user types 'back' at any prompt.

    :return: Dict with keys skills, projects, awards, or None to go back.
    """
    print("\n── Step 3/3: Skills, Projects & Awards ──")
    print("Enter skills separated by commas (e.g., 'Python, Java, AWS').")
    skills_input = _prompt("Skills")
    if skills_input is None: return None

    print("\nEnter projects (Format: Name - Description). Separate multiple with ;")
    projects_input = _prompt("Projects")
    if projects_input is None: return None

    print("\nEnter awards separated by semicolons. Leave blank if none.")
    awards_input = _prompt("Awards")
    if awards_input is None: return None

    return {
        "skills": [s.strip() for s in skills_input.split(",") if s.strip()],
        "projects": _parse_projects(projects_input),
        "awards": [a.strip() for a in awards_input.split(";") if a.strip()],
    }
