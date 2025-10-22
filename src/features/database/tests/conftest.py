import pytest
import os
import sys
import tempfile

# Add src to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from features.database.implementations import db

@pytest.fixture
def temp_db():
    """Create a temporary database for each test"""
    # Create a temporary file
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize the database
    database = db.BibliographyDB(db_path)
    
    yield database
    
    # Cleanup: close connection and delete file
    database.conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)