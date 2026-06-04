from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/ships", tags=["ships"])


@router.get("/", response_model=list[schemas.ShipWithPosition])
def list_ships(
    db: Session = Depends(get_db),
    types: Annotated[list[str] | None, Query()] = None,
    cruise_only: bool = False,  # NEW
):
    q = (
        db.query(models.ShipPositionLatest, models.Ship)
        .join(models.Ship, models.Ship.mmsi == models.ShipPositionLatest.mmsi)
    )

    if types:
        q = q.filter(models.Ship.vessel_type.in_(types))

    if cruise_only:
        q = q.filter(models.Ship.is_cruise.is_(True))  # NEW

    rows = q.all()
    result: list[schemas.ShipWithPosition] = []

    for pos, ship in rows:
        result.append(
            schemas.ShipWithPosition(
                ship=schemas.ShipBase.model_validate(ship),
                position=schemas.ShipPosition.model_validate(pos),
            )
        )

    return result


@router.get("/{mmsi}", response_model=schemas.ShipWithPosition)
def get_ship(mmsi: str, db: Session = Depends(get_db)):
    pos = db.query(models.ShipPositionLatest).filter_by(mmsi=mmsi).first()
    if not pos:
        raise HTTPException(status_code=404, detail="Ship not found")

    ship = db.query(models.Ship).filter_by(mmsi=mmsi).first()

    return schemas.ShipWithPosition(
        ship=schemas.ShipBase.model_validate(ship) if ship else None,
        position=schemas.ShipPosition.model_validate(pos),
    )