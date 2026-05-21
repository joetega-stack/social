from sqlalchemy import Column, Integer, ForeignKey
from lib.database import Base

class Follow(Base):
    __tablename__="follows"
    
    id=Column(Integer,primary_key=True,index=True)
    follower_id=Column(Integer,ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id=Column(Integer,ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
