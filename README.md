# Bibliography Manager (Tkinter + SQLite)

## Project Layout
```text
SEN-201_BibliographyManager/
├─ src/
│  ├─ features
│  │  ├─ bibtex                          # BibTeX exporter utilities
│  │  │  ├─ bibtex.py
│  │  │  └─ tests
│  │  ├─ database                        # SQLite database layer (PRAGMA foreign_keys=ON)
│  │  │  ├─ operation                    # Operation for manipulate the data in database
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ entry_ops.py
│  │  │  │  └─ entry_set.py
│  │  │  ├─ tests
│  │  │  └─ db.py                           
│  │  ├─ entries_services
│  │  │  └─ entries_service.py
│  │  ├─ refsets_services
│  │  │   └─ refsets_service.py
│  │  └─ ui                               # Tkinter UI
│  │     ├─ __init__.py
│  │     └─ main_window.py
│  └─ main
│     └─ app.py                           # Entry point (python -m src.main.app)
└─ README.md
```

## Usage
```bash
python -m src.main.app
```
