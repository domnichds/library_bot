from typing import List

from rapidfuzz import fuzz
from sqlalchemy import select

from ..models.book import Book
from ..models.db import async_session_factory

from ..config.search import (SEARCH_LIMIT, SEARCH_MIN_SCORE)

async def search_books(
        query: str,
        limit: int = SEARCH_LIMIT,
        min_score: int = SEARCH_MIN_SCORE
) -> List[Book]:
    """
    Поиск книг по свободному тексту (название/автор) с учётом опечаток.

    - Считаем fuzzy-похожесть запроса:
        * с названием,
        * с автором,
        * с "название + автор".
    - Берём максимум как итоговый score.
    - Отбрасываем результаты ниже min_score.
    - Сортируем по убыванию score и возвращаем top-N.
    """
    normolized_query = query.strip()
    if not normolized_query:
        return []

    async with async_session_factory() as session:
        result = await session.execute(
            select(Book)
        )
        all_books: List[Book] = list(result.scalars().all())

    scored: list[tuple[int, Book]] = []
    
    for book in all_books:
        title = book.title.strip()
        author = book.author.strip()
        combined = f"{title} {author}".strip()

        score_title = fuzz.WRatio(normolized_query, title)
        score_author = fuzz.WRatio(normolized_query, author)
        score_combined = fuzz.WRatio(normolized_query, combined)

        score = max(score_title, score_author, score_combined)

        if score >= min_score:
            scored.append((score, book))
        
    scored.sort(key=lambda item: item[0], reverse=True)

    top_books = [book for score, book in scored[:limit]]
    return top_books

    