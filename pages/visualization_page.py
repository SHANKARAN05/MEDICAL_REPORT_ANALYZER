import streamlit as st
from visualization.dashboard import show_dashboard_charts

def show_visualizations(analysis):

    st.header("📊 Medical Data Visualization")

    if not analysis:
        st.info("Upload a medical report to view visual analytics.")
        return

    show_dashboard_charts(analysis)


analysis_data = st.session_state.get("analysis", [])
show_visualizations(analysis_data)