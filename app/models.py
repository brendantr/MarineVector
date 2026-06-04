from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from .db import Base


class Ship(Base):
    __tablename__ = "ships"

    id = Column(Integer, primary_key=True, index=True)
    mmsi = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    vessel_type = Column(String, nullable=True)
    flag = Column(String, nullable=True)
    operator = Column(String, nullable=True)
    ship_type_code = Column(Integer, nullable=True)

    # NEW
    is_cruise = Column(Boolean, nullable=True, index=True)


class ShipPositionLatest(Base):
    __tablename__ = "ship_positions_latest"

    id = Column(Integer, primary_key=True, index=True)
    mmsi = Column(String, index=True, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    speed = Column(Float, nullable=True)   # knots
    course = Column(Float, nullable=True)  # degrees
    heading = Column(Float, nullable=True) # degrees
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)