"""
PPDJ Combined code to be one python file.
Bibliography Manager - Desktop application (single-file)
Run: python bibliography_manager.py
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime, date
import re

DB_FILE = "bibliography.db"

# --------------------- Database layer ---------------------
class BibliographyDB:
    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self._create_tables()
        self._migrate_columns()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY,
                authors TEXT NOT NULL,
                title TEXT NOT NULL,
                venue TEXT,
                year INTEGER,
                publication_date TEXT,
                volume TEXT,
                number TEXT,
                pages TEXT,
                doi TEXT,
                url TEXT,
                tags TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS refsets (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS set_entries (
                set_id INTEGER,
                entry_id INTEGER,
                PRIMARY KEY(set_id, entry_id),
                FOREIGN KEY(set_id) REFERENCES refsets(id) ON DELETE CASCADE,
                FOREIGN KEY(entry_id) REFERENCES entries(id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def _migrate_columns(self):
        c = self.conn.cursor()
        c.execute('PRAGMA table_info(entries)')
        cols = {row[1] for row in c.fetchall()}
        if 'publication_date' not in cols:
            c.execute('ALTER TABLE entries ADD COLUMN publication_date TEXT')
            self.conn.commit()
        # Note: We rely on application-level duplicate detection to avoid breaking on legacy duplicate data.

    # ---------- Duplicate detection helpers ----------
    @staticmethod
    def _norm_text(s: str) -> str:
        return (s or '').strip().lower()

    @staticmethod
    def _norm_pubdate(s: str) -> str:
        # Treat None as empty string for equality purposes
        return (s or '').strip()

    def find_duplicate_id(self, authors: str, title: str, publication_date: str, exclude_id: int = None):
        """
        Return the id of a row that duplicates (title, authors, pub_date) after normalization,
        or None if not found. Optionally exclude a specific id (for updates).
        """
        nt = self._norm_text(title)
        na = self._norm_text(authors)
        npd = self._norm_pubdate(publication_date)

        c = self.conn.cursor()
        if exclude_id is None:
            c.execute(
                """
                SELECT id FROM entries
                WHERE lower(trim(title)) = ?
                  AND lower(trim(authors)) = ?
                  AND ifnull(trim(publication_date), '') = ?
                LIMIT 1
                """,
                (nt, na, npd)
            )
        else:
            c.execute(
                """
                SELECT id FROM entries
                WHERE lower(trim(title)) = ?
                  AND lower(trim(authors)) = ?
                  AND ifnull(trim(publication_date), '') = ?
                  AND id <> ?
                LIMIT 1
                """,
                (nt, na, npd, exclude_id)
            )
        row = c.fetchone()
        return row[0] if row else None

    # ---------- Entry operations ----------
    def add_entry(self, authors, title, venue=None, year=None, publication_date=None,
                  volume=None, number=None, pages=None, doi=None, url=None, tags=None):
        if not authors.strip() or not title.strip():
            raise ValueError('Authors and Title are required')

        # Duplicate check
        dup_id = self.find_duplicate_id(authors, title, publication_date)
        if dup_id is not None:
            raise ValueError(f'Duplicate entry detected (same Title + Authors + Publication Date) as id {dup_id}')

        created_at = datetime.utcnow().isoformat()
        c = self.conn.cursor()
        c.execute('''INSERT INTO entries
                     (authors, title, venue, year, publication_date, volume, number, pages, doi, url, tags, created_at)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (authors.strip(), title.strip(), venue, year, publication_date, volume, number, pages, doi, url, tags, created_at))
        self.conn.commit()
        return c.lastrowid

    def update_entry(self, entry_id, **kwargs):
        if not kwargs:
            return

        # If any of the trio changes (or could be needed), fetch current and validate duplicates
        c = self.conn.cursor()
        c.execute('SELECT authors, title, publication_date FROM entries WHERE id = ?', (entry_id,))
        row = c.fetchone()
        if not row:
            raise ValueError('Entry not found')

        cur_authors, cur_title, cur_pubdate = row
        new_authors = kwargs.get('authors', cur_authors)
        new_title = kwargs.get('title', cur_title)
        new_pubdate = kwargs.get('publication_date', cur_pubdate)

        dup_id = self.find_duplicate_id(new_authors, new_title, new_pubdate, exclude_id=entry_id)
        if dup_id is not None:
            raise ValueError(f'Update would create a duplicate of id {dup_id} (same Title + Authors + Publication Date)')

        # Proceed with update
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)
        values.append(entry_id)
        sql = f"UPDATE entries SET {', '.join(fields)} WHERE id = ?"
        c.execute(sql, values)
        self.conn.commit()

    def delete_entry(self, entry_id):
        c = self.conn.cursor()
        c.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        self.conn.commit()

    def list_entries(self, where_clause=None, params=()):
        c = self.conn.cursor()
        sql = 'SELECT id, authors, title, venue, year, publication_date, tags, created_at FROM entries'
        if where_clause:
            sql += ' WHERE ' + where_clause
        sql += ' ORDER BY created_at DESC'
        c.execute(sql, params)
        return c.fetchall()

    def get_entry(self, entry_id):
        c = self.conn.cursor()
        c.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
        row = c.fetchone()
        if not row:
            return None
        cols = [d[0] for d in c.description]
        return dict(zip(cols, row))

    # ---------- Ref set operations ----------
    def create_refset(self, name):
        created_at = datetime.utcnow().isoformat()
        c = self.conn.cursor()
        c.execute('INSERT INTO refsets (name, created_at) VALUES (?, ?)', (name, created_at))
        self.conn.commit()
        return c.lastrowid

    def delete_refset(self, set_id):
        c = self.conn.cursor()
        c.execute('DELETE FROM refsets WHERE id = ?', (set_id,))
        c.execute('DELETE FROM set_entries WHERE set_id = ?', (set_id,))
        self.conn.commit()

    def list_refsets(self):
        c = self.conn.cursor()
        c.execute('SELECT id, name, created_at FROM refsets ORDER BY name')
        return c.fetchall()

    def add_entry_to_set(self, set_id, entry_id):
        c = self.conn.cursor()
        try:
            c.execute('INSERT INTO set_entries (set_id, entry_id) VALUES (?,?)', (set_id, entry_id))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

    def remove_entry_from_set(self, set_id, entry_id):
        c = self.conn.cursor()
        c.execute('DELETE FROM set_entries WHERE set_id = ? AND entry_id = ?', (set_id, entry_id))
        self.conn.commit()

    def list_entries_in_set(self, set_id):
        c = self.conn.cursor()
        c.execute('''SELECT e.id, e.authors, e.title, e.venue, e.year, e.publication_date, e.tags, e.created_at
                     FROM entries e JOIN set_entries s ON e.id = s.entry_id
                     WHERE s.set_id = ? ORDER BY e.created_at DESC''', (set_id,))
        return c.fetchall()

    def close(self):
        self.conn.close()

# --------------------- BibTeX exporter ---------------------
def escape_bibtex(s: str) -> str:
    if s is None:
        return ""
    return s.replace('\\', '\\\\').replace('{', '\{').replace('}', '\}').replace('%', '\%')

def entry_to_bibtex(entry: dict, bibkey=None) -> str:
    if bibkey is None:
        author = entry.get('authors', '')
        year = entry.get('year') or 'n.d.'
        m = re.search(r"([A-Za-z'-]+)(?:\s|$)", author)
        last = m.group(1) if m else 'anon'
        titleword = re.sub(r"[^A-Za-z]", '', (entry.get('title') or 'untitled'))[:6]
        bibkey = f"{last}{year}{titleword}".lower()
    bibtype = 'article' if entry.get('venue') else 'misc'
    fields = {
        'author': entry.get('authors'),
        'title': entry.get('title'),
        'journal': entry.get('venue'),
        'year': entry.get('year'),
        'date': entry.get('publication_date'),
        'volume': entry.get('volume'),
        'number': entry.get('number'),
        'pages': entry.get('pages'),
        'doi': entry.get('doi'),
        'url': entry.get('url')
    }
    lines = [f"@{bibtype}{{{bibkey},"]
    non_empty = [(k, v) for k, v in fields.items() if v is not None and str(v).strip() != ""]
    for i, (k, v) in enumerate(non_empty):
        val = escape_bibtex(str(v))
        comma = ',' if i < len(non_empty) - 1 else ''
        lines.append(f"  {k} = {{{val}}}{comma}")
    lines.append('}')
    return '\n'.join(lines)

# --------------------- Helpers ---------------------
def prefix_to_range(prefix: str):
    if not re.match(r'^\d{4}(-\d{2}){0,2}$', prefix):
        raise ValueError('Date must be YYYY, YYYY-MM, or YYYY-MM-DD')
    parts = prefix.split('-')
    if len(parts) == 1:
        y = int(parts[0])
        start = f"{y:04d}-01-01"
        end = f"{y+1:04d}-01-01"
    elif len(parts) == 2:
        y, m = int(parts[0]), int(parts[1])
        start = f"{y:04d}-{m:02d}-01"
        if m == 12:
            end = f"{y+1:04d}-01-01"
        else:
            end = f"{y:04d}-{m+1:02d}-01"
    else:
        y, m, d = (int(parts[0]), int(parts[1]), int(parts[2]))
        start = f"{y:04d}-{m:02d}-{d:02d}"
        end_date = date(y, m, d).toordinal() + 1
        ne = date.fromordinal(end_date)
        end = ne.strftime('%Y-%m-%d')
    return start, end

# --------------------- GUI ---------------------
class BibliographyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Bibliography Manager')
        self.geometry('1150x660')
        self.db = BibliographyDB()
        self.selected_entry_id = None
        self.selected_set_id = None
        self._build_ui()
        self.refresh_entries()
        self.refresh_sets()

    def _build_ui(self):
        # Top: quick search row
        top = ttk.Frame(self)
        top.pack(fill='x', padx=6, pady=6)

        ttk.Label(top, text='Quick search (e.g., tag:ml | author:smith | created:2025-10 | pub:2023-05-12):').pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=4)
        search_entry.bind('<Return>', lambda e: self.on_search())

        ttk.Button(top, text='Search', command=self.on_search).pack(side='left')
        ttk.Button(top, text='Advanced Search', command=self.open_advanced_search).pack(side='left', padx=4)
        ttk.Button(top, text='Clear filters', command=self.refresh_entries).pack(side='left', padx=4)

        main = ttk.PanedWindow(self, orient='horizontal')
        main.pack(fill='both', expand=True, padx=6, pady=6)

        # Left: entries list
        left = ttk.Frame(main, width=480)
        main.add(left, weight=1)
        ttk.Label(left, text='Entries').pack(anchor='w')

        self.entries_tree = ttk.Treeview(
            left,
            columns=('authors', 'title', 'venue', 'year', 'pubdate', 'tags', 'created'),
            show='headings',
            selectmode='browse'
        )
        col_specs = [
            ('authors', 220),
            ('title', 300),
            ('venue', 150),
            ('year', 60),
            ('pubdate', 180),
            ('tags', 180),
            ('created', 170)
        ]
        for col, w in col_specs:
            self.entries_tree.heading(col, text=('Publication Date' if col == 'pubdate' else col.title()))
            self.entries_tree.column(col, width=w, anchor='w')
        self.entries_tree.pack(fill='both', expand=True)
        self.entries_tree.bind('<<TreeviewSelect>>', self.on_select_entry)

        btns = ttk.Frame(left)
        btns.pack(fill='x')
        ttk.Button(btns, text='Add entry', command=self.show_add_dialog).pack(side='left')
        ttk.Button(btns, text='Edit entry', command=self.show_edit_dialog).pack(side='left')
        ttk.Button(btns, text='Delete entry', command=self.delete_selected_entry).pack(side='left')

        # Right: detail / form
        right = ttk.Frame(main)
        main.add(right, weight=2)
        form = ttk.Frame(right)
        form.pack(fill='both', expand=True)

        labels = [
            'Authors (required)',
            'Title (required)',
            'Venue/Journal',
            'Year',
            'Publication Date (YYYY or YYYY-MM-DD)',
            'Volume',
            'Number',
            'Pages',
            'DOI',
            'URL',
            'Tags (comma-separated)'
        ]
        self.form_vars = {}
        for label in labels:
            frame = ttk.Frame(form)
            frame.pack(fill='x', padx=4, pady=2)
            ttk.Label(frame, text=label+':', width=38).pack(side='left')
            var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=var)
            entry.pack(side='left', fill='x', expand=True)
            self.form_vars[label] = var

        form_btns = ttk.Frame(right)
        form_btns.pack(fill='x', pady=6)
        ttk.Button(form_btns, text='Save -> Add', command=self.add_entry_from_form).pack(side='left')
        ttk.Button(form_btns, text='Save -> Update selected', command=self.update_entry_from_form).pack(side='left', padx=6)
        ttk.Button(form_btns, text="Clear form", command=self.clear_form).pack(side='left')

        # Bottom: reference sets
        sets_frame = ttk.LabelFrame(self, text='Reference sets (collections)')
        sets_frame.pack(fill='x', padx=6, pady=6)
        self.sets_combo = ttk.Combobox(sets_frame, state='readonly')
        self.sets_combo.pack(side='left', padx=4)
        self.sets_combo.bind('<<ComboboxSelected>>', self.on_select_set)
        ttk.Button(sets_frame, text='Create set', command=self.create_set).pack(side='left')
        ttk.Button(sets_frame, text='Delete set', command=self.delete_set).pack(side='left')
        ttk.Button(sets_frame, text='Add selected entry to set', command=self.add_selected_to_set).pack(side='left', padx=6)
        ttk.Button(sets_frame, text='Remove selected entry from set', command=self.remove_selected_from_set).pack(side='left')
        ttk.Button(sets_frame, text='Show entries in set', command=self.show_entries_in_set).pack(side='left', padx=6)
        ttk.Button(sets_frame, text='Export set to BibTeX', command=self.export_set_bibtex).pack(side='left', padx=6)

    # ---------------- Advanced Search Dialog ----------------
    def open_advanced_search(self):
        dlg = tk.Toplevel(self)
        dlg.title("Advanced Search")
        dlg.transient(self)
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=8)
        frm.pack(fill='both', expand=True)

        def add_row(parent, label, width=18):
            f = ttk.Frame(parent)
            f.pack(fill='x', pady=2)
            ttk.Label(f, text=label, width=width).pack(side='left')
            var = tk.StringVar()
            ent = ttk.Entry(f, textvariable=var)
            ent.pack(side='left', fill='x', expand=True)
            return var

        info = ttk.Label(frm, text="Leave any field blank to ignore it. Dates accept YYYY, YYYY-MM, or YYYY-MM-DD.")
        info.pack(anchor='w', pady=(0,6))

        text_contains = add_row(frm, "Text contains")
        tag = add_row(frm, "Tag")
        author = add_row(frm, "Author")

        ttk.Label(frm, text="Created range").pack(anchor='w', pady=(8,0))
        cr_fr = ttk.Frame(frm); cr_fr.pack(fill='x', pady=2)
        ttk.Label(cr_fr, text="From", width=6).pack(side='left')
        created_from = tk.StringVar(); ttk.Entry(cr_fr, textvariable=created_from).pack(side='left', fill='x', expand=True)
        ttk.Label(cr_fr, text="To", width=4).pack(side='left', padx=(6,0))
        created_to = tk.StringVar(); ttk.Entry(cr_fr, textvariable=created_to).pack(side='left', fill='x', expand=True)

        ttk.Label(frm, text="Publication date range").pack(anchor='w', pady=(8,0))
        pd_fr = ttk.Frame(frm); pd_fr.pack(fill='x', pady=2)
        ttk.Label(pd_fr, text="From", width=6).pack(side='left')
        pub_from = tk.StringVar(); ttk.Entry(pd_fr, textvariable=pub_from).pack(side='left', fill='x', expand=True)
        ttk.Label(pd_fr, text="To", width=4).pack(side='left', padx=(6,0))
        pub_to = tk.StringVar(); ttk.Entry(pd_fr, textvariable=pub_to).pack(side='left', fill='x', expand=True)

        btns = ttk.Frame(frm); btns.pack(fill='x', pady=10)

        def run_advanced():
            where = []
            params = []

            t = text_contains.get().strip()
            if t:
                p = f"%{t}%"
                where.append("(authors LIKE ? OR title LIKE ? OR venue LIKE ? OR tags LIKE ?)")
                params += [p, p, p, p]

            tg = tag.get().strip()
            if tg:
                where.append("tags LIKE ?")
                params.append(f"%{tg}%")

            au = author.get().strip()
            if au:
                where.append("authors LIKE ?")
                params.append(f"%{au}%")

            cf = created_from.get().strip()
            ct = created_to.get().strip()
            if cf and not re.match(r'^\d{4}(-\d{2}){0,2}$', cf):
                messagebox.showerror('Error', 'Created From must be YYYY, YYYY-MM, or YYYY-MM-DD'); return
            if ct and not re.match(r'^\d{4}(-\d{2}){0,2}$', ct):
                messagebox.showerror('Error', 'Created To must be YYYY, YYYY-MM, or YYYY-MM-DD'); return
            if cf:
                cfs, cfe = prefix_to_range(cf)
                if ct:
                    _, cte = prefix_to_range(ct)
                    where.append("(created_at >= ? AND created_at < ?)")
                    params += [cfs, cte]
                else:
                    where.append("(created_at >= ? AND created_at < ?)")
                    params += [cfs, cfe]
            elif ct:
                _, cte = prefix_to_range(ct)
                where.append("(created_at < ?)")
                params += [cte]

            pf = pub_from.get().strip()
            pt = pub_to.get().strip()
            if pf and not re.match(r'^\d{4}(-\d{2}){0,2}$', pf):
                messagebox.showerror('Error', 'Publication From must be YYYY, YYYY-MM, or YYYY-MM-DD'); return
            if pt and not re.match(r'^\d{4}(-\d{2}){0,2}$', pt):
                messagebox.showerror('Error', 'Publication To must be YYYY, YYYY-MM, or YYYY-MM-DD'); return
            if pf:
                pfs, pfe = prefix_to_range(pf)
                if pt:
                    _, pte = prefix_to_range(pt)
                    where.append("(publication_date >= ? AND publication_date < ?)")
                    params += [pfs, pte]
                else:
                    where.append("(publication_date >= ? AND publication_date < ?)")
                    params += [pfs, pfe]
            elif pt:
                _, pte = prefix_to_range(pt)
                where.append("(publication_date < ?)")
                params += [pte]

            sql_where = ' AND '.join(where) if where else None
            rows = self.db.list_entries(sql_where, tuple(params))
            self._populate_entries(rows)
            dlg.destroy()

        ttk.Button(btns, text="Search", command=run_advanced).pack(side='left')
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side='left', padx=6)

        dlg.wait_visibility()
        dlg.focus_set()

    # ---------------- Quick search behavior (prefixes) ----------------
    def _like_for_prefix_date(self, value: str) -> str:
        return value.strip() + '%'

    def on_search(self):
        q = self.search_var.get().strip()
        if not q:
            self.refresh_entries()
            return

        where = None
        params = None

        m = re.match(r'^tag:(.+)$', q, flags=re.IGNORECASE)
        if m:
            tag = m.group(1).strip()
            where, params = ('tags LIKE ?', (f'%{tag}%',))

        if where is None:
            m = re.match(r'^author:(.+)$', q, flags=re.IGNORECASE)
            if m:
                author = m.group(1).strip()
                where, params = ('authors LIKE ?', (f'%{author}%',))

        if where is None:
            m = re.match(r'^created:(\d{4}(?:-\d{2})?(?:-\d{2})?)$', q, flags=re.IGNORECASE)
            if m:
                like = self._like_for_prefix_date(m.group(1))
                where, params = ('created_at LIKE ?', (like,))

        if where is None:
            m = re.match(r'^pub:(\d{4}(?:-\d{2})?(?:-\d{2})?)$', q, flags=re.IGNORECASE)
            if m:
                like = self._like_for_prefix_date(m.group(1))
                where, params = ('publication_date LIKE ?', (like,))

        if where is None and re.match(r'^\d{4}(?:-\d{2})?(?:-\d{2})?$', q):
            if '-' in q:
                where, params = ('publication_date LIKE ?', (self._like_for_prefix_date(q),))
            else:
                where = '(year = ? OR publication_date LIKE ?)'
                params = (int(q), f'{q}%')

        if where is None:
            where = '(authors LIKE ? OR title LIKE ? OR tags LIKE ? OR venue LIKE ?)'
            p = f'%{q}%'
            params = (p, p, p, p)

        rows = self.db.list_entries(where, params)
        self._populate_entries(rows)

    def refresh_entries(self):
        rows = self.db.list_entries()
        self._populate_entries(rows)

    def _populate_entries(self, rows):
        for i in self.entries_tree.get_children():
            self.entries_tree.delete(i)
        for r in rows:
            entry_id, authors, title, venue, year, pubdate, tags, created = r
            self.entries_tree.insert(
                '',
                'end',
                iid=str(entry_id),
                values=(authors, title, venue or '', year or '', pubdate or '', tags or '', created)
            )

    def on_select_entry(self, event):
        sel = self.entries_tree.selection()
        if not sel:
            self.selected_entry_id = None
            return
        eid = int(sel[0])
        self.selected_entry_id = eid
        entry = self.db.get_entry(eid)
        if entry:
            mapping = {
                'Authors (required)': 'authors',
                'Title (required)': 'title',
                'Venue/Journal': 'venue',
                'Year': 'year',
                'Publication Date (YYYY or YYYY-MM or YYYY-MM-DD)': 'publication_date',
                'Volume': 'volume',
                'Number': 'number',
                'Pages': 'pages',
                'DOI': 'doi',
                'URL': 'url',
                'Tags (comma-separated)': 'tags'
            }
            for label, key in mapping.items():
                self.form_vars[label].set('' if entry.get(key) is None else str(entry.get(key)))

    def show_add_dialog(self):
        self.clear_form()
        messagebox.showinfo('Add entry', 'Fill the right-hand form and click "Save -> Add"')

    def show_edit_dialog(self):
        if not self.selected_entry_id:
            messagebox.showwarning('Edit', 'Select an entry to edit.')
            return
        messagebox.showinfo('Edit entry', 'Edit the form on the right and click "Save -> Update selected"')

    def add_entry_from_form(self):
        try:
            kw = self._collect_form()
            eid = self.db.add_entry(**kw)
            messagebox.showinfo('Added', f'Entry added with id {eid}')
            self.refresh_entries()
            self.clear_form()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def update_entry_from_form(self):
        if not self.selected_entry_id:
            messagebox.showwarning('Update', 'Select an entry to update.')
            return
        try:
            kw = self._collect_form()
            self.db.update_entry(self.selected_entry_id, **kw)
            messagebox.showinfo('Updated', 'Entry updated')
            self.refresh_entries()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def delete_selected_entry(self):
        if not self.selected_entry_id:
            messagebox.showwarning('Delete', 'Select an entry to delete.')
            return
        if messagebox.askyesno('Confirm', 'Delete selected entry?'):
            self.db.delete_entry(self.selected_entry_id)
            self.refresh_entries()
            self.clear_form()

    def clear_form(self):
        for v in self.form_vars.values():
            v.set('')

    def _collect_form(self):
        authors = self.form_vars['Authors (required)'].get().strip()
        title = self.form_vars['Title (required)'].get().strip()
        if not authors or not title:
            raise ValueError('Authors and Title are required')

        def none_if_empty(x):
            return x.strip() if x.strip() != '' else None

        year_val = none_if_empty(self.form_vars['Year'].get())
        if year_val and not re.match(r'^\d{4}$', year_val):
            raise ValueError('Year must be a 4-digit year')

        pub_val = none_if_empty(self.form_vars['Publication Date (YYYY or YYYY-MM or YYYY-MM-DD)'].get())
        if pub_val and not re.match(r'^\d{4}(-\d{2}){0,2}$', pub_val):
            raise ValueError('Publication Date must be YYYY, YYYY-MM, or YYYY-MM-DD')

        kw = {
            'authors': authors,
            'title': title,
            'venue': none_if_empty(self.form_vars['Venue/Journal'].get()),
            'year': int(year_val) if year_val else None,
            'publication_date': pub_val,
            'volume': none_if_empty(self.form_vars['Volume'].get()),
            'number': none_if_empty(self.form_vars['Number'].get()),
            'pages': none_if_empty(self.form_vars['Pages'].get()),
            'doi': none_if_empty(self.form_vars['DOI'].get()),
            'url': none_if_empty(self.form_vars['URL'].get()),
            'tags': none_if_empty(self.form_vars['Tags (comma-separated)'].get())
        }
        return kw

    # ---------------- reference sets UI ----------------
    def refresh_sets(self):
        sets = self.db.list_refsets()
        self.sets = sets
        names = [s[1] for s in sets]
        self.sets_combo['values'] = names
        if names:
            self.sets_combo.current(0)
            self.selected_set_id = sets[0][0]
        else:
            self.selected_set_id = None

    def create_set(self):
        name = simpledialog.askstring('Create set', 'Set name:')
        if not name:
            return
        try:
            sid = self.db.create_refset(name.strip())
            messagebox.showinfo('Created', f'Reference set created: {name} (id {sid})')
            self.refresh_sets()
        except sqlite3.IntegrityError:
            messagebox.showerror('Error', 'A set with that name already exists')

    def delete_set(self):
        sel = self.sets_combo.get()
        if not sel:
            messagebox.showwarning('Delete set', 'No set selected')
            return
        sid = next((s[0] for s in self.sets if s[1] == sel), None)
        if sid and messagebox.askyesno('Confirm', f'Delete set {sel}?'):
            self.db.delete_refset(sid)
            self.refresh_sets()

    def on_select_set(self, event):
        name = self.sets_combo.get()
        sid = next((s[0] for s in self.sets if s[1] == name), None)
        self.selected_set_id = sid

    def add_selected_to_set(self):
        if not self.selected_entry_id:
            messagebox.showwarning('Add to set', 'Select an entry first')
            return
        if not self.selected_set_id:
            messagebox.showwarning('Add to set', 'Select a set first')
            return
        self.db.add_entry_to_set(self.selected_set_id, self.selected_entry_id)
        messagebox.showinfo('Added', 'Entry added to set')

    def remove_selected_from_set(self):
        if not self.selected_entry_id:
            messagebox.showwarning('Remove from set', 'Select an entry first')
            return
        if not self.selected_set_id:
            messagebox.showwarning('Remove from set', 'Select a set first')
            return
        self.db.remove_entry_from_set(self.selected_set_id, self.selected_entry_id)
        self.refresh_entries()
        messagebox.showinfo('Removed', 'Entry removed from set')

    def show_entries_in_set(self):
        if not self.selected_set_id:
            messagebox.showwarning('Show set', 'Select a set first')
            return
        rows = self.db.list_entries_in_set(self.selected_set_id)
        self._populate_entries(rows)

    def export_set_bibtex(self):
        if not self.selected_set_id:
            messagebox.showwarning('Export', 'Select a set first')
            return
        rows = self.db.list_entries_in_set(self.selected_set_id)
        if not rows:
            messagebox.showinfo('Export', 'Set is empty')
            return
        path = filedialog.asksaveasfilename(defaultextension='.bib', filetypes=[('BibTeX files','*.bib')], title='Save BibTeX file')
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            for r in rows:
                eid = r[0]
                entry = self.db.get_entry(eid)
                bib = entry_to_bibtex(entry)
                f.write(bib + '\n\n')
        messagebox.showinfo('Exported', f'BibTeX exported to {path}')

    def on_close(self):
        self.db.close()
        self.destroy()

# -------------------- Run --------------------
if __name__ == '__main__':
    app = BibliographyApp()
    app.protocol('WM_DELETE_WINDOW', app.on_close)
    app.mainloop()
