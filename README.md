# FEONIX – Crypto Anomaly Detector

**Real-time crypto anomaly detection with Telegram alerts.** Monitors BTC/USDT, ETH/USDT, BNB/USDT, XRP/USDT using Isolation Forest ML model.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)

## Quick Start (5 minutes)

### 1. Clone & Install

git clone git@github.com:GURUPRASADPANDA/FEONIX.git
cd FEONIX
python -m venv venv
source venv/bin/activate # Linux/Mac

venv\Scripts\activate # Windows
pip install -r requirements.txt


### 2. Create Telegram Bot
**Video Guide:** https://youtu.be/l5YDtSLGhqk?si=0Ah5yUBzAj6TvQb4

1. Message [@BotFather](https://t.me/BotFather) → `/newbot`
2. Get `TELEGRAM_TOKEN` 
3. Start your bot → send "hi"
4. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Copy `chat.id` as `TELEGRAM_CHAT_ID`

### 3. Create `.env` (add to `.gitignore`)
TELEGRAM_TOKEN=123456:ABCdef...
TELEGRAM_CHAT_ID=123456789


### 4. **RUN THE APP**
streamlit run app.py

✅ Opens automatically at `http://localhost:8501`

## Dashboard
- **Live/Demo mode** toggle
- **Alert threshold** slider (0.0-0.8)
- **🧪 Test Telegram** button
- Red banners + Telegram alerts for anomalies
- 5s monitoring, 30s refresh

## Sample Alert
🔥 FEONIX ALERT: BTC/USDT
Risk: 0.732
2025-01-01 12:34:56 IST


## Security
- `.env` **never** committed to Git
- Rotate token via [@BotFather](https://t.me/BotFather) if exposed


**Done! Test it for live alerts!**