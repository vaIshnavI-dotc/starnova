"""SQLite connection helper."""
import sqlite3
from pathlib import Path
from pipeline.config import DB_PATH


def get_connection(path: Path = DB_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)
