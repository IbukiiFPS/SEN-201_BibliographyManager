========================================================================= test session starts ==========================================================================
platform darwin -- Python 3.11.10, pytest-8.3.4, pluggy-1.5.0 -- /Users/ratchanonkhongsawi/anaconda3/bin/python
cachedir: .pytest_cache
rootdir: /Users/ratchanonkhongsawi/Desktop/CMKL/3rd/Software Eng/project
configfile: pytest.ini
testpaths: src/features/database/tests
plugins: typeguard-4.3.0, anyio-4.7.0
collected 23 items                                                                                                                                                     

src/features/database/tests/db_test.py::test_connect_db PASSED                                                                                                   [  4%]
src/features/database/tests/db_test.py::test_close_db PASSED                                                                                                     [  8%]
src/features/database/tests/entry_set_test.py::test_create_entry_set PASSED                                                                                      [ 13%]
src/features/database/tests/entry_set_test.py::test_delete_entry_set PASSED                                                                                      [ 17%]
src/features/database/tests/entry_set_test.py::test_list_entry_sets PASSED                                                                                       [ 21%]
src/features/database/tests/entry_set_test.py::test_list_entries_in_empty_set PASSED                                                                             [ 26%]
src/features/database/tests/entry_set_test.py::test_add_and_remove_entry_in_set PASSED                                                                           [ 30%]
src/features/database/tests/entry_set_test.py::test_remove_entry_from_set PASSED                                                                                 [ 34%]
src/features/database/tests/entry_set_test.py::test_add_existing_entry_to_set PASSED                                                                             [ 39%]
src/features/database/tests/entry_test.py::test_add_valid_entry PASSED                                                                                           [ 43%]
src/features/database/tests/entry_test.py::test_add_entry_missing_required_field PASSED                                                                          [ 47%]
src/features/database/tests/entry_test.py::test_add_entry_empty_optional_field PASSED                                                                            [ 52%]
src/features/database/tests/entry_test.py::test_list_entries PASSED                                                                                              [ 56%]
src/features/database/tests/entry_test.py::test_list_entries_with_where_clause PASSED                                                                            [ 60%]
src/features/database/tests/entry_test.py::test_list_entries_no_match PASSED                                                                                     [ 65%]
src/features/database/tests/entry_test.py::test_get_entry_id PASSED                                                                                              [ 69%]
src/features/database/tests/entry_test.py::test_get_non_existing_entry_id PASSED                                                                                 [ 73%]
src/features/database/tests/entry_test.py::test_get_entry_by_id PASSED                                                                                           [ 78%]
src/features/database/tests/entry_test.py::test_get_non_existing_entry_by_id PASSED                                                                              [ 82%]
src/features/database/tests/entry_test.py::test_delete_entry PASSED                                                                                              [ 86%]
src/features/database/tests/entry_test.py::test_delete_non_existing_entry PASSED                                                                                 [ 91%]
src/features/database/tests/entry_test.py::test_update_entry PASSED                                                                                              [ 95%]
src/features/database/tests/entry_test.py::test_update_entry_no_fields PASSED                                                                                    [100%]

========================================================================== 23 passed in 0.08s ==========================================================================