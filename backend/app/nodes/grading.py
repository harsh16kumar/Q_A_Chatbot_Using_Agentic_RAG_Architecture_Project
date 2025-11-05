from app.utils.prompts import grading_prompt
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

grading_llm = ChatGroq(temperature=0, model_name="gemma2-9b-it")
grader = grading_prompt | grading_llm | StrOutputParser()

def grade_documents(state):
    print("---CHECKING DOCUMENT RELEVANCE---")
    question = state.get("question", "")
    documents = state.get("documents", [])
    relevant_docs = []
    for d in documents:
        try:
            score = grader.invoke({"question": question, "document": d})
            if "yes" in score.lower():
                relevant_docs.append(d)
        except Exception as e:
            print("grading error", e)
    if not relevant_docs:
        print("---NO RELEVANT DOCUMENTS FOUND — RETRYING RETRIEVAL---")
        return {**state, "route": "retrieve"}
    print(f"---{len(relevant_docs)} RELEVANT DOCUMENT(S) FOUND---")
    return {**state, "documents": relevant_docs, "route": "generate"}
