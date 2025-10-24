import re
from typing import Any, Dict, List, Sequence, Tuple
from ..database.db import BibliographyDB

class EntriesService:
    def __init__(self, db: BibliographyDB) -> None:
        self.db = db

    def add(self, data: Dict[str, Any]) -> int:
        # Minimal validation
        if not data.get("authors","").strip() or not data.get("title","").strip():
            raise ValueError("Authors and Title are required")
        year = data.get("year")
        if isinstance(year, str) and year.strip() == "":
            data["year"] = None
        elif year is not None:
            if isinstance(year, str) and not re.match(r"^\d{4}$", year):
                raise ValueError("Year must be a 4-digit year")
            if isinstance(year, str):
                data["year"] = int(year)
        return self.db.add_entry(**data)

    def list(self) -> List[Tuple]:
        return self.db.list_entries()