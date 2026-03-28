import pandas as pd
import streamlit as st


COLOR_MAP = {
    "LOW": "#1d4ed8",
    "NORMAL": "#16a34a",
    "HIGH": "#dc2626",
    "UNKNOWN": "#6b7280",
}


def inject_global_styles():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

            :root {
                --primary: #0b5ed7;
                --primary-soft: #dbeafe;
                --success: #16a34a;
                --danger: #dc2626;
                --warning: #ca8a04;
                --text-main: #0f172a;
                --text-muted: #475569;
                --surface: #ffffff;
                --surface-soft: #f8fbff;
                --border: #e2e8f0;
                --shadow: 0 10px 30px rgba(11, 94, 215, 0.08);
                --radius: 16px;
            }

            .stApp {
                font-family: 'Manrope', sans-serif;
                background: radial-gradient(circle at 8% 8%, #eff6ff 0%, #ffffff 45%) fixed;
                color: var(--text-main);
            }

            .block-container {
                max-width: 1200px;
                padding-top: 1.5rem;
                padding-bottom: 2rem;
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #f8fbff 0%, #eef5ff 100%);
                border-right: 1px solid var(--border);
            }

            [data-testid="stSidebar"] * {
                font-family: 'Manrope', sans-serif !important;
            }

            [data-testid="stSidebar"] .stMarkdown,
            [data-testid="stSidebar"] .stMarkdown p,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] a,
            [data-testid="stSidebar"] span {
                color: #0f172a !important;
                opacity: 1 !important;
            }

            [data-testid="stSidebarNav"] a {
                border-radius: 10px;
                margin-bottom: 0.2rem;
            }

            [data-testid="stSidebarNav"] a:hover {
                background: #e2ecff;
            }

            .hero-banner {
                background: linear-gradient(135deg, #0b5ed7 0%, #0ea5e9 100%);
                border-radius: 18px;
                padding: 1.35rem 1.5rem;
                color: white;
                box-shadow: var(--shadow);
                margin-bottom: 1rem;
            }

            .hero-title {
                font-size: 1.5rem;
                font-weight: 800;
                letter-spacing: 0.2px;
                margin: 0;
            }

            .hero-subtitle {
                margin: 0.35rem 0 0;
                opacity: 0.94;
                font-size: 0.95rem;
            }

            .section-card {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: var(--radius);
                padding: 1rem 1.1rem;
                box-shadow: var(--shadow);
                margin-bottom: 0.9rem;
            }

            .metric-card {
                background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
                border: 1px solid var(--border);
                border-radius: var(--radius);
                box-shadow: var(--shadow);
                padding: 0.9rem 1rem;
                min-height: 112px;
            }

            .metric-label {
                color: var(--text-muted);
                font-size: 0.8rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                margin: 0;
            }

            .metric-value {
                font-size: 1.65rem;
                margin: 0.2rem 0 0;
                font-weight: 800;
                line-height: 1.1;
                color: var(--text-main);
            }

            .metric-help {
                color: var(--text-muted);
                font-size: 0.84rem;
                margin-top: 0.15rem;
            }

            .status-pill {
                display: inline-block;
                padding: 0.2rem 0.6rem;
                border-radius: 999px;
                font-size: 0.73rem;
                font-weight: 700;
                letter-spacing: 0.03em;
            }

            .status-low { background: #dbeafe; color: #1d4ed8; }
            .status-normal { background: #dcfce7; color: #166534; }
            .status-high { background: #fee2e2; color: #991b1b; }
            .status-unknown { background: #f1f5f9; color: #475569; }

            .soft-alert {
                border-radius: 12px;
                padding: 0.75rem 0.9rem;
                border: 1px solid var(--border);
                background: #f8fbff;
                color: var(--text-main);
                font-size: 0.9rem;
            }

            .soft-alert.warning { background: #fff7ed; border-color: #fed7aa; color: #9a3412; }
            .soft-alert.success { background: #ecfdf3; border-color: #bbf7d0; color: #166534; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header_banner(title, subtitle):
    st.markdown(
        f"""
        <div class=\"hero-banner\"> 
            <p class=\"hero-title\">{title}</p>
            <p class=\"hero-subtitle\">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_navigation():
    with st.sidebar:
        st.markdown("### Navigation")
        st.page_link("app.py", label="Home", icon="🏥")
        st.page_link("pages/dashboard_page.py", label="Dashboard", icon="📊")
        st.page_link("pages/lab_results_page.py", label="Lab Results", icon="🧪")
        st.page_link("pages/visualization_page.py", label="Visualization", icon="📈")
        st.page_link("pages/risk_analysis_page.py", label="Risk Analysis", icon="⚠")
        st.page_link("pages/ai_summary_page.py", label="AI Summary", icon="🤖")


def render_metric_card(column, icon, label, value, help_text):
    column.markdown(
        f"""
        <div class=\"metric-card\">
            <p class=\"metric-label\">{icon} {label}</p>
            <p class=\"metric-value\">{value}</p>
            <p class=\"metric-help\">{help_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_pill(level):
    value = str(level or "UNKNOWN").upper()
    class_name = {
        "LOW": "status-low",
        "NORMAL": "status-normal",
        "HIGH": "status-high",
    }.get(value, "status-unknown")

    st.markdown(
        f"<span class=\"status-pill {class_name}\">{value}</span>",
        unsafe_allow_html=True,
    )


def calculate_health_metrics(df):
    if df.empty:
        return {"health_score": 0, "risk_level": "Unknown", "abnormal_count": 0}

    penalty = 0
    for _, row in df.iterrows():
        flag = str(row.get("flag") or "UNKNOWN").upper()
        status = str(row.get("status") or "UNKNOWN").upper()

        if flag == "HIGH":
            penalty += 8
        elif flag == "LOW":
            penalty += 6
        elif status == "BAD":
            penalty += 6
        elif status == "UNKNOWN":
            penalty += 2

    score = max(0, 100 - penalty)

    if score >= 85:
        level = "Low"
    elif score >= 65:
        level = "Moderate"
    elif score >= 40:
        level = "High"
    else:
        level = "Critical"

    abnormal_count = int((df.get("status", pd.Series(dtype=str)).str.upper() == "BAD").sum())

    return {
        "health_score": score,
        "risk_level": level,
        "abnormal_count": abnormal_count,
    }


def render_section_card(title, subtitle=""):
    st.markdown(
        f"""
        <div class=\"section-card\">
            <h4 style=\"margin:0;color:#0f172a;\">{title}</h4>
            <p style=\"margin:0.35rem 0 0;color:#475569;font-size:0.9rem;\">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def styled_results_table(df):
    if df is None:
        return pd.DataFrame()

    if isinstance(df, list):
        df = pd.DataFrame(df)
    elif not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    if df.empty:
        return df

    def row_style(row):
        status = str(row.get("status") or "").upper()
        if status == "BAD":
            return ["background-color: #fff1f2; color: #7f1d1d;"] * len(row)
        if status == "GOOD":
            return ["background-color: #f0fdf4; color: #14532d;"] * len(row)
        return [""] * len(row)

    return df.style.apply(row_style, axis=1)


def render_soft_alert(message, kind="info"):
    safe_kind = kind if kind in {"info", "warning", "success"} else "info"
    class_name = "soft-alert" if safe_kind == "info" else f"soft-alert {safe_kind}"
    st.markdown(f"<div class=\"{class_name}\">{message}</div>", unsafe_allow_html=True)
