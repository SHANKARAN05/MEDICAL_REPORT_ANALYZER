import streamlit as st
import pandas as pd

def show_risk_analysis(analysis):

    st.header("⚠ Risk Analysis")

    if not analysis:
        st.info("Upload a medical report to view risk analysis.")
        return

    df = pd.DataFrame(analysis)

    bad = df[df["status"] == "BAD"]
    unknown = df[df["status"] == "UNKNOWN"]

    st.write(f"Detected {len(bad)} bad parameters and {len(unknown)} unknown parameters")

    st.subheader("Bad Parameters")
    if len(bad) > 0:
        st.dataframe(bad, use_container_width=True)
    else:
        st.success("No bad parameters detected.")

    st.subheader("Unknown Parameters (missing usable range)")
    if len(unknown) > 0:
        st.dataframe(unknown, use_container_width=True)
    else:
        st.success("No unknown parameters.")


analysis_data = st.session_state.get("analysis", [])
show_risk_analysis(analysis_data)