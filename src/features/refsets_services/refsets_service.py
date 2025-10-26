from typing import List, Tuple
from ..database.db import BibliographyDB

class RefSetsService:
    def __init__(self, db: BibliographyDB) -> None:
        self.db = db

    def create(self, name: str) -> int:
        name = (name or "").strip()
        if not name:
            raise ValueError("Set name cannot be empty")
        return self.db.create_refset(name)

    def delete(self, set_id: int) -> None:
        self.db.delete_refset(set_id)

    def list(self) -> List[Tuple]:
        return self.db.list_refsets()

    def add_entry(self, set_id: int, entry_id: int) -> None:
        self.db.add_entry_to_set(set_id, entry_id)

    def remove_entry(self, set_id: int, entry_id: int) -> None:
        self.db.remove_entry_from_set(set_id, entry_id)

    def list_entries(self, set_id: int) -> List[Tuple]:
        return self.db.list_entries_in_set(set_id)