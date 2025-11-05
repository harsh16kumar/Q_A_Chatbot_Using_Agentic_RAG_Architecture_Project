from langgraph.graph import END, StateGraph
from app.state import GraphState
from app.nodes.retrieval import retrieve_docs
from app.nodes.grading import grade_documents
from app.nodes.extraction import extract_contact_details, extract_ug_cgpa
from app.nodes.routing import check_cgpa
from app.nodes.email_node import send_email_node
from app.nodes.answer import generate_answer
from app.nodes.debug import print_state
from app.nodes.analyze_github import analyze_github_node

def build_workflow(retriever):
    workflow = StateGraph(GraphState)

    workflow.add_node("retrieve", lambda state: retrieve_docs(state, retriever))
    workflow.add_node("grade_documents", grade_documents)
    workflow.add_node("extract_contact", extract_contact_details)
    workflow.add_node("analyze_github", analyze_github_node)
    workflow.add_node("debug", print_state)
    workflow.add_node("extract_cgpa", extract_ug_cgpa)
    workflow.add_node("check_cgpa", check_cgpa)
    workflow.add_node("send_email", send_email_node)
    workflow.add_node("generate", generate_answer)

    workflow.set_entry_point("retrieve")

    workflow.add_edge("retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        lambda state: state["route"],
        {"generate": "extract_contact", "retrieve": "retrieve"},
    )

    workflow.add_edge("extract_contact", "analyze_github")
    workflow.add_edge("analyze_github", "debug")
    workflow.add_edge("debug", "extract_cgpa")
    workflow.add_edge("extract_cgpa", "check_cgpa")
    workflow.add_conditional_edges(
        "check_cgpa",
        lambda state: state["route"],
        {"send_email": "send_email", "generate": "generate"},
    )
    workflow.add_edge("send_email", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()
