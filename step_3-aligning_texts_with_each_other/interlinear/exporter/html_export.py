"""
HTML Export Module for Interlinear Text Creator

This module exports interlinear texts to various HTML formats:
- Basic HTML (desktop viewing)
- HTML with audio player
- HTML with YouTube QR code
- Mobile App HTML (optimized for Android Interlinear Language Learning App)
- Complete App Package (ZIP with all files ready for import)
"""

import os
import qrcode
import yaml
import zipfile
import shutil
from datetime import datetime

# =============================================================================
# DESKTOP HTML TEMPLATES (Original functionality preserved)
# =============================================================================

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

# =============================================================================
# MOBILE APP HTML TEMPLATE (New - optimized for Android app)
# =============================================================================

MOBILE_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <title>{title}</title>
    <style>
        * {{
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }}
        
        html {{
            font-size: 16px;
            -webkit-text-size-adjust: 100%;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 16px;
            background-color: #0f0f1a;
            color: #ffffff;
            min-height: 100vh;
        }}
        
        .interlinear-container {{
            max-width: 100%;
            overflow-wrap: break-word;
            word-wrap: break-word;
        }}
        
        .sentence-block {{
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid #2a2a4e;
        }}
        
        .sentence-block:last-child {{
            border-bottom: none;
        }}
        
        .word-group {{
            display: inline-block;
            vertical-align: top;
            margin: 4px 12px 12px 0;
            text-align: center;
            min-width: 40px;
        }}
        
        .original-word {{
            font-weight: 600;
            font-size: 1.1em;
            color: #ffffff;
            padding: 2px 0;
            border-bottom: 2px solid #6c5ce7;
        }}
        
        .translation-word {{
            font-size: 0.9em;
            color: #a0a0c0;
            padding-top: 4px;
            font-style: italic;
        }}
        
        .line-break {{
            display: block;
            height: 8px;
        }}
        
        /* Paragraph numbers */
        .paragraph-number {{
            display: block;
            color: #6c5ce7;
            font-size: 0.8em;
            font-weight: bold;
            margin-bottom: 8px;
            opacity: 0.7;
        }}
        
        /* Touch-friendly spacing */
        @media (max-width: 600px) {{
            body {{
                padding: 12px;
            }}
            
            .word-group {{
                margin: 3px 8px 10px 0;
            }}
            
            .original-word {{
                font-size: 1em;
            }}
            
            .translation-word {{
                font-size: 0.85em;
            }}
        }}
        
        /* Dark mode optimizations */
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #0f0f1a;
                color: #ffffff;
            }}
        }}
    </style>
</head>
<body>
    <div class="interlinear-container">
{content}
    </div>
</body>
</html>
"""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def esc(s):
    """Escape HTML special characters."""
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render_words(orig, trans, vd):
    """Render word pairs for desktop HTML (original function preserved)."""
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

def render_mobile_content(orig_lines, trans_lines):
    """
    Render interlinear content optimized for mobile viewing.
    
    Args:
        orig_lines: List of original language lines (one word per line, empty line = sentence break)
        trans_lines: List of translation lines (matching orig_lines)
    
    Returns:
        HTML string with mobile-optimized interlinear layout
    """
    html_parts = []
    sentence_num = 1
    current_sentence = []
    
    for i, (orig, trans) in enumerate(zip(orig_lines, trans_lines)):
        orig = orig.strip() if orig else ""
        trans = trans.strip() if trans else ""
        
        # Empty line indicates sentence/paragraph break
        if not orig:
            if current_sentence:
                # Output the accumulated sentence
                html_parts.append(f'        <div class="sentence-block">')
                html_parts.append(f'            <span class="paragraph-number">§{sentence_num}</span>')
                html_parts.append(''.join(current_sentence))
                html_parts.append('        </div>')
                sentence_num += 1
                current_sentence = []
            continue
        
        # Build word group
        word_html = f'''
            <div class="word-group">
                <div class="original-word">{esc(orig)}</div>
                <div class="translation-word">{esc(trans)}</div>
            </div>'''
        current_sentence.append(word_html)
    
    # Don't forget the last sentence
    if current_sentence:
        html_parts.append(f'        <div class="sentence-block">')
        html_parts.append(f'            <span class="paragraph-number">§{sentence_num}</span>')
        html_parts.append(''.join(current_sentence))
        html_parts.append('        </div>')
    
    return '\n'.join(html_parts)

# =============================================================================
# EXPORT FUNCTIONS - Original (preserved)
# =============================================================================

def generate_basic(folder, title, orig, trans, fs=12, vd=10):
    """
    Generate basic interlinear HTML for desktop viewing.
    (Original function preserved)
    """
    html = HTML_HEADER.format(title=esc(title), fs=fs, vd=vd)
    html += render_words(orig, trans, vd)
    html += HTML_FOOTER
    path = os.path.join(folder, f"{title}_interlinear.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path

def generate_with_audio(folder, title, orig, trans, audio, fs=12, vd=10):
    """
    Generate interlinear HTML with embedded audio player.
    (Original function preserved)
    """
    html = HTML_HEADER.format(title=esc(title), fs=fs, vd=vd)
    html += f"<div class='audio'><audio controls src='{os.path.basename(audio)}'></audio></div>"
    html += render_words(orig, trans, vd)
    html += HTML_FOOTER
    path = os.path.join(folder, f"{title}_interlinear_audio.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path

def generate_with_youtube(folder, title, orig, trans, url, fs=12, vd=10):
    """
    Generate interlinear HTML with YouTube QR code.
    (Original function preserved)
    """
    qr_path = os.path.join(folder, f"{title}_youtube_qr.png")
    qrcode.make(url).save(qr_path)

    html = HTML_HEADER.format(title=esc(title), fs=fs, vd=vd)
    html += f"<div class='qr'><p>{esc(url)}</p><img src='{os.path.basename(qr_path)}'></div>"
    html += render_words(orig, trans, vd)
    html += HTML_FOOTER

    path = os.path.join(folder, f"{title}_interlinear_youtube.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path

# =============================================================================
# NEW EXPORT FUNCTIONS - For Android Interlinear Language Learning App
# =============================================================================

def generate_mobile_app_html(folder, title, orig, trans, source_lang="en", target_lang="de"):
    """
    Generate mobile-optimized interlinear HTML for the Android app.
    
    This creates an HTML file specifically designed to be displayed in the
    Interlinear Language Learning App with:
    - Dark theme matching the app's UI
    - Touch-friendly spacing
    - Responsive layout for various screen sizes
    - Clean, readable typography
    
    Args:
        folder: Output directory
        title: Project title
        orig: List of original language words (one per line)
        trans: List of translations (matching orig)
        source_lang: Source language code (e.g., 'de' for German)
        target_lang: Target language code (e.g., 'en' for English)
    
    Returns:
        Path to the created HTML file
    """
    content = render_mobile_content(orig, trans)
    
    html = MOBILE_HTML_TEMPLATE.format(
        title=esc(title),
        lang=source_lang,
        content=content
    )
    
    # Save as interlinear.html (the filename expected by the app)
    path = os.path.join(folder, "interlinear.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return path

def generate_app_package(folder, title, orig, trans, source_lang, target_lang, 
                         native_lang="English", audio_path=None, author=None, 
                         source=None, description=None):
    """
    Generate a complete package ready for import into the Android app.
    
    Creates a ZIP file containing:
    - interlinear.html (mobile-optimized)
    - project.yaml (metadata)
    - audio.mp3 (if provided)
    
    Args:
        folder: Output directory
        title: Project title
        orig: List of original language words
        trans: List of translations
        source_lang: Source/target language being learned (e.g., 'Swiss German')
        target_lang: Language code for HTML lang attribute
        native_lang: User's native language (e.g., 'English')
        audio_path: Optional path to audio file
        author: Optional author name
        source: Optional source attribution
        description: Optional project description
    
    Returns:
        Path to the created ZIP file
    """
    # Create a temporary folder for the package contents
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
    package_folder = os.path.join(folder, f"{safe_title}_app_package")
    os.makedirs(package_folder, exist_ok=True)
    
    # 1. Generate mobile-optimized HTML
    generate_mobile_app_html(package_folder, title, orig, trans, target_lang, target_lang)
    
    # 2. Create project.yaml
    project_data = {
        'project_name': title,
        'target_language': source_lang,
        'native_language': native_lang,
    }
    if author:
        project_data['author'] = author
    if source:
        project_data['source'] = source
    if description:
        project_data['description'] = description
    
    yaml_path = os.path.join(package_folder, "project.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(project_data, f, allow_unicode=True, default_flow_style=False)
    
    # 3. Copy audio file if provided
    if audio_path and os.path.exists(audio_path):
        audio_dest = os.path.join(package_folder, "audio.mp3")
        shutil.copy2(audio_path, audio_dest)
    
    # 4. Create ZIP file
    zip_path = os.path.join(folder, f"{safe_title}_for_app.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_folder)
                zipf.write(file_path, arcname)
    
    # 5. Clean up temporary folder (optional - keep for inspection)
    # shutil.rmtree(package_folder)
    
    return zip_path
