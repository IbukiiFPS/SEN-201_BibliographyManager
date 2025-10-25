
import sqlite3
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

DB_FILE = "bibliography.db"

class BibliographyDB:
    def __init__(self, db_file: str = DB_FILE) -> None:
        # Enable foreign keys right after connecting
        self.conn = sqlite3.connect(db_file)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()

    def _create_tables(self) -> None:
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
            );
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS refsets (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            );
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS set_entries (
                set_id INTEGER,
                entry_id INTEGER,
                PRIMARY KEY (set_id, entry_id),
                FOREIGN KEY(set_id) REFERENCES refsets(id) ON DELETE CASCADE,
                FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE
            );
        ''')
        self.conn.commit()

    # ---------- Entry operations ----------
    def add_entry(self, authors: str, title: str, venue: Optional[str] = None,
                  year: Optional[int] = None, volume: Optional[str] = None,
                  number: Optional[str] = None, pages: Optional[str] = None,
                  doi: Optional[str] = None, url: Optional[str] = None,
                  tags: Optional[str] = None) -> int:
        if not authors.strip() or not title.strip():
            raise ValueError("Authors and Title are required")
        created_at = datetime.utcnow().isoformat()
        c = self.conn.cursor()
        c.execute(
            '''INSERT INTO entries (authors, title, venue, year, volume, number, pages, doi, url, tags, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (authors.strip(), title.strip(), venue, year, volume, number, pages, doi, url, tags, created_at)
        )
        self.conn.commit()
        return c.lastrowid

    def update_entry(self, entry_id: int, **kwargs: Any) -> None:
        if not kwargs:
            return
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)
        values.append(entry_id)
        sql = f"UPDATE entries SET {', '.join(fields)} WHERE id = ?"
        c = self.conn.cursor()
        c.execute(sql, values)
        self.conn.commit()

    def delete_entry(self, entry_id: int) -> None:
        c = self.conn.cursor()
        c.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        # rows in set_entries will cascade
        self.conn.commit()

    def list_entries(self, where_clause: Optional[str] = None, params: Sequence[Any] = ()) -> List[Tuple]:
        c = self.conn.cursor()
        sql = 'SELECT id, authors, title, venue, year, tags, created_at FROM entries'
        if where_clause:
            sql += ' WHERE ' + where_clause
        sql += ' ORDER BY created_at DESC'
        c.execute(sql, params)
        return c.fetchall()

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        c = self.conn.cursor()
        c.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
        row = c.fetchone()
        if not row:
            return None
        cols = [d[0] for d in c.description]
        return dict(zip(cols, row))

    # ---------- Ref set operations ----------
    def create_refset(self, name: str) -> int:
        created_at = datetime.utcnow().isoformat()
        c = self.conn.cursor()
        c.execute('INSERT INTO refsets (name, created_at) VALUES (?, ?)', (name, created_at))
        self.conn.commit()
        return c.lastrowid

    def delete_refset(self, set_id: int) -> None:
        c = self.conn.cursor()
        c.execute('DELETE FROM refsets WHERE id = ?', (set_id,))
        # Explicit cleanup is redundant due to cascade; kept for clarity
        c.execute('DELETE FROM set_entries WHERE set_id = ?', (set_id,))
        self.conn.commit()

    def list_refsets(self) -> List[Tuple]:
        c = self.conn.cursor()
        c.execute('SELECT id, name, created_at FROM refsets ORDER BY name')
        return c.fetchall()

    def add_entry_to_set(self, set_id: int, entry_id: int) -> None:
        c = self.conn.cursor()
        try:
            c.execute('INSERT INTO set_entries (set_id, entry_id) VALUES (?, ?)', (set_id, entry_id))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # already exists or FK violation
            pass

    def remove_entry_from_set(self, set_id: int, entry_id: int) -> None:
        c = self.conn.cursor()
        c.execute('DELETE FROM set_entries WHERE set_id = ? AND entry_id = ?', (set_id, entry_id))
        self.conn.commit()

    def list_entries_in_set(self, set_id: int) -> List[Tuple]:
        c = self.conn.cursor()
        c.execute('''
            SELECT e.id, e.authors, e.title, e.venue, e.year, e.tags, e.created_at
            FROM entries e
            JOIN set_entries s ON e.id = s.entry_id
            WHERE s.set_id = ?
            ORDER BY e.created_at DESC
        ''', (set_id,))
        return c.fetchall()

    def close(self) -> None:
        self.conn.close()
