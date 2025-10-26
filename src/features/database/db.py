
import sqlite3
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .operation import entry_ops
from .operation import entry_set_ops

DB_FILE = "bibliography.db"

class BibliographyDB:
    def __init__(self, db_file: str = DB_FILE) -> None:
        # Enable foreign keys right after connecting
        try:
            self.conn = sqlite3.connect(db_file)
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise
        
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
                publication_date TEXT,
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
    def add_entry(self, **kwargs: Any) -> int:
        return entry_ops.add_entry(self.conn, **kwargs)

    def update_entry(self, entry_id: int, **kwargs: Any) -> None:
        return entry_ops.update_entry(self.conn, entry_id, **kwargs)
    
    def delete_entry(self, entry_id: int) -> None:
        return entry_ops.delete_entry(self.conn, entry_id)
    
    def list_entries(self, where_clause: Optional[str] = None, params: Sequence[Any] = ()) -> List[Tuple]:
        return entry_ops.list_entries(self.conn, where_clause, params)
    
    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        return entry_ops.get_entry(self.conn, entry_id)
    
    def get_entry_id_by_title(self, title: str) -> Optional[int]:
        return entry_ops.get_entry_id_by_title(self.conn, title)
    
    # ---------- Ref set operations ----------
    def create_refset(self, name: str) -> int:
        return entry_set_ops.create_refset(self.conn, name)
    
    def delete_refset(self, set_id: int) -> None:
        return entry_set_ops.delete_refset(self.conn, set_id)
    
    def list_refsets(self) -> List[Tuple]:
        return entry_set_ops.list_refsets(self.conn)
    
    def add_entry_to_set(self, set_id: int, entry_id: int) -> None:
        return entry_set_ops.add_entry_to_set(self.conn, set_id, entry_id)
    
    def remove_entry_from_set(self, set_id: int, entry_id: int) -> None:
        return entry_set_ops.remove_entry_from_set(self.conn, set_id, entry_id)
    
    def list_entries_in_set(self, set_id: int) -> List[Tuple]:
        return entry_set_ops.list_entries_in_set(self.conn, set_id)
    
    def get_refset_id_by_name(self, name: str) -> Optional[int]:
        return entry_set_ops.get_refset_id_by_name(self.conn, name)
    
    def close(self) -> None:
        self.conn.close()

