"""Fetch each club terms page, save HTML to raw/, extract text to raw/*.txt,
and write paragraphs matching lockout/refund keywords to data/clauses.csv."""
import csv, re, subprocess, pathlib, hashlib, datetime
from bs4 import BeautifulSoup
root = pathlib.Path(__file__).resolve().parent.parent
raw = root / "raw"; raw.mkdir(exist_ok=True)
KW = re.compile(r"lock-?out|strike|work stoppage|labor dispute|force majeure|full season|forty-one|\(41\)|"
                r"\b81\b|refund|credit|cancel|postpone|collective bargaining|players association", re.I)
rows_out = []; status = []
for r in csv.DictReader(open(root / "data/source-urls.csv")):
    name = f"{r['club']}__{r['doc_type']}"
    html_p = raw / f"{name}.html"
    res = subprocess.run(["curl", "-sL", "-m", "25", "-A", "Mozilla/5.0", "-o", str(html_p),
                          "-w", "%{http_code} %{url_effective}", r["url"]], capture_output=True, text=True)
    code, _, final = res.stdout.partition(" ")
    soup = BeautifulSoup(html_p.read_text(errors="ignore"), "html.parser")
    for t in soup(["script", "style", "nav", "header", "footer", "noscript"]): t.decompose()
    title = (soup.title.string or "").strip() if soup.title else ""
    main = soup.find("main") or soup.body or soup
    paras = [re.sub(r"\s+", " ", p.get_text(" ")).strip() for p in main.find_all(["p", "li", "td", "h2", "h3", "h4"])]
    paras = [p for p in paras if len(p) > 30]
    (raw / f"{name}.txt").write_text("\n\n".join(paras))
    hits = [p for p in paras if KW.search(p)]
    status.append({"club": r["club"], "doc_type": r["doc_type"], "url": r["url"], "final_url": final,
                   "http": code, "title": title, "paragraphs": len(paras), "keyword_hits": len(hits),
                   "mentions_lockout_or_strike": int(any(re.search(r"lock-?out|strike|work stoppage|labor", p, re.I) for p in paras)),
                   "fetched_utc": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")})
    for i, p in enumerate(hits):
        rows_out.append({"club": r["club"], "doc_type": r["doc_type"], "n": i, "text": p})
with open(root / "data/fetch-status.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(status[0].keys())); w.writeheader(); w.writerows(status)
with open(root / "data/clauses-raw.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["club", "doc_type", "n", "text"]); w.writeheader(); w.writerows(rows_out)
print("done", len(status), "pages", len(rows_out), "hits")
