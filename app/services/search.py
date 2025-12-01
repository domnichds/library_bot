from typing import List, Tuple

from rapidfuzz import fuzz
from sqlalchemy import or_, select, func

from app.config.search import SEARCH_LIMIT, SEARCH_MIN_SCORE
from app.models.book import Book
from app.models.db import async_session_factory


# Сколько максимум кандидатов брать из БД перед RapidFuzz
CANDIDATES_LIMIT = 1000


def _book_key(book: Book) -> str:
    """
    Строка, по которой считаем похожесть.
    """
    return f"{book.title} — {book.author}"


async def _get_candidates_from_db(query: str) -> List[Book]:
    """
    Достаём из БД кандидатов по отдельным словам запроса.
    Не требуем точного совпадения всей фразы, чтобы дать шанс
    RapidFuzz догадаться при опечатках.
    """
    words = [w.strip() for w in query.split() if w.strip()]
    if not words:
        return []

    async with async_session_factory() as session:
        conditions = []

        for w in words:
            pattern = f"%{w.lower()}%"
            conditions.append(
                or_(
                    func.lower(Book.title).like(pattern),
                    func.lower(Book.author).like(pattern),
                )
            )

        where_clause = or_(*conditions)

        stmt = (
            select(Book)
            .where(where_clause)
            .limit(CANDIDATES_LIMIT)
        )

        result = await session.execute(stmt)
        books: List[Book] = list(result.scalars().all())
        return books


async def search_books(
    query: str,
    limit: int = SEARCH_LIMIT,
    min_score: int = SEARCH_MIN_SCORE,
) -> List[Book]:
    """
    Поиск книг с учётом опечаток (RapidFuzz), но без выкачивания всей
    таблицы в память.
    """
    q = (query or "").strip()
    if not q:
        return []

    candidates = await _get_candidates_from_db(q)
    if not candidates:
        return []

    results: List[Tuple[Book, float]] = []

    for book in candidates:
        key = _book_key(book)
        score = fuzz.WRatio(q, key)
        if score >= min_score:
            results.append((book, score))

    results.sort(key=lambda item: item[1], reverse=True)

    best_books: List[Book] = [item[0] for item in results[:limit]]

    return best_books