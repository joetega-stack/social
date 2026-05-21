from sqlalchemy import Column,Integer,String,Text,Boolean,DateTime
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy.sql import func
from lib.database import Base
from models.followModel import Follow
from models.followRequest import FollowRequest

class User(Base):
    __tablename__= 'users'
    
    id=Column(Integer, primary_key=True, index=True)
    username=Column(String,nullable=False,unique=True)
    password=Column(String,nullable=False)
    email=Column(String,nullable=False,unique=True)
    profile_image=Column(Text, nullable=True)
    cover_image=Column(Text, nullable=True)
    bio=Column(Text,nullable=True)
    is_private=Column(Boolean,default=False)
    created_at=Column(DateTime,server_default=func.now())
    admin: Mapped[bool] = mapped_column(default=False)
    token_version: Mapped[int] = mapped_column(default=0)
    followers= relationship("Follow",foreign_keys=[Follow.following_id],cascade="all, delete-orphan")
    following= relationship("Follow",foreign_keys=[Follow.follower_id],cascade="all, delete-orphan")
    posts=relationship("Post",back_populates="author",cascade="all, delete-orphan")
    comments=relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    likes=relationship("Like", back_populates="user", cascade="all, delete-orphan")
    sent_follow_requests = relationship(
        "FollowRequest",
        foreign_keys=[FollowRequest.requester_id],
        cascade="all, delete-orphan",
    )
    received_follow_requests = relationship(
        "FollowRequest",
        foreign_keys=[FollowRequest.target_id],
        cascade="all, delete-orphan",
    )
    
    
