import os

def load_dictionary(path):
    d = {}
    if not os.path.exists(path):
        return d

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            d[parts[0]] = list(dict.fromkeys(parts[1:]))

    return d

def save_dictionary(path, d):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for k, v in d.items():
            f.write("\t".join([k] + v) + "\n")

def merge_from_lines(existing, orig_lines, target_lines, delimiter=" // "):
    d = dict(existing)
    for i, o in enumerate(orig_lines):
        key = o.strip()
        if not key:
            continue
        parts = [p.strip() for p in (target_lines[i] if i < len(target_lines) else "").split(delimiter) if p.strip()]
        d.setdefault(key, [])
        for p in parts:
            if p not in d[key]:
                d[key].append(p)
    return d
