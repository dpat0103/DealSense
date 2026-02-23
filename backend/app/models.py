from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from datetime import datetime
from .db import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)

    source_id = Column(String, nullable=True) 
    vin = Column(String, nullable=True)      

    source = Column(String, default="csv")
    url = Column(String, nullable=True)

    year = Column(Integer, nullable=False)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    trim = Column(String, nullable=True)

    mileage = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip = Column(String, nullable=True)

    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

Index("idx_make_model_year", Listing.make, Listing.model, Listing.year)
Index("idx_vin", Listing.vin)