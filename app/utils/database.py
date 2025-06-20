from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy import create_engine
from app.utils.settings import settings


def get_db_engine(test_mode: bool = False): 
    DATABASE_URL = settings.DB_URL
    if DATABASE_URL.startswith("sqlite"):
        return create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        return create_engine(DATABASE_URL)


engine = get_db_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db_session = scoped_session(SessionLocal)

Base = declarative_base()


def create_database():
    return Base.metadata.create_all(bind=engine)


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()