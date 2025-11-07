from __future__ import annotations
import sqlite3
from src.features.database.db import BibliographyDB

def add_entry_to_set(db: BibliographyDB, set_id: int, entry_id: int):
    c = db.conn.cursor()
    try:
        c.execute("INSERT INTO set_entries (set_id, entry_id) VALUES (?,?)", (set_id, entry_id))
        db.conn.commit()
    except sqlite3.IntegrityError:
        pass

def remove_entry_from_set(db: BibliographyDB, set_id: int, entry_id: int):
    c = db.conn.cursor()
    c.execute("DELETE FROM set_entries WHERE set_id = ? AND entry_id = ?", (set_id, entry_id))
    db.conn.commit()

def list_entries_in_set(db: BibliographyDB, set_id: int):
    c = db.conn.cursor()
    c.execute(
        """SELECT e.id, e.authors, e.title, e.venue, e.year, e.publication_date, e.tags, e.created_at
           FROM entries e JOIN set_entries s ON e.id = s.entry_id
           WHERE s.set_id = ? ORDER BY e.created_at DESC""",                (set_id,),            )
    return c.fetchall()
