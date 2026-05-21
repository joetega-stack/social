from lib.database import Base

# Import all models so SQLAlchemy registers the mappers before create_all
from models.userModel import User  # noqa: F401
from models.postModel import Post  # noqa: F401
from models.commentModel import Comment  # noqa: F401
from models.likeModel import Like  # noqa: F401
from models.followModel import Follow  # noqa: F401
from models.followRequest import FollowRequest  # noqa: F401

__all__ = [
    "Base",
    "User",
    "Post",
    "Comment",
    "Like",
    "Follow",
    "FollowRequest",
]
