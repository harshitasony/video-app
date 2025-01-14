from app.models.link import Link
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from app.models.video import Video
from app.db.session import get_db
from app.core.config import settings
import uuid
from datetime import datetime, timedelta, timezone
import hashlib
import logging
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

class LinkSharingEndpoint:
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1")

    def get_router(self):
        """
        Registers API routes.
        """
        self.router.post("/generate_link", status_code=status.HTTP_200_OK)(self.generate_link)
        self.router.get("/access_video/{link_id}", status_code=status.HTTP_200_OK)(self.access_video)
        return self.router

    async def generate_link(self, video_id: str, request: Request, db: Session = Depends(get_db)):
        """
        API endpoint to generate a shareable link.
        """
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            err_str = f"Video with id {video_id} not found"
            logger.error(err_str)
            raise HTTPException(status_code=404, detail=err_str)

        link_id = str(uuid.uuid4())
        expiry_time = datetime.now(timezone.utc) + timedelta(minutes=settings.LINK_EXPIRY_MINUTES)
        link = Link(
            id=link_id,
            video_id=video_id,
            expiry_time=expiry_time
        )
        db.add(link)
        db.commit()
        db.refresh(link)
        sharable_link = f"{request.base_url}api/v1/access_video/{link_id}"
        return {"link": sharable_link, "expiry_time": expiry_time}
    
    async def access_video(self, link_id: str, db: Session = Depends(get_db)):
        """
        API endpoint to access video.
        """
        link = db.query(Link).filter(Link.id == link_id).first()
        if not link:
            err_str = f"Link with id {link_id} not found"
            logger.error(err_str)
            raise HTTPException(status_code=404, detail=err_str)

        if link.expiry_time.tzinfo is None:
            link.expiry_time = link.expiry_time.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > link.expiry_time:
            err_str = f"Link with id {link_id} has expired"
            logger.error(err_str)
            raise HTTPException(status_code=403, detail=err_str)

        video = db.query(Video).filter(Video.id == link.video_id).first()
        if not video:
            err_str = f"Video with id {link_id} not found"
            logger.error(err_str)
            raise HTTPException(status_code=404, detail=err_str)

        #return {"video_path": video.file_path}
        return FileResponse(video.file_path, media_type='video/mp4', filename=video.title)