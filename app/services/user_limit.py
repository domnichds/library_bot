from datetime import date
from typing import Tuple

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from app.models.db import async_session_factory
from app.models.user_limit import UserLimit

DAILY_LIMIT = 10

async def get_user_count(user_id: int) -> int:
    """
    Возвращает текущее количество запросовов пользователя за сегодня.
    """
    today = date.today()
    async with async_session_factory() as session:
        res = await session.execute(
            select(UserLimit).where(
                UserLimit.user_id == user_id,
                UserLimit.date == today
            )
        )
        record = res.scalar_one_or_none()
        return int(record.count) if record else 0
    
async def check_daily_limit(user_id: int) -> bool:
    """
    Проверяет, не превышен ли дневной лимит пользователя.
    Возвращает True, если лимит не превышен, иначе False.
    """
    current_count = await get_user_count(user_id)
    return current_count < DAILY_LIMIT

async def increment_daily_count(user_id: int) -> Tuple[int, bool]:
    """
    Увеличивает счётчик запросов пользователя за сегодня на 1.
    Возвращает (новый_счётчик, True), если пользователь использует впервые.
    Возвращает (текущий_счётчик, False), если пользователь уже исчерпал лимит.
    """
    today = date.today()
    async with async_session_factory() as session:
        stmt = select(UserLimit).where(
            UserLimit.user_id == user_id,
            UserLimit.date == today
        ).with_for_update()
        res = await session.execute(stmt)
        record = res.scalar_one_or_none()
        
        if record is None:
            record = UserLimit(user_id=user_id, date=today, count=1)
            session.add(record)
            await session.commit()

            return 1, True

        if record.count >= DAILY_LIMIT:
            return record.count, False
        
        record.count += 1
        session.add(record)
        await session.commit()
        return record.count, True
        