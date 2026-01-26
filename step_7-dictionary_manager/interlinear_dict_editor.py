#!/usr/bin/env python3
# interlinear_dict_editor.py
# GUI Wörterbuch-Editor (Windows 7 & 10 compatible)
# Python 3.7+, standard library only

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

# Sprache-Optionen (gleich wie im Interlinear-Tool)
LANGUAGE_OPTIONS = {
    'DE': 'Deutsch - DE',
    'CHDE': 'Schweizerdeutsch - CHDE',
    'EN': 'Englisch - EN',
    'FR': 'Französisch - FR',
    'RU': 'Russisch - RU',
    'UA': 'Ukrainisch - UA',
    'FA': 'Persisch/Farsi - FA',
}

DEFAULT_DICT_FOLDER = os.path.join(os.getcwd(), 'dicts')  # default folder, changeable via UI


class DictEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wörterbuch-Editor")
        self.geometry("1000x600")

        self.current_folder = DEFAULT_DICT_FOLDER
        self.orig_code = 'DE'
        self.target_code = 'EN'
        self.dict_data = {}  # {orig: [trans1, trans2, ...]}

        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self)
        frm.pack(fill='x', padx=8, pady=6)

        ttk.Label(frm, text="Projekt-/Dict-Ordner:").pack(side='left')
        self.folder_label = ttk.Label(frm, text=self.current_folder)
        self.folder_label.pack(side='left', padx=(6,12))

        ttk.Button(frm, text="Ordner wählen", command=self.choose_folder).pack(side='left', padx=4)

        ttk.Label(frm, text="Ausgangssprache:").pack(side='left', padx=(12,0))
        self.orig_cb = ttk.Combobox(frm, state='readonly', width=22)
        self.orig_cb['values'] = [f"{k} - {v}" for k, v in LANGUAGE_OPTIONS.items()]
        self.orig_cb.set(f"{self.orig_code} - {LANGUAGE_OPTIONS[self.orig_code]}")
        self.orig_cb.pack(side='left', padx=6)

        ttk.Label(frm, text="Zielsprache:").pack(side='left', padx=(12,0))
        self.targ_cb = ttk.Combobox(frm, state='readonly', width=22)
        self.targ_cb['values'] = [f"{k} - {v}" for k, v in LANGUAGE_OPTIONS.items()]
        self.targ_cb.set(f"{self.target_code} - {LANGUAGE_OPTIONS[self.target_code]}")
        self.targ_cb.pack(side='left', padx=6)

        ttk.Button(frm, text="Datei laden", command=self.load_dict_file).pack(side='left', padx=6)
        ttk.Button(frm, text="Datei speichern", command=self.save_dict_file).pack(side='left', padx=6)
        ttk.Button(frm, text="Backup wiederherstellen", command=self.restore_backup).pack(side='left', padx=6)

        # Search row
        search_row = ttk.Frame(self)
        search_row.pack(fill='x', padx=8, pady=(4,0))
        ttk.Label(search_row, text="Suche:").pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_row, textvariable=self.search_var, width=40)
        search_entry.pack(side='left', padx=6)
        search_entry.bind("<Return>", lambda e: self.filter_tree())
        ttk.Button(search_row, text="Suchen/Filtern", command=self.filter_tree).pack(side='left', padx=6)
        ttk.Button(search_row, text="Alle anzeigen", command=self.refresh_tree).pack(side='left', padx=6)

        # Treeview for dictionary entries
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True, padx=8, pady=8)

        columns = ("orig", "trans")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')
        self.tree.heading('orig', text='Original (Ausgangssprache)')
        self.tree.heading('trans', text='Übersetzungen (getrennt durch //)')
        self.tree.column('orig', width=300, anchor='w')
        self.tree.column('trans', width=600, anchor='w')

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Bind double-click for edit
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # Bottom controls: add / edit / delete / import
        bottom = ttk.Frame(self)
        bottom.pack(fill='x', padx=8, pady=(0,8))

        ttk.Button(bottom, text="Eintrag hinzufügen", command=self.add_entry_dialog).pack(side='left', padx=6)
        ttk.Button(bottom, text="Eintrag bearbeiten", command=self.edit_selected).pack(side='left', padx=6)
        ttk.Button(bottom, text="Eintrag löschen", command=self.delete_selected).pack(side='left', padx=6)
        ttk.Button(bottom, text="Import aus Textdateien", command=self.import_from_texts).pack(side='left', padx=6)
        ttk.Button(bottom, text="Export als TSV", command=self.export_as_tsv).pack(side='left', padx=6)

        # Status bar
        self.status = ttk.Label(self, text="Bereit", anchor='w')
        self.status.pack(fill='x', padx=8, pady=(0,6))

    # -------------------------
    # File / folder handling
    # -------------------------
    def choose_folder(self):
        folder = filedialog.askdirectory(title="Projekt- / Dictionary-Ordner wählen", initialdir=self.current_folder)
        if not folder:
            return
        self.current_folder = folder
        self.folder_label.config(text=self.current_folder)

    def dict_path_for_pair(self, orig_code, target_code):
        dicts_folder = os.path.join(self.current_folder, 'dicts')
        os.makedirs(dicts_folder, exist_ok=True)
        return os.path.join(dicts_folder, f"{orig_code}-{target_code}.dict")

    # -------------------------
    # Load / Save dict
    # -------------------------
    def load_dict_file(self):
        # get codes
        orig = self._selected_code(self.orig_cb.get())
        targ = self._selected_code(self.targ_cb.get())
        if not orig or not targ:
            messagebox.showerror("Fehler", "Bitte Ausgangs- und Zielsprache auswählen.")
            return
        self.orig_code, self.target_code = orig, targ
        path = self.dict_path_for_pair(orig, targ)
        self.dict_data = {}
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.rstrip('\n')
                    if not line:
                        continue
                    parts = line.split('\t')
                    key = parts[0]
                    translations = [p for p in parts[1:] if p]
                    # dedupe preserving order
                    seen = set(); clean = []
                    for t in translations:
                        if t not in seen:
                            seen.add(t); clean.append(t)
                    self.dict_data[key] = clean
            self.status.config(text=f"Wörterbuch geladen: {path}")
        else:
            # create empty file
            open(path, 'a', encoding='utf-8').close()
            self.status.config(text=f"Neue Datei (leer) angelegt: {path}")
        self.refresh_tree()

    def save_dict_file(self):
        if not self.dict_data:
            if not messagebox.askyesno("Leeres Wörterbuch", "Aktuell ist das Wörterbuch leer. Trotzdem speichern?"):
                return
        path = self.dict_path_for_pair(self.orig_code, self.target_code)
        # make backup
        if os.path.exists(path):
            bak = path + ".bak"
            try:
                with open(path, 'rb') as fr, open(bak, 'wb') as fw:
                    fw.write(fr.read())
            except Exception:
                pass
        # write deduped
        with open(path, 'w', encoding='utf-8') as f:
            for k in sorted(self.dict_data.keys(), key=lambda s: s.lower()):
                vals = self.dict_data.get(k, [])
                # ensure uniqueness and preserve order
                seen = set(); clean = []
                for v in vals:
                    if v and v not in seen:
                        seen.add(v); clean.append(v)
                if clean:
                    f.write("\t".join([k] + clean) + "\n")
                else:
                    f.write(k + "\n")
        self.status.config(text=f"Wörterbuch gespeichert: {path}")
        messagebox.showinfo("Gespeichert", f"Wörterbuch gespeichert:\n{path}")

    # -------------------------
    # Tree operations
    # -------------------------
    def refresh_tree(self, filtered=None):
        # filtered: optional dict to display
        data = filtered if filtered is not None else self.dict_data
        # clear
        for it in self.tree.get_children():
            self.tree.delete(it)
        # add rows
        for k in sorted(data.keys(), key=lambda s: s.lower()):
            vals = data.get(k, [])
            disp = " // ".join(vals) if vals else ""
            self.tree.insert('', 'end', values=(k, disp))
        self.status.config(text=f"{len(data)} Einträge angezeigt")

    def filter_tree(self):
        q = self.search_var.get().strip().lower()
        if not q:
            self.refresh_tree()
            return
        filtered = {}
        for k, vals in self.dict_data.items():
            if q in k.lower() or any(q in v.lower() for v in vals):
                filtered[k] = vals
        self.refresh_tree(filtered)

    def add_entry_dialog(self):
        orig = simpledialog.askstring("Neuer Eintrag - Original", "Begriff in Ausgangssprache:", parent=self)
        if orig is None:
            return
        orig = orig.strip()
        if not orig:
            messagebox.showwarning("Leerer Begriff", "Das Original darf nicht leer sein.")
            return
        trans = simpledialog.askstring("Neuer Eintrag - Übersetzung(en)", "Übersetzungen (mit ' // ' trennen oder mehrere durch Tabulator):", parent=self)
        if trans is None:
            return
        trans_list = self._parse_translations_input(trans)
        existing = self.dict_data.get(orig, [])
        # append new translations preserving order and avoiding duplicates
        for t in trans_list:
            if t not in existing:
                existing.append(t)
        self.dict_data[orig] = existing
        self.refresh_tree()

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Auswahl", "Bitte einen Eintrag auswählen zum Bearbeiten.")
            return
        item = self.tree.item(sel[0])
        orig = item['values'][0]
        current_trans = " // ".join(self.dict_data.get(orig, []))
        new_trans = simpledialog.askstring("Bearbeiten - Übersetzungen", f"Übersetzungen für '{orig}':", initialvalue=current_trans, parent=self)
        if new_trans is None:
            return
        new_list = self._parse_translations_input(new_trans)
        self.dict_data[orig] = new_list
        self.refresh_tree()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Auswahl", "Bitte einen Eintrag auswählen zum Löschen.")
            return
        item = self.tree.item(sel[0])
        orig = item['values'][0]
        if messagebox.askyesno("Löschen", f"Eintrag '{orig}' wirklich löschen?"):
            if orig in self.dict_data:
                del self.dict_data[orig]
            self.refresh_tree()

    def on_tree_double_click(self, event):
        # open edit dialog for clicked row
        self.edit_selected()

    # -------------------------
    # Import / Export helpers
    # -------------------------
    def import_from_texts(self):
        """
        Importiert Paare aus zwei Textdateien:
        - ursprungssprache_text.txt (eine Zeile = Begriffe/Token)
        - zielsprache_text.txt (eine Zeile = Übersetzung(en) für die korrespondierende Zeile)
        """
        messagebox.showinfo("Import", "Wählen Sie zuerst die Ursprungs-Textdatei (links), dann die Ziel-Textdatei (rechts).")
        orig_file = filedialog.askopenfilename(title="Ursprungssprache Textdatei wählen", filetypes=[('Text','*.txt'),('All files','*.*')])
        if not orig_file:
            return
        targ_file = filedialog.askopenfilename(title="Zielsprache Textdatei wählen", filetypes=[('Text','*.txt'),('All files','*.*')])
        if not targ_file:
            return
        with open(orig_file, 'r', encoding='utf-8') as f:
            orig_lines = [line.rstrip('\n') for line in f.readlines()]
        with open(targ_file, 'r', encoding='utf-8') as f:
            targ_lines = [line.rstrip('\n') for line in f.readlines()]
        # merge
        added = 0
        for i, o in enumerate(orig_lines):
            k = o.strip()
            if not k:
                continue
            t_line = targ_lines[i] if i < len(targ_lines) else ''
            parts = [p.strip() for p in t_line.split(' // ') if p.strip()]
            existing = self.dict_data.get(k, [])
            for p in parts:
                if p and p not in existing:
                    existing.append(p)
                    added += 1
            if existing:
                self.dict_data[k] = existing
        self.refresh_tree()
        messagebox.showinfo("Import abgeschlossen", f"Import beendet. Neue Übersetzungen hinzugefügt: {added}")

    def export_as_tsv(self):
        path = filedialog.asksaveasfilename(title="Exportiere Wörterbuch als TSV", defaultextension=".tsv", filetypes=[('TSV','*.tsv'),('Text','*.txt')])
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            for k, vals in sorted(self.dict_data.items(), key=lambda kv: kv[0].lower()):
                line = "\t".join([k] + vals)
                f.write(line + "\n")
        messagebox.showinfo("Export", f"TSV exportiert nach:\n{path}")

    # -------------------------
    # Utilities
    # -------------------------
    @staticmethod
    def _parse_translations_input(s: str):
        # accept either ' // ' delimiter or tabs or commas; return list of cleaned strings
        if '\t' in s:
            parts = [p.strip() for p in s.split('\t') if p.strip()]
        elif ' // ' in s:
            parts = [p.strip() for p in s.split(' // ') if p.strip()]
        else:
            # fallback: split on semicolon or comma
            if ';' in s:
                parts = [p.strip() for p in s.split(';') if p.strip()]
            elif ',' in s:
                parts = [p.strip() for p in s.split(',') if p.strip()]
            else:
                parts = [s.strip()] if s.strip() else []
        # remove duplicates preserving order
        seen = set(); clean = []
        for p in parts:
            if p not in seen:
                seen.add(p); clean.append(p)
        return clean

    @staticmethod
    def _selected_code(raw: str):
        if not raw:
            return None
        parts = raw.split(' - ')
        return parts[0] if parts else None


if __name__ == "__main__":
    app = DictEditor()
    app.mainloop()
