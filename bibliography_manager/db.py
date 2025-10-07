import sqlite3
from datetime import datetime

DB_FILE = "bibliography.db"

class BibliographyDB:
    def __init__(self, db_file: str = DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY,
                authors TEXT NOT NULL,
                title TEXT NOT NULL,
                venue TEXT,
                year INTEGER,
                volume TEXT,
                number TEXT,
                pages TEXT,
                doi TEXT,
                url TEXT,
                tags TEXT,
                created_at TEXT NOT NULL
            )''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS refsets (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            )''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS set_entries (
                set_id INTEGER,
                entry_id INTEGER,
                PRIMARY KEY(set_id, entry_id),
                FOREIGN KEY(set_id) REFERENCES refsets(id) ON DELETE CASCADE,
                FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE
            )''')
        self.conn.commit()