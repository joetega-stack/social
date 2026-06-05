from sqlalchemy import Column,Integer,ForeignKey,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from lib.database import Base

class Message(Base):
    __tablename__= "messages"
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer,ForeignKey("conversations.id",ondelete="CASCADE"),nullable=False,)
    sender_id = Column(Integer,ForeignKey("conversations.id",ondelete="CASCADE"),nullable=False,)
    content = Column(DateTime, server_default=func.now())
    conversation = relationship("Conversation",back_populates="messages",)
    sender = relationship("User")