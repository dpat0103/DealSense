from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from sklearn.linear_model import Ridge
import joblib

from sqlalchemy import select
from app.db import SessionLocal
from app.models import Listing

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


from .features import CAT_COLS, NUM_COLS

ARTIFACT_DIR = Path("./backend/artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

def train_from_df(df: pd.DataFrame):
    df = df.copy()

    for c in ["make", "model", "trim", "state"]:
        df[c] = df[c].fillna("unknown").astype(str).str.strip().str.lower()

    for c in ["year", "mileage", "lat", "lon", "price"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=["price", "year", "mileage"])
    df["lat"] = df["lat"].fillna(df["lat"].median() if df["lat"].notna().any() else 0.0)
    df["lon"] = df["lon"].fillna(df["lon"].median() if df["lon"].notna().any() else 0.0)

    X = df[CAT_COLS + NUM_COLS]
    y = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    model = None
    meta = {"model_type": None}

    try:
        from catboost import CatBoostRegressor
        cat_features = [X.columns.get_loc(c) for c in CAT_COLS]
        cb = CatBoostRegressor(
            depth=8,
            learning_rate=0.08,
            loss_function="MAE",
            iterations=1500,
            random_seed=42,
            verbose=False,
        )
        cb.fit(X_train, y_train, cat_features=cat_features)
        preds = cb.predict(X_test)
        mae = float(mean_absolute_error(y_test, preds))
        model = cb
        meta.update({"model_type": "catboost", "mae": mae, "cat_cols": CAT_COLS, "num_cols": NUM_COLS})
    except Exception:
        pre = ColumnTransformer(
        transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
                ("num", "passthrough", NUM_COLS),
            ]
        )

        ridge = Ridge(alpha=1.0, random_state=42)
        pipe = Pipeline([("pre", pre), ("model", ridge)])
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        mae = float(mean_absolute_error(y_test, preds))
        model = pipe
        meta.update({"model_type": "sklearn_hgbr", "mae": mae, "cat_cols": CAT_COLS, "num_cols": NUM_COLS})

    return model, meta

def load_training_data_from_db() -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = db.execute(select(Listing)).scalars().all()
        if not rows:
            raise SystemExit("No listings in DB. Load CSV first (load_csv.py).")

        data = []
        for r in rows:
            data.append({
                "year": r.year,
                "make": r.make,
                "model": r.model,
                "trim": r.trim or "unknown",
                "state": r.state or "unknown",
                "mileage": r.mileage,
                "price": r.price,
                "lat": r.lat,
                "lon": r.lon,
            })
        df = pd.DataFrame(data)
        if "lat" not in df.columns: df["lat"] = None
        if "lon" not in df.columns: df["lon"] = None
        return df
    finally:
        db.close()

def main():
    df = load_training_data_from_db()
    model, meta = train_from_df(df)

    model_path = Path("./backend/artifacts/model.pkl")
    meta_path = Path("./backend/artifacts/meta.json")

    joblib.dump(model, model_path)
    meta_path.write_text(json.dumps(meta, indent=2))

    print("Saved model to:", model_path)
    print("Saved meta to:", meta_path)
    print("MAE:", meta.get("mae"))

if __name__ == "__main__":
    main()