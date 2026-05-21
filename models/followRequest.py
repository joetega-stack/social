from lib.database import Base
from sqlalchemy import Column,Integer,ForeignKey,DateTime
from sqlalchemy.sql import func

class FollowRequest(Base):
    __tablename__="follow_requests"
    id=Column(Integer,primary_key=True)
    requester_id=Column(Integer,ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_id=Column(Integer,ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at=Column(DateTime,server_default=func.now())
