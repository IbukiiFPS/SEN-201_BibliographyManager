import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import Dict
import re

from ..refsets_services.refsets_service import RefSetsService
from ..database.db import BibliographyDB
from ..entries_services.entries_service import EntriesService
from ..bibtex import entry_to_bibtex

class BibliographyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Bibliography Manager')
        self.geometry('1000x600')

        # Services (dependency injection-friendly)
        self.db = BibliographyDB()
        self.entries = EntriesService(self.db)
        self.refsets = RefSetsService(self.db)

        self.selected_entry_id = None
        self.selected_set_id = None

        self._build_ui()
        self.refresh_entries()
        self.refresh_sets()

    def _build_ui(self):
        # Top frame: search
        top = ttk.Frame(self)
        top.pack(fill='x', padx=6, pady=6)
        ttk.Label(top, text='Search:').pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=4)
        search_entry.bind('<Return>', lambda e: self.on_search())
        ttk.Button(top, text='Search', command=self.on_search).pack(side='left')
        ttk.Button(top, text='Show all', command=self.refresh_entries).pack(side='left', padx=4)

        main = ttk.PanedWindow(self, orient='horizontal')
        main.pack(fill='both', expand=True, padx=6, pady=6)

        # Left: entries list
        left = ttk.Frame(main, width=420)
        main.add(left, weight=1)
        ttk.Label(left, text='Entries').pack(anchor='w')
        self.entries_tree = ttk.Treeview(left, columns=('authors', 'title', 'venue', 'year', 'tags', 'created'), show='headings', selectmode='browse')
        for col, w in [('authors', 180), ('title', 260), ('venue', 120), ('year', 60), ('tags', 140), ('created', 140)]:
            self.entries_tree.heading(col, text=col.title())
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

        labels = ['Authors (required)', 'Title (required)', 'Venue/Journal', 'Year', 'Volume', 'Number', 'Pages', 'DOI', 'URL', 'Tags (comma-separated)']
        self.form_vars: Dict[str, tk.StringVar] = {}
        for label in labels:
            frame = ttk.Frame(form)
            frame.pack(fill='x', padx=4, pady=2)
            ttk.Label(frame, text=label+':', width=20).pack(side='left')
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

    # ------------- UI actions -------------
    def on_search(self):
        q = self.search_var.get().strip()
        if not q:
            self.refresh_entries()
            return
        where, params = self.entries.search_query(q)
        rows = self.entries.list(where, params)
        self._populate_entries(rows)

    def refresh_entries(self):
        rows = self.entries.list()
        self._populate_entries(rows)

    def _populate_entries(self, rows):
        for i in self.entries_tree.get_children():
            self.entries_tree.delete(i)
        for r in rows:
            entry_id, authors, title, venue, year, tags, created = r
            self.entries_tree.insert('', 'end', iid=str(entry_id), values=(authors, title, venue or '', year or '', tags or '', created))

    def on_select_entry(self, event):
        sel = self.entries_tree.selection()
        if not sel:
            self.selected_entry_id = None
            return
        eid = int(sel[0])
        self.selected_entry_id = eid
        entry = self.entries.get(eid)
        if entry:
            mapping = {
                'Authors (required)': 'authors',
                'Title (required)': 'title',
                'Venue/Journal': 'venue',
                'Year': 'year',
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

    def _collect_form(self):
        authors = self.form_vars['Authors (required)'].get().strip()
        title = self.form_vars['Title (required)'].get().strip()
        if not authors or not title:
            raise ValueError('Authors and Title are required')

        def none_if_empty(x: str):
            x = (x or "").strip()
            return x if x != "" else None

        year_val = none_if_empty(self.form_vars['Year'].get() or "")
        if year_val and not re.match(r'^\d{4}$', year_val):
            raise ValueError('Year must be a 4-digit year')

        doi = none_if_empty(self.form_vars['DOI'].get() or "")
        if doi and not re.match(r'^10.\d{4,9}/[-._;()/:A-Z0-9]+$', doi, re.IGNORECASE):
            raise ValueError('DOI format is invalid')
        
        data = {
            'authors': authors,
            'title': title,
            'venue': none_if_empty(self.form_vars['Venue/Journal'].get() or ""),
            'year': int(year_val) if year_val else None,
            'volume': none_if_empty(self.form_vars['Volume'].get() or ""),
            'number': none_if_empty(self.form_vars['Number'].get() or ""),
            'pages': none_if_empty(self.form_vars['Pages'].get() or ""),
            'doi': none_if_empty(self.form_vars['DOI'].get() or ""),
            'url': none_if_empty(self.form_vars['URL'].get() or ""),
            'tags': none_if_empty(self.form_vars['Tags (comma-separated)'].get() or ""),
        }
        return data

    def add_entry_from_form(self):
        try:
            data = self._collect_form()
            eid = self.entries.add(data)
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
            data = self._collect_form()
            self.entries.update(self.selected_entry_id, data)
            messagebox.showinfo('Updated', 'Entry updated')
            self.refresh_entries()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def delete_selected_entry(self):
        if not self.selected_entry_id:
            messagebox.showwarning('Delete', 'Select an entry to delete.')
            return
        if messagebox.askyesno('Confirm', 'Delete selected entry?'):
            self.entries.remove(self.selected_entry_id)
            self.refresh_entries()
            self.clear_form()

    def clear_form(self):
        for v in self.form_vars.values():
            v.set('')

    # ------------- Ref sets UI -------------
    def refresh_sets(self):
        sets = self.refsets.list()
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
            sid = self.refsets.create(name.strip())
            messagebox.showinfo('Created', f'Reference set created: {name} (id {sid})')
            self.refresh_sets()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def delete_set(self):
        sel = self.sets_combo.get()
        if not sel:
            messagebox.showwarning('Delete set', 'No set selected')
            return
        sid = next((s[0] for s in self.sets if s[1] == sel), None)
        if sid and messagebox.askyesno('Confirm', f'Delete set {sel}?'):
            self.refsets.delete(sid)
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
        self.refsets.add_entry(self.selected_set_id, self.selected_entry_id)
        messagebox.showinfo('Added', 'Entry added to set')

    def remove_selected_from_set(self):
        if not self.selected_entry_id:
            messagebox.showwarning('Remove from set', 'Select an entry first')
            return
        if not self.selected_set_id:
            messagebox.showwarning('Remove from set', 'Select a set first')
            return
        self.refsets.remove_entry(self.selected_set_id, self.selected_entry_id)
        messagebox.showinfo('Removed', 'Entry removed from set')

    def show_entries_in_set(self):
        if not self.selected_set_id:
            messagebox.showwarning('Show set', 'Select a set first')
            return
        rows = self.refsets.list_entries(self.selected_set_id)
        self._populate_entries(rows)

    def export_set_bibtex(self):
        if not self.selected_set_id:
            messagebox.showwarning('Export', 'Select a set first')
            return
        rows = self.refsets.list_entries(self.selected_set_id)
        if not rows:
            messagebox.showinfo('Export', 'Set is empty')
            return
        path = filedialog.asksaveasfilename(defaultextension='.bib', filetypes=[('BibTeX files','*.bib')], title='Save BibTeX file')
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            for r in rows:
                eid = r[0]
                entry = self.entries.get(eid)
                bib = entry_to_bibtex(entry) if entry else ''
                if bib:
                    f.write(bib + '\\n\\n')
        messagebox.showinfo('Exported', f'BibTeX exported to {path}')

    def on_close(self):
        self.db.close()
        self.destroy()