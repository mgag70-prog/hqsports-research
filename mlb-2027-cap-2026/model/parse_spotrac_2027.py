#!/usr/bin/env python3
"""Parse the saved Spotrac 2027 team tables (raw/*.html, fetched Oct 27, 2026 from the Mac)
into data/spotrac-2027-*.csv. Raw HTML is gitignored; rerun fetch on the Mac to refresh."""
import csv, html, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
def cell(x): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x))).strip()
for k in ["tax", "payroll", "aav", "cash"]:
    s = (ROOT / "raw" / f"spotrac_{k}_2027.html").read_text(errors="ignore")
    t = re.search(r"<table.*?</table>", s, re.S).group(0)
    rows = [[cell(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)] for tr in re.findall(r"<tr.*?</tr>", t, re.S)]
    h = rows[0]
    out = [r for r in rows[1:] if len(r) == len(h) and r[0].isdigit()]
    with open(ROOT / "data" / f"spotrac-2027-{k}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([f"# Spotrac 2027 {k} table, https://www.spotrac.com/mlb/{k}/_/year/2027, fetched 2026-10-27; values as displayed"])
        w.writerow(["team"] + h[:1] + h[2:])
        for r in out: w.writerow([r[1].split(" ")[0]] + r[:1] + r[2:])
    print(k, len(out))
