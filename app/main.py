from fastapi import FastAPI
from app.api.v1.endpoints import video_endpoint_router

app = FastAPI()

app.include_router(router=video_endpoint_router)