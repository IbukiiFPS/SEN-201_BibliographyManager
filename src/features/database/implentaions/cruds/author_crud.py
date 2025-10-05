# author_crud.py
from sqlalchemy.orm import Session
from models.author_model import Author
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any
from sqlalchemy import select, inspect
from sqlalchemy.exc import SQLAlchemyError



class AuthorRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        
    # ---------- CREATE ----------
    def create_author(self, first_name: str, last_name: str, middle_name: Optional[str] = None) -> Author:
        with self.db.get_session() as session: 
            try:
                author = Author(first_name=first_name, middle_name=middle_name, last_name=last_name)
                session.add(author)
                session.commit()        
                session.refresh(author) 
                return author
            except:
                session.rollback()
                raise

    # ---------- READ ----------

    def get_all_authors(self) -> list[Author]:
        return self.db_session.query(Author).all()

    def get_author_by_id(self, author_id: int) -> Author | None:
        return self.db_session.query(Author).filter(Author.id == author_id).first()

    # ---------- UPDATE ----------
    def update_author(self, author_id: int, updates: Dict[str, Any]) -> Optional["Author"]:
        pass
    
    # ---------- DELETE ----------
    def delete_author(self, author_id: int) -> bool:
        pass