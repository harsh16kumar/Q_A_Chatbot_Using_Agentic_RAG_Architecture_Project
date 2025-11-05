import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embedding_model():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name
    )
    return embeddings



# ======================================================
# Helper Function
# ======================================================
def _save_faiss(db, save_dir: str, index_name: str):
    """
    Saves FAISS index using its native folder structure:
    <save_dir>/<index_name>/index.faiss and index.pkl
    """
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, index_name)
    db.save_local(save_path)

    # index_file = os.path.join(save_path, "index.faiss")
    # meta_file = os.path.join(save_path, "index.pkl")
    index_file = f"{save_path}.faiss"
    meta_file = f"{save_path}.pkl"

    if os.path.exists(index_file) and os.path.exists(meta_file):
        print(f"✅ FAISS index saved successfully at: {save_path}")
    else:
        print(f"⚠️ Warning: FAISS index files not found at {save_path}")


# ======================================================
# Resume Embedding Function
# ======================================================
def embed_resume_text(parsed_resume):
    """
    Create semantically rich embeddings from a structured resume JSON.
    Saved to backend/data/embeddings/resume/resume_index/
    """
    base_dir = os.path.join("data", "embeddings", "resume")
    os.makedirs(base_dir, exist_ok=True)
    index_name = "resume_index"

    # --- Convert resume to descriptive text ---
    resume_text = f"""
    This is the resume of {parsed_resume.get('name', 'the candidate')}.

    Contact Information:
    Email: {parsed_resume.get('email', 'N/A')}
    Phone: {parsed_resume.get('phone', 'N/A')}
    LinkedIn: {parsed_resume.get('linkedin', 'N/A')}
    GitHub: {parsed_resume.get('github', 'N/A')}

    Education Background:
    """ + "\n".join([
        f"{e.get('degree', '')} at {e.get('institution', '')} ({e.get('period', '')}) "
        f"with CGPA {e.get('cgpa', '')} in {e.get('location', '')}."
        for e in parsed_resume.get("education", [])
    ]) + """

    Work Experience:
    """ + "\n".join([
        f"Served as {exp.get('role', '')} at {exp.get('company', '')} "
        f"from {exp.get('start', '')} to {exp.get('end', '')}, "
        f"where responsibilities included: {' '.join(exp.get('items', []))}"
        for exp in parsed_resume.get("experience", [])
    ]) + """

    Achievements and Leadership:
    """ + "\n".join([
        f"{a.get('title', '')} ({a.get('category', '')}): {' '.join(a.get('items', []))}"
        for a in parsed_resume.get("achievements", [])
    ])

    # --- Generate Embeddings ---
    print("🔍 Generating embeddings for resume...")
    embeddings = get_embedding_model()

    db = FAISS.from_texts([resume_text], embedding=embeddings)
    _save_faiss(db, base_dir, index_name)

    print(f"✅ Resume embeddings stored successfully at {base_dir}\\{index_name}")
    return os.path.join(base_dir, index_name)


# ======================================================
# Project Embedding Function
# ======================================================
def embed_project_summaries(projects):
    """
    Create semantic embeddings for summarized GitHub projects.
    Saved to backend/data/embeddings/projects/projects_index/
    """
    base_dir = os.path.join("data", "embeddings", "projects")
    os.makedirs(base_dir, exist_ok=True)
    index_name = "projects_index"

    # --- Convert each project to natural language ---
    project_texts = []
    for p in projects:
        title = p.get("title", "Untitled Project")
        tech = ", ".join(p.get("technologies", []))
        features = "\n".join(p.get("features", []))

        full_text = f"""
        Project Title: {title}.
        Technologies Used: {tech}.
        Key Features:
        {features}.
        This project demonstrates skills in {tech} and practical experience in {title}.
        """
        project_texts.append(full_text.strip())

    # --- Generate Embeddings ---
    print(f"🔍 Generating embeddings for {len(project_texts)} projects...")
    embeddings = get_embedding_model()

    db = FAISS.from_texts(project_texts, embedding=embeddings)
    _save_faiss(db, base_dir, index_name)

    print(f"✅ Project embeddings stored successfully at {base_dir}\\{index_name}")
    return os.path.join(base_dir, index_name)


# ======================================================
# Optional: Validator Function
# ======================================================
def validate_embeddings():
    """
    Checks whether FAISS indexes exist and are readable.
    """
    paths = {
        "Resume": os.path.join("backend", "data", "embeddings", "resume", "resume_index", "index.faiss"),
        "Projects": os.path.join("backend", "data", "embeddings", "projects", "projects_index", "index.faiss"),
    }

    print("\n🔎 Checking Embedding Files...")
    for name, path in paths.items():
        if os.path.exists(path):
            print(f"✅ {name} embeddings exist at: {path}")
        else:
            print(f"❌ {name} embeddings missing at: {path}")
