import os
import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'LSamovar69')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'aiohttp')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

DSN = (f'postgresql+asyncpg://'
       f'{POSTGRES_USER}:{POSTGRES_PASSWORD}@'
       f'{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')

engine = create_async_engine(DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):

    @property
    def post_id(self):
        return {'id': self.id}


class Post(Base):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    @property
    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime.datetime) else None
        }


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()
