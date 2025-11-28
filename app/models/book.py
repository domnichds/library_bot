from typing import List

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Связь "один ко многим" с Book
    books: Mapped[List["Book"]] = relationship(
        back_populates="genre",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Genre(id={self.id!r}, name={self.name!r})"
    
class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(200), nullable=False)

    # Внешний ключ на Genre
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genres.id", ondelete="CASCADE"),
        nullable=False
    )

    # Связь "много к одному" с Genre
    genre: Mapped[Genre] = relationship(back_populates="books")

    # Связь "один ко многим" с BookFile
    files: Mapped[List["BookFile"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Book(id={self.id!r}, title={self.title!r}, author={self.author!r})"
    
class BookFile(Base):
    __tablename__ = "book_files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Внешний ключ на Book
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False
    )

    format: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)

    # Связь "много к одному" с Book
    book: Mapped[Book] = relationship(back_populates="files")

    def __repr__(self) -> str:
        return (
            f"BookFile(id={self.id!r}, book_id={self.book_id!r}, "
            f"format={self.format!r}, path={self.path!r})"
        )
