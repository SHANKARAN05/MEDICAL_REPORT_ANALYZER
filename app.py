import streamlit as st
from document_processing.pdf_reader import extract_text_from_pdf
from extraction.parser_controller import parse_report
from analysis.risk_engine import detect_risks

from pages.dashboard_page import show_dashboard
from pages.lab_results_page import show_lab_results
from pages.visualization_page import show_visualizations
from pages.risk_analysis_page import show_risk_analysis
from pages.ai_summary_page import show_ai_summary

st.set_page_config(page_title="AI Healthcare Analyzer", layout="wide")

st.title("🏥 AI Healthcare Report Analyzer")

# Upload
uploaded_file = st.file_uploader("Upload Medical Report", type=["pdf"])

if uploaded_file:

    text = extract_text_from_pdf(uploaded_file)

    results = parse_report(text)

    analysis = detect_risks(results)

    st.session_state["analysis"] = analysis
    st.session_state["results"] = results

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Lab Results",
        "Visual Analytics",
        "Risk Analysis",
        "AI Doctor Summary"
    ]
)

if "analysis" in st.session_state:

    if page == "Dashboard":
        show_dashboard(st.session_state["analysis"])

    elif page == "Lab Results":
        show_lab_results(st.session_state["analysis"])

    elif page == "Visual Analytics":
        show_visualizations(st.session_state["analysis"])

    elif page == "Risk Analysis":
        show_risk_analysis(st.session_state["analysis"])

    elif page == "AI Doctor Summary":
        show_ai_summary(st.session_state["analysis"])

else:
    st.info("Upload a medical report to begin analysis.")