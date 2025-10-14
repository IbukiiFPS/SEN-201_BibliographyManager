import sqlite3
from datetime import datetime

def create_connection(db_name="bibliography.db"):
    """Connect to SQLite database or create it."""
    conn = sqlite3.connect(db_name)
    return conn

def setup_database(conn):
    """Create table if not exists."""
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                title TEXT NOT NULL,
                publication TEXT,
                pub_date TEXT,
                doi TEXT,
                url TEXT,
                tags TEXT,
                created_at TEXT
            )
        """)

def add_reference(conn, author, title, publication=None, pub_date=None, doi=None, url=None, tags=None):
    """Add a new bibliographic reference."""
    # Simple validation
    if not author or not title:
        print("Author and title are required.")
        return

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with conn:
        conn.execute("""
            INSERT INTO references (author, title, publication, pub_date, doi, url, tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (author, title, publication, pub_date, doi, url, tags, created_at))

    print("Reference added.")

# ------------------------------
# Example Usage
# ------------------------------

if __name__ == "__main__":
    conn = create_connection()
    setup_database(conn)

    # Example: add one reference
    add_reference(
        conn,
        author="Ada Lovelace",
        title="Notes on the Analytical Engine",
        publication="Scientific Memoirs",
        pub_date="1843",
        doi=None,
        url="https://example.com/lovelace1843",
        tags="computing, history"
    )
