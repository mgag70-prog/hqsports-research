import json, subprocess

rows = [
    ("2027", "age 25", "pre-arbitration", 10.0, 1.0),
    ("2028", "age 26", "arbitration 1",   10.0, 15.8),
    ("2029", "age 27", "arbitration 2",   10.0, 26.0),
    ("2030", "age 28", "arbitration 3",   20.0, 37.8),
    ("2031", "age 29", "free agent",      30.0, 36.5),
    ("2032", "age 30", "free agent",      30.0, 36.5),
]

X0, X1 = 100, 1060
Y0, Y1 = 60, 400          # top of scale, baseline
VMAX = 40.0
BW = 54                    # bar width
GAP = 10

def y(v):
    return Y1 - (v / VMAX) * (Y1 - Y0)

svg = [f'<svg viewBox="0 0 1120 510" xmlns="http://www.w3.org/2000/svg">']

# gridlines and axis labels
for v in [0, 10, 20, 30, 40]:
    yy = y(v)
    svg.append(f'<line x1="{X0}" y1="{yy:.1f}" x2="{X1}" y2="{yy:.1f}" '
               f'stroke="{"#33518F" if v == 0 else "#1B3166"}" stroke-width="1"/>')
    svg.append(f'<text x="{X0-16}" y="{yy+6:.1f}" text-anchor="end" fill="#8FA6D6" '
               f'font-size="17" font-family="DejaVu Sans, Arial" font-weight="bold">${v}M</text>')

gw = (X1 - X0) / len(rows)
for i, (yr, age, status, paid, counter) in enumerate(rows):
    cx = X0 + gw * i + gw / 2
    xp = cx - BW - GAP / 2
    xc = cx + GAP / 2

    svg.append(f'<rect x="{xp:.1f}" y="{y(paid):.1f}" width="{BW}" '
               f'height="{Y1-y(paid):.1f}" fill="#2E6BD4"/>')
    svg.append(f'<rect x="{xc:.1f}" y="{y(counter):.1f}" width="{BW}" '
               f'height="{Y1-y(counter):.1f}" fill="#7C8AA8"/>')

    sav = counter - paid
    top = min(y(paid), y(counter))
    col = "#4ADE80" if sav > 0 else "#F87171"
    txt = ("+" if sav > 0 else "-") + f"${abs(sav):,.1f}M"
    svg.append(f'<text x="{cx:.1f}" y="{top-16:.1f}" text-anchor="middle" fill="{col}" '
               f'font-size="25" font-family="DejaVu Sans, Arial" font-weight="bold">{txt}</text>')

    svg.append(f'<text x="{cx:.1f}" y="432" text-anchor="middle" fill="#FFFFFF" '
               f'font-size="23" font-family="DejaVu Sans, Arial" font-weight="bold">{yr}</text>')
    svg.append(f'<text x="{cx:.1f}" y="457" text-anchor="middle" fill="#8FA6D6" '
               f'font-size="17" font-family="DejaVu Sans, Arial">{age}</text>')
    svg.append(f'<text x="{cx:.1f}" y="481" text-anchor="middle" fill="#8FA6D6" '
               f'font-size="17" font-family="DejaVu Sans, Arial">{status}</text>')

svg.append('</svg>')
svg = "\n".join(svg)

html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#fff; font-family:"DejaVu Sans", Arial, sans-serif; }}
.card {{ width:1120px; background:#0B1E47; padding:0 0 30px 0; }}
.head {{ background:#0E3386; padding:26px 38px 22px 38px; border-bottom:4px solid #CC3433; }}
.title {{ font-family:"DejaVu Sans Condensed","DejaVu Sans",Arial,sans-serif;
          font-size:40px; font-weight:bold; color:#fff; letter-spacing:0.8px; line-height:1.12; }}
.sub {{ font-size:16px; color:#A9BCE4; margin-top:12px; letter-spacing:2.4px; font-weight:bold; }}
.key {{ display:flex; gap:34px; margin:24px 38px 4px 38px; }}
.key div {{ display:flex; align-items:center; gap:11px; font-size:18px; color:#DCE5F5; }}
.sw {{ width:26px; height:16px; border-radius:2px; display:inline-block; }}
.chart {{ padding:6px 0 0 0; }}
.take {{ margin:18px 38px 0 38px; padding-top:22px; border-top:2px solid #CC3433;
         font-size:23px; color:#fff; line-height:1.5; font-weight:bold; }}
.take em {{ color:#FFC72C; font-style:normal; }}
.src {{ margin:18px 38px 0 38px; font-size:12.5px; color:#6E84B0; line-height:1.65; }}
</style></head>
<body><div class="card">
  <div class="head">
    <div class="title">Where the Cubs actually save money<br>on Pete Crow-Armstrong</div>
    <div class="sub">SIX YEARS, $115 MILLION &nbsp;&middot;&nbsp; SIGNED MARCH 24, 2026</div>
  </div>

  <div class="key">
    <div><span class="sw" style="background:#2E6BD4"></span>Paid under the extension</div>
    <div><span class="sw" style="background:#7C8AA8"></span>Cost with no extension (modeled)</div>
  </div>

  <div class="chart">{svg}</div>

  <div class="take">
    The two free agent years the extension buys out are worth <em>$9.4 million</em>.<br>
    The four years the Cubs already controlled are worth <em>$19.1 million</em>.
  </div>

  <div class="src">
    Contract terms from the Associated Press and MLB.com, March 2026. Service time of 1.170 at signing from Baseball Reference,
    which put free agency after the 2030 season.<br>
    Counterfactual assumes 6.5 wins of true talent entering age 25, a standard aging curve, $9.0 million per win in 2027 inflating
    three percent a year, arbitration awards at 25, 40 and 60 percent of open market value, and a hypothetical eight year free
    agent contract covering ages 29 through 36. Present values discounted to 2026 at six percent.<br>
    A model, not a forecast. Move the true-talent assumption and these bars move with it.
  </div>
</div></body></html>'''

open("savings_chart_source.html", "w").write(html)
print("built")
