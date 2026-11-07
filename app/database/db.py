
import sqlite3
from pathlib import Path

# Locate the main project directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Database file location
DB_PATH = BASE_DIR / "data" / "adops.db"


def get_connection():
    """Create and return a SQLite database connection."""
    return sqlite3.connect(DB_PATH)
