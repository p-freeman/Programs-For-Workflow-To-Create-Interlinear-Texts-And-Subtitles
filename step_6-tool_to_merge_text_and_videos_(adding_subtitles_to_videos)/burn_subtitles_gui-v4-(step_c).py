#!/usr/bin/env python3
"""
burn_subtitles_gui.py - GUI to burn interlinear subtitles
onto videos (CHDE + DE) based on groups of JSON-files.

Requires: Pillow, moviepy (pip install pillow moviepy)
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import json, os

class App:
    def __init__(self, root):
        self.root = root
        root.title("Burn Subtitles GUI")
        frame = tk.Frame(root, padx=8, pady=8)
        frame.pack(fill='both', expand=True)

        # Video-Selection
        tk.Label(frame, text="Video file:").grid(row=0,column=0,sticky='w')
        self.video_entry = tk.Entry(frame, width=60); self.video_entry.grid(row=0,column=1)
        tk.Button(frame, text="Browse", command=self.browse_video).grid(row=0,column=2)

        # Groups JSON
        tk.Label(frame, text="Groups JSON:").grid(row=1,column=0,sticky='w')
        self.json_entry = tk.Entry(frame, width=60); self.json_entry.grid(row=1,column=1)
        tk.Button(frame, text="Browse", command=self.browse_json).grid(row=1,column=2)

        # CHDE File (Source Language File)
        tk.Label(frame, text="CHDE file:").grid(row=2,column=0,sticky='w')
        self.chde_entry = tk.Entry(frame, width=60); self.chde_entry.grid(row=2,column=1)
        tk.Button(frame, text="Browse", command=self.browse_chde).grid(row=2,column=2)

        # DE File (Target Language File)
        tk.Label(frame, text="DE file:").grid(row=3,column=0,sticky='w')
        self.de_entry = tk.Entry(frame, width=60); self.de_entry.grid(row=3,column=1)
        tk.Button(frame, text="Browse", command=self.browse_de).grid(row=3,column=2)

        # Font
        tk.Label(frame, text="Font (TTF):").grid(row=4,column=0,sticky='w')
        self.font_entry = tk.Entry(frame, width=60); self.font_entry.grid(row=4,column=1)
        tk.Button(frame, text="Browse", command=self.browse_font).grid(row=4,column=2)

        # Font size
        tk.Label(frame, text="Font size:").grid(row=5,column=0,sticky='w')
        self.fontsize = tk.Entry(frame, width=10); self.fontsize.grid(row=5,column=1,sticky='w'); self.fontsize.insert(0,"36")

        # Output file
        tk.Label(frame, text="Output file:").grid(row=6,column=0,sticky='w')
        self.output_entry = tk.Entry(frame, width=60); self.output_entry.grid(row=6,column=1)
        tk.Button(frame, text="Browse", command=self.browse_output).grid(row=6,column=2)

        tk.Button(frame, text="Burn Subtitles", command=self.burn_subtitles).grid(row=7,column=1, pady=8)

    def browse_video(self):
        p = filedialog.askopenfilename(filetypes=[("Video files","*.mp4;*.mov;*.avi"),("All files","*.*")])
        if p: self.video_entry.delete(0,tk.END); self.video_entry.insert(0,p)

    def browse_json(self):
        p = filedialog.askopenfilename(filetypes=[("JSON files","*.json"),("All files","*.*")])
        if p: self.json_entry.delete(0,tk.END); self.json_entry.insert(0,p)

    def browse_chde(self):
        p = filedialog.askopenfilename(filetypes=[("Text files","*.txt"),("All files","*.*")])
        if p: self.chde_entry.delete(0,tk.END); self.chde_entry.insert(0,p)

    def browse_de(self):
        p = filedialog.askopenfilename(filetypes=[("Text files","*.txt"),("All files","*.*")])
        if p: self.de_entry.delete(0,tk.END); self.de_entry.insert(0,p)

    def browse_font(self):
        p = filedialog.askopenfilename(filetypes=[("Font files","*.ttf;*.otf"),("All files","*.*")])
        if p: self.font_entry.delete(0,tk.END); self.font_entry.insert(0,p)

    def browse_output(self):
        p = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files","*.mp4"),("All files","*.*")])
        if p: self.output_entry.delete(0,tk.END); self.output_entry.insert(0,p)

    def burn_subtitles(self):
        video_path = self.video_entry.get().strip()
        json_path = self.json_entry.get().strip()
        chde_path = self.chde_entry.get().strip()
        de_path = self.de_entry.get().strip()
        font_path = self.font_entry.get().strip() or None
        fontsize = int(self.fontsize.get().strip() or 36)
        output_path = self.output_entry.get().strip()

        if not all([video_path,json_path,chde_path,de_path,output_path]):
            messagebox.showerror("Error","Please select all required files and output path.")
            return

        # Load JSON Groups
        with open(json_path,'r',encoding='utf-8') as f:
            data = json.load(f)

        # Load CHDE/DE Lines (Load Lines of Source Language and Target Language)
        with open(chde_path,'r',encoding='utf-8') as f: ch_lines = [ln.strip() for ln in f]
        with open(de_path,'r',encoding='utf-8') as f: de_lines = [ln.strip() for ln in f]

        # Load Video
        clip = VideoFileClip(video_path)
        txt_clips = []

        for g in data['groups']:
            start = g['start_line']-1
            end = g['end_line']
            ch_text = " ".join(ch_lines[start:end])
            de_text = " ".join(de_lines[start:end])

            # Create Textclips
            ch_clip = TextClip(ch_text, fontsize=fontsize, font=font_path, color='white', bg_color='dimgray', align='center')
            de_clip = TextClip(de_text, fontsize=fontsize, font=font_path, color='white', bg_color='dimgray', align='center')

            # Position: 80% from the top border
            ch_clip = ch_clip.set_position(('center', clip.h*0.8 - fontsize)).set_duration(clip.duration)
            de_clip = de_clip.set_position(('center', clip.h*0.8)).set_duration(clip.duration)

            txt_clips.extend([ch_clip,de_clip])

        final = CompositeVideoClip([clip]+txt_clips)
        final.write_videofile(output_path, codec="libx264")
        messagebox.showinfo("Done","Video with subtitles saved!")

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
