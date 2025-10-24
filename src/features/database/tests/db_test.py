import features.database.db as db
import pytest

def test_connect_db(temp_db):
    database = temp_db
    assert database.conn is not None
    database.close()

def test_close_db(temp_db):
    database = temp_db
    database.close()
    with pytest.raises(Exception):
        database.conn.execute("SELECT 1")