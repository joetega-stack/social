from sqlalchemy import Column,Integer,ForeignKey,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from lib.database import Base

class Conversation(Base):
    __tablename__= "conversations"
    
    id = Column(Integer, primary_key=True)
    
    user_one_id=Column(Integer, ForeignKey("users.id",ondelete="CASCADE"),nullable=False,)
    user_two_id=Column(Integer, ForeignKey("users.id",ondelete="CASCADE"),nullable=False,)
    created_at=Column(DateTime, server_default=func.now())
    user_one = relationship("User", foreign_keys=[user_one_id])
    user_two = relationship("User", foreign_keys=[user_two_id])
    messages = relationship("Message", back_populates="conversation",cascade="all, delete-orphan",)
    