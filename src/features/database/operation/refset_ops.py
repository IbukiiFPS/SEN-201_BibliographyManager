from __future__ import annotations
from src.features.database.db import BibliographyDB

def create_refset(db: BibliographyDB, name: str) -> int:
    created_at = db.utcnow_iso()
    c = db.conn.cursor()
    c.execute("INSERT INTO refsets (name, created_at) VALUES (?, ?)", (name, created_at))
    db.conn.commit()
    return c.lastrowid

def delete_refset(db: BibliographyDB, set_id: int):
    c = db.conn.cursor()
    c.execute("DELETE FROM refsets WHERE id = ?", (set_id,))
    c.execute("DELETE FROM set_entries WHERE set_id = ?", (set_id,))
    db.conn.commit()

def list_refsets(db: BibliographyDB):
    c = db.conn.cursor()
    c.execute("SELECT id, name, created_at FROM refsets ORDER BY name")
    return c.fetchall()
