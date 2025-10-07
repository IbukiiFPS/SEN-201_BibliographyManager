# author_crud.py
from sqlalchemy.orm import Session
from models.author_model import Author
from sqlalchemy.exc import IntegrityError
from typing import Optional, Dict, Any
from sqlalchemy import column, select, inspect
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
    
    def get_author_by(self, **kwargs: Any) -> Optional[Author]:
        valid_columns = {column.key for column in inspect(Author).mapper.column_attrs}
        filters = {key: value for key, value in kwargs.items() if key in valid_columns}
        if not filters:
            raise ValueError("No valid columns provided for filtering.")
        sql = select(Author).filter_by(**filters)
        result = self.db_session.execute(sql).scalars().all()
        return result

    # ---------- UPDATE ----------
    def update_author(self, author_id: int, updates: Dict[str, Any]) -> "Author":
        try:
            author = self.db_session.get(Author, author_id)
            if author is None:
                raise ValueError(f"Author with id {author_id} not found.")

            # Whitelist: only allow column attributes except PK
            mapper = inspect(Author)
            updatable_cols = {
                attr.key
                for attr in mapper.attrs
                if getattr(attr, "columns", None)  # column property (not relationship)
            }
            # Don’t allow changing the primary key
            pk_names = {col.key for col in mapper.primary_key}
            updatable_cols -= pk_names

            # Apply updates that are allowed
            for key, value in updates.items():
                if key in updatable_cols:
                    setattr(author, key, value)
                else:
                    # You can choose to ignore silently or raise:
                    raise AttributeError(f"Attribute '{key}' is not updatable.")

            self.db_session.commit()
            self.db_session.refresh(author)
            return author

        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise

    # ---------- DELETE ----------
    def delete_author(self, author_id: int) -> bool:
        try:
            author = self.db_session.get(Author, author_id)
            if author is None:
                raise ValueError(f"Author with id {author_id} not found.")
            self.db_session.delete(author)
            self.db_session.commit()
            return True
        except IntegrityError as e:
            self.db_session.rollback()
            raise ValueError(f"Integrity error: {str(e)}")
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise