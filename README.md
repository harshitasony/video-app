# Video Processing API

This repository provides a REST API for handling video files, including features like uploading, trimming, merging, and generating time-limited shareable links. The API is built using FastAPI, with SQLite as the database for storage and it uses MoviePy for video processing.

---

## Features

1. **Authentication**: All API calls require a static API token for access.
2. **Video Upload**: Upload video files with configurable size and duration limits.
3. **Video Trimming**: Trim uploaded videos from the start or end.
4. **Video Merging**: Merge multiple uploaded video clips into a single video file.
5. **Link Sharing**: Generate shareable video links with time-based expiry.
6. **Testing**: Unit and end-to-end tests provided, with commands for test coverage.
7. **API Documentation**: Available as a Postman collection JSON.

---

## Setup

### Prerequisites

- Python 3.9 or higher
- Virtual environment (optional but recommended)

### Commands to Set Up the Repo

1. Clone the repository:

    ```sh
    git clone https://github.com/your-username/video-processing-api.git
    cd video-processing-api
    ```

2. Create and activate a virtual environment:

    ```sh
    python3 -m venv env
    source env/bin/activate 
    ```

3. Install the dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Set up the environment variables:

    Create a [.env](http://_vscodecontentref_/1) file in the root directory with the following content:

    ```properties
    API_KEY = "test-static-api-token"
   API_KEY_NAME = "API-Key"
   DATABASE_URL = "sqlite:///./video_manager.db"
   MAX_VIDEO_SIZE_MB = 25
   MIN_VIDEO_DURATION_SEC = 5
   MAX_VIDEO_DURATION_SEC = 60
   LINK_EXPIRY_MINUTES = 15
    ```

   (Committed in this repo for ease. Please omit this step)

### Commands to Run the Test Suite

1. Run the tests:

    ```sh
    coverage run -m unittest discover -s tests
    ```

2. Generate the test coverage report:

    ```sh
    coverage report -m
    ```

### Command to Run the API Server

1. Start the FastAPI server:

    ```sh
    uvicorn app.main:app --reload
    ```

The API will be available at `http://127.0.0.1:8000`.
Swagger documentation at `http://127.0.0.1:8000/docs/`.
You can find the Postman collection for this API as `video-app.postman_collection.json` in the root directory. Import the collection into Postman to test the API endpoints.

---

## Configuration

- **Video Size Limit**: Configure the maximum upload size in `.env`.
- **Duration Limits**: Set minimum and maximum video durations in `.env`.
- **API Token**: Update the static API token in `.env` for authentication.

---

## Why We Used MoviePy

MoviePy is a versatile library for video editing in Python. It supports a wide range of video processing tasks, including trimming, merging, adding effects, and more. It is easy to use and integrates well with other Python libraries.

## Option to Use Cloudinary and Its Benefits

Cloudinary is a cloud-based media management service that provides a comprehensive solution for uploading, storing, processing, and delivering images and videos. Some benefits of using Cloudinary include:

- **Scalability**: Cloudinary can handle large volumes of media files and provides automatic scaling.
- **Security**: Cloudinary offers secure storage and delivery of media files.
- **Performance**: Cloudinary optimizes media files for fast delivery and provides a global content delivery network (CDN).
- **Advanced Features**: Cloudinary offers advanced features like automatic format conversion, video transcoding, and more.

To use Cloudinary, you would need to set up an account and configure the Cloudinary SDK in your project.

## Why We Are Storing in Local Store and Where Else Can We Store

We are storing videos locally in the [store](http://_vscodecontentref_/2) directory for simplicity and ease of access during development. However, for production, it is recommended to use cloud storage solutions like:

- **AWS S3**: Amazon Simple Storage Service (S3) is a scalable object storage service.
- **Google Cloud Storage**: Google Cloud Storage is a scalable and secure object storage service.
- **Cloudinary**: Cloudinary provides a comprehensive solution for media management.

Using cloud storage solutions provides benefits like scalability, security, and performance optimization.

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MoviePy Documentation](https://zulko.github.io/moviepy/)
- [SQLite Documentation](https://sqlite.org/docs.html)

