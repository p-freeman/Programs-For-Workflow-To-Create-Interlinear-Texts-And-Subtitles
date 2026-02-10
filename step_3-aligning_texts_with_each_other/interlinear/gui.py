"""
GUI Module for Interlinear Text Creator

Provides the main graphical user interface using tkinter.
Works on Linux Mint Debian Edition and other Linux distributions.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .dictionary import load_dictionary, save_dictionary, merge_from_lines
from .project_io import save_text_file, save_project_json, load_text_file, load_project_json
from .exporter.html_export import (
    generate_basic, 
    generate_with_audio, 
    generate_with_youtube,
    generate_mobile_app_html,
    generate_app_package
)

# Available languages
LANG_SOURCE = [
    "German-DE", "Swissgerman-CHDE", "English-EN", "Spanish-ES",
    "French-FR", "Italian-IT", "Portuguese-PT", "Russian-RU",
    "Ukrainian-UA", "Turkish-TR", "Kurdish-KU", "Persian-FA"
]

LANG_TARGET = [
    "English-EN", "German-DE", "French-FR", "Spanish-ES",
    "Italian-IT", "Portuguese-PT", "Russian-RU", "Ukrainian-UA",
    "Turkish-TR", "Kurdish-KU", "Persian-FA"
]

# Language display names for the app
LANG_DISPLAY_NAMES = {
    "German-DE": "German",
    "Swissgerman-CHDE": "Swiss German",
    "English-EN": "English",
    "Spanish-ES": "Spanish",
    "French-FR": "French",
    "Italian-IT": "Italian",
    "Portuguese-PT": "Portuguese",
    "Russian-RU": "Russian",
    "Ukrainian-UA": "Ukrainian",
    "Turkish-TR": "Turkish",
    "Kurdish-KU": "Kurdish",
    "Persian-FA": "Persian"
}


class InterlinearApp(tk.Tk):
    """
    Main application window for creating interlinear texts.
    """
    
    def __init__(self):
        super().__init__()
        self.title("Interlinear Text Creator v5 (with Android App Export)")
        self.geometry("1200x800")
        self.project_folder = ""
        self._build()
    
    def _build(self):
        """Build the GUI components."""
        
        # Top frame - Title and YouTube URL
        top = tk.Frame(self)
        top.pack(fill="x", pady=5, padx=10)
        
        tk.Label(top, text="Title:").pack(side="left")
        self.title_entry = tk.Entry(top, width=40)
        self.title_entry.pack(side="left", padx=5)
        
        tk.Label(top, text="YouTube URL:").pack(side="left")
        self.yt_entry = tk.Entry(top, width=40)
        self.yt_entry.pack(side="left", padx=5)
        
        # Language selection frame
        lang = tk.Frame(self)
        lang.pack(fill="x", padx=10)
        
        tk.Label(lang, text="Source Language (learning):").pack(side="left")
        self.src = ttk.Combobox(lang, values=LANG_SOURCE, state="readonly", width=20)
        self.src.pack(side="left", padx=5)
        self.src.set(LANG_SOURCE[1])  # Default: Swiss German
        
        tk.Label(lang, text="Target Language (native):").pack(side="left")
        self.tgt = ttk.Combobox(lang, values=LANG_TARGET, state="readonly", width=20)
        self.tgt.pack(side="left", padx=5)
        self.tgt.set(LANG_TARGET[0])  # Default: English
        
        # Metadata frame
        meta = tk.Frame(self)
        meta.pack(fill="x", pady=5, padx=10)
        
        tk.Label(meta, text="Author:").pack(side="left")
        self.author_entry = tk.Entry(meta, width=25)
        self.author_entry.pack(side="left", padx=5)
        
        tk.Label(meta, text="Source:").pack(side="left")
        self.source_entry = tk.Entry(meta, width=25)
        self.source_entry.pack(side="left", padx=5)
        
        tk.Label(meta, text="Description:").pack(side="left")
        self.desc_entry = tk.Entry(meta, width=40)
        self.desc_entry.pack(side="left", padx=5)
        
        # Button frame
        btn = tk.Frame(self)
        btn.pack(fill="x", pady=5, padx=10)
        
        tk.Button(btn, text="📂 Open Project", command=self.open_project).pack(side="left", padx=2)
        tk.Button(btn, text="💾 Save Project", command=self.save).pack(side="left", padx=2)
        
        ttk.Separator(btn, orient="vertical").pack(side="left", padx=10, fill="y")
        
        tk.Button(btn, text="📄 Export HTML (Desktop)", command=self.export_desktop).pack(side="left", padx=2)
        tk.Button(btn, text="📱 Export for Android App", command=self.export_mobile, 
                  bg="#6c5ce7", fg="white").pack(side="left", padx=2)
        tk.Button(btn, text="📦 Create App Package (ZIP)", command=self.export_package,
                  bg="#00b894", fg="white").pack(side="left", padx=2)
        
        # Audio checkbox
        self.audio = tk.BooleanVar()
        tk.Checkbutton(btn, text="Audio available", variable=self.audio).pack(side="left", padx=10)
        
        # Text editing area with labels
        text_frame = tk.Frame(self)
        text_frame.pack(expand=True, fill="both", padx=10, pady=5)
        
        # Left side - Original text
        left_frame = tk.Frame(text_frame)
        left_frame.pack(side="left", expand=True, fill="both")
        tk.Label(left_frame, text="Original Text (one word per line, empty line = sentence break)",
                 font=("Arial", 10, "bold")).pack(anchor="w")
        self.orig = tk.Text(left_frame, wrap="none", font=("Consolas", 11))
        self.orig.pack(expand=True, fill="both")
        
        # Right side - Translation
        right_frame = tk.Frame(text_frame)
        right_frame.pack(side="left", expand=True, fill="both")
        tk.Label(right_frame, text="Translation (matching lines)",
                 font=("Arial", 10, "bold")).pack(anchor="w")
        self.tran = tk.Text(right_frame, wrap="none", font=("Consolas", 11))
        self.tran.pack(expand=True, fill="both")
        
        # Status bar
        self.status = tk.Label(self, text="Ready - Select a project folder to begin", 
                                bd=1, relief="sunken", anchor="w")
        self.status.pack(fill="x", side="bottom")
    
    def set_status(self, msg):
        """Update status bar message."""
        self.status.config(text=msg)
        self.update_idletasks()
    
    def open_project(self):
        """Open an existing project folder."""
        folder = filedialog.askdirectory(title="Select Project Folder")
        if not folder:
            return
        
        self.project_folder = folder
        
        # Try to load existing files
        source_text = load_text_file(folder, "source.txt")
        target_text = load_text_file(folder, "target.txt")
        
        if source_text:
            self.orig.delete("1.0", tk.END)
            self.orig.insert("1.0", source_text)
        
        if target_text:
            self.tran.delete("1.0", tk.END)
            self.tran.insert("1.0", target_text)
        
        # Try to load project metadata
        for f in os.listdir(folder):
            if f.endswith(".project.json"):
                try:
                    data = load_project_json(os.path.join(folder, f))
                    if "title" in data:
                        self.title_entry.delete(0, tk.END)
                        self.title_entry.insert(0, data["title"])
                    if "youtube_url" in data:
                        self.yt_entry.delete(0, tk.END)
                        self.yt_entry.insert(0, data.get("youtube_url", ""))
                    if "source_language" in data:
                        self.src.set(data["source_language"])
                    if "target_language" in data:
                        self.tgt.set(data["target_language"])
                    if "audio" in data:
                        self.audio.set(data["audio"])
                except:
                    pass
                break
        
        self.set_status(f"Opened project: {folder}")
    
    def save(self):
        """Save the current project."""
        if not self.project_folder:
            self.project_folder = filedialog.askdirectory(title="Select Project Folder")
            if not self.project_folder:
                return
        
        title = self.title_entry.get().strip() or "Project"
        orig = self.orig.get("1.0", tk.END).splitlines()
        tran = self.tran.get("1.0", tk.END).splitlines()
        
        # Save text files
        save_text_file(self.project_folder, "source.txt", "\n".join(orig))
        save_text_file(self.project_folder, "target.txt", "\n".join(tran))
        
        # Save project metadata
        save_project_json(self.project_folder, title, {
            "title": title,
            "source_language": self.src.get(),
            "target_language": self.tgt.get(),
            "youtube_url": self.yt_entry.get(),
            "audio": self.audio.get(),
            "author": self.author_entry.get(),
            "source": self.source_entry.get(),
            "description": self.desc_entry.get()
        })
        
        # Save/update dictionary
        dict_path = os.path.join(self.project_folder, 
                                  f"{self.src.get()}_{self.tgt.get()}.dict.txt")
        save_dictionary(dict_path, merge_from_lines(load_dictionary(dict_path), orig, tran))
        
        self.set_status(f"Project saved to: {self.project_folder}")
        messagebox.showinfo("Saved", "Project saved successfully!")
    
    def export_desktop(self):
        """Export HTML files for desktop viewing (original functionality)."""
        if not self.project_folder:
            messagebox.showwarning("Warning", "Please save the project first!")
            return
        
        title = self.title_entry.get().strip() or "Project"
        orig = self.orig.get("1.0", tk.END).splitlines()
        tran = self.tran.get("1.0", tk.END).splitlines()
        
        # Generate basic HTML
        generate_basic(self.project_folder, title, orig, tran, 12, 10)
        
        # Generate with audio if available
        if self.audio.get():
            audio_path = os.path.join(self.project_folder, f"{title}.mp3")
            generate_with_audio(self.project_folder, title, orig, tran, audio_path, 12, 10)
        
        # Generate with YouTube QR if URL provided
        if self.yt_entry.get().strip():
            generate_with_youtube(self.project_folder, title, orig, tran,
                                   self.yt_entry.get().strip(), 12, 10)
        
        self.set_status(f"Desktop HTML exported to: {self.project_folder}")
        messagebox.showinfo("Export", "Desktop HTML files created!")
    
    def export_mobile(self):
        """Export mobile-optimized HTML for Android app."""
        if not self.project_folder:
            messagebox.showwarning("Warning", "Please save the project first!")
            return
        
        title = self.title_entry.get().strip() or "Project"
        orig = self.orig.get("1.0", tk.END).splitlines()
        tran = self.tran.get("1.0", tk.END).splitlines()
        
        # Get language code for HTML
        src_lang = self.src.get().split("-")[-1].lower() if self.src.get() else "de"
        
        path = generate_mobile_app_html(self.project_folder, title, orig, tran, src_lang)
        
        self.set_status(f"Mobile HTML exported: {path}")
        messagebox.showinfo("Export", 
            f"Mobile-optimized HTML created!\n\n"
            f"File: interlinear.html\n\n"
            f"This file can be imported into the\n"
            f"Interlinear Language Learning App.")
    
    def export_package(self):
        """Export complete ZIP package for Android app."""
        if not self.project_folder:
            messagebox.showwarning("Warning", "Please save the project first!")
            return
        
        title = self.title_entry.get().strip() or "Project"
        orig = self.orig.get("1.0", tk.END).splitlines()
        tran = self.tran.get("1.0", tk.END).splitlines()
        
        # Get language names for app
        src_lang_code = self.src.get()
        tgt_lang_code = self.tgt.get()
        source_lang = LANG_DISPLAY_NAMES.get(src_lang_code, src_lang_code)
        native_lang = LANG_DISPLAY_NAMES.get(tgt_lang_code, tgt_lang_code)
        lang_code = src_lang_code.split("-")[-1].lower() if src_lang_code else "de"
        
        # Check for audio file
        audio_path = None
        for ext in [".mp3", ".MP3"]:
            potential_path = os.path.join(self.project_folder, f"{title}{ext}")
            if os.path.exists(potential_path):
                audio_path = potential_path
                break
        
        # Also check for audio.mp3
        if not audio_path:
            potential_path = os.path.join(self.project_folder, "audio.mp3")
            if os.path.exists(potential_path):
                audio_path = potential_path
        
        zip_path = generate_app_package(
            folder=self.project_folder,
            title=title,
            orig=orig,
            trans=tran,
            source_lang=source_lang,
            target_lang=lang_code,
            native_lang=native_lang,
            audio_path=audio_path,
            author=self.author_entry.get().strip() or None,
            source=self.source_entry.get().strip() or None,
            description=self.desc_entry.get().strip() or None
        )
        
        self.set_status(f"App package created: {zip_path}")
        messagebox.showinfo("Export", 
            f"App package created!\n\n"
            f"File: {os.path.basename(zip_path)}\n\n"
            f"This ZIP file can be directly imported\n"
            f"into the Interlinear Language Learning App\n"
            f"on your Android device.")


def main():
    """Main entry point."""
    app = InterlinearApp()
    app.mainloop()


if __name__ == "__main__":
    main()
