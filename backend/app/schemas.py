from pydantic import BaseModel
from typing import Optional, List

class ListingBase(BaseModel):
    source_id: Optional[str] = None
    vin: Optional[str] = None

    year: int
    make: str
    model: str
    trim: Optional[str] = None
    mileage: int
    price: int
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    url: Optional[str] = None
    source: Optional[str] = "csv"

class ListingOut(ListingBase):
    id: int
    class Config:
        from_attributes = True

class SearchResultItem(BaseModel):
    listing: ListingOut
    predicted_price: float
    diff: float
    diff_pct: float
    deal_score: int
    badge: str

class SearchResponse(BaseModel):
    results: List[SearchResultItem]

class Factor(BaseModel):
    feature: str
    impact: float
    direction: str
    note: str

class CompItem(BaseModel):
    id: int
    year: int
    make: str
    model: str
    trim: Optional[str]
    mileage: int
    price: int
    location: str

class ListingDetailResponse(BaseModel):
    listing: ListingOut
    predicted_price: float
    diff: float
    diff_pct: float
    deal_score: int
    badge: str
    top_factors: list[Factor]
    comps: list[CompItem]