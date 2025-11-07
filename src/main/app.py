from src.features.ui.main_window import BibliographyApp

def run():
    app = BibliographyApp()
    app.protocol('WM_DELETE_WINDOW', app.on_close)
    app.mainloop()

if __name__ == "__main__":
    run()