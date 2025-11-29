from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Используем абсолютный путь к файлу БД, чтобы не зависеть от текущей рабочей директории
DB_PATH = Path(__file__).resolve().parents[0] / "library.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH.as_posix()}"

# Базовый класс для всех ORM-моделей
class Base(DeclarativeBase):
    pass

# Создаем асинхронный движок для SQLite
engine = create_async_engine(
    DATABASE_URL,
    echo=True # Включаем вывод SQL для отладки
)

# Фабррика асинхронных сессий
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Иницилизация БД и создание таблиц (если еще не созданы)
async def init_db() -> None:
    # Импорт моделей внутри функции, чтобы гарантировать регистрацию метаданных
    from .book import Genre, Book, BookFile

    print(f"Иницилизация базы данных по пути: {DB_PATH}")
    print(f"Используется DATABASE_URL: {DATABASE_URL}")

    async with engine.begin() as conn:
        # run_sync ожидает синхронную функцию; передаём ссылку на create_all
        await conn.run_sync(Base.metadata.create_all)
    print("Инициализация базы данных завершена")