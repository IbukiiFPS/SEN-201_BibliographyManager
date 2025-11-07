# Bibliography Manager (Tkinter + SQLite)

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/1c9bb424-55e9-4359-b29e-ae55fb12c222" />

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
