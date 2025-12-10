from datetime import date

from sqlalchemy import Integer, UniqueConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base

class UserLimit(Base):
    __tablename__ = "user_daily_limits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Обеспечиваем уникальность записи для каждого пользователя на каждую дату
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_user_daily_limit_user_date"),
    )

    def __repr__(self) -> str:
        return f"UserLimit(id={self.id!r}, user_id={self.user_id!r}, date={self.date!r}, count={self.count!r})"

