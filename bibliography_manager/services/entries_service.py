import re
from typing import Any, Dict, List, Sequence, Tuple
from ..db import BibliographyDB

class EntriesService:
    def init(self, db: BibliographyDB) -> None:
        self.db = db
        
    def add(self, data: Dict[str, Any]) -> int:
        # Minimal validation
        if not data.get("authors","").strip() or not data.get("title","").strip():
            raise ValueError("Authors and Title are required")
        year = data.get("year")
        if isinstance(year, str) and year.strip() == "":
            data["year"] = None