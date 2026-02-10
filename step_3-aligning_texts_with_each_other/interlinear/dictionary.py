"""
Dictionary Module for Interlinear Text Creator

Handles loading, saving, and merging word translation dictionaries.
"""

import os

def load_dictionary(path):
    """
    Load a dictionary file into a dict.
    
    Format: one entry per line, "original_word\ttranslation"
    """
    d = {}
    if not os.path.exists(path):
        return d
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "\t" not in line:
                continue
            parts = line.split("\t", 1)
            if len(parts) == 2:
                d[parts[0]] = parts[1]
    return d

def save_dictionary(path, d):
    """
    Save a dictionary to file.
    """
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for k, v in sorted(d.items()):
            f.write(f"{k}\t{v}\n")

def merge_from_lines(existing_dict, orig_lines, trans_lines):
    """
    Merge word pairs from aligned lines into existing dictionary.
    """
    d = dict(existing_dict)
    for o, t in zip(orig_lines, trans_lines):
        o = o.strip()
        t = t.strip()
        if o and t:
            d[o] = t
    return d
