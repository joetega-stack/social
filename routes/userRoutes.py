from fastapi import APIRouter, Response, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from lib.database import get_db
from models.userModel import User
from models.followModel import Follow
from models.followRequest import FollowRequest
from utils.crypto import verify_token, validate_admin,hash_password
from typing import Optional


router=APIRouter(tags=['User'])



class UpdateUser(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    cover_image: Optional[str] = None

class UpdatePassword(BaseModel):
    password: Optional[str] = None
    


#get all users admin
@router.get("/users")
def get_users(db: Session=Depends(get_db),admin = Depends(validate_admin)):
    try:
        if not admin:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorised")
        users = db.query(User).all()
        return users
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(500,detail="Failed to get users")

@router.get("/all/users")
def get_all_users(db:Session=Depends(get_db),current_user: User=Depends(verify_token)):
    try:
        users = db.query(User).filter(User.id != current_user.id, User.admin == False).all()
        if not current_user.id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Unauthorized" )
        return users
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(500, detail="Failed to get users")
    

#get current user
@router.get("/users/current")
def get_current_user(current_user: User=Depends(verify_token)):
    try:
        return {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "followers_count": len(current_user.followers),
            "following_count": len(current_user.following),
            "bio": current_user.bio,
            "profile_image": current_user.profile_image,
            "cover_photo":current_user.cover_image,
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to get user")
    
    
# get user profile
@router.get("/user/{id}")
def get_user(id: int, db: Session = Depends(get_db), admin=Depends(validate_admin)):
    try:
        user = db.query(User).filter(User.id == id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorised"
            )
        return {
            "id": user.id,
            "username": user.username,
            "followers_count": len(user.followers),
            "following_count": len(user.following),
            "bio": user.bio,
            "profile_image": user.profile_image,
            "cover_image": user.cover_image,
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to get user")


# update user profile
@router.patch("/update-profile")
def update_profile(
    update: UpdateUser,
    db: Session = Depends(get_db),
    current_user: User=Depends(verify_token),
):
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(404, detail="User not found")
        update_data = update.model_dump(exclude_unset=True,exclude_none=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return {
            "message": "Profile updated successfully",
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
    
@router.patch("/update-password")
def update_password(update: UpdatePassword, db: Session=Depends(get_db), current_user:User=Depends(verify_token)):
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(404, detail="User not found")
        update_data = update.model_dump(exclude_unset=True)
        if "password" in update_data:
            user.password= hash_password(update_data["password"])
            db.commit()
            db.refresh(user)
            return {"message":"Password update successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=(e))


# toggle follow and unfollow user
@router.post("/follow/{id}")
def follow_user(
    id: int, db: Session = Depends(get_db), current_user: User = Depends(verify_token)
):
    try:
        if current_user.id == id:
            raise HTTPException(status_code=400, detail="You cannot follow yourself")
        target = db.query(User).filter(User.id == id).first()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        if target.is_private:
            existing_request = (
                db.query(FollowRequest).filter(FollowRequest.requester_id == current_user.id,FollowRequest.target_id == id).first()
            )
            if existing_request:
                db.delete(existing_request)
                db.commit()
                return{"action":"follow_request_cancelled",
                       "message": f"Your follow request to {target.username} has been cancelled"}
            else:
                new_request = FollowRequest(requester_id=current_user.id, target_id=id)
                db.add(new_request)
                db.commit()
                return{
                    "action":"follow_request_sent",
                    "message": f"Follow request sent to {target.username}"
                }
        existing = (
            db.query(Follow)
            .filter(Follow.follower_id == current_user.id, Follow.following_id == id)
            .first()
        )
        if existing:
            db.delete(existing)
            db.commit()
            action = {"message": "Unfollowed successfully"}
        else:
            new_follow = Follow(follower_id=current_user.id, following_id=id)
            db.add(new_follow)
            db.commit()
            action= {"message": f"You are now following {target.username}"}
        followers_count = db.query(Follow).filter(Follow.following_id == id).count()
        following_count = db.query(Follow).filter(Follow.follower_id == current_user.id).count()
        
        return {
            "action": action,
            "target_user":{
                "id": target.id,
                "username": target.username,
                "followers_count": followers_count
            },
            "current_user":{
                "id": current_user.id,
                "username": current_user.username,
                "following_count": following_count 
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# get followers list
@router.get("/me/followers")
def my_followers(
    db: Session = Depends(get_db), current_user: User = Depends(verify_token)
):
    followers = (
        db.query(User)
        .join(Follow, Follow.follower_id == User.id)
        .filter(Follow.following_id == current_user.id)
        .all()
    )
    return [
        {
            "id": f.id,
            "username": f.username,
            "email": f.email,
            "followers_count": len(f.followers),
            "following_count": len(f.following),
            "profile_image": f.profile_image,
            "bio": f.bio,
        }
        for f in followers
    ]


# get following list
@router.get("/me/following")
def my_following(
    db: Session = Depends(get_db), current_user: User = Depends(verify_token)
):
    following = (
        db.query(User)
        .join(Follow, Follow.following_id == User.id)
        .filter(Follow.follower_id == current_user.id)
        .all()
    )
    return [
        {
            "id": f.id,
            "username": f.username,
            "email": f.email,
            "followers_count": len(f.followers),
            "following_count": len(f.following),
            "profile_image": f.profile_image,
            "bio": f.bio,
        }
        for f in following
    ]


#toggle update privacy
@router.patch("/privacy")
def update_privacy(db: Session = Depends(get_db),current_user: User=Depends(verify_token)):
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.is_private = not user.is_private
        db.commit()
        db.refresh(user)
        
        return{
            "id": user.id,
            "username": user.username,
            "is_private": user.is_private,
            "message": f"Privacy set to {'private' if user.is_private else 'Public'}"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


#admin delete account
@router.delete("/admin/delete-account/{id}")
def admin_delete_account(id: int, db:Session=Depends(get_db),admin: User=Depends(validate_admin)):
    try:
        user = db.query(User).filter(User.id == id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return {"message":"user deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=(e))
    
    

#user delete account
@router.delete("/me/delete")
def self_delete_account(db:Session=Depends(get_db), current_user: User = Depends(verify_token)):
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return{
            "message":"Account deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
