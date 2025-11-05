# frontend/project_display.py
import streamlit as st
from project_refine_modal import show_refine_modal
import os, sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app.services.llm_service import summarize_project

def show_project_display(projects):
    """Display all summarized projects with per-project refinement modals."""

    # Summarize all projects via LLM if not already done
    if "project_tiles" not in st.session_state:
        st.session_state["project_tiles"] = [summarize_project(p) for p in projects]

    st.subheader("AI-Generated Project Summaries")
    updated_tiles = []

    for i, proj in enumerate(st.session_state["project_tiles"]):
        with st.container(border=True):
            st.markdown(f"### {proj['title']} | {', '.join(proj.get('technologies', []))}")
            features = proj.get("features", [])
            if features:
                for f in features:
                    st.markdown(f"- {f}")
            else:
                st.info("⚠️ No features detected.")

            # Selection
            proj["selected"] = st.checkbox("Select this project", key=f"select_proj_{i}", value=proj.get("selected", False))

            # Refine modal open trigger
            if st.button("Refine", key=f"refine_button_{i}"):
                st.session_state[f"refine_open_{i}"] = True

            # If modal is open for this project
            if st.session_state.get(f"refine_open_{i}", False):
                show_refine_modal(proj, i)

            updated_tiles.append(proj)

    st.session_state["project_tiles"] = updated_tiles
    st.session_state["projects"] = [p for p in updated_tiles if p.get("selected")]
