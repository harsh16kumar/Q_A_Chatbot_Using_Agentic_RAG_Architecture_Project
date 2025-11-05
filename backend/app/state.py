from typing import List, Dict, TypedDict

class GraphState(TypedDict, total=False):
    question: str
    documents: List[str]
    solution: str
    phone_number: str
    email_id: str
    linkedin: str
    github: str
    other_links: List[str]
    ug_cgpa: float
    projects: List[Dict]
    route: str
    latex_code: str
