"""
Alignment Module for Interlinear Text Creator

Handles text alignment operations.
"""

def align_texts(source_lines, target_lines):
    """
    Align source and target text lines.
    Pads shorter list with empty strings.
    """
    max_len = max(len(source_lines), len(target_lines))
    
    # Pad lists to equal length
    while len(source_lines) < max_len:
        source_lines.append("")
    while len(target_lines) < max_len:
        target_lines.append("")
    
    return source_lines, target_lines

def count_words(lines):
    """
    Count non-empty words in a list of lines.
    """
    return sum(1 for line in lines if line.strip())

def count_sentences(lines):
    """
    Count sentences (groups separated by empty lines).
    """
    count = 0
    in_sentence = False
    
    for line in lines:
        if line.strip():
            if not in_sentence:
                count += 1
                in_sentence = True
        else:
            in_sentence = False
    
    return count
