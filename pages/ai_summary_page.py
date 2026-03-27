import streamlit as st
from ai_engine.ollama_client import generate_explanation

def show_ai_summary(analysis):

    st.header("🤖 AI Doctor Summary")

    explanation = generate_explanation(analysis)

    st.write(explanation)