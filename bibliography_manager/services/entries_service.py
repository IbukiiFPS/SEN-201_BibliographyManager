import re
from typing import Any, Dict, List, Sequence, Tuple
from ..db import BibliographyDB

class EntriesService:
    def init(self, db: BibliographyDB) -> None:
        self.db = db