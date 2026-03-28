import pandas as pd
import plotly.express as px
import streamlit as st
from ui.theme import COLOR_MAP, render_section_card


def show_dashboard_charts(analysis):

    df = pd.DataFrame(analysis)

    if df.empty:
        st.warning("No lab data available for visualization.")
        return

    col1, col2 = st.columns(2)

    df["flag"] = df.get("flag", pd.Series(["UNKNOWN"] * len(df))).fillna("UNKNOWN").str.upper()
    df["status"] = df.get("status", pd.Series(["UNKNOWN"] * len(df))).fillna("UNKNOWN").str.upper()

    with col1:
        render_section_card("Flag Distribution", "LOW/NORMAL/HIGH split across extracted parameters")
        flag_counts = df["flag"].replace({"BAD": "HIGH", "GOOD": "NORMAL"}).value_counts()

        fig = px.pie(
            values=flag_counts.values,
            names=flag_counts.index,
            title="LOW / NORMAL / HIGH Distribution",
            color=flag_counts.index,
            color_discrete_map=COLOR_MAP,
            hole=0.45,
        )

        fig.update_traces(hovertemplate="Flag: %{label}<br>Count: %{value}<extra></extra>")
        fig.update_layout(margin=dict(l=20, r=20, t=55, b=20), legend_title_text="Flag")

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        render_section_card("Abnormal Values", "Parameters currently marked HIGH or LOW")
        abnormal = df[df["flag"].isin(["HIGH", "LOW"])]

        if len(abnormal) > 0:
            fig = px.bar(
                abnormal,
                x="parameter",
                y="value",
                color="flag",
                title="Abnormal Parameter Values",
                color_discrete_map=COLOR_MAP,
                hover_data=["reference", "unit", "status"],
            )

            fig.update_layout(margin=dict(l=20, r=20, t=55, b=20), xaxis_tickangle=-35)
            fig.update_traces(
                hovertemplate="Parameter: %{x}<br>Value: %{y}<br>Flag: %{marker.color}<extra></extra>"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.success("No abnormal values detected.")

    st.divider()
    render_section_card("All Lab Values", "Complete panel overview with status-aware coloring")

    fig = px.bar(
        df,
        x="parameter",
        y="value",
        color="flag",
        title="Patient Lab Values",
        color_discrete_map=COLOR_MAP,
        hover_data=["reference", "unit", "status"],
    )

    fig.update_layout(
        xaxis_tickangle=-40,
        height=520,
        margin=dict(l=20, r=20, t=55, b=20),
        legend_title_text="Flag",
    )

    st.plotly_chart(fig, use_container_width=True)