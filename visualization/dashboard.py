import pandas as pd
import plotly.express as px
import streamlit as st


def show_dashboard_charts(analysis):

    df = pd.DataFrame(analysis)

    if df.empty:
        st.warning("No lab data available for visualization.")
        return

    col1, col2 = st.columns(2)

    # Chart 1 — Status Distribution
    with col1:

        st.subheader("Lab Result Distribution")

        status_counts = df["status"].value_counts()

        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Good vs Bad Results",
            color=status_counts.index,
            color_discrete_map={
                "GOOD": "green",
                "BAD": "red",
                "UNKNOWN": "gray"
            }
        )

        st.plotly_chart(fig, use_container_width=True)


    # Chart 2 — Abnormal Results
    with col2:

        st.subheader("Abnormal Parameters")

        abnormal = df[df["status"] == "BAD"]

        if len(abnormal) > 0:

            color_col = "flag" if "flag" in abnormal.columns else "status"

            fig = px.bar(
                abnormal,
                x="parameter",
                y="value",
                color=color_col,
                title="Bad Lab Values",
                color_discrete_map={
                    "LOW": "blue",
                    "HIGH": "red",
                    "BAD": "red"
                }
            )

            fig.update_layout(
                xaxis_tickangle=-45
            )

            st.plotly_chart(fig, use_container_width=True)

        else:

            st.success("No abnormal values detected.")


    st.divider()


    # Chart 3 — All Lab Values
    st.subheader("All Lab Values Overview")

    fig = px.bar(
        df,
        x="parameter",
        y="value",
        color="status",
        title="Patient Lab Values",
        color_discrete_map={
            "GOOD": "green",
            "BAD": "red",
            "UNKNOWN": "gray"
        }
    )

    fig.update_layout(
        xaxis_tickangle=-60,
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)