class RefSetsService:
    def __init__(self, db: BibliographyDB) -> None:
        self.db = db

    def create(self, name: str) -> int:
        name = (name or "").strip()
        if not name:
            raise ValueError("Set name cannot be empty")
        return self.db.create_refset(name)
