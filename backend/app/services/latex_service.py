from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
TEMPLATES_DIR = os.path.abspath(TEMPLATES_DIR)  # normalize path


env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape([])  # no autoescape for tex
)

def generate_resume_latex(context: dict) -> str:

    template = env.get_template("resume_template.tex.j2")
    return template.render(**context)
