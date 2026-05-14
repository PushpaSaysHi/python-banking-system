"""
database.py — Database connection and table creation
"""

import sqlite3
from config import DB_FILE


def get_connection():
    """Open and return a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row          # access columns by name
    conn.execute("PRAGMA foreign_keys = ON")  # enforce foreign keys
    return conn


def setup_database():
    """Create all tables if they don't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()

    # accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id          TEXT PRIMARY KEY,
            owner_name          TEXT NOT NULL,
            pin_hash            TEXT NOT NULL,
            email               TEXT,
            account_type        TEXT NOT NULL,
            interest_rate       REAL NOT NULL,
            balance             REAL DEFAULT 0,
            last_interest_date  TEXT NOT NULL,
            is_locked           INTEGER DEFAULT 0,
            failed_attempts     INTEGER DEFAULT 0
        )
    """)

    # transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id  TEXT NOT NULL,
            date        TEXT NOT NULL,
            type        TEXT NOT NULL,
            amount      REAL NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        )
    """)

    # login activity log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id  TEXT NOT NULL,
            date        TEXT NOT NULL,
            status      TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        )
    """)

    conn.commit()
    conn.close()
