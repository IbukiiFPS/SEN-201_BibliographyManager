from __future__ import annotations
from typing import Any, Iterable

from src.features.database.db import BibliographyDB

def _norm_text(s: str | None) -> str:
    return (s or "").strip().lower()

def _norm_pubdate(s: str | None) -> str:
    return (s or "").strip()

def find_duplicate_id(db: BibliographyDB, authors: str, title: str, publication_date: str | None, exclude_id: int | None = None) -> int | None:
    nt = _norm_text(title)
    na = _norm_text(authors)
    npd = _norm_pubdate(publication_date)
    c = db.conn.cursor()
    if exclude_id is None:
        c.execute("""
            SELECT id FROM entries
            WHERE lower(trim(title)) = ?
              AND lower(trim(authors)) = ?
              AND ifnull(trim(publication_date), '') = ?
            LIMIT 1
        """, (nt, na, npd))
    else:
        c.execute("""
            SELECT id FROM entries
            WHERE lower(trim(title)) = ?
              AND lower(trim(authors)) = ?
              AND ifnull(trim(publication_date), '') = ?
              AND id <> ?
            LIMIT 1
        """, (nt, na, npd, exclude_id))
    row = c.fetchone()
    return row[0] if row else None

def add_entry(db: BibliographyDB, **kwargs) -> int:
    authors = (kwargs.get("authors") or "").strip()
    title = (kwargs.get("title") or "").strip()
    if not authors or not title:
        raise ValueError("Authors and Title are required")

    dup_id = find_duplicate_id(db, authors, title, kwargs.get("publication_date"))
    if dup_id is not None:
        raise ValueError(f"Duplicate entry detected (same Title + Authors + Publication Date) as id {dup_id}")

    created_at = db.utcnow_iso()
    c = db.conn.cursor()
    c.execute(
        """INSERT INTO entries
           (authors, title, venue, year, publication_date, volume, number, pages, doi, url, tags, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",                (                    authors,                    title,                    kwargs.get("venue"),                    kwargs.get("year"),                    kwargs.get("publication_date"),                    kwargs.get("volume"),                    kwargs.get("number"),                    kwargs.get("pages"),                    kwargs.get("doi"),                    kwargs.get("url"),                    kwargs.get("tags"),                    created_at,                ),            )
    db.conn.commit()
    return c.lastrowid

def update_entry(db: BibliographyDB, entry_id: int, **kwargs):
    if not kwargs:
        return
    c = db.conn.cursor()
    c.execute("SELECT authors, title, publication_date FROM entries WHERE id = ?", (entry_id,))
    row = c.fetchone()
    if not row:
        raise ValueError("Entry not found")
    cur_authors, cur_title, cur_pubdate = row
    new_authors = kwargs.get("authors", cur_authors)
    new_title = kwargs.get("title", cur_title)
    new_pubdate = kwargs.get("publication_date", cur_pubdate)

    dup_id = find_duplicate_id(db, new_authors, new_title, new_pubdate, exclude_id=entry_id)
    if dup_id is not None:
        raise ValueError(f"Update would create a duplicate of id {dup_id} (same Title + Authors + Publication Date)")

    fields, values = [], []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(entry_id)
    sql = f"UPDATE entries SET {', '.join(fields)} WHERE id = ?"
    c.execute(sql, values)
    db.conn.commit()

def delete_entry(db: BibliographyDB, entry_id: int):
    c = db.conn.cursor()
    c.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    db.conn.commit()

def list_entries(db: BibliographyDB, where_clause: str | None = None, params: Iterable[Any] = ()):
    c = db.conn.cursor()
    sql = "SELECT id, authors, title, venue, year, publication_date, tags, created_at FROM entries"
    if where_clause:
        sql += " WHERE " + where_clause
    sql += " ORDER BY created_at DESC"
    c.execute(sql, tuple(params) if params else ())
    return c.fetchall()

def get_entry(db: BibliographyDB, entry_id: int) -> dict | None:
    c = db.conn.cursor()
    c.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    row = c.fetchone()
    if not row:
        return None
    cols = [d[0] for d in c.description]
    return dict(zip(cols, row))
