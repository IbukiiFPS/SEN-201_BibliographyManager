
import features.bibtex.implementations.bibtex as bibtex

# create entry set tests
def test_export_bibtex(temp_db):
    database = temp_db
    kwargs = {
        "authors": "Test Set",
        "title": "A test entry set"
    }
    entry_set_id = database.add_entry(**kwargs)
    assert isinstance(entry_set_id, int)
    assert entry_set_id > 0
    entry = database.get_entry(entry_set_id)
    bibtex_str = bibtex.entry_to_bibtex(entry)
    
    assert isinstance(bibtex_str, str)
    assert "@misc" in bibtex_str  # Check for entry type
    assert "author = {Test Set}" in bibtex_str  # Check for author field
    assert "title = {A test entry set}" in bibtex_str  # Check for title field  

