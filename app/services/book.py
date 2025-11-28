from sqlalchemy import select
from pathlib import Path

from ..models.book import BookFile
from ..models.db import async_session_factory

async def get_book_files(book_id: int) -> list[BookFile]:
    async with async_session_factory() as session:
            result = await session.execute(
                select(BookFile).
                where(BookFile.book_id == book_id)
            )
            book_files = list(result.scalars().all())
    return book_files

async def get_book_file_path(file_id: int, format_: str) -> Path | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(BookFile).
            where(BookFile.id == file_id,
                  BookFile.format == format_)
        )

        book_file = result.scalar_one_or_none()
        if book_file is None:
            return None
        path = Path(book_file.path)

        return path

