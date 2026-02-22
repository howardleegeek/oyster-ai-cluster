from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from sqlalchemy.orm import declarative_base


settings = get_settings()
SQLALCHEMY_DATABASE_URL = f"mysql://{settings.db_user}:{settings.db_passwd}@{settings.db_host}/{settings.db_name}"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_recycle=3600,
    pool_size=settings.db_pool_size,
    max_overflow=5,
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

