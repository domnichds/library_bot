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

async def get_books_page_by_genre(
        genre_id: int,
        page: int,
        page_size: int = 10,
    ) -> tuple[List[Book], int]:

    async with async_session_factory() as session:
        # Подсчитываем общее количество книг в жанре
        count_result = await session.execute(
            select(func.count()).
            select_from(Book).
            where(Book.genre_id == genre_id)
        )
        total_count = count_result.scalar_one() or 0

        if total_count == 0:
            return [], 0
        
        total_pages = (total_count + page_size - 1) // page_size
        # Защита от выхода за диапазон
        page = max(1, min(page, total_pages))
        offset = (page - 1) * page_size

        # Выбираем книги для текущей страницы
        result = await session.execute(
            select(Book).
            where(Book.genre_id == genre_id).
            order_by(Book.title).
            offset(offset).
            limit(page_size)
        )
        books = list(result.scalars().all())

        return books, total_pages
    
