from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.api.v1.endpoints.video import VideoEndpoint
from app.core.config import settings
from app.db.session import engine, Base
import os 

os.makedirs("store", exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

video_endpoint = VideoEndpoint()
app.include_router(video_endpoint.get_router())