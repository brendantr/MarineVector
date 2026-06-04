from datetime import datetime
from pydantic import BaseModel


class ShipBase(BaseModel):
    mmsi: str
    name: str | None = None
    vessel_type: str | None = None  # will hold "passenger","cargo","tanker",...
    flag: str | None = None
    operator: str | None = None
    ship_type_code: int | None = None  # NEW, raw AIS code

    class Config:
        from_attributes = True  # Pydantic v2 (from_orm=True in v1)


class ShipPosition(BaseModel):
    mmsi: str
    lat: float
    lon: float
    speed: float | None = None
    course: float | None = None
    heading: float | None = None
    timestamp: datetime

    class Config:
        from_attributes = True


class ShipWithPosition(BaseModel):
    ship: ShipBase | None = None
    position: ShipPosition

    class Config:
        from_attributes = True

class PaginatedShips(BaseModel):
    total: int
    limit: int
    offset: int
    results: list[ShipWithPosition]