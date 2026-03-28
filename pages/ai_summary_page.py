import streamlit as st
from ai_engine.ollama_client import generate_explanation

def show_ai_summary(analysis):

    st.header("🤖 AI Doctor Summary")

    if not analysis:
        st.info("Upload a medical report to generate an AI summary.")
        return

    try:
        explanation = generate_explanation(analysis)
        st.write(explanation)
    except Exception as exc:
        st.error(f"Unable to generate AI summary: {exc}")


analysis_data = st.session_state.get("analysis", [])
show_ai_summary(analysis_data)