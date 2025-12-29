# data_pipeline.py
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from config import BINANCE, IST, LOOKBACK, TIMEFRAME


def fetch_realtime_data(symbol):
    """Fetch real-time OHLCV from Binance, fallback to demo."""
    try:
        since = int((datetime.now(IST) - timedelta(minutes=LOOKBACK)).timestamp() * 1000)
        ohlcv = BINANCE.fetch_ohlcv(symbol, TIMEFRAME, since=since, limit=LOOKBACK)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = (
            pd.to_datetime(df["timestamp"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(IST)
        )
        return df.sort_values("timestamp").tail(LOOKBACK).reset_index(drop=True)
    except Exception:
        return generate_demo_data(symbol)


def generate_demo_data(symbol):
    """Generate synthetic OHLCV with occasional spikes."""
    np.random.seed(int(time.time()) % 100)
    timestamps = pd.date_range(end=datetime.now(IST), periods=LOOKBACK, freq="1T")

    if "BTC" in symbol:
        base_price = 65000
    elif "ETH" in symbol:
        base_price = 3200
    elif "BNB" in symbol:
        base_price = 320
    else:
        base_price = 0.6

    prices = [base_price]
    for _ in range(1, LOOKBACK):
        change = np.random.normal(0, 0.0015)
        prices.append(prices[-1] * (1 + change))

    df = pd.DataFrame({
        "timestamp": timestamps,
        "open": prices,
        "high": [p * (1 + abs(np.random.normal(0, 0.0008))) for p in prices],
        "low": [p * (1 - abs(np.random.normal(0, 0.0008))) for p in prices],
        "close": prices,
        "volume": np.random.randint(500, 80000, LOOKBACK) * np.random.uniform(0.5, 2, LOOKBACK),
    })

    current_min = datetime.now(IST).minute % LOOKBACK
    for pos in [(current_min - 3) % LOOKBACK, (current_min - 15) % LOOKBACK]:
        if 0 <= pos < len(df):
            if pos % 2 == 0:
                df.loc[pos, "close"] *= 0.93
                df.loc[pos, "low"] *= 0.90
            else:
                df.loc[pos, "close"] *= 1.08
                df.loc[pos, "high"] *= 1.13
            df.loc[pos, "volume"] *= 7

    return df


def rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def bb_position(prices):
    bb_upper = prices.rolling(20).mean() + 2 * prices.rolling(20).std()
    bb_lower = prices.rolling(20).mean() - 2 * prices.rolling(20).std()
    return (prices - bb_lower) / (bb_upper - bb_lower)


def engineer_features(df):
    df = df.copy()
    df["returns"] = df["close"].pct_change()
    df["volatility"] = df["returns"].rolling(8).std()
    df["volume_change"] = df["volume"].pct_change()
    df["rsi"] = rsi(df["close"])
    df["bb_position"] = bb_position(df["close"])
    df["momentum"] = df["close"].pct_change(3)
    df["volume_sma"] = df["volume"] / df["volume"].rolling(20).mean()
    return df.dropna()
