import streamlit as st
import pandas as pd
from ui.theme import (
    inject_global_styles,
    render_header_banner,
    render_section_card,
    render_sidebar_navigation,
    styled_results_table,
)

def show_lab_results(analysis):
    inject_global_styles()
    render_sidebar_navigation()
    render_header_banner(
        "Lab Results",
        "Review extracted test values with filtering and abnormal highlighting.",
    )

    render_section_card("Lab Result Table", "Filter by all values or only abnormal parameters")

    if not analysis:
        st.info("Upload a medical report to view lab results.")
        return

    df = pd.DataFrame(analysis)

    preferred_columns = ["parameter", "value", "reference", "status", "flag", "unit"]
    display_columns = [col for col in preferred_columns if col in df.columns]

    filter_mode = st.radio(
        "Filter",
        options=["All", "Abnormal only"],
        horizontal=True,
        help="Use this to focus on abnormal findings quickly.",
    )

    table_df = df if filter_mode == "All" else df[df["status"] == "BAD"]

    st.dataframe(styled_results_table(table_df[display_columns]), use_container_width=True, hide_index=True)

    abnormal = df[df["status"] == "BAD"]
    render_section_card("Abnormal Summary", "Parameters requiring attention")

    if len(abnormal) > 0:
        st.dataframe(styled_results_table(abnormal[display_columns]), use_container_width=True, hide_index=True)
    else:
        st.success("No bad parameters detected from available ranges.")


analysis_data = st.session_state.get("analysis", [])
show_lab_results(analysis_data)