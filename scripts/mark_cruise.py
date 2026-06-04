import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models import Ship

CRUISE_MMSIS = [
    "309906000",  # FREEDOM OF THE SEAS (Royal Caribbean)
    "308045000",  # CARNIVAL SUNRISE (Carnival)
    "311001056",  # RESILIENT LADY (Virgin Voyages)
]

def mark_cruise_ships():
    db = SessionLocal()
    try:
        updated = 0
        for mmsi in CRUISE_MMSIS:
            ship = db.query(Ship).filter_by(mmsi=mmsi).first()
            if ship:
                ship.is_cruise = True
                updated += 1
                print(f"  Marked: {ship.name} ({mmsi})")
            else:
                print(f"  Not found in DB: {mmsi}")
        db.commit()
        print(f"\nDone. {updated} ship(s) marked as cruise.")
    finally:
        db.close()

if __name__ == "__main__":
    mark_cruise_ships()