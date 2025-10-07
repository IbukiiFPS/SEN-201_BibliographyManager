class RefSetsService:
    def __init__(self, db: BibliographyDB) -> None:
        self.db = db

    def create(self, name: str) -> int:
        name = (name or "").strip()
        if not name:
            raise ValueError("Set name cannot be empty")
        return self.db.create_refset(name)
    
    def list(self) -> List[Tuple]:
        return self.db.list_refsets()
    
    def delete(self, refset_id: int) -> None:  
        self.db.delete_refset(refset_id)