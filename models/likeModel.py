from lib.database import Base
from sqlalchemy import Column,ForeignKey,Integer,DateTime,UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Like(Base):
    __tablename__="likes"
    
    id=Column(Integer,primary_key=True,index=True)
    post_id=Column(Integer, ForeignKey("posts.id",ondelete="CASCADE"),nullable=False)
    user_id=Column(Integer,ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    created_at=Column(DateTime,server_default=func.now())
    
    post= relationship("Post", back_populates="likes")
    user=relationship("User", back_populates="likes")
    
    __table_args__= (
        UniqueConstraint("post_id", "user_id", name="unique_like"),
    )
