import asyncio
import json
import os

import websockets
from websockets.exceptions import ConnectionClosedError
from dotenv import load_dotenv

load_dotenv()

AISSTREAM_URL = os.getenv("AISSTREAM_URL", "wss://stream.aisstream.io/v0/stream")
API_KEY = os.getenv("AISSTREAM_API_KEY", "")


async def main():
    print("Using API key:", API_KEY[:6] + "..." if API_KEY else "(missing)")
    if not API_KEY:
        print("Missing AISSTREAM_API_KEY in .env")
        return

    try:
        async with websockets.connect(AISSTREAM_URL) as ws:
            subscribe_message = {
                "APIKey": API_KEY,
                "BoundingBoxes": [
                    [[-90, -180], [90, 180]],
                ],
                # No MMSI filter: get all ships
                "FilterMessageTypes": ["PositionReport"],
            }
            await ws.send(json.dumps(subscribe_message))
            print("Sent subscription:", subscribe_message)

            try:
                # Wait up to 30 seconds for the first message
                msg = await asyncio.wait_for(ws.recv(), timeout=30)
                print("FIRST RAW:", msg[:800], "...")
            except asyncio.TimeoutError:
                print("Timed out waiting for first AIS message (30s).")
            except ConnectionClosedError as e:
                print(f"Connection closed by server while waiting for first message: {e}")

    except ConnectionClosedError as e:
        print(f"Connection closed by server before reading messages: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())