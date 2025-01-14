from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEY: str
    API_KEY_NAME: str
    DATABASE_URL: str
    MAX_VIDEO_SIZE_MB: int
    MIN_VIDEO_DURATION_SEC: int
    MAX_VIDEO_DURATION_SEC: int
    LINK_EXPIRY_MINUTES: int

    class Config:
        env_file = ".env" 

settings = Settings()