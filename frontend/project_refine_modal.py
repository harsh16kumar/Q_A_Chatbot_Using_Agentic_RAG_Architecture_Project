# frontend/project_refine_modal.py

import os, sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from streamlit_modal import Modal
from backend.app.services.llm_service import refine_project

def show_refine_modal(project, idx):
    """Floating modal to refine a single project via LLM."""
    modal = Modal(
        key=f"refine_modal_{idx}",
        title=f"🧠 Refine Project — {project.get('title','Untitled')}",
        max_width=700
    )

    with modal.container():
        st.markdown(f"**Current Summary:**")
        st.markdown("---")
        st.markdown(f"**{project.get('title','Untitled')}**")
        if project.get("features"):
            for feat in project["features"]:
                st.markdown(f"- {feat}")

        st.markdown("---")
        user_msg = st.text_area("Describe what changes you'd like", key=f"refine_input_{idx}")

        if st.button("Refine Now", key=f"refine_btn_{idx}"):
            with st.spinner("Talking to LLM..."):
                refined = refine_project(project, user_msg)
                st.session_state["project_tiles"][idx] = refined
                st.success("✅ Project refined successfully!")
                st.session_state[f"refine_open_{idx}"] = False
                st.rerun()
