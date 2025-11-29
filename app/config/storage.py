from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

BOOKS_DIR_STORAGE = BASE_DIR / "storage" / "books"

GENRE_MAP = {
    "fantasy": "Фантастика",
    "detective": "Детектив",
    "romance": "Любовный роман",
    "thriller": "Триллер",
    "classic": "Классика",
    "adventure": "Приключения",
}
