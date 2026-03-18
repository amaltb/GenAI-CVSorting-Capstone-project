# ── State schema ──────────────────────────────────────────────────────────────
from typing import Optional

from typing_extensions import TypedDict


class AgentState(TypedDict):
    """
    Defines the shared state schema for the LangGraph CV generation workflow.
    Each key represents a piece of data that flows between graph nodes, tracking
    the user's resume data, job description, generated CV, and routing decisions
    for conditional edges.
    """

    resume_data: Optional[dict]
    job_description: Optional[str]
    job_data: Optional[str]
    generated_cv: Optional[str]
    next_route: Optional[str]           # used by conditional routers
    review_route: Optional[str]
