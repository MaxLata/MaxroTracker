from __future__ import annotations

import sqlite3
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
MIGRATIONS_DIR = PACKAGE_DIR / "migrations"
SEEDS_DIR = PACKAGE_DIR / "seeds"
DEFAULT_DB_PATH = Path("data/maxro_tracker.sqlite")


def initialize_database(db_path: Path = DEFAULT_DB_PATH, seed: bool = True) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        _run_sql_files(connection, MIGRATIONS_DIR)
        if seed:
            _run_sql_files(connection, SEEDS_DIR)

    return db_path


def _run_sql_files(connection: sqlite3.Connection, directory: Path) -> None:
    for sql_file in sorted(directory.glob("*.sql")):
        connection.executescript(sql_file.read_text())

