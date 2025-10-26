    
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple

# ---------- Ref set operations ----------
def create_refset(connector: sqlite3.Connection, name: str) -> int:
    created_at = datetime.utcnow().isoformat()
    cursor = connector.cursor()
    cursor.execute('INSERT INTO refsets (name, created_at) VALUES (?, ?)', (name, created_at))
    connector.commit()
    return cursor.lastrowid

def delete_refset(connector: sqlite3.Connection, set_id: int) -> None:
    cursor = connector.cursor()
    cursor.execute('DELETE FROM refsets WHERE id = ?', (set_id,))
    # Explicit cleanup is redundant due to cascade; kept for clarity
    cursor.execute('DELETE FROM set_entries WHERE set_id = ?', (set_id,))
    connector.commit()

def list_refsets(connector: sqlite3.Connection) -> List[Tuple]:
    cursor = connector.cursor()
    cursor.execute('SELECT id, name, created_at FROM refsets ORDER BY name')
    return cursor.fetchall()

def add_entry_to_set(connector: sqlite3.Connection, set_id: int, entry_id: int) -> None:
    cursor = connector.cursor()
    try:
        cursor.execute('INSERT INTO set_entries (set_id, entry_id) VALUES (?, ?)', (set_id, entry_id))
        connector.commit()
    except sqlite3.IntegrityError:
        # already exists or FK violation
        pass

def remove_entry_from_set(connector: sqlite3.Connection, set_id: int, entry_id: int) -> None:
    cursor = connector.cursor()
    cursor.execute('DELETE FROM set_entries WHERE set_id = ? AND entry_id = ?', (set_id, entry_id))
    connector.commit()

def list_entries_in_set(connector: sqlite3.Connection, set_id: int) -> List[Tuple]:
    cursor = connector.cursor()
    cursor.execute('''
        SELECT e.id, e.authors, e.title, e.venue, e.year, e.publication_date, e.tags, e.created_at
        FROM entries e
        JOIN set_entries s ON e.id = s.entry_id
        WHERE s.set_id = ?
        ORDER BY e.created_at DESC
    ''', (set_id,))
    return cursor.fetchall()

def get_refset_id_by_name(connector: sqlite3.Connection, name: str) -> Optional[int]:
    cursor = connector.cursor()
    cursor.execute('SELECT id FROM refsets WHERE name = ?', (name,))
    row = cursor.fetchone()
    return row[0] if row else None