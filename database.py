from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from config import settings


engine = create_async_engine(settings.database_url)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

Base = declarative_base()
