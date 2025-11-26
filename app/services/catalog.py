from typing import List

from sqlalchemy import select

from app.models.db import async_session_factory
from app.models.book import Genre, Book

async def get_all_genres() -> List[Genre]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Genre).order_by(Genre.name)
        )
        return list(result.scalar().all())

async def get_all_books(genre_id: int) -> List[Book]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Book).
            where(Book.genre_id == genre_id).
            order_by(Book.title)
        )
        return list(result.scalar().all())
