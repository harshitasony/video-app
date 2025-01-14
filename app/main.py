from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.api.v1.endpoints import video, link_sharing
from app.core.config import settings
from app.db.session import engine, Base
import os 

os.makedirs("store", exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

video_endpoint = video.VideoEndpoint()
link_sharing_endpoint = link_sharing.LinkSharingEndpoint()

app.include_router(video_endpoint.get_router())
app.include_router(link_sharing_endpoint.get_router())