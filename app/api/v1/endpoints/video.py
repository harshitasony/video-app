from fastapi import APIRouter, HTTPException, status

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
            "/videos/upload", status_code=status.HTTP_200_OK
        )(self.upload_video)
        self.router.post(
            "/videos/trim", status_code=status.HTTP_200_OK
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

    async def upload_video(self):
        """
        API endpoint for uploading a video.
        """
        return {"message": "Hello World!"}
    
    async def trim_video(self):
        """
        API endpoint for trimming a video.
        """
        return {"message": "Hello World!"}

    async def merge_videos(self):
        """
        API endpoint for merging videos.
        """
        return {"message": "Hello World!"}
