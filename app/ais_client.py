import asyncio
import json
import logging

import websockets
from websockets.exceptions import ConnectionClosedError, InvalidStatusCode
from sqlalchemy.orm import Session

from .config import settings
from .db import SessionLocal
from .tracking import handle_ais_message

logger = logging.getLogger(__name__)


async def ais_stream_worker():
    url = settings.aisstream_url
    api_key = settings.aisstream_api_key

    if not api_key:
        logger.error("AISSTREAM_API_KEY is not set; AIS stream will not start.")
        return

    while True:
        try:
            logger.info(f"Connecting to AISstream at {url} ...")
            async with websockets.connect(url, ping_interval=20, ping_timeout=20) as websocket:
                subscription = {
                    "APIKey": api_key,
                    "BoundingBoxes": [
                        [[-90, -180], [90, 180]],
                    ],
                    # TEMP: allow all message types so we can see static messages
                    # "FilterMessageTypes": ["PositionReport"],
                }
                await websocket.send(json.dumps(subscription))
                logger.info(f"Subscribed to AISstream: {subscription}")

                async for message in websocket:
                    logger.info(f"Raw AIS message: {message[:200]}...")

                    try:
                        payload = json.loads(message)
                    except json.JSONDecodeError:
                        logger.warning("Failed to decode AIS message")
                        continue

                    msg_type = payload.get("MessageType")
                    if msg_type != "PositionReport":
                        logger.info(f"Full non-position AIS message: {payload}")

                    db: Session = SessionLocal()
                    try:
                        handle_ais_message(payload, db)
                    except Exception as e:
                        logger.exception(f"Error handling AIS message: {e}")
                    finally:
                        db.close()

        except InvalidStatusCode as e:
            logger.error(
                f"AISstream refused connection (status={e.status_code}). "
                f"Check API key / URL."
            )
            await asyncio.sleep(15)

        except ConnectionClosedError as e:
            logger.warning(f"AISstream connection closed: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"Unexpected AISstream error: {e}. Reconnecting in 10s...")
            await asyncio.sleep(10)