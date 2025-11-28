from sqlalchemy import select
from pathlib import Path

from ..models.book import BookFile
from ..models.db import async_session_factory

async def get_book_files(book_id: int) -> list[BookFile]:
    """
    Вернуть все файловые варианты (форматы) для указанной книги.

    Используется при показе клавиатуры форматов:
    каждый объект BookFile соответствует одному конкретному файлу
    (fb2/pdf/epub и т.п.) для книги с данным book_id.
    """
    async with async_session_factory() as session:
            result = await session.execute(
                select(BookFile).
                where(BookFile.book_id == book_id)
            )
            # scalars() извлекает именно объекты BookFile, а не сырые строки
            book_files = list(result.scalars().all())
    return book_files

async def get_book_file_path(file_id: int, format_: str) -> Path | None:
    """
    Найти относительный путь к файлу книги по id файла и формату.

    Формат дополнительно проверяется, чтобы убедиться, что пользователь
    действительно запрашивает тот тип файла, который был в callback_data.

    Возвращает:
      - Path(relative_path) — относительный путь от BOOKS_DIR_STORAGE,
      - None, если файл с такими параметрами не найден в БД.
    """
    async with async_session_factory() as session:
        result = await session.execute(
            select(BookFile).
            where(BookFile.id == file_id,
                  BookFile.format == format_)
        )

        book_file = result.scalar_one_or_none()
        if book_file is None:
            return None
        # В БД хранится как строка, приводим к Path для удобства
        path = Path(book_file.path)

        return path

