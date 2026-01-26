def align_word_for_word(orig_line, trans_line, delimiter=" // "):
    orig_tokens = orig_line.split()
    trans_pieces = [p.strip() for p in trans_line.split(delimiter) if p.strip()]

    if not orig_tokens:
        return []

    if not trans_pieces:
        return [(o, "") for o in orig_tokens]

    if len(orig_tokens) == len(trans_pieces):
        return list(zip(orig_tokens, trans_pieces))

    if len(trans_pieces) < len(orig_tokens):
        expanded = []
        for p in trans_pieces:
            expanded.extend(p.split())
        while len(expanded) < len(orig_tokens):
            expanded.append("")
        return list(zip(orig_tokens, expanded[:len(orig_tokens)]))

    per = len(trans_pieces) // len(orig_tokens)
    extra = len(trans_pieces) % len(orig_tokens)

    pairs = []
    idx = 0
    for i, o in enumerate(orig_tokens):
        take = per + (1 if i < extra else 0)
        pairs.append((o, " ".join(trans_pieces[idx:idx+take])))
        idx += take

    return pairs
