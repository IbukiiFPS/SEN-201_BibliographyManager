import tkinter as tk
from ..features.database.db import BibliographyDB
from ..features.ui.main_window import BibliographyApp

def run():
    db = BibliographyDB()
    ui = BibliographyApp()
    ui.db = db
    ui.mainloop()
    db.close()
    root = tk.Tk()
    root.title("Bibliography Manager")
    tk.Label(root, text="DB initialized. Next stage is for the UI…", padx=12, pady=12).pack()
    def on_close():
        db.close()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    run()
