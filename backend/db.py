import sqlite3

def get_db_connection():
    """
    Establish a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A connection object to the SQLite database.
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Enable accessing columns by name
    return conn