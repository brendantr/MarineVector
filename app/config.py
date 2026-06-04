import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    aisstream_api_key: str = os.getenv("AISSTREAM_API_KEY", "")
    aisstream_url: str = os.getenv("AISSTREAM_URL", "wss://stream.aisstream.io/v0/stream")
    db_url: str = os.getenv("DB_URL", "sqlite:///./marinevector.db")


settings = Settings()