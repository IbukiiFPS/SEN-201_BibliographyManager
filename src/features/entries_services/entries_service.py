from __future__ import annotations
from typing import Iterable, Any
from src.features.database.db import BibliographyDB
from src.features.database.operation import entry_ops

class EntriesService:
    def __init__(self, db: BibliographyDB):
        self.db = db

    def add(self, **kwargs) -> int:
        return entry_ops.add_entry(self.db, **kwargs)

    def update(self, entry_id: int, **kwargs):
        return entry_ops.update_entry(self.db, entry_id, **kwargs)

    def delete(self, entry_id: int):
        return entry_ops.delete_entry(self.db, entry_id)

    def list(self, where_clause: str | None = None, params: Iterable[Any] = ()):
        return entry_ops.list_entries(self.db, where_clause, params)

    def get(self, entry_id: int) -> dict | None:
        return entry_ops.get_entry(self.db, entry_id)
