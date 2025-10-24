import pytest
import features.database.db as db
import conftest

# Add entry tests
def test_add_valid_entry(temp_db):
    database = temp_db
    kwargs = {
        "authors": "Doe, J.",
        "title": "Sample Title",
        "venue": "Sample Venue",
        "year": 2023,
        "volume": "1",
        "number": "1",
        "pages": "1-10",
        "doi": "10.1000/sampledoi",
        "url": "http://example.com",
        "tags": "sample, test"
    }
    entry_id = database.add_entry(**kwargs)
    assert isinstance(entry_id, int)
    
def test_add_entry_missing_required_field(temp_db):
    database = temp_db
    kwargs = {
        "title": "Sample Title Without Authors"
    }
    with pytest.raises(ValueError) as excinfo:
        database.add_entry(**kwargs)
    assert "Authors is required" in str(excinfo.value)

def test_add_entry_empty_optional_field(temp_db):
    database = temp_db
    kwargs = {
        "authors": "Smith, A.",
        "title": "Title with Empty Optional Fields",
        "venue": "",
        "year": None,
        "volume": "",
        "number": "",
        "pages": "",
        "doi": "",
        "url": "",
        "tags": ""
    }
    entry_id = database.add_entry(**kwargs)
    assert isinstance(entry_id, int)


# List entries tests
def test_list_entries(temp_db):
    database = temp_db
    database.add_entry(authors="Doe, J.", title="First Entry")
    database.add_entry(authors="Smith, A.", title="Second Entry")
    entries = database.list_entries()
    assert isinstance(entries, list)
    for entry in entries:
        assert isinstance(entry, tuple)
        
def test_list_entries_with_where_clause(temp_db):
    database = temp_db
    kwargs = {
        "authors": "Doe, J.",
        "title": "Unique Title for Listing"
    }
    database.add_entry(**kwargs)
    entries = database.list_entries("authors = ?", ("Doe, J.",))
    assert any(entry[1] == "Doe, J." for entry in entries)
    
    
def test_list_entries_no_match(temp_db):
    database = temp_db
    entries = database.list_entries("authors = ?", ("Non Existing Author",))
    assert len(entries) == 0
    

# Get entry ID by title
def test_get_entry_id(temp_db):
    database = temp_db
    kwargs = {
        "authors": "Johnson, K.",
        "title": "Unique Title for ID Test"
    }
    database.add_entry(**kwargs)
    entry_id = database.get_entry_id_by_title("Unique Title for ID Test")
    assert isinstance(entry_id, int)
    assert entry_id > 0

    
def test_get_non_existing_entry_id(temp_db):
    database = temp_db
    non_existing_title = "This Title Does Not Exist"
    entry_id = database.get_entry_id_by_title(non_existing_title)
    assert entry_id is None
    

# Get entry by ID
def test_get_entry_by_id(temp_db):
    database = temp_db
    kwargs = {
        "authors": "Williams, S.",
        "title": "Entry for Get by ID Test"
    }
    database.add_entry(**kwargs)
    entry_id = database.get_entry_id_by_title("Entry for Get by ID Test")
    entry = database.get_entry(entry_id)
    assert entry is not None
    assert entry['id'] == entry_id
    assert entry['authors'] == "Williams, S."
    assert entry['title'] == "Entry for Get by ID Test" 
    
    
def test_get_non_existing_entry_by_id(temp_db):
    database = temp_db
    non_existing_id = 999999
    entry = database.get_entry(non_existing_id)
    assert entry is None
    

# Delete entry tests
def test_delete_entry(temp_db):
    database = temp_db
    kwargs = {
        "authors": "Smith, A.",
        "title": "Entry to be deleted"
    }
    entry_id = database.add_entry(**kwargs)
    database.delete_entry(entry_id)
    entries = database.list_entries("id = ?", (entry_id,))
    assert len(entries) == 0
    
    
def test_delete_non_existing_entry(temp_db):
    database = temp_db
    non_existing_id = 999999
    # Should not raise an error
    database.delete_entry(non_existing_id)
    entries = database.list_entries("id = ?", (non_existing_id,))
    assert len(entries) == 0
    

# Update entry tests
def test_update_entry(temp_db):
    database = temp_db
    kwargs = {
        "authors": "Brown, B.",
        "title": "Original Title"
    }
    database.add_entry(**kwargs)
    entry_id = database.get_entry_id_by_title("Original Title")
    database.update_entry(entry_id, title="Updated Title")
    entries = database.list_entries("id = ?", (entry_id,))
    assert len(entries) == 1
    assert entries[0][2] == "Updated Title"  # title is the third field
    
    
def test_update_entry_no_fields(temp_db):
    database = temp_db
    kwargs = {
        "authors": "Green, G.",
        "title": "Title Before No-Op Update"
    }
    entry_id = database.add_entry(**kwargs)
    # No fields to update
    database.update_entry(entry_id)
    entries = database.list_entries("id = ?", (entry_id,))
    assert len(entries) == 1
    assert entries[0][2] == "Title Before No-Op Update"  # title is the third field
    
    
