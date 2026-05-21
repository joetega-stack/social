from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from os import getenv

load_dotenv()

database_url = getenv("CONNECTION_STRING")

if not database_url:
    raise ValueError("CONNECTION_STRING is not set in environment variables")
    
engine = create_engine(database_url)

Sessionmaker = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = Sessionmaker()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()