import requests
import base64
import ast
import json
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIG ==========
EXCLUDED_DIRS = {"venv", "__pycache__", "node_modules", "dist", "build", ".git"}
INCLUDE_EXTENSIONS = {".py", ".js", ".ts", ".ipynb", ".java"}


def safe_int_env(var_name: str, default: int) -> int:
    val = os.getenv(var_name)
    try:
        return int(val) if val is not None else default
    except ValueError:
        return default

OUTPUT_DIR = "data/github_repos"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}




MAX_FILE_SIZE = safe_int_env("MAX_FILE_SIZE", 50000)  # default 50 KB
MAX_LINES = safe_int_env("MAX_LINES", 500)            # default 500 lines




# ---------- CORE FETCHERS ----------

def fetch_github_repos(username: str) -> List[Dict]:
    url = f"https://api.github.com/users/{username}/repos"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print(f"[ERROR] Failed to fetch repos: {resp.status_code}")
        return []
    data = resp.json()
    print(f"[INFO] Found {len(data)} repositories for '{username}'.")
    return data


def fetch_repo_contents(owner: str, repo: str, path: str = "", all_files: List[str] = None) -> List[Dict]:
    """Recursively fetch contents of a repository and record *all* file names."""
    if all_files is None:
        all_files = []

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print(f"[WARN] Cannot fetch '{path}' in '{repo}' (HTTP {resp.status_code})")
        return []

    data = resp.json()
    filtered_files = []

    for item in data:
        if item["type"] == "dir":
            # Record the directory name in all_files too (for full structure if needed)
            fetch_repo_contents(owner, repo, item["path"], all_files)
        elif item["type"] == "file":
            all_files.append(item["path"])  # ✅ record every file, regardless of filter
            ext = os.path.splitext(item["name"])[1].lower()
            if ext in INCLUDE_EXTENSIONS and item["size"] <= MAX_FILE_SIZE:
                # filter only relevant files for deeper analysis
                if not any(ex in item["path"].lower() for ex in EXCLUDED_DIRS):
                    filtered_files.append(item)
    return filtered_files


# ---------- FILE UTILITIES ----------

def fetch_file_text(item: Dict) -> str:
    """Fetch file content using download_url or Base64 API fallback."""
    url = item.get("download_url")
    if url:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            return resp.text

    api_url = item.get("url")
    if api_url:
        resp = requests.get(api_url, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("encoding") == "base64":
                return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
    return ""


# ---------- MAIN ANALYZER ----------

def analyze_repository(owner: str, repo: str) -> Dict:
    print(f"\n[INFO] 🔍 Analyzing repository '{repo}'...")

    repo_data = {
        "repository": repo,
        "readme": "",
        "requirements": "",
        "files_name": []
    }

    # --- Fetch top-level README and requirements.txt ---
    for file_name in ["README.md", "readme.md"]:
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{file_name}"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            repo_data["readme"] = resp.text
            break

    for req_file in ["requirements.txt", "setup.py"]:
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{req_file}"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            repo_data["requirements"] = resp.text
            break

    all_files_collector = []
    filtered_files = fetch_repo_contents(owner, repo, "", all_files_collector)
    repo_data["files_name"] = all_files_collector  # ✅ store all file names

    return repo_data


# ---------- ENTRY POINT ----------

def fetch_and_analyze_github(username: str):
    repos = fetch_github_repos(username)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = []
    for r in repos:
        repo_name = r.get("name")
        save_path = os.path.join(OUTPUT_DIR, f"{repo_name}.json")

        # ✅ Skip repo if JSON already exists
        if os.path.exists(save_path):
            print(f"[SKIP] 💤 '{repo_name}' already analyzed. Skipping...")
            # Optionally, load the data instead of re-fetching
            with open(save_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            results.append(existing_data)
            continue

        # Otherwise analyze normally
        analysis = analyze_repository(username, repo_name)
        results.append(analysis)

        # Save the new analysis
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"[SAVED] 💾 {save_path}")

    return results


if __name__ == "__main__":
    username = input("Enter GitHub username: ").strip()
    all_results = fetch_and_analyze_github(username)
    print(f"\n[INFO] Analysis complete for {len(all_results)} repositories.")
