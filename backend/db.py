import sqlite3
import os
from pathlib import Path

DB_PATH = Path(os.environ.get(
    "MOBILITY_DB",
    Path(__file__).resolve().parent.parent / "data-pipeline" / "mobility.db",
))

def get_db_connection():
    """
    Establish a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A connection object to the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable accessing columns by name
    return conn