# "Which products have anomalous prices compared to their category average?"

import logging
import pandas as pd
from models import PriceSnapshot

logger = logging.getLogger(__name__)

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
    logger.info(
        "Analysis complete — %d products, %d anomalies (%.1f%%)",
        report["total_products"],
        report["anomalies_detected"],
        report["anomaly_rate"],
    )
    return report


def health_check(report: dict, success_rate: float = 100.0) -> dict:
    """Return pipeline health based on success_rate and anomaly_rate."""
    anomaly_rate = report.get("anomaly_rate", 0.0)

    if success_rate <= 80 or anomaly_rate > 5:
        status = "critical"
    elif anomaly_rate >= 2:
        status = "warning"
    else:
        status = "healthy"

    result = {
        "status": status,
        "success_rate": success_rate,
        "anomaly_rate": anomaly_rate,
    }
    logger.info("Health check — status: %s (success_rate=%.1f%%, anomaly_rate=%.1f%%)",
                status, success_rate, anomaly_rate)
    return result


if __name__ == "__main__":
    import asyncio
    import json
    import streamlit as st
    from fetcher import fetch_and_validate, get_mock_snapshots

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    try:
        snapshots = asyncio.run(fetch_and_validate())
        success_rate = 100.0
    except Exception as e:
        logger.error("API unavailable: %s — falling back to mock data", e)
        snapshots = get_mock_snapshots()
        success_rate = 0.0

    report = detect_anomalies(snapshots)
    health = health_check(report, success_rate=success_rate)
    logger.info(json.dumps({"report": report, "health": health}, indent=2, default=str))
