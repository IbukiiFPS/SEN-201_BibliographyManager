# database_connector.py

Class: DatabaseConnector
    Constructor: databaseConnector(db_url: str, echo: bool = True)
    Method:
        create_all_tables() # use to initiate all table
        get_session() return session for CRUD operation
        close() * use when exit the application

--------------------------------------------–––––--------------------------------------
# author_repository.py

Class: AuthorRepository
    Constructor: author_repository(first_name: str, last_name: str, middle_name: Optional[str] = None)
    Method:
        create_author(first_name: str, last_name: str, middle_name: Optional[str] = None) # create author instance in db
        get_all_authors() # get all author in db
        get_author_by(**kwargs: Any) return author if found # search author by valid attribute
    
