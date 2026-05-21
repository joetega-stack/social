from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload, selectinload
from lib.database import get_db
from utils.crypto import verify_token, validate_admin
from models.userModel import User
from models.postModel import Post
from models.followModel import Follow
from models.likeModel import Like
from models.commentModel import Comment
from pydantic import BaseModel
from typing import Optional


router = APIRouter(prefix="/posts", tags=["Posts"])


class createPost(BaseModel):
    content: Optional[str] = None
    media_url: Optional[str] = None
    visibility: Optional[str] = "public"


class updatePost(BaseModel):
    content: Optional[str] = None
    media_url: Optional[str] = None


class createComment(BaseModel):
    content: str
    



# create post
@router.post("/create")
def create_post(
    post: createPost,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token),
    admin=Depends(validate_admin),
):
    try:
        if not post.content and not post.media_url:
            raise HTTPException(
                status_code=400, detail="Post must contain content or media"
            )
        new_post = Post(
            content=post.content,
            media_url=post.media_url,
            visibility=post.visibility,
            user_id=current_user.id,
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        return {
            "message": "Post created successfully",
            "post": {
                "id": new_post.id,
                "author_id": new_post.user_id,
                "content": new_post.content,
                "visibility": new_post.visibility,
                "created_at": new_post.created_at,
                "media_url": new_post.media_url,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# get fetch one post by ID
@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = (
        db.query(Post)
        .options(joinedload(Post.comments), joinedload(Post.likes))
        .filter(Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/me")
def get_my_post(db: Session = Depends(get_db), current_user=Depends(verify_token)):
    return db.query(Post).filter(Post.user_id == current_user.id).all()


# get user post
@router.get("/user/{user_id}")
def get_user_post(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token),
    admin=Depends(validate_admin),
):
    if current_user.id != user_id and not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    posts = (
        db.query(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.likes),
            selectinload(Post.comments).selectinload(Comment.author),
        )
        .filter(Post.user_id == user_id)
        .all()
    )
    
    result = []

    for post in posts:
        result.append({
            "id":post.id,
            "content": post.content,
            "media_url": post.media_url,
            "visibility": post.visibility,
            "created_at": post.created_at,
            
            #user info from relationship
            "username": post.author.username,
            "profile_image": post.author.profile_image,
            
            #likes
            "likes_count": len(post.likes),
            
            "comments_count": len(post.comments),
            #comments
            "comments": [
                {
                    "id": c.id,
                    "content": c.content,
                    "created_at": c.created_at,
                    
                    #comment.author relationship
                    "username": c.author.username if c.author else None,
                    "profile_image": c.author.profile_image if c.author else None,
                }
                for c in sorted(post.comments, key=lambda x: x.created_at, reverse=True)[:2]
            ]
        })
        
    return result



@router.put("/update/{post_id}")
def update_post(
    post_id: int,
    update: updatePost,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this post",
        )
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return {"message": "Post updated successfully", "post": post}


@router.delete("/delete/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token),
    admin: bool = Depends(validate_admin),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if post.user_id != current_user.id and not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized"
        )
    db.delete(post)
    db.commit()
    return {"message": "Post successfully deleted", "deleted_post_id": post_id}


@router.get("/feed/public")
def public_feed(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
):
    posts = (
        db.query(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.likes),
            selectinload(Post.comments).selectinload(Comment.author),
        )
        .filter(Post.visibility == "public")
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []

    for post in posts:
        result.append({
            "id":post.id,
            "content": post.content,
            "media_url": post.media_url,
            "visibility": post.visibility,
            "created_at": post.created_at,
            
            #user info from relationship
            "username": post.author.username,
            "profile_image": post.author.profile_image,
            
            #likes
            "likes_count": len(post.likes),
            
            "comments_count": len(post.comments),
            #comments
            "comments": [
                {
                    "id": c.id,
                    "content": c.content,
                    "created_at": c.created_at,
                    
                    #comment.author relationship
                    "username": c.author.username if c.author else None,
                    "profile_image": c.author.profile_image if c.author else None,
                }
                for c in sorted(post.comments, key=lambda x: x.created_at, reverse=True)[:2]
            ]
        })
        
    return result



@router.get("/feed/following")
def following_feed(
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=50),
):
    following_ids = (
        db.query(Follow.follower_id)
        .filter(Follow.follower_id == current_user.id)
        .subquery()
    )
    posts = (
        db.query(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.likes),
            selectinload(Post.comments).selectinload(Comment.author),
        )
        .filter(Post.user_id.in_(following_ids))
        .filter(Post.visibility.in_(["public", "followers"]))
        .filter((Post.user_id.in_(following_ids)) | (Post.user_id == current_user.id))
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    result = []

    for post in posts:
        result.append({
            "id":post.id,
            "content": post.content,
            "media_url": post.media_url,
            "visibility": post.visibility,
            "created_at": post.created_at,
            
            #user info from relationship
            "username": post.author.username,
            "profile_image": post.author.profile_image,
            
            #likes
            "likes_count": len(post.likes),
            
            "comments_count": len(post.comments),
            #comments
            "comments": [
                {
                    "id": c.id,
                    "content": c.content,
                    "created_at": c.created_at,
                    
                    #comment.author relationship
                    "username": c.author.username if c.author else None,
                    "profile_image": c.author.profile_image if c.author else None,
                }
                for c in sorted(post.comments, key=lambda x: x.created_at, reverse=True)[:2]
            ]
        })
        
    return result

@router.post("/{post_id}/like")
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    like = (
        db.query(Like)
        .filter(Like.post_id == post_id, Like.user_id == current_user.id)
        .first()
    )
    if like:
        db.delete(like)
        db.commit()
        likes_count = db.query(Like).filter(Like.post_id == post_id).count()
        return {"message": "Post unliked", "liked": False, "likes_count": likes_count}
    new_like = Like(post_id=post_id, user_id=current_user.id)
    db.add(new_like)
    db.commit()

    likes_count = db.query(Like).filter(Like.post_id == post_id).count()
    return {"message": "Post liked", "liked": True, "likes_count": likes_count}


@router.get("/{post_id}/likes")
def get_likes(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    likes_count = db.query(Like).filter(Like.post_id == post_id).count()

    like = (
        db.query(Like)
        .filter(Like.post_id == post_id, Like.user_id == current_user.id)
        .first()
    )

    return {"liked": bool(like), "likes_count": likes_count}


@router.post("/{post_id}/comment")
def comment_post(
    post_id: int,
    comment: createComment,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    new_comment = Comment(
        content=comment.content, user_id=current_user.id, post_id=post_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    comments_count = db.query(Comment).filter(Comment.post_id == post_id).count()
    return {
        "message": "Comment add successfully",
        "comment": new_comment,
        "comments_count": comments_count,
    }


@router.get("/{post_id}/comments")
def get_comments(
    post_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=50),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    comments_query = (
        db.query(Comment, User.username, User.profile_image)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    comments = [
        {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at,
            "username": username,
            "profile_image": profile_image,
        }
        for comment, username, profile_image in comments_query
    ]

    return {"post_id": post_id, "count": len(comments), "comments": comments}
