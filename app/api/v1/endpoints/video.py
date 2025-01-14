import shutil
from app.models.video import Video
from fastapi import APIRouter, UploadFile, HTTPException, status, Depends
from app.core.config import settings
import ffmpeg
import moviepy
from moviepy.editor import VideoFileClip
import os
import logging
from app.db.session import get_db
from sqlalchemy.orm import Session
import uuid

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

class VideoEndpoint:
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1")

    def get_router(self):
        """
        Registers API routes.
        """
        self.router.get("/test", status_code=status.HTTP_200_OK)(self.test)
        self.router.post(
            "/video/upload", status_code=status.HTTP_200_OK
        )(self.upload_video)
        self.router.post(
            "/video/trim", status_code=status.HTTP_200_OK
        )(self.trim_video)
        self.router.post(
            "/videos/merge", status_code=status.HTTP_200_OK
        )(self.merge_videos)
        return self.router

    def test(self):
        """
        Test endpoint.
        """
        return {"message": "Hello World!"}

    async def upload_video(self, uploaded_file: UploadFile, db: Session = Depends(get_db)):
        """
        API endpoint for uploading a video.
        """
        input_file = await uploaded_file.read()
        file_size = round((len(input_file) / (1024 * 1024)), 2)
        if file_size > settings.MAX_VIDEO_SIZE_MB:
            err_str = f"Video size exceeds {settings.MAX_VIDEO_SIZE_MB} MB"
            logger.error(err_str)
            raise HTTPException(
                status_code=400, detail=err_str
            )

        temp_file_path = f"temp_{uploaded_file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(input_file)

        try:
            video_file = VideoFileClip(temp_file_path)
            video_duration = int(video_file.duration)

            if not (settings.MIN_VIDEO_DURATION_SEC <= video_duration <= settings.MAX_VIDEO_DURATION_SEC):
                err_str = f"Video duration must be between {settings.MIN_VIDEO_DURATION_SEC} and {settings.MAX_VIDEO_DURATION_SEC} seconds"
                logger.error(err_str)
                raise HTTPException(
                    status_code=400,
                    detail=err_str,
                )
            
            unique_id = str(uuid.uuid4())
            file_extension = os.path.splitext(uploaded_file.filename)[1]
            file_location = f"store/{unique_id}{file_extension}"
            with open(file_location, "wb") as buffer:
                buffer.write(input_file)
            
            video = Video(id=unique_id, title=uploaded_file.filename, duration=video_duration, size_mb=file_size, file_path=file_location)
            db.add(video)
            db.commit()
            db.refresh(video)
            
            logger.info("Video uploaded successfully")
            return {"message": "Video uploaded successfully", "video_id": video.id}

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            err_str = f"Error during video upload: {e}"
            logger.error(err_str)
            raise HTTPException(status_code=400, detail=err_str)

        finally:
            video_file.close()
            os.remove(temp_file_path)

    async def trim_video(self, video_id: str, start_time: int, end_time: int, save_as_new: bool, db: Session = Depends(get_db)):
        """
        API endpoint for trimming a video.
        """
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            err_str = f"Video with id {video_id} not found"
            logger.error(err_str)
            raise HTTPException(status_code=404, detail=err_str)

        try:
            video_file = VideoFileClip(video.file_path)
            if not (0 <= start_time < end_time <= video_file.duration):
                err_str = "Invalid start and end time"
                logger.error(err_str)
                raise HTTPException(status_code=400, detail=err_str)

            trimmed_video = video_file.subclip(start_time, end_time)
            trimmed_video_duration = int(trimmed_video.duration)

            if save_as_new:
                unique_id = str(uuid.uuid4())
                file_extension = os.path.splitext(video.title)[1]
                file_location = f"store/{unique_id}{file_extension}"
                with open(file_location, "wb") as buffer:
                    buffer.write(trimmed_video)

                trimmed_video_size = os.path.getsize(file_location) / (1024 * 1024),
                trimmed_video = Video(id=unique_id, title=video.file_name, duration=trimmed_video_duration, size_mb=trimmed_video_size, file_path=file_location)
                db.add(trimmed_video)
                db.commit()
                db.refresh(trimmed_video)

            else:
                with open(video.file_path, "wb") as buffer:
                    buffer.write(trimmed_video)
                
                video.duration = trimmed_video_duration
                video.size_mb = os.path.getsize(video.file_path) / (1024 * 1024)
                db.commit()
                db.refresh(video)

            logger.info("Video trimmed successfully")
            return {"message": "Video trimmed successfully", "video_id": video.id}
        
        except Exception as e:
            err_str = f"Error during video trimming: {e}"
            logger.error(err_str)
            raise HTTPException(status_code=400, detail=err_str)

        finally:
            video_file.close()
            trimmed_video.close()
            if not save_as_new:
                os.remove(video.file_path)
    

    async def merge_videos(self, video_id: str, start_time: int, end_time: int, save_as_new: bool, db: Session = Depends(get_db)):
        """
        API endpoint for trimming a video.
        """
        pass