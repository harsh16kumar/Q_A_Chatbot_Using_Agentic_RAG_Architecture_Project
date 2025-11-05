from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from app.utils.prompts import resume_answer_prompt

llm = ChatGroq(temperature=0, model_name="gemma2-9b-it")
rag_chain = resume_answer_prompt | llm | StrOutputParser()

def generate_answer(state):
    print("---GENERATING ANSWER---")
    question = state.get("question", "")
    documents = state.get("documents", [])
    try:
        solution = rag_chain.invoke({"context": "\n".join(documents), "question": question})
    except Exception as e:
        solution = "Could not generate answer."
        print("generate error", e)
    return {**state, "solution": solution}
