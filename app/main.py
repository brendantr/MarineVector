import asyncio
import logging

from fastapi import FastAPI
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

# CORS — allows browser to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(ships_router.router)

# Serve static files (the map)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(ais_stream_worker())
    logger.info("AIS stream worker started.")