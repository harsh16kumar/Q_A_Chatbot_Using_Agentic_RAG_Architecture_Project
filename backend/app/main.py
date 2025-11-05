from app.utils.vectorstore import load_vectorstore
from app.workflow import build_workflow

def run_app():
    retriever = load_vectorstore()
    if not retriever:
        print("Could not run the RAG system because the retriever was not initialized.")
        return
    app = build_workflow(retriever)
    user_question = "how is candidate's profile and also list its credentials?"
    inputs = {"question": user_question}
    for output in app.stream(inputs):
        for key, value in output.items():
            if key == "generate":
                print(f"Final Answer: {value.get('solution')}")
