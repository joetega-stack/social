from lib.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=True)
    media_url = Column(Text, nullable=True)
    visibility = Column(String, default="public")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    author = relationship("User", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", cascade="all,delete-orphan"
    )
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
