import hashlib
import io

import streamlit as st
from analysis.patient_context import extract_patient_context
from document_processing.pdf_reader import extract_text_from_pdf
from document_processing.table_detector import detect_tables
from extraction.parser_controller import parse_report
from analysis.risk_engine import detect_risks

st.set_page_config(page_title="AI Healthcare Analyzer", layout="wide")

st.title("🏥 AI Healthcare Report Analyzer")

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

# Upload
uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=["pdf"],
    key="medical_report_uploader",
)

if uploaded_file:

    file_bytes = uploaded_file.getvalue()
    current_hash = hashlib.md5(file_bytes).hexdigest()
    is_new_report = current_hash != st.session_state["report_hash"]

    st.session_state["report_name"] = uploaded_file.name
    st.session_state["report_size"] = len(file_bytes)

    if is_new_report:

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

        st.success(f"Extracted {len(analysis)} lab entries from report.")
    else:
        st.info("Using previously processed results for this report.")

    st.caption(
        f"Current report: {st.session_state['report_name']} ({st.session_state['report_size']} bytes)"
    )
    context = st.session_state.get("patient_context", {})
    st.caption(
        f"Detected context -> Gender: {context.get('gender') or 'Unknown'}, Age: {context.get('age') or 'Unknown'}"
    )

    preview = st.session_state["analysis"][:10]
    st.subheader("Quick Preview")
    st.dataframe(preview, use_container_width=True)
else:
    if st.session_state["report_name"] and st.session_state["analysis"]:
        st.info(
            "No file selected in uploader. Showing stored results from your last uploaded report."
        )
        st.caption(
            f"Current report: {st.session_state['report_name']} ({st.session_state['report_size']} bytes)"
        )
        context = st.session_state.get("patient_context", {})
        st.caption(
            f"Detected context -> Gender: {context.get('gender') or 'Unknown'}, Age: {context.get('age') or 'Unknown'}"
        )

        preview = st.session_state["analysis"][:10]
        st.subheader("Quick Preview")
        st.dataframe(preview, use_container_width=True)
    else:
        st.info("Upload a medical report, then open any page from the left sidebar.")