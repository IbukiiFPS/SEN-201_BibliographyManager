# Bibliography Manager (Tkinter + SQLite)

## Project Layout
BibliographyManagerModular/
├─ bibliography_manager/
│  ├─ __init__.py
│  ├─ app.py                # Entry point (python -m bibliography_manager.app)
│  ├─ db.py                 # SQLite database layer
│  ├─ bibtex.py             # BibTeX exporter utilities
│  ├─ services/             # App/business logic
│  │  ├─ __init__.py
│  │  ├─ entries_service.py
│  │  └─ refsets_service.py
│  └─ ui/                   # Tkinter UI
│     ├─ __init__.py
│     └─ main_window.py
└─ README.md

## Usage
```bash
python -m bibliography_manager.app
```
