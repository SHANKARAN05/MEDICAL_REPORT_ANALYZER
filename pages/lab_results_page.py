import streamlit as st
import pandas as pd

def show_lab_results(analysis):

    st.header("🧪 Lab Results")

    df = pd.DataFrame(analysis)

    st.dataframe(df, use_container_width=True)

    abnormal = df[df["status"] != "NORMAL"]

    st.subheader("⚠ Abnormal Parameters")

    st.dataframe(abnormal, use_container_width=True)