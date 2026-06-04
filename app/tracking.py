import logging
from sqlalchemy.orm import Session
from . import models

from .utils.parsing import extract_position_from_aisstream, extract_static_from_aisstream
from .utils.ais_types import ship_type_group_from_code

logger = logging.getLogger(__name__)


def is_cruise_ship(ship_type: str | None) -> bool:
    # TEMP: accept all ships while we bring up the pipeline
    return True

def handle_ais_message(raw_message: dict, db: Session) -> None:
    msg_type = raw_message.get("MessageType")

    # 1. Static data: update Ship metadata (name, type code)
    static_data = extract_static_from_aisstream(raw_message)
    if static_data:
        mmsi = static_data["mmsi"]
        ship = db.query(models.Ship).filter_by(mmsi=mmsi).first()
        if not ship:
            ship = models.Ship(mmsi=mmsi)
            db.add(ship)

        if static_data.get("name"):
            ship.name = static_data["name"]

        code = static_data.get("ship_type_code")
        if code is not None:
            ship.ship_type_code = code
            ship.vessel_type = ship_type_group_from_code(code)

        db.commit()
        # Fall through: static messages usually don't have position, so return
        if msg_type != "PositionReport":
            return

    # 2. Position reports: update latest position
    data = extract_position_from_aisstream(raw_message)
    if not data:
        return

    logger.info(f"Parsed AIS position: {data}")

    mmsi = data["mmsi"]

    # Upsert Ship record (if created only by position before static arrives)
    ship = db.query(models.Ship).filter_by(mmsi=mmsi).first()
    if not ship:
        ship = models.Ship(
            mmsi=mmsi,
            name=data.get("name"),
        )
        db.add(ship)
    else:
        if data.get("name") and ship.name != data["name"]:
            ship.name = data["name"]

    # Upsert latest position (unchanged from your current logic)
    existing_pos = db.query(models.ShipPositionLatest).filter_by(mmsi=mmsi).first()
    if not existing_pos:
        existing_pos = models.ShipPositionLatest(
            mmsi=mmsi,
            lat=data["lat"],
            lon=data["lon"],
            speed=data.get("speed"),
            course=data.get("course"),
            heading=data.get("heading"),
        )
        db.add(existing_pos)
    else:
        existing_pos.lat = data["lat"]
        existing_pos.lon = data["lon"]
        existing_pos.speed = data.get("speed")
        existing_pos.course = data.get("course")
        existing_pos.heading = data.get("heading")

    db.commit()