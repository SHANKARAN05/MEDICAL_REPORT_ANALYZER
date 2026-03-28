import streamlit as st
import pandas as pd

def show_lab_results(analysis):

    st.header("🧪 Lab Results")

    if not analysis:
        st.info("Upload a medical report to view lab results.")
        return

    df = pd.DataFrame(analysis)

    preferred_columns = ["parameter", "value", "reference", "status", "flag", "unit"]
    display_columns = [col for col in preferred_columns if col in df.columns]

    st.dataframe(df[display_columns], use_container_width=True)

    abnormal = df[df["status"] == "BAD"]

    st.subheader("⚠ Bad Parameters")

    if len(abnormal) > 0:
        st.dataframe(abnormal[display_columns], use_container_width=True)
    else:
        st.success("No bad parameters detected from available ranges.")


analysis_data = st.session_state.get("analysis", [])
show_lab_results(analysis_data)