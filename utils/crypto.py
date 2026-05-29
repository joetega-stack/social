from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException
from jose import jwt,ExpiredSignatureError
from dotenv import load_dotenv
from os import getenv
from pathlib import Path
from datetime import datetime,timedelta,timezone
from sqlalchemy.orm import Session
from lib.database import get_db
from models.userModel import User

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)

secret = getenv("SECRET")

ALGORITHM= "HS256"
expires = 60

hash_context = CryptContext(schemes=['argon2'],deprecated="auto")
oauth = OAuth2PasswordBearer(tokenUrl="login")

def get_user_by_id(id: int,db:Session):
    try:
        found = db.query(User).get(id)
        return found
    except Exception as err:
        raise err
    
def create_token(body: dict):
    if not secret:
        raise RuntimeError("SECRET is not set")
    encode = body.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires)
    encode.update({"exp":expire})
    
    return jwt.encode(encode,secret,algorithm=ALGORITHM)

def verify_token(token = Depends(oauth),db: Session= Depends(get_db)):
    try:
        value = jwt.decode(token,str(secret),algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(400,detail="Token expired")
    except:
        raise HTTPException(400,detail="Invalid jwt")
    
    id = value["id"]
    found = get_user_by_id(id,db)
    if not found:
        raise HTTPException(status_code=400,detail="Invalid token")
    if not value["token_version"] == found.token_version:
        raise HTTPException(status_code=400,detail="Expired Token")
    return found

def validate_admin(token = Depends(oauth),db:Session= Depends(get_db)):
    user = verify_token(token,db)
    return user.admin

def hash_password(password):
    hashed = hash_context.hash(password)
    return hashed

def verify(password, hashed):
    v= hash_context.verify(password, hashed)
    return v
