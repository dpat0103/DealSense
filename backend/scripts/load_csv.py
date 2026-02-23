from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.db import SessionLocal, Base, engine
from app.models import Listing


EXPECTED_HEADER = ["id", "price", "year", "mileage", "city", "state", "vin", "make", "model"]


def _clean(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    t = str(s).strip()
    return t if t else None


def _parse_int(s: Optional[str]) -> Optional[int]:
    if s is None:
        return None
    t = str(s).strip()
    if not t:
        return None
    try:
        return int(float(t))
    except Exception:
        return None


def _normalize_state(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    t = s.strip().lower()
    return t if t else None


def _normalize_make_model(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    t = s.strip().lower()
    return t if t else None


def _looks_like_vin(s: str) -> bool:
    # VINs are typically 17 chars, alphanumeric, no I/O/Q (often)
    t = s.strip()
    if len(t) != 17:
        return False
    return t.isalnum()


def _read_rows_robust(csv_path: Path) -> list[dict]:
    rows = []
    bad = 0

    with csv_path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError("CSV is empty.")

        header_norm = [h.strip().lower() for h in header]
        if len(header_norm) < 8:
            raise ValueError(f"Unexpected header: {header}")

        for line_num, tokens in enumerate(reader, start=2):
            if not tokens or all(not t.strip() for t in tokens):
                continue

            tokens = [t.strip() for t in tokens]

            if len(tokens) == 9:
                row = {
                    "source_id": tokens[0],
                    "price": tokens[1],
                    "year": tokens[2],
                    "mileage": tokens[3],
                    "city": tokens[4],
                    "state": tokens[5],
                    "vin": tokens[6],
                    "make": tokens[7],
                    "model": tokens[8],
                }
                rows.append(row)
                continue

          
            if len(tokens) >= 9:
                source_id = tokens[0]
                price = tokens[1] if len(tokens) > 1 else None
                year = tokens[2] if len(tokens) > 2 else None
                mileage = tokens[3] if len(tokens) > 3 else None

                state = tokens[-4] if len(tokens) >= 4 else None
                vin = tokens[-3] if len(tokens) >= 3 else None
                make = tokens[-2] if len(tokens) >= 2 else None
                model = tokens[-1] if len(tokens) >= 1 else None

                city_parts = tokens[4:-4]
                city = ", ".join([p for p in city_parts if p])

                if (state and len(state.strip()) > 3) and not city:
                    if len(tokens) >= 10:
                        city = tokens[4]
                        state = tokens[5]

                row = {
                    "source_id": source_id,
                    "price": price,
                    "year": year,
                    "mileage": mileage,
                    "city": city,
                    "state": state,
                    "vin": vin,
                    "make": make,
                    "model": model,
                }
                rows.append(row)
                continue

            bad += 1

    if not rows:
        raise ValueError("No usable rows parsed from CSV.")

    print(f"Parsed {len(rows)} rows from CSV.")
    if bad:
        print(f"Skipped {bad} badly formatted lines (rare).")

    return rows


def canonicalize_rows(rows: list[dict]) -> pd.DataFrame:
    rebuilt = []
    for r in rows:
        source_id = _clean(r.get("source_id"))
        vin = _clean(r.get("vin"))
        price = _parse_int(r.get("price"))
        year = _parse_int(r.get("year"))
        mileage = _parse_int(r.get("mileage"))

        make = _normalize_make_model(r.get("make"))
        model = _normalize_make_model(r.get("model"))
        city = _clean(r.get("city"))
        state = _normalize_state(r.get("state"))

        if price is None or year is None or mileage is None or not make or not model:
            continue

        if price <= 0 or mileage < 0 or year < 1980 or year > 2026:
            continue

        rebuilt.append(
            {
                "source_id": source_id,
                "vin": vin,
                "price": int(price),
                "year": int(year),
                "mileage": int(mileage),
                "make": make,
                "model": model,
                "trim": "unknown",
                "city": city,
                "state": state,
                "zip": None,
                "lat": None,
                "lon": None,
                "url": None,
                "source": "csv",
            }
        )

    df = pd.DataFrame(rebuilt)
    if df.empty:
        raise ValueError("After cleaning, no valid rows remained. Check your CSV content.")
    print(f"Cleaned to {len(df)} valid rows.")
    return df


def load_into_db(df: pd.DataFrame, db: Session) -> int:
    inserted = 0
    for _, r in df.iterrows():
        l = Listing(
            source_id=r.get("source_id"),
            vin=r.get("vin"),
            source=r.get("source") or "csv",
            url=r.get("url"),

            year=int(r["year"]),
            make=str(r["make"]),
            model=str(r["model"]),
            trim=str(r.get("trim") or "unknown"),
            mileage=int(r["mileage"]),
            price=int(r["price"]),

            city=r.get("city"),
            state=r.get("state"),
            zip=None,
            lat=None,
            lon=None,
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

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    if args.reset:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    else:
        Base.metadata.create_all(bind=engine)

    rows = _read_rows_robust(csv_path)
    df = canonicalize_rows(rows)

    db = SessionLocal()
    try:
        inserted = load_into_db(df, db)
        print(f"Inserted {inserted} listings into SQLite.")
    finally:
        db.close()


if __name__ == "__main__":
    main()