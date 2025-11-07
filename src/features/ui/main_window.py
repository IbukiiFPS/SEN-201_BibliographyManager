from __future__ import annotations
import re
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from src.features.database.db import BibliographyDB
from src.features.entries_services.entries_service import EntriesService
from src.features.refsets_services.refsets_service import RefsetsService
from src.features.bibtex.bibtex import entry_to_bibtex

def prefix_to_range(prefix: str):
    if not re.match(r'^\d{4}(-\d{2}){0,2}$', prefix):
        raise ValueError('Date must be YYYY, YYYY-MM, or YYYY-MM-DD')
    parts = prefix.split('-')
    if len(parts) == 1:
        y = int(parts[0]); start = f"{y:04d}-01-01"; end = f"{y+1:04d}-01-01"
    elif len(parts) == 2:
        y, m = int(parts[0]), int(parts[1])
        start = f"{y:04d}-{m:02d}-01"
        end = f"{(y if m < 12 else y+1):04d}-{(m+1 if m < 12 else 1):02d}-01"
    else:
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        start = f"{y:04d}-{m:02d}-{d:02d}"
        ne = date.fromordinal(date(y, m, d).toordinal() + 1)
        end = ne.strftime('%Y-%m-%d')
    return start, end

class BibliographyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bibliography Manager"); self.geometry("1150x660")
        self.db = BibliographyDB()
        self.entries = EntriesService(self.db)
        self.refsets = RefsetsService(self.db)
        self.selected_entry_id = None
        self.selected_set_id = None
        self._build_ui()
        self.refresh_entries(); self.refresh_sets()

    def _build_ui(self):
        top = ttk.Frame(self); top.pack(fill="x", padx=6, pady=6)
        ttk.Label(top, text="Quick search (e.g., tag:ml | author:smith | created:2025-10 | pub:2023-05-12):").pack(side="left")
        self.search_var = tk.StringVar()
        ent = ttk.Entry(top, textvariable=self.search_var); ent.pack(side="left", fill="x", expand=True, padx=4)
        ent.bind("<Return>", lambda e: self.on_search())
        ttk.Button(top, text="Search", command=self.on_search).pack(side="left")
        ttk.Button(top, text="Advanced Search", command=self.open_advanced_search).pack(side="left", padx=4)
        ttk.Button(top, text="Clear filters", command=self.refresh_entries).pack(side="left", padx=4)

        main = ttk.PanedWindow(self, orient="horizontal"); main.pack(fill="both", expand=True, padx=6, pady=6)
        left = ttk.Frame(main, width=480); main.add(left, weight=1)
        ttk.Label(left, text="Entries").pack(anchor="w")

        self.entries_tree = ttk.Treeview(
            left,
            columns=("authors", "title", "venue", "year", "pubdate", "tags", "created"),
            show="headings", selectmode="browse",
        )
        for col, w, header in [
            ("authors", 220, "Authors"),
            ("title", 300, "Title"),
            ("venue", 150, "Venue"),
            ("year", 60, "Year"),
            ("pubdate", 180, "Publication Date"),
            ("tags", 180, "Tags"),
            ("created", 170, "Created"),
        ]:
            self.entries_tree.heading(col, text=header)
            self.entries_tree.column(col, width=w, anchor="w")
        self.entries_tree.pack(fill="both", expand=True)
        self.entries_tree.bind("<<TreeviewSelect>>", self.on_select_entry)

        btns = ttk.Frame(left); btns.pack(fill="x")
        ttk.Button(btns, text="Add entry", command=self.show_add_dialog).pack(side="left")
        ttk.Button(btns, text="Edit entry", command=self.show_edit_dialog).pack(side="left")
        ttk.Button(btns, text="Delete entry", command=self.delete_selected_entry).pack(side="left")

        right = ttk.Frame(main); main.add(right, weight=2)
        form = ttk.Frame(right); form.pack(fill="both", expand=True)

        labels = [
            "Authors (required)","Title (required)","Venue/Journal","Year",
            "Publication Date (YYYY or YYYY-MM or YYYY-MM-DD)","Volume","Number","Pages","DOI","URL","Tags (comma-separated)",
        ]
        self.form_vars = {}
        for label in labels:
            row = ttk.Frame(form); row.pack(fill="x", padx=4, pady=2)
            ttk.Label(row, text=label + ":", width=38).pack(side="left")
            var = tk.StringVar(); ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)
            self.form_vars[label] = var

        fbtns = ttk.Frame(right); fbtns.pack(fill="x", pady=6)
        ttk.Button(fbtns, text="Save -> Add", command=self.add_entry_from_form).pack(side="left")
        ttk.Button(fbtns, text="Save -> Update selected", command=self.update_entry_from_form).pack(side="left", padx=6)
        ttk.Button(fbtns, text="Clear form", command=self.clear_form).pack(side="left")

        sets = ttk.LabelFrame(self, text="Reference sets (collections)")
        sets.pack(fill="x", padx=6, pady=6)
        self.sets_combo = ttk.Combobox(sets, state="readonly"); self.sets_combo.pack(side="left", padx=4)
        self.sets_combo.bind("<<ComboboxSelected>>", self.on_select_set)
        ttk.Button(sets, text="Create set", command=self.create_set).pack(side="left")
        ttk.Button(sets, text="Delete set", command=self.delete_set).pack(side="left")
        ttk.Button(sets, text="Add selected entry to set", command=self.add_selected_to_set).pack(side="left", padx=6)
        ttk.Button(sets, text="Remove selected entry from set", command=self.remove_selected_from_set).pack(side="left")
        ttk.Button(sets, text="Show entries in set", command=self.show_entries_in_set).pack(side="left", padx=6)
        ttk.Button(sets, text="Export set to BibTeX", command=self.export_set_bibtex).pack(side="left", padx=6)

    def _like_for_prefix_date(self, value: str) -> str:
        return value.strip() + "%"

    def _collect_form(self) -> dict:
        def none_if_empty(x: str):
            x = x.strip(); return x if x != "" else None

        import re
        authors = self.form_vars["Authors (required)"].get().strip()
        title = self.form_vars["Title (required)"].get().strip()
        if not authors or not title:
            raise ValueError("Authors and Title are required")

        year_val = none_if_empty(self.form_vars["Year"].get())
        if year_val and not re.match(r"^\d{4}$", year_val):
            raise ValueError("Year must be a 4-digit year")

        pub_val = none_if_empty(self.form_vars["Publication Date (YYYY or YYYY-MM or YYYY-MM-DD)"].get())
        if pub_val and not re.match(r"^\d{4}(-\d{2}){0,2}$", pub_val):
            raise ValueError("Publication Date must be YYYY, YYYY-MM, or YYYY-MM-DD")

        vol_val = none_if_empty(self.form_vars["Volume"].get())
        if vol_val and not vol_val.isdigit():
            raise ValueError("Volume must be numeric (integers only)")

        num_val = none_if_empty(self.form_vars["Number"].get())
        if num_val and not num_val.isdigit():
            raise ValueError("Number must be numeric (integers only)")

        return {
            "authors": authors, "title": title,
            "venue": none_if_empty(self.form_vars["Venue/Journal"].get()),
            "year": int(year_val) if year_val else None,
            "publication_date": pub_val,
            "volume": int(vol_val) if vol_val else None,
            "number": int(num_val) if num_val else None,
            "pages": none_if_empty(self.form_vars["Pages"].get()),
            "doi": none_if_empty(self.form_vars["DOI"].get()),
            "url": none_if_empty(self.form_vars["URL"].get()),
            "tags": none_if_empty(self.form_vars["Tags (comma-separated)"].get()),
        }

    def refresh_entries(self):
        rows = self.entries.list()
        self._populate_entries(rows)

    def _populate_entries(self, rows):
        for i in self.entries_tree.get_children():
            self.entries_tree.delete(i)
        for r in rows:
            entry_id, authors, title, venue, year, pubdate, tags, created = r
            self.entries_tree.insert(
                "", "end", iid=str(entry_id),
                values=(authors, title, venue or "", year or "", pubdate or "", tags or "", created)
            )

    def on_search(self):
        import re
        q = self.search_var.get().strip()
        if not q:
            self.refresh_entries(); return

        where, params = None, None
        m = re.match(r"^tag:(.+)$", q, flags=re.IGNORECASE)
        if m:
            where, params = ("tags LIKE ?", (f"%{m.group(1).strip()}%",))

        if where is None:
            m = re.match(r"^author:(.+)$", q, flags=re.IGNORECASE)
            if m:
                where, params = ("authors LIKE ?", (f"%{m.group(1).strip()}%",))

        if where is None:
            m = re.match(r"^created:(\d{4}(?:-\d{2})?(?:-\d{2})?)$", q, flags=re.IGNORECASE)
            if m:
                where, params = ("created_at LIKE ?", (self._like_for_prefix_date(m.group(1)),))

        if where is None:
            m = re.match(r"^pub:(\d{4}(?:-\d{2})?(?:-\d{2})?)$", q, flags=re.IGNORECASE)
            if m:
                where, params = ("publication_date LIKE ?", (self._like_for_prefix_date(m.group(1)),))

        if where is None and re.match(r"^\d{4}(?:-\d{2})?(?:-\d{2})?$", q):
            if "-" in q:
                where, params = ("publication_date LIKE ?", (self._like_for_prefix_date(q),))
            else:
                where = "(year = ? OR publication_date LIKE ?)"
                params = (int(q), f"{q}%")

        if where is None:
            where = "(authors LIKE ? OR title LIKE ? OR tags LIKE ? OR venue LIKE ?)"
            p = f"%{q}%"; params = (p, p, p, p)

        self._populate_entries(self.entries.list(where, params))

    def open_advanced_search(self):
        dlg = tk.Toplevel(self); dlg.title("Advanced Search"); dlg.transient(self); dlg.grab_set()
        frm = ttk.Frame(dlg, padding=8); frm.pack(fill="both", expand=True)

        def add_row(parent, label, width=18):
            f = ttk.Frame(parent); f.pack(fill="x", pady=2)
            ttk.Label(f, text=label, width=width).pack(side="left")
            var = tk.StringVar(); ttk.Entry(f, textvariable=var).pack(side="left", fill="x", expand=True)
            return var

        ttk.Label(frm, text="Leave any field blank to ignore it. Dates accept YYYY, YYYY-MM, or YYYY-MM-DD.").pack(anchor="w", pady=(0,6))
        text_contains = add_row(frm, "Text contains")
        tag = add_row(frm, "Tag")
        author = add_row(frm, "Author")

        ttk.Label(frm, text="Created range").pack(anchor="w", pady=(8,0))
        cr_fr = ttk.Frame(frm); cr_fr.pack(fill="x", pady=2)
        ttk.Label(cr_fr, text="From", width=6).pack(side="left")
        created_from = tk.StringVar(); ttk.Entry(cr_fr, textvariable=created_from).pack(side="left", fill="x", expand=True)
        ttk.Label(cr_fr, text="To", width=4).pack(side="left", padx=(6,0))
        created_to = tk.StringVar(); ttk.Entry(cr_fr, textvariable=created_to).pack(side="left", fill="x", expand=True)

        ttk.Label(frm, text="Publication date range").pack(anchor="w", pady=(8,0))
        pd_fr = ttk.Frame(frm); pd_fr.pack(fill="x", pady=2)
        ttk.Label(pd_fr, text="From", width=6).pack(side="left")
        pub_from = tk.StringVar(); ttk.Entry(pd_fr, textvariable=pub_from).pack(side="left", fill="x", expand=True)
        ttk.Label(pd_fr, text="To", width=4).pack(side="left", padx=(6,0))
        pub_to = tk.StringVar(); ttk.Entry(pd_fr, textvariable=pub_to).pack(side="left", fill="x", expand=True)

        def run_advanced():
            import re
            where, params = [], []

            t = text_contains.get().strip()
            if t:
                p = f"%{t}%"
                where.append("(authors LIKE ? OR title LIKE ? OR venue LIKE ? OR tags LIKE ?)")
                params += [p, p, p, p]

            tg = tag.get().strip()
            if tg:
                where.append("tags LIKE ?"); params.append(f"%{tg}%")

            au = author.get().strip()
            if au:
                where.append("authors LIKE ?"); params.append(f"%{au}%")

            cf = created_from.get().strip()
            ct = created_to.get().strip()
            if cf and not re.match(r'^\d{4}(-\d{2}){0,2}$', cf):
                messagebox.showerror("Error", "Created From must be YYYY, YYYY-MM, or YYYY-MM-DD"); return
            if ct and not re.match(r'^\d{4}(-\d{2}){0,2}$', ct):
                messagebox.showerror("Error", "Created To must be YYYY, YYYY-MM, or YYYY-MM-DD"); return
            if cf:
                cfs, cfe = prefix_to_range(cf)
                if ct:
                    _, cte = prefix_to_range(ct)
                    where.append("(created_at >= ? AND created_at < ?)"); params += [cfs, cte]
                else:
                    where.append("(created_at >= ? AND created_at < ?)"); params += [cfs, cfe]
            elif ct:
                _, cte = prefix_to_range(ct)
                where.append("(created_at < ?)"); params += [cte]

            pf = pub_from.get().strip()
            pt = pub_to.get().strip()
            if pf and not re.match(r'^\d{4}(-\d{2}){0,2}$', pf):
                messagebox.showerror("Error", "Publication From must be YYYY, YYYY-MM, or YYYY-MM-DD"); return
            if pt and not re.match(r'^\d{4}(-\d{2}){0,2}$', pt):
                messagebox.showerror("Error", "Publication To must be YYYY, YYYY-MM, or YYYY-MM-DD"); return
            if pf:
                pfs, pfe = prefix_to_range(pf)
                if pt:
                    _, pte = prefix_to_range(pt)
                    where.append("(publication_date >= ? AND publication_date < ?)"); params += [pfs, pte]
                else:
                    where.append("(publication_date >= ? AND publication_date < ?)"); params += [pfs, pfe]
            elif pt:
                _, pte = prefix_to_range(pt)
                where.append("(publication_date < ?)"); params += [pte]

            sql_where = " AND ".join(where) if where else None
            rows = self.entries.list(sql_where, tuple(params))
            self._populate_entries(rows)
            dlg.destroy()

        btns = ttk.Frame(frm); btns.pack(fill="x", pady=10)
        ttk.Button(btns, text="Search", command=run_advanced).pack(side="left")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side="left", padx=6)
        dlg.wait_visibility(); dlg.focus_set()

    def on_select_entry(self, _):
        sel = self.entries_tree.selection()
        self.selected_entry_id = int(sel[0]) if sel else None
        if not self.selected_entry_id: return
        entry = self.entries.get(self.selected_entry_id)
        if not entry: return
        mapping = {
            "Authors (required)": "authors","Title (required)": "title","Venue/Journal": "venue","Year": "year",
            "Publication Date (YYYY or YYYY-MM or YYYY-MM-DD)": "publication_date","Volume": "volume",
            "Number": "number","Pages": "pages","DOI": "doi","URL": "url","Tags (comma-separated)": "tags",
        }
        for label, key in mapping.items():
            self.form_vars[label].set("" if entry.get(key) is None else str(entry.get(key)))

    def show_add_dialog(self):
        self.clear_form()
        messagebox.showinfo("Add entry", 'Fill the right-hand form and click "Save -> Add"')

    def show_edit_dialog(self):
        if not self.selected_entry_id:
            messagebox.showwarning("Edit", "Select an entry to edit."); return
        messagebox.showinfo("Edit entry", 'Edit the form on the right and click "Save -> Update selected"')

    def add_entry_from_form(self):
        try:
            eid = self.entries.add(**self._collect_form())
            messagebox.showinfo("Added", f"Entry added with id {eid}")
            self.refresh_entries(); self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_entry_from_form(self):
        if not self.selected_entry_id:
            messagebox.showwarning("Update", "Select an entry to update."); return
        try:
            self.entries.update(self.selected_entry_id, **self._collect_form())
            messagebox.showinfo("Updated", "Entry updated")
            self.refresh_entries()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected_entry(self):
        if not self.selected_entry_id:
            messagebox.showwarning("Delete", "Select an entry to delete."); return
        if messagebox.askyesno("Confirm", "Delete selected entry?"):
            self.entries.delete(self.selected_entry_id)
            self.refresh_entries(); self.clear_form()

    def clear_form(self):
        for v in self.form_vars.values():
            v.set("")

    def refresh_sets(self):
        sets = self.refsets.list()
        self._sets_cache = sets
        names = [s[1] for s in sets]
        self.sets_combo["values"] = names
        if names:
            self.sets_combo.current(0); self.selected_set_id = sets[0][0]
        else:
            self.selected_set_id = None

    def on_select_set(self, _):
        name = self.sets_combo.get()
        self.selected_set_id = next((s[0] for s in self._sets_cache if s[1] == name), None)

    def create_set(self):
        name = simpledialog.askstring("Create set", "Set name:")
        if not name: return
        try:
            sid = self.refsets.create(name.strip())
            messagebox.showinfo("Created", f"Reference set created: {name} (id {sid})")
            self.refresh_sets()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_set(self):
        sel = self.sets_combo.get()
        if not sel:
            messagebox.showwarning("Delete set", "No set selected"); return
        sid = next((s[0] for s in self._sets_cache if s[1] == sel), None)
        if sid and messagebox.askyesno("Confirm", f"Delete set {sel}?"):
            self.refsets.delete(sid); self.refresh_sets()

    def add_selected_to_set(self):
        if not self.selected_entry_id:
            messagebox.showwarning("Add to set", "Select an entry first"); return
        if not self.selected_set_id:
            messagebox.showwarning("Add to set", "Select a set first"); return
        self.refsets.add_entry(self.selected_set_id, self.selected_entry_id)
        messagebox.showinfo("Added", "Entry added to set")

    def remove_selected_from_set(self):
        if not self.selected_entry_id:
            messagebox.showwarning("Remove from set", "Select an entry first"); return
        if not self.selected_set_id:
            messagebox.showwarning("Remove from set", "Select a set first"); return
        self.refsets.remove_entry(self.selected_set_id, self.selected_entry_id)
        self.refresh_entries()
        messagebox.showinfo("Removed", "Entry removed from set")

    def show_entries_in_set(self):
        if not self.selected_set_id:
            messagebox.showwarning("Show set", "Select a set first"); return
        rows = self.refsets.list_entries(self.selected_set_id)
        self._populate_entries(rows)

    def export_set_bibtex(self):
        if not self.selected_set_id:
            messagebox.showwarning("Export", "Select a set first"); return
        rows = self.refsets.list_entries(self.selected_set_id)
        if not rows:
            messagebox.showinfo("Export", "Set is empty"); return
        path = filedialog.asksaveasfilename(defaultextension=".bib", filetypes=[("BibTeX files","*.bib")], title="Save BibTeX file")
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                eid = r[0]
                entry = self.entries.get(eid)
                bib = entry_to_bibtex(entry)
                f.write(bib + "\n\n")
        messagebox.showinfo("Exported", f"BibTeX exported to {path}")

    def on_close(self):
        self.db.close(); self.destroy()
