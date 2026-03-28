import streamlit as st
import pandas as pd
from ui.theme import (
    inject_global_styles,
    render_header_banner,
    render_section_card,
    render_sidebar_navigation,
    styled_results_table,
)

def show_risk_analysis(analysis):
    inject_global_styles()
    render_sidebar_navigation()
    render_header_banner(
        "Risk Analysis",
        "Prioritize clinical follow-up by reviewing abnormal and uncertain parameters.",
    )

    render_section_card("Risk Overview", "Actionable risk view from extracted report values")

    if not analysis:
        st.info("Upload a medical report to view risk analysis.")
        return

    df = pd.DataFrame(analysis)

    bad = df[df["status"] == "BAD"]
    unknown = df[df["status"] == "UNKNOWN"]

    c1, c2 = st.columns(2)
    c1.metric("Bad Parameters", len(bad))
    c2.metric("Unknown Parameters", len(unknown))

    mode = st.radio("View", ["Bad", "Unknown", "Both"], horizontal=True)

    render_section_card("Bad Parameters", "Values outside expected range")
    if len(bad) > 0:
        if mode in {"Bad", "Both"}:
            st.dataframe(styled_results_table(bad), use_container_width=True, hide_index=True)
    else:
        st.success("No bad parameters detected.")

    render_section_card("Unknown Parameters", "Missing or unusable reference ranges")
    if len(unknown) > 0:
        if mode in {"Unknown", "Both"}:
            st.dataframe(styled_results_table(unknown), use_container_width=True, hide_index=True)
    else:
        st.success("No unknown parameters.")


analysis_data = st.session_state.get("analysis", [])
show_risk_analysis(analysis_data)