from __future__ import annotations
from src.features.database.db import BibliographyDB
from src.features.database.operation import refset_ops, set_entries_ops

class RefsetsService:
    def __init__(self, db: BibliographyDB):
        self.db = db

    def create(self, name: str) -> int:
        return refset_ops.create_refset(self.db, name)

    def delete(self, set_id: int):
        return refset_ops.delete_refset(self.db, set_id)

    def list(self):
        return refset_ops.list_refsets(self.db)

    def add_entry(self, set_id: int, entry_id: int):
        return set_entries_ops.add_entry_to_set(self.db, set_id, entry_id)

    def remove_entry(self, set_id: int, entry_id: int):
        return set_entries_ops.remove_entry_from_set(self.db, set_id, entry_id)

    def list_entries(self, set_id: int):
        return set_entries_ops.list_entries_in_set(self.db, set_id)
