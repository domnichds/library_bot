from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./library.db"

# Базовый класс для всех ORM-моделей
class Base(DeclarativeBase):
    pass

# Создаем асинхронный движок для SQLite
engine = create_async_engine(
    DATABASE_URL,
    echo=False # Флаг отлдаки
)

# Фабррика асинхронных сессий
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Иницилизация БД и создание таблиц (если еще не созданы)
async def init_db() -> None:
    async with engine.begin() as conn:
        from app.models.book import Genre, Book, BookFile
        await conn.run_sync(Base.metadata.create_all)