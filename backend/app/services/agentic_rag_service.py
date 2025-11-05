import os
import random
import faiss
import json
import pickle
import re
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from qualification_service import send_email_gmail

# def send_meeting_email(to_email: str, subject: str, body: str):
#     """
#     Sends an email notifying the user of a scheduled meeting.
#     Uses environment variables for sender credentials.
#     """
#     sender_email = os.getenv("EMAIL_USER")
#     sender_password = os.getenv("EMAIL_PASS")

#     if not sender_email or not sender_password:
#         print("⚠️ Missing BOT_EMAIL or BOT_EMAIL_PASSWORD in .env")
#         return

#     msg = MIMEMultipart()
#     msg["From"] = sender_email
#     msg["To"] = to_email
#     msg["Subject"] = subject
#     msg.attach(MIMEText(body, "plain"))

#     try:
#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()
#             server.login(sender_email, sender_password)
#             server.send_message(msg)
#             print(f"📧 Email sent successfully to {to_email}")
#     except Exception as e:
#         print(f"❌ Failed to send email: {e}")



# ================================================================
# Helper: Random LLM selector
# ================================================================
def get_random_llm(model="openai/gpt-oss-120b", temperature=0.7):
    api_keys = [
        os.getenv("GROQ_API_KEY_1"),
        os.getenv("GROQ_API_KEY_2"),
        os.getenv("GROQ_API_KEY_3"),
        os.getenv("GROQ_API_KEY_4"),
        os.getenv("GROQ_API_KEY_5"),
    ]
    key = random.choice([k for k in api_keys if k])
    return ChatGroq(api_key=key, model=model, temperature=temperature)

def load_user_resume_json(json_path: str):
    """
    Loads user's raw resume JSON and converts it into readable text for LLM.
    """
    if not os.path.exists(json_path):
        print(f"⚠️ Resume JSON not found at: {json_path}")
        return ""

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert JSON to descriptive text
    sections = []
    sections.append(f"Name: {data.get('name', 'N/A')}")
    sections.append(f"Email: {data.get('email', 'N/A')}")
    sections.append(f"Phone: {data.get('phone', 'N/A')}")
    sections.append("\nEducation:")
    for edu in data.get("education", []):
        sections.append(f"- {edu.get('degree', '')} from {edu.get('institution', '')} ({edu.get('period', '')}), CGPA: {edu.get('cgpa', '')}")

    sections.append("\nExperience:")
    for exp in data.get("experience", []):
        sections.append(f"- {exp.get('role', '')} at {exp.get('company', '')} ({exp.get('start', '')} - {exp.get('end', '')})")
        for item in exp.get("items", []):
            sections.append(f"  • {item}")

    sections.append("\nAchievements:")
    for ach in data.get("achievements", []):
        sections.append(f"- {ach.get('title', '')}: {' '.join(ach.get('items', []))}")

    return "\n".join(sections)


def load_flat_faiss(index_base_path: str, embeddings):
    """
    Load FAISS index when stored as flat files:
    <index_base_path>.faiss + <index_base_path>.pkl

    Supports multiple legacy and modern formats.
    """
    faiss_path = index_base_path + ".faiss"
    pkl_path = index_base_path + ".pkl"

    if not (os.path.exists(faiss_path) and os.path.exists(pkl_path)):
        raise FileNotFoundError(f"Missing FAISS files: {faiss_path} or {pkl_path}")

    print(f"✅ Loading FAISS from flat files: {faiss_path}")
    index = faiss.read_index(faiss_path)

    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    # --- Handle different saved formats ---
    docstore = None
    index_to_docstore_id = None

    # Case 1: Dict-based (modern)
    if isinstance(data, dict):
        docstore = data.get("docstore")
        index_to_docstore_id = data.get("index_to_docstore_id")

    # Case 2: Tuple (older LC versions)
    elif isinstance(data, tuple):
        for item in data:
            from langchain_community.docstore.in_memory import InMemoryDocstore
            if isinstance(item, InMemoryDocstore):
                docstore = item
            elif isinstance(item, dict):
                index_to_docstore_id = item
        if not index_to_docstore_id:
            # fallback: use numeric mapping
            index_to_docstore_id = {i: str(i) for i in range(index.ntotal)}

    else:
        raise ValueError(f"Unexpected FAISS pickle format: {type(data)}")

    # --- Safety net ---
    if not docstore:
        from langchain_community.docstore.in_memory import InMemoryDocstore
        docstore = InMemoryDocstore()

    if not index_to_docstore_id:
        index_to_docstore_id = {i: str(i) for i in range(index.ntotal)}

    # --- Build FAISS object ---
    db = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id
    )

    print(f"✅ Successfully reconstructed FAISS store — {index.ntotal} vectors loaded.")
    return db


# ================================================================
# 1️⃣ ROUTER AGENT  (LLM-A)
# ================================================================
def route_query(user_query: str) -> str:
    """
    Decide which knowledge base to use: resume / project / both
    """
    llm = get_random_llm(temperature=0.3)
    prompt = f"""
    You are a routing AI deciding which knowledge base best answers the user's query.

    Knowledge bases available:
    1. resume  — contains user's education, skills, achievements, and experiences.
    2. project — contains GitHub project summaries and technical work.
    3. meeting - when user asks to schedule any kind of meeting

    Query: "{user_query}"

    Reply with only one word: resume, project,both or meeting.
    """
    resp = llm.invoke(prompt)
    answer = getattr(resp, "content", str(resp)).strip().lower()

    if "project" in answer and "resume" in answer:
        return "both"
    elif "project" in answer:
        return "project"
    elif "meeting" in answer:
        return "meeting"
    else:
        return "resume"


def retrieve_answer(user_query: str, source: str) -> str:
    """
    Retrieves context and generates response from flat FAISS indexes.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY_1"), model="openai/gpt-oss-120b", temperature=0.6)

    # --- Your actual paths ---
    base_dir = os.path.join("data", "embeddings")
    resume_path = os.path.join(base_dir, "resume", "resume_index","index")
    project_path = os.path.join(base_dir, "projects", "projects_index")

    print(f"Resume path: {os.path.abspath(resume_path)}")
    print(f"Project path: {os.path.abspath(project_path)}")

    dbs = []
    if source in ["resume", "both"] and os.path.exists(resume_path + ".faiss"):
        dbs.append(load_flat_faiss(resume_path, embeddings))
    if source in ["project", "both"] and os.path.exists(project_path + ".faiss"):
        dbs.append(load_flat_faiss(project_path, embeddings))

    if not dbs:
        return "⚠️ No embeddings found. Please re-upload resume or fetch projects first."

    # Combine contexts if both are used
    all_docs = []
    for db in dbs:
        docs = db.similarity_search(user_query, k=4)
        all_docs.extend(docs)

    if not all_docs:
        return "I found the embeddings, but they didn’t contain relevant information for your query."

    # Build context
    context = "\n\n".join(doc.page_content for doc in all_docs)

    if source in ["resume", "both"]:
        resume_json_path = os.path.join("data", "user_data.json")
        with open(resume_json_path, "r", encoding="utf-8") as f:
            resume_raw_text = f.read()
            context = f"\n\n[Raw Resume Data]\n{resume_raw_text}"

        # print(resume_raw_text)
        # if resume_raw_text:
        #     context = f"\n\n[Raw Resume Data]\n{resume_raw_text}"
        #     print("📎 Added raw resume JSON content to context.")

    prompt = f"""
    You are an intelligent assistant using embedded context data.

    Context:
    {context}

    Question:
    {user_query}

    Give a precise and factual answer based only on the context.
    """
    resp = llm.invoke(prompt)
    return getattr(resp, "content", str(resp))



# ================================================================
# 3️⃣ GRADER AGENT  (LLM-B)
# ================================================================
def grade_answer(user_query: str, answer: str) -> tuple:
    """
    Uses another LLM (LLM-B) to send pass .
    """
    llm = get_random_llm(temperature=0.0)
    prompt = f"""
    You are an evaluator checking if an AI's answer satisfies a user's query.

    Question: {user_query}
    Answer: {answer}

    Evaluate accuracy, completeness, and relevance.
    Respond with JSON only:
    {{
      "grade": "pass",
      "feedback": "Explain why it passed"
    }}
    """
    resp = llm.invoke(prompt)
    text = getattr(resp, "content", str(resp))
    match = re.search(r'\{[\s\S]*\}', text)

    if match:
        try:
            result = json.loads(match.group(0))
            grade = result.get("grade", "").lower()
            feedback = result.get("feedback", "")
            return (grade == "pass", feedback)
        except Exception:
            return (False, "Invalid grader JSON")
    return (False, "Could not parse grader response.")

def meeting_scheduler_node():

    subject = "📅 Congrats Meeting Scheduled Notification"
    body = (
        "Hello,\n\n"
        "A meeting has been successfully scheduled as per your request.\n\n"
        "Details will follow shortly.\n\n"
        "Best,\nAgentic RAG Bot 🤖"
    )

    # Send email
    send_email_gmail(subject, body)


# ================================================================
# 4️⃣ MAIN AGENTIC PIPELINE
# ================================================================
def agentic_rag_pipeline(user_query: str) -> str:
    """
    Agentic RAG Flow:
    1. Router decides source
    2. Retrieve & answer
    3. Grade
    4. Retry if failed
    """
    print("\n========== AGENTIC RAG START ==========")
    print("User Query:", user_query)

    # ----- Step 1: Routing -----
    source = route_query(user_query)
    print("🔍 Router decided:", source)

    if(source == "meeting"):
        meeting_scheduler_node()
        return "✅ Meeting scheduled! Email notification sent."


    # ----- Step 2: Retrieve Answer -----
    answer = retrieve_answer(user_query, source)
    print("📚 Retrieved answer snippet:", answer[:250])


    # ----- Step 3: Grade -----
    passed, feedback = grade_answer(user_query, answer)
    print("🧠 Grader result:", "PASS" if passed else "FAIL", "-", feedback)

    # ----- Step 4: Retry loop if needed -----
    if not passed:
        correction_prompt = f"""
        Your last answer did not meet expectations because:
        {feedback}

        Please revise the answer to fully satisfy the user's query:
        {user_query}
        """
        llm = get_random_llm(temperature=0.5)
        resp = llm.invoke(correction_prompt)
        answer = getattr(resp, "content", str(resp))
        print("🔁 Revised answer generated.")

    print("========== AGENTIC RAG END ==========\n")
    return answer
