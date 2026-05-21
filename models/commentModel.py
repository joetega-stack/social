from lib.database import Base
from sqlalchemy import Column,ForeignKey,Integer,String,Text,Boolean,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Comment(Base):
    __tablename__="comments"
    
    id=Column(Integer,primary_key=True)
    content = Column(Text, nullable=False)
    
    post_id=Column(Integer,ForeignKey("posts.id",ondelete="CASCADE"),nullable=False)
    user_id=Column(Integer,ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at=Column(DateTime,server_default=func.now())
    
    post = relationship("Post",back_populates="comments")
    author=relationship("User", back_populates="comments")
