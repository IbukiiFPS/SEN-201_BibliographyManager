import sqlite3
from datetime import datetime
from typing import cast

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

    def add_entry(self, authors: str, title: str, **kwargs) -> int:
        if not authors.strip() or not title.strip():
            raise ValueError("Authors and Title are required")
        created_at = datetime.utcnow().isoformat()
        cols = ["authors","title","venue","year","volume","number","pages","doi","url","tags","created_at"]
        vals = [authors.strip(), title.strip(),
                kwargs.get("venue"), kwargs.get("year"), kwargs.get("volume"),
                kwargs.get("number"), kwargs.get("pages"), kwargs.get("doi"),
                kwargs.get("url"), kwargs.get("tags"), created_at]
        qmarks = ",".join(["?"]*len(cols))
        sql = f"INSERT INTO entries ({','.join(cols)}) VALUES ({qmarks})"
        c = self.conn.cursor()
        c.execute(sql, vals)
        self.conn.commit()
        return cast(int, c.lastrowid)

    def list_entries(self):
        c = self.conn.cursor()
        c.execute("SELECT id, authors, title, venue, year, tags, created_at FROM entries ORDER BY created_at DESC")
        return c.fetchall()

    def close(self):
        self.conn.close()