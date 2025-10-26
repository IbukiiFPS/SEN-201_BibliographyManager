from __future__ import annotations
import sys
from pathlib import Path
# import tkinter as tk
# from ..features.ui.main_window import BibliographyApp

# Allow running as top-level script for PyInstaller and as a module (-m)
if __package__ is None or __package__ == "":
    # project root for SEN-201_BibliographyManager
    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

# use absolute import to your UI class
from src.features.ui.main_window import BibliographyApp

def run() -> None:
    app = BibliographyApp()
    app.protocol('WM_DELETE_WINDOW', app.on_close)
    app.mainloop()

if __name__ == "__main__":
    run()