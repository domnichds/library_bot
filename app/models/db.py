from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ..config.bot import DATABASE_URL


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""
    pass


# Асинхронный движок для PostgreSQL
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)


# Фабрика асинхронных сессий
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def init_db() -> None:
    """
    Инициализирует базу данных: создаёт таблицы, если их ещё нет.
    """
    # импортируем модели внутри функции, чтобы зарегистрировать метаданные
    from .book import Genre, Book, BookFile
    from .user_limit import UserLimit

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)