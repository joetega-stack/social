from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from lib.database import get_db
from models.userModel import User
from models.followModel import Follow
from models.chatModel import Conversation
from models.messageModel import Message
from utils.crypto import verify_token

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/start/{target_user_id}")
def start_chat(
    target_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_token),
):
    if current_user.id == target_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    follow = (
        db.query(Follow)
        .filter(
            Follow.follower_id == current_user.id,
            Follow.following_id == target_user_id,
        )
        .first()
    )

    if not follow:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only message users you follow",
        )
    conversation = (
        db.query(Conversation)
        .filter(
            or_(
                and_(
                    Conversation.user_one_id == current_user.id,
                    Conversation.user_two_id == target_user_id,
                ),
                and_(
                    Conversation.user_one_id == target_user_id,
                    Conversation.user_two_id == current_user.id,
                ),
            )
        )
        .first()
    )

    if conversation:
        return {
           "message": "Conversation already exists",
           "conversation_id": conversation.id, 
        }
    new_conversation = Conversation(user_one_id=current_user.id, user_two_id=target_user_id)
    
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    
    return {
        "message": "Conversation created successfully",
        "conversation_id": new_conversation.id,
    }
    
    

@router.post("/{conversation_id}/message")
def send_message(conversation_id:int, content:str, db: Session=Depends(get_db),current_user:User=Depends(verify_token),):
    conversation = (db.query(Conversation).filter(Conversation.id == conversation_id).first())
    
    if not conversation:
        raise HTTPException(status_code=404,detail="Conversation not found",)
    
    if current_user.id not in [conversation.user_one_id, conversation.user_two_id]:
        raise HTTPException(status_code=403,detail="Not authorized",)
    
    message = Message(conversation_id=conversation.id, sender_id=current_user.id, content=content,)
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return {
        "message": "Message sent",
        "data": message,
    }