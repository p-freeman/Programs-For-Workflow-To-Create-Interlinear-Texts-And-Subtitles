import os, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .dictionary import load_dictionary, save_dictionary, merge_from_lines
from .project_io import save_text_file, save_project_json
from .exporter.html_export import (
    generate_basic, generate_with_audio, generate_with_youtube
)

LANG_SOURCE = [
    "German-DE", "Swissgerman-CHDE", "English-EN", "Spanish-ES"
]
LANG_TARGET = [
    "English-EN", "German-DE", "French-FR",
    "Russian-RU", "Ukrainian-UA", "Persian-FA"
]

class InterlinearApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gegenübersteller-App v4")
        self.geometry("1200x750")
        self.project_folder = ""
        self._build()

    def _build(self):
        top = tk.Frame(self); top.pack(fill="x", pady=5)

        tk.Label(top,text="Title:").pack(side="left")
        self.title_entry = tk.Entry(top,width=40)
        self.title_entry.pack(side="left", padx=5)

        tk.Label(top,text="YouTube URL:").pack(side="left")
        self.yt_entry = tk.Entry(top,width=40)
        self.yt_entry.pack(side="left", padx=5)

        lang = tk.Frame(self); lang.pack(fill="x")
        self.src = ttk.Combobox(lang,values=LANG_SOURCE,state="readonly")
        self.tgt = ttk.Combobox(lang,values=LANG_TARGET,state="readonly")
        tk.Label(lang,text="Source").pack(side="left"); self.src.pack(side="left")
        tk.Label(lang,text="Target").pack(side="left"); self.tgt.pack(side="left")

        btn = tk.Frame(self); btn.pack(fill="x", pady=5)
        tk.Button(btn,text="Save Project",command=self.save).pack(side="left")
        tk.Button(btn,text="Export HTML",command=self.export).pack(side="left")

        self.audio = tk.BooleanVar()
        tk.Checkbutton(btn,text="Audio available",variable=self.audio).pack(side="left", padx=10)

        texts = tk.Frame(self); texts.pack(expand=True, fill="both")
        self.orig = tk.Text(texts); self.orig.pack(side="left",expand=True,fill="both")
        self.tran = tk.Text(texts); self.tran.pack(side="left",expand=True,fill="both")

    def save(self):
        if not self.project_folder:
            self.project_folder = filedialog.askdirectory()
            if not self.project_folder:
                return

        title = self.title_entry.get().strip() or "Project"
        orig = self.orig.get("1.0",tk.END).splitlines()
        tran = self.tran.get("1.0",tk.END).splitlines()

        save_text_file(self.project_folder,"source.txt","\n".join(orig))
        save_text_file(self.project_folder,"target.txt","\n".join(tran))

        save_project_json(self.project_folder,title,{
            "title":title,
            "source_language":self.src.get(),
            "target_language":self.tgt.get(),
            "youtube_url":self.yt_entry.get(),
            "audio":self.audio.get()
        })

        dict_path = os.path.join(self.project_folder,f"{self.src.get()}_{self.tgt.get()}.dict.txt")
        save_dictionary(dict_path, merge_from_lines(load_dictionary(dict_path), orig, tran))

        messagebox.showinfo("Saved","Project saved")

    def export(self):
        title = self.title_entry.get().strip() or "Project"
        orig = self.orig.get("1.0",tk.END).splitlines()
        tran = self.tran.get("1.0",tk.END).splitlines()

        generate_basic(self.project_folder,title,orig,tran,12,10)

        if self.audio.get():
            generate_with_audio(
                self.project_folder,title,orig,tran,
                os.path.join(self.project_folder,title+".mp3"),12,10
            )

        if self.yt_entry.get().strip():
            generate_with_youtube(
                self.project_folder,title,orig,tran,
                self.yt_entry.get().strip(),12,10
            )

        messagebox.showinfo("Export","HTML files created")
