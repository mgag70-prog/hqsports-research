#!/usr/bin/env python3
"""Fetch Spotrac MLB team tables (payroll, tax, cash, aav) by season and save raw HTML
plus one tidy CSV per table type. Run from the repo root on the Mac:
    python3 mlb-floor-2026/model/fetch_spotrac.py
Raw HTML is gitignored; the CSVs record the fetch time."""
import csv, html, re, subprocess, sys, time, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, DATA = ROOT / "raw", ROOT / "data"
HEADERS = [
 "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
 "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
 "Accept-Language: en-US,en;q=0.9",
 'sec-ch-ua: "Chromium";v="129", "Google Chrome";v="129"', "sec-ch-ua-mobile: ?0",
 'sec-ch-ua-platform: "macOS"', "Sec-Fetch-Dest: document", "Sec-Fetch-Mode: navigate",
 "Sec-Fetch-Site: none", "Upgrade-Insecure-Requests: 1"]
KINDS = {"payroll": range(2011, 2027), "tax": range(2011, 2027), "cash": range(2011, 2027), "aav": range(2011, 2027)}

def fetch(url, out):
    if out.exists() and out.stat().st_size > 50000:
        return out.read_text(errors="ignore")
    cmd = ["curl", "-sL", "--compressed", url, "-o", str(out)]
    for h in HEADERS: cmd[1:1] = ["-H", h]
    subprocess.run(cmd, check=True); time.sleep(1.5)
    return out.read_text(errors="ignore")

def cell(x):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x))).strip()

def first_table(s):
    m = re.search(r"<table.*?</table>", s, re.S)
    if not m: return []
    rows = []
    for tr in re.findall(r"<tr.*?</tr>", m.group(0), re.S):
        rows.append([cell(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)])
    return rows

def main():
    RAW.mkdir(exist_ok=True); DATA.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
    for kind, years in KINDS.items():
        out_rows, header = [], None
        for y in years:
            url = f"https://www.spotrac.com/mlb/{kind}/_/year/{y}"
            s = fetch(url, RAW / f"spotrac_{kind}_{y}.html")
            t = first_table(s)
            if not t: print("NO TABLE", url, file=sys.stderr); continue
            h = t[0]
            if header is None: header = h
            for r in t[1:]:
                if len(r) != len(h) or not r[0].isdigit(): continue
                d = dict(zip(h, r)); d["season"] = y; d["team"] = r[1].split(" ")[0]; d["url"] = url
                out_rows.append(d)
        cols = ["season", "team"] + [c for c in dict.fromkeys(k for d in out_rows for k in d) if c not in ("season","team","Team","url")] + ["url"]
        with open(DATA / f"spotrac-{kind}-by-season.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["# fetched " + stamp + " from spotrac.com; values as displayed"])
            w.writerow(cols)
            for d in out_rows: w.writerow([d.get(c, "") for c in cols])
        print(kind, len(out_rows), "rows")
    # multi-year cash commitments
    s = fetch("https://www.spotrac.com/mlb/cash/yearly", RAW / "spotrac_cash_yearly.html")
    t = first_table(s)
    with open(DATA / "spotrac-cash-commitments.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["# fetched " + stamp + " from https://www.spotrac.com/mlb/cash/yearly"])
        w.writerow(["team"] + t[0][1:])
        for r in t[1:]:
            if len(r) == len(t[0]) and r[0]: w.writerow([r[0].split(" ")[0]] + r[1:])
    print("commitments", len(t) - 1)
main()
