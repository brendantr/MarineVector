import asyncio
import logging

from fastapi import FastAPI

from .db import Base, engine
from . import models
from .ais_client import ais_stream_worker
from .routers import ships as ships_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("marinevector")

# Ensure tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MarineVector")

app.include_router(ships_router.router)


@app.on_event("startup")
async def startup_event():
    # Start AIS stream worker as background task
    loop = asyncio.get_event_loop()
    loop.create_task(ais_stream_worker())
    logger.info("AIS stream worker started.")