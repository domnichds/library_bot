from typing import List

from sqlalchemy import select, func

from ..models.book import Book
from ..models.db import async_session_factory
from ..config.search import SEARCH_LIMIT


FTS_LANGUAGE = "russian"
ALPHA = 0.8
MIN_SIMILARITY = 0.15

async def search_books(
        query: str,
        limit: int = SEARCH_LIMIT,
) -> List[Book]:
    """
    Поиск книг в PostgreSQL с учётом опечаток.

    - Основной поиск: FTS по колонке Book.search_vector.
    - Ранжирование: комбинированный скор rank + similarity по "title + author".
    - Если FTS ничего не нашёл — fallback на триграммы.

    Требования в БД:
      - столбец books.search_vector tsvector
      - индекс:
          CREATE INDEX idx_books_search_vector
          ON books USING gin (search_vector);
      - расширения pg_trgm (для similarity и %)
    """
    normolized_query = query.strip().lower()
    if not normolized_query:
        return []

    async with async_session_factory() as session:
        ta = Book.title + " " + Book.author
        
        # Превращаем запрос в tsquery
        tsq = func.plainto_tsquery(FTS_LANGUAGE, normolized_query)
        # Получаем ссылку на колонку tsvector
        tvs = Book.search_vector

        # Считаем похожесть запроса и колонки title+author (0 - менее похожи, 1 - идентичны)
        rank_expr = func.ts_rank_cd(tvs, tsq)
        # Считаем похожесть по триграммам (1 - идентичны, 0 - не похожи )
        sim_expr = func.similarity(func.lower(ta), normolized_query)

        combined_score = rank_expr * ALPHA + sim_expr * (1 - ALPHA)

        stmt_fts = (
            select(Book)
            .where(tvs.op("@@")(tsq))
            .order_by(combined_score.desc())
            .limit(limit)
        )

        res_fts = await session.execute(stmt_fts)
        books_fts: List[Book] = list(res_fts.scalars().all())

        if books_fts:
            return books_fts

        stmt_trgm = (
            select(Book)
            .where(func.lower(ta).op("%")(normolized_query)) 
            .where(sim_expr >= MIN_SIMILARITY)
            .order_by(sim_expr.desc())
            .limit(limit)
        )

        res_trgm = await session.execute(stmt_trgm)
        books_trgm: List[Book] = list(res_trgm.scalars().all())

        return books_trgm

    