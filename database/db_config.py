import asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config import settings

DB_URI = f"postgresql://{settings.postgres_db_user}:{settings.postgres_db_password}"
DB_URI += f"@{settings.postgres_db_host}:{settings.postgres_db_port}/{settings.postgres_db_name}"


engine = create_engine(DB_URI)
db_session = scoped_session(sessionmaker(bind=engine))

# async_engine = create_async_engine(DB_URI)
# async_db_session = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)


Base = declarative_base()
Base.query = db_session.query_property()