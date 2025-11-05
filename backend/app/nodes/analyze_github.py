from app.services.github_service import fetch_and_analyze_github

def analyze_github_node(state):
    github_url = state.get("github") or state.get("linkedin") or ""
    if not github_url or github_url == "Not mentioned":
        print("⚠️ No GitHub profile found.")
        return {**state, "projects": []}
    username = github_url.rstrip("/").split("/")[-1]
    projects = fetch_and_analyze_github(username)
    print("✅ Extracted Projects:", [p.get("repo") for p in projects])
    return {**state, "projects": projects}
