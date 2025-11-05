from langchain.prompts import PromptTemplate

resume_answer_prompt = PromptTemplate(
    template="""
    You are an assistant that answers questions about a candidate's resume.

    The resume context below contains details such as:
    - Name and contact info
    - Skills and technologies
    - Education and certifications
    - Work experience and achievements
    - Projects and publications
    - Extracurricular activities

    When answering:
    - Use only the provided resume context, do not assume anything.
    - If not found, say: "Not mentioned in the resume."
    - Keep the answer concise and professional.
    - Prefer bullet points for lists.

    Question: {question}
    Resume Context: {context}
    Answer:
    """,
    input_variables=["question", "context"],
)

grading_prompt = PromptTemplate(
    template="""
    You are checking if a retrieved piece of a resume contains information relevant to the given question.

    Return only "yes" if relevant, otherwise "no".

    Document: {document}
    Question: {question}
    """,
    input_variables=["question", "document"],
)

contact_prompt = PromptTemplate(
    template="""
     You are an information extraction assistant.
     From the resume text below, extract ONLY:
     - phone_number
     - email_id (prefer Gmail if multiple emails)
     - linkedin (profile link)
     - github (profile link)
     - other_links (any portfolio, website, or other professional links)

     Rules:
     - If not found, write "Not mentioned".
     - For `other_links`, return a JSON array of strings (URLs).
     - Output ONLY valid JSON. Do not add explanations.

     Resume Text:
     {resume}
    """,
    input_variables=["resume"],
)


cgpa_prompt = PromptTemplate(
    template="""
    From the following resume text, extract ONLY the undergraduate CGPA.
    - If multiple GPAs are mentioned, choose the undergraduate one.
    - Return only the numeric value (e.g., 9.2).
    - If not mentioned, return "0".

    Resume Text:
    {resume}

    Output should be just cgpa (e.g., 8.01, 9.12)
    """,
    input_variables=["resume"],
)
