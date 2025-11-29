from typing import List

from sqlalchemy import func, select

from ..models.book import Book, Genre
from ..models.db import async_session_factory

async def get_all_genres() -> List[Genre]:
    """
    Возвращает все жанры отсортированные по имени.

    Используется для построения главного каталога жанров.
    """
    async with async_session_factory() as session:
        result = await session.execute(
            select(Genre).order_by(Genre.name)
        )
        return list(result.scalars().all())

async def get_books_page_by_genre(
        genre_id: int,
        page: int,
        page_size: int = 10,
    ) -> tuple[List[Book], int]:
    """
    Получает одну страницу списка книг для указанного жанра.

    Параметры:
      - genre_id: id жанра, по которому фильтруем книги.
      - page: номер страницы (1-based). Если он выходит за допустимый диапазон,
        будет автоматически "подрезан" до ближайшего корректного.
      - page_size: количество книг на одной странице.

    Возвращает:
      - список книг для текущей страницы;
      - общее количество страниц total_pages (0, если в жанре нет книг).
    """
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
    
