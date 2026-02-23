from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, List
from .models import Listing

def get_listing(db: Session, listing_id: int) -> Optional[Listing]:
    return db.get(Listing, listing_id)

def search_listings(
    db: Session,
    make: Optional[str] = None,
    model: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    mileage_max: Optional[int] = None,
    state: Optional[str] = None,
    limit: int = 50,
) -> List[Listing]:
    stmt = select(Listing)

    if make:
        stmt = stmt.where(Listing.make.ilike(make.strip()))
    if model:
        stmt = stmt.where(Listing.model.ilike(model.strip()))
    if state:
        stmt = stmt.where(Listing.state.ilike(state.strip()))
    if year_min is not None:
        stmt = stmt.where(Listing.year >= int(year_min))
    if year_max is not None:
        stmt = stmt.where(Listing.year <= int(year_max))
    if mileage_max is not None:
        stmt = stmt.where(Listing.mileage <= int(mileage_max))

    stmt = stmt.limit(int(limit))
    return list(db.execute(stmt).scalars().all())

def comps_for_listing(db: Session, base: Listing, limit: int = 5) -> List[Listing]:
    stmt = (
        select(Listing)
        .where(Listing.make == base.make)
        .where(Listing.model == base.model)
        .where(Listing.id != base.id)
        .where(Listing.year >= base.year - 2)
        .where(Listing.year <= base.year + 2)
        .limit(200)
    )
    candidates = list(db.execute(stmt).scalars().all())

    def key_fn(x: Listing):
        return (abs((x.year or 0) - base.year), abs((x.mileage or 0) - base.mileage))

    candidates.sort(key=key_fn)
    return candidates[:limit]