import streamlit as st
from visualization.dashboard import show_dashboard_charts
from ui.theme import (
    inject_global_styles,
    render_header_banner,
    render_section_card,
    render_sidebar_navigation,
)

def show_visualizations(analysis):
    inject_global_styles()
    render_sidebar_navigation()
    render_header_banner(
        "Visualization",
        "Interactive charts for status distribution and parameter-level trends.",
    )

    render_section_card("Clinical Visual Analytics", "Chart palette: LOW blue, NORMAL green, HIGH red")

    if not analysis:
        st.info("Upload a medical report to view visual analytics.")
        return

    show_dashboard_charts(analysis)


analysis_data = st.session_state.get("analysis", [])
show_visualizations(analysis_data)