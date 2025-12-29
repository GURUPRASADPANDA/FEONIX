# app.py
import os
import time

import nest_asyncio
import streamlit as st
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

from alerts import (
    alert_queue,
    safe_queue_process,
    send_telegram_alert_sync,
    start_monitor_thread,
)
from config import IST, SYMBOLS
from model import detect
from ui_components import (
    set_feonix_page,
    render_top_status,
    render_alert_banner,
    render_symbol_chart,
)

nest_asyncio.apply()
load_dotenv()

set_feonix_page()

if "latest_results" not in st.session_state:
    st.session_state.latest_results = {}
if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = {}
if "active_alerts" not in st.session_state:
    st.session_state.active_alerts = {}

start_monitor_thread()

st_autorefresh(interval=30 * 1000, key="feonix_refresh")

render_top_status()

with st.sidebar:
    st.markdown("## ⚙️ FEONIX Configuration")
    mode = st.radio("Display Mode:", ["Live Market Data", "Demo Mode"])
    use_demo = mode == "Demo Mode"

    selected_symbols = st.multiselect("Symbols:", SYMBOLS, default=SYMBOLS)
    threshold = st.slider("Alert Threshold:", 0.0, 0.8, 0.4)

    st.markdown("---")
    st.success("🔥 FEONIX real-time monitoring: Active (5s intervals)")

    if st.button("🧪 Test FEONIX Telegram"):
        success = send_telegram_alert_sync("FEONIX/TEST", 0.85)
        st.success("✅ FEONIX Test sent!" if success else "❌ Test failed - check terminal")
        safe_queue_process(st.session_state.active_alerts)
        st.rerun()

    queue_size = alert_queue.qsize()
    colA, colB = st.columns(2)
    colA.metric("Alert Queue", queue_size)
    if queue_size > 0:
        colB.error(f"⏳ {queue_size} alerts waiting...")
        safe_queue_process(st.session_state.active_alerts)

portfolio_risk = 0
results = {}
live_alerts_count = len(st.session_state.active_alerts)

for symbol in selected_symbols:
    df = detect(symbol, use_demo=use_demo)
    if df.empty:
        continue
    results[symbol] = df

    high_risk = df[df["risk_score"] > threshold]
    if not high_risk.empty:
        max_score = high_risk["risk_score"].max()
        portfolio_risk += max_score * 0.3

        now = time.time()
        if (symbol not in st.session_state.last_alert_time or
                now - st.session_state.last_alert_time.get(symbol, 0) > 60):
            st.session_state.last_alert_time[symbol] = now
            print(f"🚨 FEONIX: DIRECT SCREEN ALERT → TELEGRAM for {symbol} {max_score:.3f}")
            send_telegram_alert_sync(symbol, max_score)

        render_alert_banner(symbol, max_score)
    else:
        portfolio_risk += df["risk_score"].tail(10).mean() * 0.1

col1, col2, col3, col4 = st.columns(4)
col1.metric("FEONIX Portfolio Risk", f"{portfolio_risk:.3f}")
col2.metric("FEONIX Live Anomalies", live_alerts_count)
col3.metric("Check Rate", "5 seconds")
col4.metric("Visual Refresh", "30 seconds")

st.markdown("## 📊 FEONIX Real-time Analysis")
for symbol, df in results.items():
    render_symbol_chart(symbol, df, threshold)

st.markdown("---")
st.markdown("*🔥 FEONIX - 5s anomaly detection | 30s visual refresh | © 2025*")
