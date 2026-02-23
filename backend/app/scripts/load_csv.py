from __future__ import annotations
import argparse
import pandas as pd
from sqlalchemy.orm import Session

from backend.app.db import SessionLocal, Base, engine
from backend.app.models import Listing
from backend.app.utils.geo import zip_to_latlon

def canonicalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})

    needed = {"year", "make", "model", "mileage", "price"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    for col in ["trim", "city", "state", "zip", "lat", "lon", "url", "source"]:
        if col not in df.columns:
            df[col] = None

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["mileage"] = pd.to_numeric(df["mileage"], errors="coerce").astype("Int64")
    df["price"] = pd.to_numeric(df["price"], errors="coerce").astype("Int64")

    for c in ["make", "model", "trim", "city", "state"]:
        df[c] = df[c].fillna("").astype(str).str.strip()
    df["make"] = df["make"].str.lower()
    df["model"] = df["model"].str.lower()
    df["trim"] = df["trim"].replace("", "unknown").str.lower()
    df["state"] = df["state"].replace("", "unknown").str.lower()

    df = df.dropna(subset=["year", "mileage", "price"])
    return df

def load_into_db(df: pd.DataFrame, db: Session):
    inserted = 0
    for _, r in df.iterrows():
        lat = r["lat"]
        lon = r["lon"]
        if (pd.isna(lat) or pd.isna(lon)) and r.get("zip"):
            zlat, zlon = zip_to_latlon(str(r["zip"]))
            lat = zlat
            lon = zlon

        l = Listing(
            source=r.get("source") or "csv",
            url=r.get("url") or None,
            year=int(r["year"]),
            make=str(r["make"]),
            model=str(r["model"]),
            trim=str(r.get("trim") or "unknown"),
            mileage=int(r["mileage"]),
            price=int(r["price"]),
            city=(r.get("city") or None),
            state=(r.get("state") or None),
            zip=(str(r.get("zip")) if r.get("zip") is not None and str(r.get("zip")).strip() != "" else None),
            lat=(None if pd.isna(lat) else float(lat)),
            lon=(None if pd.isna(lon) else float(lon)),
        )
        db.add(l)
        inserted += 1

    db.commit()
    return inserted

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to listings CSV")
    parser.add_argument("--reset", action="store_true", help="Drop & recreate tables first")
    args = parser.parse_args()

    if args.reset:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    else:
        Base.metadata.create_all(bind=engine)

    df = pd.read_csv(args.csv)
    df = canonicalize(df)

    db = SessionLocal()
    try:
        inserted = load_into_db(df, db)
        print(f"Inserted {inserted} listings.")
    finally:
        db.close()

if __name__ == "__main__":
    main()