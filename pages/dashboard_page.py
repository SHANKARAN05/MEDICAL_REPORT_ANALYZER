import streamlit as st
import pandas as pd


def show_dashboard(analysis):

    st.header("📊 Patient Health Dashboard")

    df = pd.DataFrame(analysis)

    total_tests = len(df)
    abnormal_tests = len(df[df["status"] != "NORMAL"])
    normal_tests = len(df[df["status"] == "NORMAL"])

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Tests", total_tests)
    col2.metric("Normal", normal_tests)
    col3.metric("Abnormal", abnormal_tests)

    st.subheader("⚠ Abnormal Results")

    abnormal = df[df["status"] != "NORMAL"]

    if len(abnormal) > 0:
        st.dataframe(abnormal, use_container_width=True)
    else:
        st.success("All lab values are normal.")