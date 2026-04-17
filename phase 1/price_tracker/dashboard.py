import logging
import streamlit as st
import plotly.express as px
import asyncio
import pandas as pd
from fetcher import get_mock_snapshots
from analyzer import detect_anomalies, health_check

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Price Intelligence Pipeline",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Scope Poppins to your content only — not Streamlit's UI chrome */
.stMarkdown, .stDataFrame, h1, h2, h3, h4, p,
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
.stPlotlyChart {
    font-family: 'Poppins', sans-serif !important;
}

/* Explicitly reset Streamlit's internal UI to system font */
.stDeployButton,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.streamlit-wide,
button,
.stSelectbox,
header {
    font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
}
</style>
""", unsafe_allow_html=True)


st.title("📊 Price Intelligence Pipeline")
st.caption("Real-time price validation and anomaly detection")

# --- Load Data ---
with st.spinner("Fetching and validating products..."):
    snapshots = get_mock_snapshots()
    report = detect_anomalies(snapshots)
    df = pd.DataFrame([s.model_dump() for s in snapshots])
    logger.info("Dashboard loaded %d snapshots", len(snapshots))

# --- Health Status Badge ---
health = health_check(report)

_badge_colors = {
    "healthy":  {"bg": "#1a4731", "border": "#22c55e", "text": "#22c55e", "label": "● Healthy"},
    "warning":  {"bg": "#422006", "border": "#f59e0b", "text": "#f59e0b", "label": "● Warning"},
    "critical": {"bg": "#3b0a0a", "border": "#ef4444", "text": "#ef4444", "label": "● Critical"},
}
_c = _badge_colors[health["status"]]

st.markdown(f"""
<div style="
    display: inline-block;
    background-color: {_c['bg']};
    border: 1px solid {_c['border']};
    border-radius: 8px;
    padding: 10px 20px;
    margin-bottom: 16px;
">
    <span style="color: {_c['text']}; font-size: 1rem; font-weight: 600; font-family: Poppins, sans-serif;">
        {_c['label']}
    </span>
    <span style="color: #aaa; font-size: 0.85rem; margin-left: 12px; font-family: Poppins, sans-serif;">
        Success rate: {health['success_rate']:.0f}% &nbsp;|&nbsp; Anomaly rate: {health['anomaly_rate']:.1f}%
    </span>
</div>
""", unsafe_allow_html=True)

# --- Pipeline Summary ---

st.subheader("Pipeline Summary")

col1, col2, col3, col4 = st.columns(4)

def metric_card(col, label, value):
    col.markdown(f"""
    <div style="
        background-color: #1e1e2e;
        border: 1px solid #2e2e3e;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        margin: 4px;
        transition: transform 0.2s ease;
    ">
        <p style="
            color: #888;
            font-size: 0.85rem;
            margin: 0 0 8px 0;
            font-family: Poppins, sans-serif;
            font-weight: 500;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        ">{label}</p>
        <p style="
            color: #ffffff;
            font-size: 2rem;
            font-weight: 600;
            margin: 0;
            font-family: Poppins, sans-serif;
        ">{value}</p>
    </div>
    """, unsafe_allow_html=True)

metric_card(col1, "Total Products", report["total_products"])
metric_card(col2, "Valid Snapshots", report["total_products"])
metric_card(col3, "Anomalies Detected", report["anomalies_detected"])
metric_card(col4, "Anomaly Rate", f"{report['anomaly_rate']}%")
st.divider()

# --- Price Distribution ---
st.subheader("Price Distribution by Category")
fig = px.box(
    df,
    x="category",
    y="price",
    color="category",
    title="Price spread per category — dots outside box = potential anomalies",
    points="all"
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Anomalies Table ---
st.subheader("🚨 Flagged Anomalies")
if report["anomalies_detected"] > 0:
    anomaly_df = pd.DataFrame(report["anomalies"])
    st.dataframe(
        anomaly_df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No anomalies detected in current dataset")

st.divider()

# --- Category Summary ---
st.subheader("Category Summary")
summary_df = pd.DataFrame(report["category_summary"]).T.reset_index()
summary_df.columns = ["Category", "Mean", "Std", "Count", "Min", "Max"]
st.dataframe(summary_df, use_container_width=True, hide_index=True)
