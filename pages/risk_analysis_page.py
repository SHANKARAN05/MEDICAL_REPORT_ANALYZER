import streamlit as st
import pandas as pd

def show_risk_analysis(analysis):

    st.header("⚠ Risk Analysis")

    df = pd.DataFrame(analysis)

    abnormal = df[df["status"] != "NORMAL"]

    st.write(f"Detected {len(abnormal)} abnormal parameters")

    st.dataframe(abnormal)