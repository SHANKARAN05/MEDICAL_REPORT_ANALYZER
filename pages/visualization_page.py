import streamlit as st
from visualization.dashboard import show_dashboard_charts

def show_visualizations(analysis):

    st.header("📊 Medical Data Visualization")

    show_dashboard_charts(analysis)