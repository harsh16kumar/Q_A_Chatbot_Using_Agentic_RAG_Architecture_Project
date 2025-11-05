from app.utils.prompts import contact_prompt, cgpa_prompt
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

llm = ChatGroq(temperature=0, model_name="gemma2-9b-it")

def extract_contact_details(state):
    print("---EXTRACTING CONTACT DETAILS---")
    documents = state.get("documents", [])
    resume_text = "\n".join(documents)
    extractor_chain = contact_prompt | llm | JsonOutputParser()
    try:
        extracted = extractor_chain.invoke({"resume": resume_text})
    except Exception as e:
        print("contact extraction error", e)
        extracted = {}
    return {
        **state,
        "phone_number": extracted.get("phone_number", "Not mentioned"),
        "email_id": extracted.get("email_id", "Not mentioned"),
        "linkedin": extracted.get("linkedin", "Not mentioned"),
        "github": extracted.get("github", "Not mentioned"),
        "other_links": extracted.get("other_links", []),
    }

def extract_ug_cgpa(state):
    print("---EXTRACTING UG CGPA---")
    resume_text = "\n".join(state.get("documents", []))
    extractor_chain = cgpa_prompt | llm | StrOutputParser()
    try:
        cgpa_str = extractor_chain.invoke({"resume": resume_text})
        cgpa_val = float(cgpa_str.strip())
    except Exception:
        cgpa_val = 0.0
    return {**state, "ug_cgpa": cgpa_val}
