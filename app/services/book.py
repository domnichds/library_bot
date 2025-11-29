from pathlib import Path

from sqlalchemy import select

from ..models.book import Book, BookFile
from ..models.db import async_session_factory

async def get_book_files(book_id: int) -> list[BookFile]:
    """
    Возвращает список объектов BookFile для указанной книги.

    Используется при формировании клавиатуры форматов: каждый BookFile
    представляет отдельный файл (fb2/pdf/epub и т.п.) для данного book_id.

    Всегда возвращает список, который может быть пустым.
    """
    async with async_session_factory() as session:
            result = await session.execute(
                select(BookFile).
                where(BookFile.book_id == book_id)
            )
            # scalars() извлекает именно объекты BookFile, а не сырые строки
            book_files = list(result.scalars().all())
    return book_files

async def get_book_file_path(book_id: int, format_: str) -> Path | None:
    """
    Определяет относительный путь к файлу книги по её id и запрошенному формату, 
    дополнительно проверяя, что формат соответствует callback_data. 

    - Возвращает Path(relative_path) относительно BOOKS_DIR_STORAGE
    - Возвращает None, если файл с такими параметрами не найден в БД.
    """
    async with async_session_factory() as session:
        result = await session.execute(
            select(BookFile).
            where(BookFile.book_id == book_id,
                  BookFile.format == format_)
        )

        book_file = result.scalar_one_or_none()
        if book_file is None:
            return None
        # В БД хранится как строка, приводим к Path для удобства
        path = Path(book_file.path)

        return path

async def get_book_name(book_id: int) -> str:
    """
    Получает название и автора книги по её ID.

    - Всегда возвращает строку.
    - Если книга не найдена - возвращает строку "Неизвестная книга".
    """
    async with async_session_factory() as session:
        book = await session.execute(
            select(Book).
            where(Book.id == book_id)
        )
        book_obj = book.scalar_one_or_none()
        if book_obj is None:
            return "Неизвестная книга"
        return f"{book_obj.title} — {book_obj.author}"