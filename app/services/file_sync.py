from pathlib import Path
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config_storage import BOOKS_DIR_STORAGE, GENRE_MAP
from app.models.db import async_session_factory
from app.models.book import Genre, Book, BookFile


@dataclass
class BookData:
    """
    Простая структура для данных о книге, извлечённых из пути к файлу.
    """
    genre: str
    title: str
    author: str
    format: str


def parse_file_path(file_path: Path) -> BookData:
    """
    Получаем информацию о книге по пути к файлу.

    Ожидаемая структура пути относительно BOOKS_DIR_STORAGE:
        /<genre_slug>/<Название> - <Автор>.<расширение>

    Например:
        /fantasy/Hobbit - Tolkien.fb2

    Вернёт:
        BookData(
            genre='fantasy',
            title='Hobbit',
            author='Tolkien',
            format='fb2',
        )
    """
    rel_path = file_path.relative_to(BOOKS_DIR_STORAGE)
    path = rel_path.parts

    if len(path) < 2:
        raise ValueError("Неверный путь к хранилищу книг")

    # Получаем название жанра и полное имя файла
    genre_slug = path[0]
    file_name = path[-1]

    if "." not in file_name:
        raise ValueError(f"В файле {file_name} отсутствует расширение")

    name_part, ext = file_name.rsplit(".", 1)
    format_ = ext.lower()

    if " - " not in name_part:
        raise ValueError(f"Не могу разделить название и автора: {file_name}")

    title, author = name_part.split(" - ", 1)
    title = title.strip()
    author = author.strip()

    # genre здесь — ключ/slug жанра (например, 'fantasy')
    genre = genre_slug

    # Приводим путь к POSIX-стилю (если понадобится — можно использовать rel_path_str)
    rel_path_str = str(rel_path).replace("\\", "/")

    return BookData(genre=genre, title=title, author=author, format=format_)


async def get_or_create_genre(session: AsyncSession, genre_slug: str) -> Genre:
    """
    Получаем или создаём жанр по его slug'у.

    В БД жанр хранится человекочитаемым именем (например, "Фэнтези"),
    а slug (например, "fantasy") маппится через GENRE_MAP.
    """
    display_name = GENRE_MAP.get(genre_slug, genre_slug)

    result = await session.execute(
        select(Genre).where(Genre.name == display_name)
    )
    genre = result.scalar_one_or_none()

    if genre:
        return genre

    genre = Genre(name=display_name)
    session.add(genre)
    await session.flush()
    return genre


async def get_or_create_book(
    session: AsyncSession,
    genre: Genre,
    book_data: BookData,
) -> Book:
    """
    Получаем или создаём книгу в рамках конкретного жанра.

    Книга считается той же самой, если совпадают:
      - genre_id,
      - title,
      - author.
    """
    result = await session.execute(
        select(Book).where(
            Book.genre_id == genre.id,
            Book.title == book_data.title,
            Book.author == book_data.author,
        )
    )
    book = result.scalar_one_or_none()
    if book:
        return book

    book = Book(
        title=book_data.title,
        author=book_data.author,
        genre=genre,
    )
    session.add(book)
    await session.flush()
    return book


async def get_or_create_book_file(
    session: AsyncSession,
    book: Book,
    format_: str,
    rel_path: str,
) -> BookFile:
    """
    Получаем или создаём файловый вариант книги (конкретный формат и путь).

    Условие уникальности:
      - одна запись BookFile на пару (book_id, format_).

    Если запись уже есть, просто обновляем путь (на случай, если файл
    был перемещён в файловой системе).
    """
    result = await session.execute(
        select(BookFile).where(
            BookFile.book_id == book.id,
            BookFile.format == format_,
        )
    )
    bf = result.scalar_one_or_none()
    if bf:
        bf.path = rel_path
        return bf

    bf = BookFile(
        book_id=book.id,
        format=format_,
        path=rel_path,
    )

    session.add(bf)
    await session.flush()
    return bf


async def sync_book_from_fs() -> None:
    """
    Обойти локальный каталог BOOKS_DIR_STORAGE и синхронизировать содержимое с БД.

    Алгоритм:
      - рекурсивно ищем все файлы в BOOKS_DIR_STORAGE;
      - для каждого файла:
          * парсим путь в BookData;
          * находим/создаём Genre;
          * находим/создаём Book;
          * находим/создаём BookFile (формат + относительный путь).
    """
    if not BOOKS_DIR_STORAGE.exists():
        raise ValueError(f"Директория {BOOKS_DIR_STORAGE} не существует")

    async with async_session_factory() as session:
        for file_path in BOOKS_DIR_STORAGE.rglob("*"):
            if not file_path.is_file():
                continue

            try:
                book_data = parse_file_path(file_path)
            except ValueError as e:
                print(f"Ошибка при разборе файла {file_path}: {e}")
                continue

            genre = await get_or_create_genre(session, book_data.genre)
            book = await get_or_create_book(session, genre, book_data)
            rel_path = str(file_path.relative_to(BOOKS_DIR_STORAGE)).replace("\\", "/")
            await get_or_create_book_file(session, book, book_data.format, rel_path)

        await session.commit()