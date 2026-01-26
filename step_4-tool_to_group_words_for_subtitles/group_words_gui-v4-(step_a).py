#!/usr/bin/env python3
"""
group_words_gui.py
A GUI-Wrapper for the grouping (Greedy).
With DE/EN-language-switching, Folder-Choosing-Ability and new readable txt-Output.
Requires: Pillow (pip install pillow)
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import json, os
from PIL import ImageFont, ImageDraw, Image

# ------------------ Hilfsfunktionen ------------------

def measure_text_px(text, font):
    img = Image.new('RGB', (1,1))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0,0), text, font=font)
    return bbox[2] - bbox[0]

def load_lines(path):
    with open(path,'r',encoding='utf-8') as f:
        return [ln.rstrip('\n') for ln in f]

def default_font(fontpath, size):
    try:
        if fontpath:
            return ImageFont.truetype(fontpath, size=size)
        for p in ["arial.ttf","DejaVuSans.ttf","LiberationSans-Regular.ttf"]:
            try:
                return ImageFont.truetype(p, size=size)
            except:
                pass
        return ImageFont.load_default()
    except Exception as e:
        raise

def group_pairs(chde_lines, de_lines, font, max_line_px, padding):
    n = max(len(chde_lines), len(de_lines))
    chde = chde_lines + [''] * (n - len(chde_lines))
    de = de_lines + [''] * (n - len(de_lines))
    pair_widths = []
    for a,b in zip(chde,de):
        wa = measure_text_px(a, font) if a else 0
        wb = measure_text_px(b, font) if b else 0
        pair_widths.append(max(wa, wb) + padding)
    groups = []
    cur_start = 0
    acc = 0
    for i,w in enumerate(pair_widths):
        if acc + w <= max_line_px:
            acc += w
        else:
            groups.append({'start_line': cur_start+1, 'end_line': i, 'width_px': acc})
            cur_start = i
            acc = w
    if cur_start < n:
        groups.append({'start_line': cur_start+1, 'end_line': n, 'width_px': acc})
    mapping = {}
    for gi,g in enumerate(groups, start=1):
        for ln in range(g['start_line'], g['end_line']+1):
            mapping[ln] = gi
    return groups, mapping

# ------------------ GUI-Class ------------------

class App:
    def __init__(self, root):
        self.root = root
        root.title("Group Words GUI")
        frame = tk.Frame(root, padx=8, pady=8)
        frame.pack(fill='both', expand=True)

        # Language: DE or EN
        tk.Label(frame, text="Language:").grid(row=0,column=0,sticky='w')
        self.lang_var = tk.StringVar(value='DE')
        tk.OptionMenu(frame, self.lang_var, 'DE','EN', command=self.update_labels).grid(row=0,column=1,sticky='w')

        # Labels & Inputs
        self.labels = {}
        row = 1
        for key,default in [("chde","CHDE file:"), ("de","DE file:"),
                             ("font","Font (TTF):"), ("fontsize","Font size:"),
                             ("maxpx","Max line width (px)"), ("padding","Padding per pair (px)"),
                             ("outpref","Output prefix:"), ("outfolder","Output folder:")]:
            self.labels[key] = tk.Label(frame, text=default)
            self.labels[key].grid(row=row,column=0,sticky='w')
            if key in ["chde","de","font","outpref","outfolder"]:
                entry = tk.Entry(frame, width=60)
                entry.grid(row=row,column=1)
                setattr(self, key+"_entry", entry)
                if key=="chde": tk.Button(frame, text="Browse", command=self.browse_chde).grid(row=row,column=2)
                if key=="de": tk.Button(frame, text="Browse", command=self.browse_de).grid(row=row,column=2)
                if key=="font": tk.Button(frame, text="Browse", command=self.browse_font).grid(row=row,column=2)
                if key=="outfolder": tk.Button(frame, text="Browse", command=self.browse_outfolder).grid(row=row,column=2)
            else:
                entry = tk.Entry(frame, width=12)
                entry.grid(row=row,column=1,sticky='w')
                setattr(self, key, entry)
            row += 1

        # Standardwerte
        self.fontsize.insert(0,"36")
        self.maxpx.insert(0,"1200")
        self.padding.insert(0,"10")
        self.outpref_entry.insert(0,"out/groups")

        tk.Button(frame, text="Create Groups", command=self.create_groups).grid(row=row,column=1,pady=8)
        self.update_labels()  # initial

    # ------------------ Browsing ------------------
    def browse_chde(self):
        p = filedialog.askopenfilename(filetypes=[("Text files","*.txt"),("All files","*.*")])
        if p: self.chde_entry.delete(0,tk.END); self.chde_entry.insert(0,p)
    def browse_de(self):
        p = filedialog.askopenfilename(filetypes=[("Text files","*.txt"),("All files","*.*")])
        if p: self.de_entry.delete(0,tk.END); self.de_entry.insert(0,p)
    def browse_font(self):
        p = filedialog.askopenfilename(filetypes=[("Font files","*.ttf;*.otf"),("All files","*.*")])
        if p: self.font_entry.delete(0,tk.END); self.font_entry.insert(0,p)
    def browse_outfolder(self):
        p = filedialog.askdirectory()
        if p: self.outfolder_entry.delete(0,tk.END); self.outfolder_entry.insert(0,p)

    # ------------------ Labels DE/EN ------------------
    def update_labels(self, *_):
        lang = self.lang_var.get()
        if lang=='DE':
            self.labels["chde"].config(text="Datei auf Schweizerdeutsch:")
            self.labels["de"].config(text="Datei auf Deutsch:")
            self.labels["font"].config(text="Schriftart (TTF):")
            self.labels["fontsize"].config(text="Schriftgrösse")
            self.labels["maxpx"].config(text="Maximale Zeilenbreite (px)")
            self.labels["padding"].config(text="Pufferzone pro Paar (px)")
            self.labels["outpref"].config(text="Ausgabe Präfix")
            self.labels["outfolder"].config(text="Ausgabe Ordner:")
        else:
            self.labels["chde"].config(text="CHDE file:")
            self.labels["de"].config(text="DE file:")
            self.labels["font"].config(text="Font (TTF):")
            self.labels["fontsize"].config(text="Font size:")
            self.labels["maxpx"].config(text="Max line width (px)")
            self.labels["padding"].config(text="Padding per pair (px)")
            self.labels["outpref"].config(text="Output prefix:")
            self.labels["outfolder"].config(text="Output folder:")

    # ------------------ Create Groups ------------------
    def create_groups(self):
        chde_path = self.chde_entry.get().strip()
        de_path = self.de_entry.get().strip()
        outfolder = self.outfolder_entry.get().strip()
        if not chde_path or not de_path:
            messagebox.showerror("Fehler" if self.lang_var.get()=="DE" else "Error", 
                                 "Bitte CHDE- und DE-Datei auswählen." if self.lang_var.get()=="DE" else "Please select CHDE and DE files.")
            return
        if not outfolder:
            messagebox.showerror("Fehler" if self.lang_var.get()=="DE" else "Error",
                                 "Bitte Ausgabeordner auswählen." if self.lang_var.get()=="DE" else "Please select output folder.")
            return
        try:
            ch_lines = load_lines(chde_path)
            de_lines = load_lines(de_path)
            fontpath = self.font_entry.get().strip() or None
            fs = int(self.fontsize.get() or 36)
            font = default_font(fontpath, fs)
            maxpx = int(self.maxpx.get() or 1200)
            padding = int(self.padding.get() or 10)

            groups, mapping = group_pairs(ch_lines, de_lines, font, maxpx, padding)

            # Write files
            outpref = self.outpref_entry.get().strip() or "groups"
            os.makedirs(outfolder, exist_ok=True)
            json_path = os.path.join(outfolder, "groups.json")
            txt_path = os.path.join(outfolder, "groups_readable.txt")

            # JSON
            with open(json_path,'w',encoding='utf-8') as f:
                json.dump({'groups':groups,'mapping':mapping}, f, ensure_ascii=False, indent=2)

            # Readable TXT only with CHDE-Words
            with open(txt_path,'w',encoding='utf-8') as f:
                for gi,g in enumerate(groups, start=1):
                    f.write(f"Group {gi}: lines {g['start_line']}..{g['end_line']}, width_px={g['width_px']}\n")
                    for ln in range(g['start_line']-1, g['end_line']):
                        left = ch_lines[ln] if ln < len(ch_lines) else ''
                        f.write(f"  {left}\n")
                    f.write("\n")

            messagebox.showinfo("Fertig" if self.lang_var.get()=="DE" else "Done",
                                f"Dateien erstellt:\n{json_path}\n{txt_path}")
        except Exception as e:
            messagebox.showerror("Fehler" if self.lang_var.get()=="DE" else "Error", str(e))

# ------------------ Main ------------------

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
