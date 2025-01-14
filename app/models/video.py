from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from app.db.session import Base
import datetime


class Video(Base):
    __tablename__ = "video_details"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    duration = Column(Integer, nullable=False)
    size_mb = Column(Float, nullable=False)
    file_path = Column(String, unique=True, index=True, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    trimmed = Column(Boolean, default=False)
