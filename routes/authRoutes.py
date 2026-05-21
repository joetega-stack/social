from fastapi import APIRouter,Response,Depends,HTTPException,status
from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from lib.database import get_db
from models.userModel import User
from utils.crypto import hash_password,verify,create_token




router=APIRouter(prefix="/auth",tags=['Auth'])


class LoginUser(BaseModel):
    password: str
    email: str

class SignUpItem(BaseModel):
    username: str
    email: str
    password: str
    # admin: bool
    
class Found(BaseModel):
    token_version: int
    


#register user
@router.post("/register")
def register_user(user: SignUpItem,db: Session = Depends(get_db)):
    try:
        newUser = User(
            username = user.username,
            password= hash_password(user.password),
            email= user.email,
            # admin=user.admin
        )
        db.add(newUser)
        db.commit()
        db.refresh(newUser)
        status.HTTP_201_CREATED
        return {"message": "user created"}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already exists")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    
#login user
@router.post("/login")
def login_user(user: LoginUser,db: Session = Depends(get_db)):
    try:
        found = db.query(User).filter(User.email == user.email).first()
        if not found:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not verify(user.password, found.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        found.token_version += 1
        db.commit()
        token = create_token({"username":found.username,"id":found.id,"token_version":found.token_version,"admin":found.admin})
        return {"access_token": token,"token_type": "bearer"}
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error during login")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
