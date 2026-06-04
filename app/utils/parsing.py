from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


def extract_position_from_aisstream(message: dict[str, Any]) -> Optional[dict[str, Any]]:
    msg_type = message.get("MessageType")
    if msg_type != "PositionReport":
        return None

    meta = message.get("MetaData") or {}
    msg_wrapper = message.get("Message") or {}
    body = msg_wrapper.get("PositionReport") or {}

    if not meta or not body:
        logger.warning(f"Missing MetaData or PositionReport in message: {message}")
        return None

    try:
        mmsi_val = meta["MMSI"]
        lat_val = body["Latitude"]
        lon_val = body["Longitude"]
    except KeyError as e:
        logger.warning(f"KeyError in AIS parse: {e} in message: {message}")
        return None

    try:
        mmsi = str(mmsi_val)
        lat = float(lat_val)
        lon = float(lon_val)
    except (TypeError, ValueError) as e:
        logger.warning(
            f"Type conversion error in AIS parse: {e} for values "
            f"mmsi={mmsi_val}, lat={lat_val}, lon={lon_val}"
        )
        return None

    ship_name = meta.get("ShipName")
    sog = body.get("Sog")
    cog = body.get("Cog")
    heading = body.get("TrueHeading")

    return {
        "mmsi": mmsi,
        "lat": lat,
        "lon": lon,
        "speed": float(sog) if sog is not None else None,
        "course": float(cog) if cog is not None else None,
        "heading": float(heading) if heading is not None else None,
        "name": ship_name,
        "vessel_type": None,
    }


def extract_static_from_aisstream(message: dict[str, Any]) -> Optional[dict[str, Any]]:
    """
    Extract static ship info, including AIS ship type code, from AISstream messages
    that are NOT PositionReport, using the actual structures you logged:
      - StaticDataReport (MessageID 24)
      - ShipStaticData (MessageID 5)
    """
    msg_type = message.get("MessageType")
    if msg_type not in ("StaticDataReport", "ShipStaticData"):
        return None

    meta = message.get("MetaData") or {}
    body = message.get("Message") or {}

    name: Optional[str] = None
    type_code: Any = None
    mmsi: Any = None

    if msg_type == "StaticDataReport":
        # Example:
        # 'StaticDataReport': {
        #   'ReportA': {'Name': 'ZOWEH', ...},
        #   'ReportB': {'ShipType': 0, ...},
        #   'UserID': 367604470,
        #   ...
        # }
        static = body.get("StaticDataReport") or {}
        report_a = static.get("ReportA") or {}
        report_b = static.get("ReportB") or {}

        name = report_a.get("Name") or meta.get("ShipName")
        type_code = report_b.get("ShipType")
        mmsi = meta.get("MMSI") or static.get("UserID")

    elif msg_type == "ShipStaticData":
        # Example:
        # 'ShipStaticData': {
        #   'Name': '8TENYOMARU          ',
        #   'Type': 70,
        #   'UserID': 431800709,
        #   ...
        # }
        static = body.get("ShipStaticData") or {}

        name = static.get("Name") or meta.get("ShipName")
        type_code = static.get("Type")
        mmsi = meta.get("MMSI") or static.get("UserID")

    if not mmsi:
        return None

    if type_code is None:
        type_code_int: Optional[int] = None
    else:
        try:
            type_code_int = int(type_code)
        except (TypeError, ValueError):
            logger.warning(f"Could not parse ship type code {type_code} for MMSI {mmsi}")
            type_code_int = None

    return {
        "mmsi": str(mmsi),
        "name": name,
        "ship_type_code": type_code_int,
    }