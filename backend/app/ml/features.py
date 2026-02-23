from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
import pandas as pd

CAT_COLS = ["make", "model", "trim", "state"]
NUM_COLS = ["year", "mileage", "lat", "lon"]

@dataclass
class FeatureRow:
    year: int
    make: str
    model: str
    trim: Optional[str]
    mileage: int
    state: Optional[str]
    lat: Optional[float]
    lon: Optional[float]

def to_frame(rows: list[FeatureRow]) -> pd.DataFrame:
    data: Dict[str, list[Any]] = {c: [] for c in (CAT_COLS + NUM_COLS)}
    for r in rows:
        data["year"].append(int(r.year))
        data["mileage"].append(int(r.mileage))
        data["lat"].append(None if r.lat is None else float(r.lat))
        data["lon"].append(None if r.lon is None else float(r.lon))
        data["make"].append((r.make or "").strip().lower())
        data["model"].append((r.model or "").strip().lower())
        data["trim"].append((r.trim or "unknown").strip().lower())
        data["state"].append((r.state or "unknown").strip().lower())
    df = pd.DataFrame(data)
    df["lat"] = df["lat"].fillna(df["lat"].median() if df["lat"].notna().any() else 0.0)
    df["lon"] = df["lon"].fillna(df["lon"].median() if df["lon"].notna().any() else 0.0)
    return df