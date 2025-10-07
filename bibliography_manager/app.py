import tkinter as tk
from .db import BibliographyDB

def run():
    db = BibliographyDB()
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
