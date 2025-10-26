import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

# ---------- Entry operations ----------

def add_entry(connector: sqlite3.Connection, **kwargs) -> int:
    """
    Adds a new bibliographic entry using keyword arguments.
    Required fields: authors, title
    Optional fields: venue, year, volume, number, pages, doi, url, tags
    """
    required_fields = ['authors', 'title']
    optional_fields = ['venue', 'year', 'publication_date', 'volume', 'number', 'pages', 'doi', 'url', 'tags']

    # Validate required fields
    for field in required_fields:
        if field not in kwargs or not str(kwargs[field]).strip():
            raise ValueError(f"{field.capitalize()} is required")

    # Prepare values
    created_at = datetime.utcnow().isoformat()
    values = [kwargs.get(field) for field in required_fields + optional_fields] + [created_at]
    sql = f"INSERT INTO entries ({', '.join(required_fields + optional_fields)}, created_at) VALUES ({', '.join(['?'] * len(values))})"
    # Build SQL dynamically (but safely)
    cursor = connector.cursor()
    cursor.execute( sql, values)
    connector.commit()
    return cursor.lastrowid

def update_entry(connector: sqlite3.Connection, entry_id: int, **kwargs: Any) -> None:
    if not kwargs:
        return
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(entry_id)
    sql = f"UPDATE entries SET {', '.join(fields)} WHERE id = ?"
    cursor = connector.cursor()
    cursor.execute(sql, values)
    connector.commit()

def delete_entry(connector: sqlite3.Connection, entry_id: int) -> None:
    cursor = connector.cursor()
    cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
    # rows in set_entries will cascade
    connector.commit()

def list_entries(connector: sqlite3.Connection, where_clause: Optional[str] = None, params: Sequence[Any] = ()) -> List[Tuple]:
    cursor = connector.cursor()
    sql = 'SELECT id, authors, title, venue, year, publication_date, tags, created_at FROM entries'
    if where_clause:
        sql += ' WHERE ' + where_clause
    sql += ' ORDER BY created_at DESC'
    cursor.execute(sql, params)
    return cursor.fetchall()

def get_entry(connector: sqlite3.Connection, entry_id: int) -> Optional[Dict[str, Any]]:
    cursor = connector.cursor()
    cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
    row = cursor.fetchone()
    if not row:
        return None
    cols = [d[0] for d in cursor.description]
    return dict(zip(cols, row))

def get_entry_id_by_title(connector: sqlite3.Connection, title: str) -> Optional[int]:
    cursor = connector.cursor()
    cursor.execute('SELECT id FROM entries WHERE title = ?', (title,))
    row = cursor.fetchone()
    if not row:
        return None
    return row[0]