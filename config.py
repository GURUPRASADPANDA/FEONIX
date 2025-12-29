# config.py
import logging
import warnings
import ccxt
import pytz
from datetime import timedelta

warnings.filterwarnings("ignore")

logging.getLogger("streamlit.runtime.caching").disabled = True
logging.getLogger("streamlit.runtime.scriptrunner_utils").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime.scriptrunner").setLevel(logging.ERROR)

IST = pytz.timezone("Asia/Kolkata")

BINANCE = ccxt.binance({
    "sandbox": False,
    "rateLimit": 1200,
    "enableRateLimit": True,
    "options": {"defaultType": "spot"},
})

SYMBOLS = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT"]
TIMEFRAME = "1m"
LOOKBACK = 150
ALERT_INTERVAL_SECONDS = 60
MONITOR_SLEEP_SECONDS = 5
