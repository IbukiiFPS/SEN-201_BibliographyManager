import tkinter as tk
from tkinter import ttk, messagebox
from ..db import BibliographyDB
from ..services.entries_service import EntriesService

class BibliographyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Bibliography Manager')
        self.geometry('900x500')
        self.db = BibliographyDB()
        self.entries = EntriesService(self.db)
        self._build_ui()
        self.refresh_entries()