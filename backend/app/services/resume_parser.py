# lightweight parser: when user uploads PDF we'll extract via PyPDFLoader in frontend or backend vectorstore.
# Provide helper to normalize form data into the template context.

def normalize_form_to_context(form_data: dict) -> dict:
    # form_data fields: name, phone, email, linkedin, github, education entries, coursework (comma separated), languages (csv), tools (csv), projects (list), experience (list), achievements (list)
    def csv_to_list(s):
        if not s:
            return []
        if isinstance(s, list):
            return s
        return [x.strip() for x in s.split(",") if x.strip()]

    context = {
        "name": form_data.get("name", ""),
        "phone": form_data.get("phone", ""),
        "email": form_data.get("email", ""),
        "linkedin": form_data.get("linkedin", ""),
        "github": form_data.get("github", ""),
        "education": form_data.get("education", []),  # expect list of dicts with keys: institution, period, degree, cgpa, location
        "coursework": form_data.get("coursework", []),
        "languages": csv_to_list(form_data.get("languages", "")),
        "tools": csv_to_list(form_data.get("tools", "")),
        "projects": form_data.get("projects", []),
        "experience": form_data.get("experience", []),
        "achievements": form_data.get("achievements", []),
    }
    return context
