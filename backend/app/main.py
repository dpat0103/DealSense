from __future__ import annotations
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from . import crud, schemas
from .ml.features import FeatureRow
from .ml.predict import predict_price, deal_score, top_factors_simple

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Car Deal Analyzer MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/search", response_model=schemas.SearchResponse)
def search(
    make: str | None = None,
    model: str | None = None,
    state: str | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    mileage_max: int | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    listings = crud.search_listings(
        db=db,
        make=make,
        model=model,
        state=state,
        year_min=year_min,
        year_max=year_max,
        mileage_max=mileage_max,
        limit=limit,
    )

    results = []
    for l in listings:
        row = FeatureRow(
            year=l.year,
            make=l.make,
            model=l.model,
            trim=l.trim,
            mileage=l.mileage,
            state=l.state,
            lat=l.lat,
            lon=l.lon,
        )
        pred = predict_price(row)
        score, badge, diff, diff_pct = deal_score(float(l.price), float(pred))

        results.append(
            schemas.SearchResultItem(
                listing=schemas.ListingOut.model_validate(l),
                predicted_price=pred,
                diff=float(diff),
                diff_pct=float(diff_pct),
                deal_score=score,
                badge=badge,
            )
        )

    results.sort(key=lambda x: x.deal_score, reverse=True)
    return schemas.SearchResponse(results=results)

@app.get("/listing/{listing_id}", response_model=schemas.ListingDetailResponse)
def listing_detail(listing_id: int, db: Session = Depends(get_db)):
    l = crud.get_listing(db, listing_id)
    if not l:
        raise HTTPException(status_code=404, detail="Listing not found")

    row = FeatureRow(
        year=l.year,
        make=l.make,
        model=l.model,
        trim=l.trim,
        mileage=l.mileage,
        state=l.state,
        lat=l.lat,
        lon=l.lon,
    )
    pred = predict_price(row)
    score, badge, diff, diff_pct = deal_score(float(l.price), float(pred))
    factors = top_factors_simple(row, predicted=float(pred), actual=float(l.price))

    comps = crud.comps_for_listing(db, l, limit=5)
    comp_items = []
    for c in comps:
        location = ", ".join([x for x in [c.city, c.state] if x])
        comp_items.append(
            schemas.CompItem(
                id=c.id,
                year=c.year,
                make=c.make,
                model=c.model,
                trim=c.trim,
                mileage=c.mileage,
                price=c.price,
                location=location or (c.state or ""),
            )
        )

    return schemas.ListingDetailResponse(
        listing=schemas.ListingOut.model_validate(l),
        predicted_price=float(pred),
        diff=float(diff),
        diff_pct=float(diff_pct),
        deal_score=score,
        badge=badge,
        top_factors=[schemas.Factor(**f) for f in factors],
        comps=comp_items,
    )