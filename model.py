# model.py
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from data_pipeline import fetch_realtime_data, generate_demo_data, engineer_features

model = IsolationForest(contamination=0.08, random_state=42)
is_fitted = False


def detect(symbol, use_demo=False):
    """Run full detection pipeline for one symbol."""
    global model, is_fitted

    df = generate_demo_data(symbol) if use_demo else fetch_realtime_data(symbol)

    if df.empty:
        df["anomaly"] = False
        df["risk_score"] = 0.0
        return df

    df_eng = engineer_features(df)
    features = ["returns", "volatility", "volume_change", "rsi", "bb_position", "momentum", "volume_sma"]
    X = df_eng[features].fillna(0).values

    if len(X) > 15 and not is_fitted:
        model.fit(X)
        is_fitted = True

    if len(X) > 0 and is_fitted:
        preds = model.predict(X)
        scores = model.decision_function(X)
        df["anomaly"] = (
            pd.Series(preds == -1, index=df_eng.index).reindex(df.index, fill_value=False)
        )
        df["risk_score"] = (
            np.abs(pd.Series(scores, index=df_eng.index))
            .reindex(df.index, fill_value=0)
            .fillna(0)
        )
    else:
        df["anomaly"] = False
        df["risk_score"] = 0.0

    return df
