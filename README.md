# Bibliography Manager (Tkinter + SQLite)

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/1c9bb424-55e9-4359-b29e-ae55fb12c222" />

## Project Layout
```text
SEN-201_BibliographyManager/
├─ src/
│  ├─ features
│  │  ├─ bibtex/                          # BibTeX exporter utilities
│  │  │  └─ bibtex.py
│  │  ├─ database/                        # SQLite database layer (PRAGMA foreign_keys=ON)
│  │  │  ├─ operation/                    # Operation for manipulate the data in database
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ entry_ops.py
│  │  │  │  ├─ refset_ops.py
│  │  │  │  └─ set_entries_ops.py
│  │  │  └─ db.py
│  │  ├─ entries_services/
│  │  │  └─ entries_service.py
│  │  ├─ refsets_services/
│  │  │  └─ refsets_service.py
│  │  └─ ui/                              # Tkinter UI
│  │     ├─ __init__.py
│  │     └─ main_window.py
│  └─ main/
│     └─ app.py                            # Entry point (python -m src.main.app)
└─ README.md
```

## Usage
```bash
python -m src.main.app
```

## Requirements

- Python 3.10+ (3.11 also OK)
- Tkinter installed for your OS

### Install Tkinter

**Ubuntu/Debian/Mint**
```bash
sudo apt update
sudo apt install -y python3-tk
```

**Fedora**
```bash
sudo dnf install -y python3-tkinter
```

**Arch**
```bash
sudo pacman -S tk
```

**Windows/macOS**  
Comes with the standard Python.org installers. If missing, reinstall Python from python.org.

