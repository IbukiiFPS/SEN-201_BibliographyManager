# database_connector.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, scoped_session

class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass

class DatabaseConnector:
    def __init__(self, db_url: str, echo: bool = True):
        self.db_url = db_url
        self.engine = create_engine(self.db_url, echo=echo)
        self.SessionLocal = scoped_session(
            sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        )

    def create_all_tables(self):
        """Create all tables defined by models that inherit from Base."""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        return self.SessionLocal()

    def close(self):
        self.SessionLocal.remove()
        
    def update(self, instance, **updates):
        pass
    
    def query(self, model, **filters):
        pass
        
    def alter(self, instance, **updates):
        pass
        
    def delete(self, instance):
        pass
    

