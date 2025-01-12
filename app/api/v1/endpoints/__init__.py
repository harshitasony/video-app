from app.api.v1.endpoints.video import VideoEndpoint

video_endpoint_instance = VideoEndpoint()
video_endpoint_router = video_endpoint_instance.get_router()