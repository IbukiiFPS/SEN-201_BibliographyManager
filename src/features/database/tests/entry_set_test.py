# create entry set tests
def test_create_entry_set(temp_db):
    database = temp_db
    database.create_refset("Test Set")
    entry_set_id = database.get_refset_id_by_name("Test Set")
    assert isinstance(entry_set_id, int)
    assert entry_set_id > 0

# delete entry set tests
def test_delete_entry_set(temp_db):
    database = temp_db
    set_id = database.create_refset("Set to be deleted")
    database.delete_refset(set_id)
    entry_sets = database.list_refsets()
    assert all(es[0] != set_id for es in entry_sets)
    
# list entry sets tests
def test_list_entry_sets(temp_db):
    database = temp_db
    set_name = "List Test Set"
    database.create_refset(set_name)
    entry_sets = database.list_refsets()
    assert any(es[1] == set_name for es in entry_sets)

def test_list_entries_in_empty_set(temp_db):
    database = temp_db
    set_id = database.create_refset("Empty Set Test")
    entries_in_set = database.list_entries_in_set(set_id)
    assert len(entries_in_set) == 0

# add and remove entry in set tests
def test_add_and_remove_entry_in_set(temp_db):
    database = temp_db
    set_id = database.create_refset("Set for Add/Remove Test")
    kwargs = {
        "authors": "Doe, J.",
        "title": "Sample Entry for Set Test"
    }
    entry_id = database.add_entry(**kwargs)
    
    database.add_entry_to_set(set_id, entry_id)
    entries_in_set = database.list_entries_in_set(set_id)
    assert any(e[0] == entry_id for e in entries_in_set)
    
def test_remove_entry_from_set(temp_db):
    database = temp_db
    set_id = database.create_refset("Set for Remove Entry Test")
    kwargs = {
        "authors": "Doe, J.",
        "title": "Sample Entry for Removal Test"
    }
    entry_id = database.add_entry(**kwargs)
    database.add_entry_to_set(set_id, entry_id)
    database.remove_entry_from_set(set_id, entry_id)
    entries_in_set_after_removal = database.list_entries_in_set(set_id)
    assert all(e[0] != entry_id for e in entries_in_set_after_removal)

    entries_in_set = database.list_entries_in_set(set_id)
    assert all(e[0] != entry_id for e in entries_in_set)

    
def test_add_existing_entry_to_set(temp_db):
    database = temp_db
    set_id = database.create_refset("Set for Existing Entry Test")
    kwargs = {
        "authors": "Smith, A.",
        "title": "Another Sample Entry for Set Test"
    }
    entry_id = database.add_entry(**kwargs)
    database.add_entry_to_set(set_id, entry_id)
    entries_in_set = database.list_entries_in_set(set_id)
    assert any(e[0] == entry_id for e in entries_in_set)
    
