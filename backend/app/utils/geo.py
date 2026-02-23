from __future__ import annotations
from typing import Optional, Tuple
import math
import pgeocode

_nom = pgeocode.Nominatim("us")

def zip_to_latlon(zip_code: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    if not zip_code:
        return None, None
    z = str(zip_code).strip()
    if len(z) < 5:
        return None, None
    rec = _nom.query_postal_code(z[:5])
    if rec is None:
        return None, None
    lat = rec.get("latitude", None)
    lon = rec.get("longitude", None)
    if lat is None or lon is None or (isinstance(lat, float) and math.isnan(lat)):
        return None, None
    return float(lat), float(lon)

def haversine_miles(lat1, lon1, lat2, lon2) -> float:
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))