import re
from typing import List, Tuple, Set

from rapidfuzz import fuzz
from sqlalchemy import or_, select, func

from app.config.search import (
    AUTHOR_WEIGHT,
    CANDIDATES_LIMIT,
    SEARCH_LIMIT,
    SEARCH_MIN_SCORE,
    TITLE_WEIGHT,
)
from app.models.book import Book
from app.models.db import async_session_factory


# Русские (и общие) стоп‑слова, которые не будем учитывать при поиске кандидатов
STOPWORDS: Set[str] = {
    "и", "в", "на", "с", "по", "за", "о", "об", "не", "то", "же",
    "а", "я", "ты", "он", "она", "оно", "они", "как", "что", "к",
    "из", "от", "до", "для", "при", "его", "ее", "ее", "ли", "бы"
}


def _normalize_words(query: str) -> List[str]:
    """
    Извлекаем слова из запроса, приводим к нижнему регистру,
    убираем короткие слова и стоп-слова.
    """
    raw_words = re.findall(r"\w+", (query or "").lower(), flags=re.UNICODE)
    # Оставляем слова длиной >=3, убираем стоп-слова
    filtered = [w for w in raw_words if len(w) >= 3 and w not in STOPWORDS]
    return filtered


async def _get_candidates_from_db(query: str) -> List[Book]:
    """
    Берём кандидатов из БД по словам запроса, но игнорируем короткие и стоп-слова.
    Если после фильтрации слов ничего не осталось — делаем более широкую выборку по всей фразе.
    """
    words_filtered = _normalize_words(query)
    async with async_session_factory() as session:
        if words_filtered:
            conditions = []
            for w in words_filtered:
                pattern = f"%{w}%"
                conditions.append(func.lower(Book.title).like(pattern))
                conditions.append(func.lower(Book.author).like(pattern))

            where_clause = or_(*conditions)

            stmt = select(Book).where(where_clause).limit(CANDIDATES_LIMIT)
            result = await session.execute(stmt)
            books: List[Book] = list(result.scalars().all())
            return books

        # Если в запросе только стоп-слова / одна буква и т.п
        # Ищем по всей фразе (вплоть до обычного LIKE '%query%')
        q = (query or "").strip().lower()
        if not q:
            return []

        stmt = (
            select(Book)
            .where(
                or_(
                    func.lower(Book.title).like(f"%{q}%"),
                    func.lower(Book.author).like(f"%{q}%"),
                )
            )
            .limit(CANDIDATES_LIMIT)
        )
        result = await session.execute(stmt)
        books = list(result.scalars().all())
        return books


def _score_book(query: str, book: Book) -> float:
    """
    Комбинированный скор:
      - отдельно считаем метрики по title и author (несколько метрик RapidFuzz),
      - даём бонусы за точную фразу в названии и за совпавшие слова (не стоп-слова).
    """
    q = (query or "").strip()
    if not q:
        return 0.0

    q_lower = q.lower()
    title = (book.title or "").strip()
    author = (book.author or "").strip()
    title_lower = title.lower()
    author_lower = author.lower()

    # Разные метрики RapidFuzz — берем максимум, чтобы учесть разные типы схожести
    title_ratios = [
        fuzz.WRatio(q, title),
        fuzz.token_set_ratio(q, title),
        fuzz.partial_ratio(q, title),
    ]
    title_score = max(title_ratios)

    author_ratios = [
        fuzz.WRatio(q, author),
        fuzz.token_set_ratio(q, author),
        fuzz.partial_ratio(q, author),
    ]
    author_score = max(author_ratios)

    # Бонус за точное вхождение всей фразы в title
    if q_lower and q_lower in title_lower:
        title_score += 25.0

    # Бонусы за совпадающие (ненулевые) слова из запроса
    words_filtered = _normalize_words(q)
    if words_filtered:
        matched_title = sum(1 for w in words_filtered if w in title_lower)
        matched_author = sum(1 for w in words_filtered if w in author_lower)

        # Каждый совпавший слов даёт небольшой бонус; если все слова найдены — большой бонус
        title_score += matched_title * 6.0
        author_score += matched_author * 3.0

        if matched_title == len(words_filtered):
            title_score += 18.0

    # Собираем итоговый скор с приоритетом title
    total = TITLE_WEIGHT * title_score + AUTHOR_WEIGHT * author_score

    # Нормируем (необязательно) — ограничим сверху 100..200 диапазон не критичен, но можем не превышать 100
    if total > 100.0:
        total = 100.0

    return total


async def search_books(
    query: str,
    limit: int = SEARCH_LIMIT,
    min_score: int = SEARCH_MIN_SCORE,
) -> List[Book]:
    """
    Поиск книг с учётом опечаток (RapidFuzz), но улучшенный выбор кандидатов и скоринг.
    """
    q = (query or "").strip()
    if not q:
        return []

    candidates = await _get_candidates_from_db(q)
    if not candidates:
        return []

    results: List[Tuple[Book, float]] = []

    for book in candidates:
        score = _score_book(q, book)
        if score >= min_score:
            results.append((book, score))

    # сортируем по убыванию score
    results.sort(key=lambda item: item[1], reverse=True)

    best_books: List[Book] = [item[0] for item in results[:limit]]

    return best_books