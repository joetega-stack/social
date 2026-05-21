from models.userModel import User

def user_with_counts(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "followers_count": len(user.followers),
        "following_count": len(user.following),
        "is_private": user.is_private
    }
    
    
# from sqlalchemy.orm import Session
# from sqlalchemy import func
# from models.userModel import User
# from models.followModel import Follow

# def user_with_counts(user_id: int, db: Session):
#     """
#     Return user data with follower/following counts efficiently
#     """
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         return None

#     # Efficient COUNT queries
#     followers_count = db.query(func.count(Follow.id)).filter(Follow.following_id == user_id).scalar()
#     following_count = db.query(func.count(Follow.id)).filter(Follow.follower_id == user_id).scalar()

#     return {
#         "id": user.id,
#         "username": user.username,
#         "email": user.email,
#         "followers_count": followers_count,
#         "following_count": following_count,
#         "is_private": user.is_private,
#         "bio": user.bio,
#         "profile_image": user.profile_image
#     }