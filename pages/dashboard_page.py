import streamlit as st
import pandas as pd


def show_dashboard(analysis):

    st.header("📊 Patient Health Dashboard")

    if not analysis:
        st.info("Upload a medical report to view dashboard insights.")
        return

    df = pd.DataFrame(analysis)

    total_tests = len(df)
    good_tests = len(df[df["status"] == "GOOD"])
    bad_tests = len(df[df["status"] == "BAD"])
    unknown_tests = len(df[df["status"] == "UNKNOWN"])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tests", total_tests)
    col2.metric("Good", good_tests)
    col3.metric("Bad", bad_tests)
    col4.metric("Unknown", unknown_tests)

    st.subheader("⚠ Bad Results")

    abnormal = df[df["status"] == "BAD"]

    if len(abnormal) > 0:
        st.dataframe(abnormal, use_container_width=True)
    else:
        st.success("No bad values detected from available ranges.")


analysis_data = st.session_state.get("analysis", [])
show_dashboard(analysis_data)