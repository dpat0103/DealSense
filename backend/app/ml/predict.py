from __future__ import annotations
import json
from pathlib import Path
import joblib
import numpy as np
from .features import to_frame, FeatureRow

MODEL_PATH = Path("./backend/artifacts/model.pkl")
META_PATH = Path("./backend/artifacts/meta.json")

_model = None
_meta = None

def load_model():
    global _model, _meta
    if _model is not None and _meta is not None:
        return _model, _meta

    if not MODEL_PATH.exists() or not META_PATH.exists():
        raise RuntimeError("Model not found. Train it first: python -m backend.app.ml.train")

    _model = joblib.load(MODEL_PATH)
    _meta = json.loads(META_PATH.read_text())
    return _model, _meta

def predict_price(row: FeatureRow) -> float:
    model, meta = load_model()

    df = to_frame([row])
    pred = model.predict(df)[0]
    pred = float(pred)
    return max(500.0, pred)

def top_factors_simple(row: FeatureRow, predicted: float, actual: float) -> list[dict]:
    """
    MVP explainability (no SHAP dependency):
    Create human-readable reasons using heuristics + comparison to expected mileage.
    """
    factors = []


    age = max(0, 2026 - row.year)
    expected_miles = age * 12000
    mile_delta = row.mileage - expected_miles

    if abs(mile_delta) > 15000:
        direction = "negative" if mile_delta > 0 else "positive"
        impact = min(3500.0, abs(mile_delta) * 0.06)
        note = f"Mileage is {'higher' if mile_delta>0 else 'lower'} than typical for a {row.year} vehicle."
        factors.append({"feature": "mileage", "impact": float(impact), "direction": direction, "note": note})

    if age >= 8:
        factors.append({"feature": "year", "impact": 1200.0, "direction": "negative", "note": "Older vehicles generally depreciate faster."})
    elif age <= 3:
        factors.append({"feature": "year", "impact": 900.0, "direction": "positive", "note": "Newer model years typically command higher prices."})

    if row.state and row.state.lower() in {"ca", "ny", "nj", "ma", "wa"}:
        factors.append({"feature": "location", "impact": 700.0, "direction": "positive", "note": "Some regions tend to have higher listing prices."})

    if not factors:
        factors.append({"feature": "market", "impact": 600.0, "direction": "neutral", "note": "Price is driven by local supply/demand for this configuration."})

    factors = sorted(factors, key=lambda x: x["impact"], reverse=True)[:3]
    return factors

def deal_score(actual: float, predicted: float) -> tuple[int, str, float, float]:
    diff = actual - predicted
    diff_pct = diff / predicted if predicted else 0.0

    capped = float(np.clip(diff_pct, -0.25, 0.25))
    score = int(round(50 - (capped / 0.25) * 50))
    score = int(np.clip(score, 0, 100))

    if diff_pct <= -0.10:
        badge = "GREAT"
    elif diff_pct <= 0.08:
        badge = "FAIR"
    else:
        badge = "OVERPRICED"

    return score, badge, diff, diff_pct