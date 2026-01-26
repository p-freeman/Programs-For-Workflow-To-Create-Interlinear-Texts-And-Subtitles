import os
import qrcode

HTML_HEADER = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
body {{ font-family:sans-serif; margin:16px; }}
.word {{ display:inline-block; margin-right:20px; margin-bottom:{vd}px; vertical-align:top; }}
.orig {{ font-weight:bold; }}
.trans {{ margin-top:5px; }}
.audio {{ margin-bottom:15px; }}
.qr {{ margin:20px 0; }}
</style>
</head>
<body style="font-size:{fs}px;">
<h1>{title}</h1>
"""

HTML_FOOTER = """
</body>
</html>
"""

def esc(s):
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def render_words(orig, trans, vd):
    rows = []
    for o, t in zip(orig, trans):
        if not o.strip():
            rows.append("<br>")
            continue
        rows.append(
            f"<div class='word'><div class='orig'>{esc(o)}</div>"
            f"<div class='trans'>{esc(t)}</div></div>"
        )
    return "\n".join(rows)

def generate_basic(folder, title, orig, trans, fs, vd):
    html = HTML_HEADER.format(title=esc(title), fs=fs, vd=vd)
    html += render_words(orig, trans, vd)
    html += HTML_FOOTER
    path = os.path.join(folder, f"{title}_interlinear.html")
    open(path,"w",encoding="utf-8").write(html)

def generate_with_audio(folder, title, orig, trans, audio, fs, vd):
    html = HTML_HEADER.format(title=esc(title), fs=fs, vd=vd)
    html += f"<div class='audio'><audio controls src='{os.path.basename(audio)}'></audio></div>"
    html += render_words(orig, trans, vd)
    html += HTML_FOOTER
    path = os.path.join(folder, f"{title}_interlinear_audio.html")
    open(path,"w",encoding="utf-8").write(html)

def generate_with_youtube(folder, title, orig, trans, url, fs, vd):
    qr_path = os.path.join(folder, f"{title}_youtube_qr.png")
    qrcode.make(url).save(qr_path)

    html = HTML_HEADER.format(title=esc(title), fs=fs, vd=vd)
    html += f"<div class='qr'><p>{esc(url)}</p><img src='{os.path.basename(qr_path)}'></div>"
    html += render_words(orig, trans, vd)
    html += HTML_FOOTER

    path = os.path.join(folder, f"{title}_interlinear_youtube.html")
    open(path,"w",encoding="utf-8").write(html)
