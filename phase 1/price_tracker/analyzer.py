# "Which products have anomalous prices compared to their category average?"

import pandas as pd
from models import PriceSnapshot
import streamlit as st 

def detect_anomalies(snapshots: list[PriceSnapshot]) -> dict:
    df = pd.DataFrame([s.model_dump() for s in snapshots])

    # Calculate per-category statistics directly
    df["category_mean"] = df.groupby("category")["price"].transform("mean")
    df["category_median"] = df.groupby("category")["price"].transform("median")
    df["category_q1"] = df.groupby("category")["price"].transform(
        lambda x: x.quantile(0.25)
    )
    df["category_q3"] = df.groupby("category")["price"].transform(
        lambda x: x.quantile(0.75)
    )
    df["category_iqr"] = df["category_q3"] - df["category_q1"]
    df["lower_fence"] = df["category_q1"] - 1.5 * df["category_iqr"]
    df["upper_fence"] = df["category_q3"] + 1.5 * df["category_iqr"]

    # Flag anomalies
    df["is_anomaly"] = (
        (df["price"] < df["lower_fence"]) |
        (df["price"] > df["upper_fence"])
    )

    anomalies = df[df["is_anomaly"]][[
        "product_id", "title", "price",
        "category", "lower_fence", "upper_fence"
    ]]

    report = {
        "total_products": len(df),
        "anomalies_detected": len(anomalies),
        "anomaly_rate": round(len(anomalies) / len(df) * 100, 1),
        "anomalies": anomalies.to_dict(orient="records"),
        "category_summary": df.groupby("category")["price"].agg(
            mean="mean",
            std="std",
            count="count",
            min="min",
            max="max"
        ).round(2).to_dict(orient="index")
    }
    return report
# USED WHEN GETTING DATA FROM REAL API.

if __name__ == "__main__":
    import asyncio
    from fetcher import fetch_and_validate, get_mock_snapshots
    import json
    
    # snapshots = asyncio.run(fetch_and_validate())
    try:
        snapshots = asyncio.run(fetch_and_validate())
    except Exception as e:
        st.error(f"API unavailable: {e}")
        st.info("Falling back to mock data...")
        snapshots = get_mock_snapshots()
    report = detect_anomalies(snapshots)
    print(json.dumps(report, indent=2, default=str))

