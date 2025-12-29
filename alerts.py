# alerts.py
import os
import time
import threading
from datetime import datetime
from queue import Queue

import requests

from config import IST, SYMBOLS, ALERT_INTERVAL_SECONDS, MONITOR_SLEEP_SECONDS
from model import detect

import streamlit as st



alert_queue = Queue()
_FEONIX_MONITOR_ACTIVE = True


def send_telegram_alert_sync(symbol, score):
    token = st.secrets.get("TELEGRAM_TOKEN", "")
    chat_id = st.secrets.get("TELEGRAM_CHAT_ID", "")

    print("FEONIX DEBUG TOKEN:", repr(token))
    print("FEONIX DEBUG CHAT:", repr(chat_id))

    if not token or not chat_id:
        print("❌ MISSING TELEGRAM_TOKEN or TELEGRAM_CHAT_ID in .env")
        return False

    token = token.strip()
    chat_id = chat_id.strip()

    message = (
        f"🔥 FEONIX ALERT: {symbol}\n"
        f"Risk: {score:.3f}\n"
        f"{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(url, data={"chat_id": chat_id, "text": message})
        print("FEONIX TELEGRAM STATUS:", resp.status_code)
        print("FEONIX TELEGRAM BODY:", resp.text)
        if resp.status_code == 200:
            print(f"✅ FEONIX TELEGRAM SENT: {symbol} {score:.3f}")
            return True
        return False
    except Exception as e:
        print(f"❌ FEONIX TELEGRAM ERROR: {e}")
        return False


def safe_queue_process(session_state_active_alerts):
    processed = 0
    debug_count = alert_queue.qsize()
    if debug_count > 0:
        print(f"🔄 FEONIX: Processing {debug_count} queued alerts")

    while not alert_queue.empty():
        try:
            symbol, score = alert_queue.get_nowait()
            print(f"📤 FEONIX: Sending queued alert {symbol} {score:.3f}")
            if send_telegram_alert_sync(symbol, score):
                processed += 1
                session_state_active_alerts[symbol] = {
                    "score": score,
                    "time": datetime.now(IST),
                }
        except Exception as e:
            print(f"❌ Queue process error: {e}")
            break

    if processed > 0:
        print(f"✅ FEONIX: Processed {processed} alerts")
    return processed


def feonix_monitor():
    """Background monitoring loop, no Streamlit calls here."""
    last_alert_time = {}
    while _FEONIX_MONITOR_ACTIVE:
        try:
            for symbol in SYMBOLS:
                df = detect(symbol, use_demo=False)
                if df.empty:
                    continue

                high_risk = df[df["risk_score"] > 0.4]
                if not high_risk.empty:
                    score = high_risk["risk_score"].max()
                    now = time.time()
                    if (symbol not in last_alert_time or
                            now - last_alert_time.get(symbol, 0) > ALERT_INTERVAL_SECONDS):
                        last_alert_time[symbol] = now
                        alert_queue.put((symbol, score))
            time.sleep(MONITOR_SLEEP_SECONDS)
        except Exception:
            time.sleep(MONITOR_SLEEP_SECONDS)


def start_monitor_thread():
    if "_FEONIX_MONITOR_STARTED" not in globals():
        monitor_thread = threading.Thread(target=feonix_monitor, daemon=True)
        monitor_thread.start()
        globals()["_FEONIX_MONITOR_STARTED"] = True
