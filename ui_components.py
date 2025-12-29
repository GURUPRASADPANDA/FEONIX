# ui_components.py
from datetime import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from config import IST


def set_feonix_page():
    st.set_page_config(
        page_title="FEONIX - Crypto Anomaly Detector",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .stApp { background-color: #0f0f0f; }
        .main .block-container { padding-top: 2rem; }
        div.element-container .stSpinner { display: none !important; }
        .stMetric > label { color: #00ff88 !important; font-size: 14px; font-weight: 600; }
        .stMetric > div > div { color: #ffffff !important; font-size: 28px; font-weight: 700; }
        .stPlotlyChart {
            border-radius: 12px; border: 1px solid #333; background: #1a1a1a;
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.1);
        }
        .stButton > button {
            background: linear-gradient(90deg, #ff6b35, #f7931e); color: #000;
            border: none; border-radius: 8px; font-weight: 600; height: 42px;
        }
        .stButton > button:hover {
            background: linear-gradient(90deg, #f7931e, #ff6b35);
            box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
        }
        .stSlider > div > div > div > div { background: linear-gradient(90deg, #ff6b35, #ff4444); }
        .stRadio > div > label { color: #ff6b35 !important; }
        h1 {
            color: #ff6b35 !important;
            font-size: 3.2rem !important;
            font-weight: 900 !important;
            text-shadow: 0 0 30px rgba(255, 107, 53, 0.5);
            letter-spacing: 2px;
            background: linear-gradient(45deg, #ff6b35, #f7931e, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .feonix-tagline {
            color: #00ff88 !important;
            font-size: 1.2rem !important;
            font-weight: 400 !important;
            margin-top: -10px;
        }
        .stMarkdown { color: #ffffff !important; }
        .stError {
            background-color: #ff4444 !important; color: white !important;
            border-radius: 8px; padding: 12px; border-left: 5px solid #ff6666;
        }
        .alert-banner {
            background: linear-gradient(90deg, #ff4444, #ff6666);
            color: white; padding: 15px; border-radius: 10px; margin: 10px 0;
            font-weight: 600; text-align: center; box-shadow: 0 4px 15px rgba(255,68,68,0.3);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("# 🔥 FEONIX")
    st.markdown(
        '<p class="feonix-tagline">Real-time Crypto Anomaly Detection | Indian Standard Time</p>',
        unsafe_allow_html=True,
    )


def render_top_status():
    col1, col2 = st.columns([3, 1])
    col1.metric("FEONIX Status", f"Live - {datetime.now(IST).strftime('%H:%M:%S IST')}")
    if col2.button("Force Refresh", type="primary"):
        st.cache_data.clear()
        st.rerun()


def render_alert_banner(symbol, score):
    st.markdown(
        f"""
        <div class="alert-banner">
            🔥 FEONIX LIVE ALERT: {symbol} | Risk: {score:.3f} | {datetime.now(IST).strftime('%H:%M:%S IST')}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_symbol_chart(symbol, df, threshold):
    st.markdown(f"### {symbol}")

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.7, 0.3],
        subplot_titles=(f"{symbol} Price", "FEONIX Risk Score"),
        vertical_spacing=0.08,
    )

    fig.add_trace(
        go.Candlestick(
            x=df["timestamp"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            increasing_line_color="#00ff88",
            decreasing_line_color="#ff4444",
        ),
        row=1,
        col=1,
    )

    anomalies = df[df["anomaly"]]
    if not anomalies.empty:
        fig.add_trace(
            go.Scatter(
                x=anomalies["timestamp"],
                y=anomalies["high"] * 1.01,
                mode="markers",
                marker=dict(
                    color="#ff6b35",
                    size=14,
                    symbol="diamond",
                    line=dict(width=2, color="white"),
                ),
                hovertemplate="<b>FEONIX ALERT</b><br>Risk: %{customdata:.3f}<extra></extra>",
                customdata=anomalies["risk_score"],
            ),
            row=1,
            col=1,
        )

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["risk_score"],
            mode="lines",
            line=dict(color="#ff6b35", width=3),
        ),
        row=2,
        col=1,
    )

    fig.add_hline(y=threshold, line_dash="dash", line_color="#ff4444", row=2, col=1)

    fig.update_layout(
        height=520,
        showlegend=False,
        plot_bgcolor="#1a1a1a",
        paper_bgcolor="#1a1a1a",
        font_color="#ffffff",
        xaxis_rangeslider_visible=False,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#333", color="#ff6b35")
    fig.update_yaxes(showgrid=True, gridcolor="#333", color="#ff6b35")

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("")
