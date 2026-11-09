#!/usr/bin/env python3
"""Make paste-into-substack.html from draft.md: everything above "Not for publication", tables as
bulleted lists, links live, a marked slot and caption per figure. The output is gitignored.
Usage: python3 build_paste.py"""
import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAPTIONS = dict(re.findall(r"^\*\*(fig-[\w-]+)\*\*.*\n(.+)$", (HERE / "figures/captions.md").read_text(), re.M))
HEAD = ('<!doctype html><html><head><meta charset="utf-8"><title>Paste into Substack</title><style>'
        "body{font-family:Georgia,serif;max-width:720px;margin:40px auto;line-height:1.5}</style></head><body>")


def inline(text):
    out = html.escape(text, quote=False)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", lambda m: f'<a href="{m[2]}">{m[1]}</a>', out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return re.sub(r"(?<![\w*])\*(.+?)\*(?![\w*])", r"<em>\1</em>", out)


def table_items(rows):
    """Header row and data rows of a markdown table as list items: 'Left: right'."""
    cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows if not re.fullmatch(r"\|[-| ]+\|", r)]
    return "<ul>\n" + "\n".join(f"<li>{inline(a)}: {inline(b)}</li>" for a, b in cells) + "\n</ul>"


def convert(md):
    blocks, para = [], md.split("## Not for publication")[0].rsplit("\n---\n", 1)[0]
    for block in re.split(r"\n\s*\n", para.strip()):
        lines = block.strip().splitlines()
        first = lines[0]
        if first == "---":
            continue
        if first.startswith("# "):
            blocks.append(f"<h1>{inline(first[2:])}</h1>")
        elif first.startswith("## "):
            blocks.append(f"<h2>{inline(first[3:])}</h2>")
        elif first.startswith("!["):
            key = re.search(r"figures/(fig-[\w-]+)\.png", first)[1]
            blocks.append(f"<p><strong>[Insert image: figures/{key}.png]</strong></p>")
        elif first.startswith("*[Caption"):
            key = re.search(r"fig-[\w-]+", first)[0]
            blocks.append(f"<p><em>{inline(CAPTIONS[key])}</em></p>")
        elif first.startswith("|"):
            blocks.append(table_items(lines))
        elif first.startswith("- "):
            blocks.append("<ul>\n" + "\n".join(f"<li>{inline(l[2:])}</li>" for l in lines) + "\n</ul>")
        else:
            blocks.append(f"<p>{inline(' '.join(lines))}</p>")
    return "\n".join(blocks)


(HERE / "paste-into-substack.html").write_text(HEAD + convert((HERE / "draft.md").read_text()) + "\n</body></html>\n")
print("wrote paste-into-substack.html")
