import streamlit as st
import pandas as pd
from ui.theme import (
    calculate_health_metrics,
    inject_global_styles,
    render_header_banner,
    render_metric_card,
    render_section_card,
    render_sidebar_navigation,
    styled_results_table,
)


def show_dashboard(analysis):
    inject_global_styles()
    render_sidebar_navigation()
    render_header_banner(
        "Dashboard",
        "A quick clinical snapshot of health score, risk, and abnormal parameter trends.",
    )

    render_section_card("Patient Health Dashboard", "Key health indicators and abnormal result summary")

    if not analysis:
        st.info("Upload a medical report to view dashboard insights.")
        return

    df = pd.DataFrame(analysis)
    metrics = calculate_health_metrics(df)

    col1, col2, col3 = st.columns(3)
    render_metric_card(col1, "🩺", "Health Score", f"{metrics['health_score']}/100", "Composite score from current panel")
    render_metric_card(col2, "⚠", "Risk Level", metrics["risk_level"], "Derived from score and abnormal distribution")
    render_metric_card(col3, "🧪", "Abnormal Parameters", str(metrics["abnormal_count"]), "Parameters currently outside expected range")

    col4, col5, col6 = st.columns(3)
    col4.metric("Total Tests", len(df))
    col5.metric("Good", len(df[df["status"] == "GOOD"]))
    col6.metric("Unknown", len(df[df["status"] == "UNKNOWN"]))

    render_section_card("Flagged Results", "Parameters marked as BAD based on detected reference range")

    abnormal = df[df["status"] == "BAD"]

    if len(abnormal) > 0:
        st.dataframe(styled_results_table(abnormal), use_container_width=True, hide_index=True)
    else:
        st.success("No bad values detected from available ranges.")


analysis_data = st.session_state.get("analysis", [])
show_dashboard(analysis_data)