import shutil
from app.models.video import Video
from fastapi import APIRouter, UploadFile, HTTPException, status, Depends
from app.core.config import settings
import ffmpeg
import moviepy
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
import logging
from app.db.session import get_db
from sqlalchemy.orm import Session
import uuid
from app.core.auth import authenticate
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

class TrimVideoRequest(BaseModel):
    video_id: str
    start_time: int
    end_time: int
    save_as_new: bool

class VideoEndpoint:
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1")

    def get_router(self):
        """
        Registers API routes.
        """
        self.router.get("/test", status_code=status.HTTP_200_OK)(self.test)
        self.router.post(
            "/video/upload", status_code=status.HTTP_200_OK, dependencies=[Depends(authenticate)]
        )(self.upload_video)
        self.router.post(
            "/video/trim", status_code=status.HTTP_200_OK, dependencies=[Depends(authenticate)]
        )(self.trim_video)
        self.router.post(
            "/videos/merge", status_code=status.HTTP_200_OK, dependencies=[Depends(authenticate)]
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
        video_file = None

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
            video_ob = Video(
                id=unique_id, 
                title=uploaded_file.filename, 
                duration=video_duration, 
                size_mb=file_size, 
                file_path=file_location
            )
            db.add(video_ob)
            db.commit()
            db.refresh(video_ob)
            
            logger.info("Video uploaded successfully")
            return {"message": "Video uploaded successfully", "video_id": unique_id}

        except Exception as e:
            err_str = f"Error during video upload: {e}"
            logger.error(err_str)
            raise HTTPException(status_code=400, detail=err_str)

        finally:
            if video_file:
                video_file.close()
            os.remove(temp_file_path)

    async def trim_video(self, trim_data: TrimVideoRequest, db: Session = Depends(get_db)):
        """
        API endpoint for trimming a video.
        """
        video_id = trim_data.video_id
        start_time = trim_data.start_time
        end_time = trim_data.end_time
        save_as_new = trim_data.save_as_new

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
            unique_id = video.id

            if save_as_new:
                unique_id = str(uuid.uuid4())
                file_extension = os.path.splitext(video.title)[1]
                file_location = f"store/{unique_id}{file_extension}"
                trimmed_video.write_videofile(file_location, codec="libx264")
                video_ob = Video(
                    id=unique_id, 
                    title=video.title, 
                    duration=int(trimmed_video.duration), 
                    size_mb=os.path.getsize(file_location) / (1024 * 1024), 
                    file_path=file_location, 
                    trimmed=True
                )
                db.add(video_ob)
                db.commit()
                db.refresh(video_ob)
            else:
                trimmed_video.write_videofile(video.file_path, codec="libx264")
                video.duration = int(trimmed_video.duration)
                video.size_mb = os.path.getsize(video.file_path) / (1024 * 1024)
                video.trimmed = True
                db.commit()
                db.refresh(video)

            logger.info("Video trimmed successfully")
            return {"message": "Video trimmed successfully", "video_id": unique_id}
        
        except Exception as e:
            err_str = f"Error during video trimming: {e}"
            logger.error(err_str)
            raise HTTPException(status_code=400, detail=err_str)

        finally:
            video_file.close()
            if not save_as_new:
                os.remove(video.file_path)
    

    async def merge_videos(self, video_id1: str, video_id2: str, db: Session = Depends(get_db)):
        """
        API endpoint for trimming a video.
        """
        video1 = db.query(Video).filter(Video.id == video_id1).first()
        video2 = db.query(Video).filter(Video.id == video_id2).first()

        if not video1:
            err_str = f"Video with id {video_id1} not found"
            logger.error(err_str)
            raise HTTPException(status_code=404, detail=err_str)
        
        if not video2:
            err_str = f"Video with id {video_id2} not found"
            logger.error(err_str)
            raise HTTPException(status_code=404, detail=err_str)

        video_file1 = None
        video_file2 = None
        merged_video = None

        try:
            video_file1 = VideoFileClip(video1.file_path)
            video_file2 = VideoFileClip(video2.file_path)
            merged_video = concatenate_videoclips([video_file1, video_file2])
            unique_id = str(uuid.uuid4())
            file_extension = os.path.splitext(video1.file_path)[1]
            file_location = f"store/{unique_id}{file_extension}"
            merged_video.write_videofile(file_location, codec="libx264")
            video_ob = Video(
                id=unique_id,
                title=f"{video1.title}_merged_{video2.title}",
                duration=int(merged_video.duration),
                size_mb=os.path.getsize(file_location) / (1024 * 1024),
                file_path=file_location
            )
            db.add(video_ob)
            db.commit()
            db.refresh(video_ob)

            logger.info("Videos merged successfully")
            return {"message": "Videos merged successfully", "video_id": unique_id}


        except Exception as e:
            err_str = f"Error during video trimming: {e}"
            logger.error(err_str)
            raise HTTPException(status_code=400, detail=err_str)

        finally:
            if video_file1:
                video_file1.close()
            if video_file2:
                video_file2.close()
            if merged_video:
                merged_video.close()