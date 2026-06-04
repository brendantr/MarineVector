import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models import Ship
from app.utils.ais_types import ship_type_group_from_code

def backfill_vessel_types():
    db = SessionLocal()
    try:
        ships = (
            db.query(Ship)
            .filter(Ship.ship_type_code.isnot(None))
            .filter(Ship.vessel_type.is_(None))
            .all()
        )

        print(f"Found {len(ships)} ships to backfill...")

        updated = 0
        for ship in ships:
            vessel_type = ship_type_group_from_code(ship.ship_type_code)
            if vessel_type:
                ship.vessel_type = vessel_type
                updated += 1

        db.commit()
        print(f"Done. {updated} ship(s) updated with vessel_type.")

    finally:
        db.close()

if __name__ == "__main__":
    backfill_vessel_types()