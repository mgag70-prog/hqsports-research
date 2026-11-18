#!/usr/bin/env python3
"""Make paste-into-substack.html from draft.md: links live, lists kept, a marked slot for the week card
and the subscribe button. The output is gitignored.
Usage: python3 build_paste.py"""
import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent  # start-here
WEEK_CARD = "notes/the-ledger/header/week-card-1200x630.png"
HEAD = ('<!doctype html><html><head><meta charset="utf-8"><title>Paste into Substack</title><style>'
        "body{font-family:Georgia,serif;max-width:720px;margin:40px auto;line-height:1.5}</style></head><body>")
assert (HERE.parent / WEEK_CARD).exists(), WEEK_CARD


def inline(text):
    out = html.escape(text, quote=False)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", lambda m: f'<a href="{m[2]}">{m[1]}</a>', out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return re.sub(r"(?<![\w*])\*(.+?)\*(?![\w*])", r"<em>\1</em>", out)


def convert(md):
    blocks = []
    for block in re.split(r"\n\s*\n", md.strip()):
        lines = block.strip().splitlines()
        first = lines[0]
        if first == "---":
            continue
        if first.startswith("# "):
            blocks.append(f"<h1>{inline(first[2:])}</h1>")
        elif first.startswith("## "):
            blocks.append(f"<h2>{inline(first[3:])}</h2>")
        elif first == "[Insert image: week card]":
            blocks.append(f"<p><strong>[Insert image: week card, {WEEK_CARD}]</strong></p>")
        elif first.startswith("[Insert "):
            blocks.append(f"<p><strong>{html.escape(first)}</strong></p>")
        elif first.startswith("- "):
            blocks.append("<ul>\n" + "\n".join(f"<li>{inline(l[2:])}</li>" for l in lines) + "\n</ul>")
        elif re.match(r"\d+\. ", first):
            blocks.append("<ol>\n" + "\n".join(f"<li>{inline(l.split('. ', 1)[1])}</li>" for l in lines) + "\n</ol>")
        else:
            blocks.append(f"<p>{inline(' '.join(lines))}</p>")
    return "\n".join(blocks)


(HERE / "paste-into-substack.html").write_text(HEAD + convert((HERE / "draft.md").read_text()) + "\n</body></html>\n")
print("wrote paste-into-substack.html")
