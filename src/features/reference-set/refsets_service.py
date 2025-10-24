
from typing import List, Tuple
from ..database.db import BibliographyDB

class RefSetsService:
    def __init__(self, db: BibliographyDB) -> None:
        self.db = db