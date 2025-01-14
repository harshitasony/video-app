from sqlalchemy import Column, String, DateTime
from app.db.session import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(String, primary_key=True, index=True, nullable=False)
    video_id = Column(String, index=True, nullable=False)
    expiry_time = Column(DateTime, nullable=False)
