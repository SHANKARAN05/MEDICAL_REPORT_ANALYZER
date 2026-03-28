import hashlib
import io

import pandas as pd
import streamlit as st
from analysis.patient_context import extract_patient_context
from document_processing.pdf_reader import extract_text_from_pdf
from document_processing.table_detector import detect_tables
from extraction.parser_controller import parse_report
from analysis.risk_engine import detect_risks
from ui.theme import (
    inject_global_styles,
    render_header_banner,
    render_sidebar_navigation,
    render_section_card,
    render_soft_alert,
    styled_results_table,
)

st.set_page_config(
    page_title="AI Healthcare Analyzer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()
render_sidebar_navigation()

render_header_banner(
    "AI Healthcare Report Analyzer",
    "Clinical-grade report extraction, risk detection, and visual analytics in one workflow.",
)

if "analysis" not in st.session_state:
    st.session_state["analysis"] = []

if "results" not in st.session_state:
    st.session_state["results"] = []

if "report_hash" not in st.session_state:
    st.session_state["report_hash"] = None

if "report_name" not in st.session_state:
    st.session_state["report_name"] = None

if "report_size" not in st.session_state:
    st.session_state["report_size"] = None

if "patient_context" not in st.session_state:
    st.session_state["patient_context"] = {"gender": None, "age": None}

render_section_card(
    "Report Upload",
    "Upload a PDF medical report to extract values and generate dashboard insights.",
)

uploaded_file = st.file_uploader("Upload Medical Report", type=["pdf"], key="medical_report_uploader")

if uploaded_file:

    file_bytes = uploaded_file.getvalue()
    current_hash = hashlib.md5(file_bytes).hexdigest()
    is_new_report = current_hash != st.session_state["report_hash"]

    st.session_state["report_name"] = uploaded_file.name
    st.session_state["report_size"] = len(file_bytes)

    if is_new_report:
        with st.spinner("Analyzing report... extracting clinical values and calculating risk indicators"):
            pdf_buffer = io.BytesIO(file_bytes)

            text = extract_text_from_pdf(pdf_buffer)
            patient_context = extract_patient_context(text)

            pdf_buffer.seek(0)
            tables = detect_tables(pdf_buffer)

            results = parse_report(text, tables=tables)
            analysis = detect_risks(results, patient_context=patient_context)

            st.session_state["analysis"] = analysis
            st.session_state["results"] = results
            st.session_state["report_hash"] = current_hash
            st.session_state["patient_context"] = patient_context

        render_soft_alert(f"Successfully extracted {len(analysis)} lab entries.", kind="success")
    else:
        render_soft_alert("Using previously processed results for this report.", kind="info")

    col_meta_1, col_meta_2 = st.columns(2)
    with col_meta_1:
        render_section_card(
            "Active Report",
            f"{st.session_state['report_name']} ({st.session_state['report_size']} bytes)",
        )
    with col_meta_2:
        context = st.session_state.get("patient_context", {})
        render_section_card(
            "Patient Context",
            f"Gender: {context.get('gender') or 'Unknown'} | Age: {context.get('age') or 'Unknown'}",
        )

    preview = pd.DataFrame(st.session_state["analysis"][:10])
    render_section_card("Quick Preview", "Top extracted parameters from current report")
    st.dataframe(styled_results_table(preview), use_container_width=True, hide_index=True)
else:
    if st.session_state["report_name"] and st.session_state["analysis"]:
        render_soft_alert(
            "No file selected in uploader. Showing stored results from the most recent report.",
            kind="warning",
        )

        render_section_card(
            "Active Report",
            f"{st.session_state['report_name']} ({st.session_state['report_size']} bytes)",
        )

        context = st.session_state.get("patient_context", {})
        render_section_card(
            "Patient Context",
            f"Gender: {context.get('gender') or 'Unknown'} | Age: {context.get('age') or 'Unknown'}",
        )

        preview = pd.DataFrame(st.session_state["analysis"][:10])
        render_section_card("Quick Preview", "Top extracted parameters from stored report")
        st.dataframe(styled_results_table(preview), use_container_width=True, hide_index=True)
    else:
        render_soft_alert(
            "Upload a medical report, then use the sidebar to open Dashboard, Lab Results, Visualization, Risk Analysis, or AI Summary.",
            kind="info",
        )