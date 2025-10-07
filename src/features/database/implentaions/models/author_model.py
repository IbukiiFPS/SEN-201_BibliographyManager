# author_model.py
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from database_connector import Base

class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    middle_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=False)