import asyncio
import json
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .db import Base, engine
from . import models
from .ais_client import ais_stream_worker
from .routers import ships as ships_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("marinevector")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MarineVector")

# --- WebSocket connection manager ---
connected_clients: set[WebSocket] = set()

async def broadcast(message: dict):
    global connected_clients          
    if not connected_clients:
        return
    data = json.dumps(message)
    dead = set()
    for ws in connected_clients:
        try:
            await ws.send_text(data)
        except Exception:
            dead.add(ws)
    connected_clients -= dead

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ships_router.router)

# WebSocket endpoint — must be before StaticFiles mount
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info(f"WebSocket client connected. Total: {len(connected_clients)}")
    try:
        while True:
            await websocket.receive_text()  # keep-alive; client can send pings
    except WebSocketDisconnect:
        connected_clients.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(connected_clients)}")

# Serve static files (the map) — must be last
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(ais_stream_worker())
    logger.info("AIS stream worker started.")