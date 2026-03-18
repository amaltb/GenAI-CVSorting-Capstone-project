from typing import List

from pydantic import BaseModel


class Education(BaseModel):
    """
    Schema defining the structure of education data in resume.
    """

    degree: str = ""
    institution: str = ""
    year: str = ""


class Experience(BaseModel):
    """
    Schema defining the structure of experience data in resume.
    """

    role: str = ""
    company: str = ""
    duration: str = ""
    description: str = ""


class Project(BaseModel):
    """
    Schema defining the structure of project data in resume.
    """

    name: str = ""
    description: str = ""

class ResumeSchema(BaseModel):
    """
    Schema defining the structure of extracted resume data.
    """

    name: str
    email: str
    phone: str

    skills: List[str]
    education: List[Education]
    experience: List[Experience]
    projects: List[Project]

    awards: List[str]
