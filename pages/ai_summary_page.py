import streamlit as st
from ai_engine.ollama_client import generate_explanation
from ui.theme import (
    inject_global_styles,
    render_header_banner,
    render_section_card,
    render_sidebar_navigation,
    render_soft_alert,
)

def show_ai_summary(analysis):
    inject_global_styles()
    render_sidebar_navigation()
    render_header_banner(
        "AI Summary",
        "Narrative interpretation of extracted parameters with clinical context.",
    )

    render_section_card("AI Doctor Summary", "Model-generated explanation for current report")

    if not analysis:
        st.info("Upload a medical report to generate an AI summary.")
        return

    try:
        with st.spinner("Generating AI clinical summary..."):
            explanation = generate_explanation(analysis)

        with st.container(border=True):
            st.markdown(explanation)
        render_soft_alert("Summary generated successfully.", kind="success")
    except Exception as exc:
        st.error(f"Unable to generate AI summary: {exc}")


analysis_data = st.session_state.get("analysis", [])
show_ai_summary(analysis_data)