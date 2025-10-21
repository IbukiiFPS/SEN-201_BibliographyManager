import features.database.implentaions.db as db

def test_connect_db(temp_db):
    database = temp_db
    assert database.conn is not None
    database.close()
