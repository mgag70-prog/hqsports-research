from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

INPUT = Font(name="Arial", size=10, color="0000FF")
LINK = Font(name="Arial", size=10, color="008000")
CALC = Font(name="Arial", size=10, color="000000")
BOLD = Font(name="Arial", size=10, bold=True)
HEAD = Font(name="Arial", size=11, bold=True, color="FFFFFF")
TITLE = Font(name="Arial", size=14, bold=True)
NOTE = Font(name="Arial", size=8, italic=True, color="595959")
YELLOW = PatternFill("solid", fgColor="FFFF00")
NAVY = PatternFill("solid", fgColor="0E3386")
GREYF = PatternFill("solid", fgColor="F2F2F2")
THIN = Border(top=Side(style="thin", color="BFBFBF"))

MONEY = '$#,##0.0;($#,##0.0);-'
PCT = '0.0%'
NUM = '0.00'

wb = Workbook()

# ============================ ASSUMPTIONS ============================
a = wb.active
a.title = "Assumptions"
a.sheet_view.showGridLines = False
a["A1"] = "Pete Crow-Armstrong extension model  |  assumptions"
a["A1"].font = TITLE
a["A2"] = "Blue cells are inputs. Change them and every other tab recalculates. Yellow marks the three that move the answer most."
a["A2"].font = NOTE

a["A4"] = "Contract facts (do not change)"
a["A4"].font = BOLD
facts = [
    ("Extension guarantee ($M)", 115.0, "AP and MLB.com, March 24 2026. Six years, 2027 through 2032, no club options."),
    ("Signing bonus ($M)", 5.0, "Payable by May 15 2026."),
    ("Service time at signing", 1.170, "Spotrac / Baseball Reference, January 2026. Free agency would have followed the 2030 season."),
    ("Base year for discounting", 2026, "All present values are stated as of 2026."),
]
r = 5
for label, val, src in facts:
    a[f"A{r}"] = label
    a[f"A{r}"].font = CALC
    a[f"B{r}"] = val
    a[f"B{r}"].font = INPUT
    a[f"B{r}"].number_format = MONEY if "$M" in label else ('0.000' if "Service" in label else '0')
    a[f"C{r}"] = src
    a[f"C{r}"].font = NOTE
    r += 1

a["A10"] = "Performance and market assumptions"
a["A10"].font = BOLD
inputs = [
    ("True talent WAR entering 2027 (age 25)", 6.5, NUM, True,
     "Regressed estimate, not the 2026 result. A 10.0 WAR season regresses heavily. Single most important input."),
    ("Market rate per win in 2027 ($M)", 9.0, MONEY, True,
     "Open market clearing price for one win. Industry estimates have run $8M to $10M. Top of market runs higher."),
    ("Annual inflation in $ per win", 0.03, PCT, False, "Applied from 2027 forward."),
    ("Discount rate", 0.06, PCT, False, "Club cost of capital. Backloaded money is worth less."),
    ("2027 pre-arbitration salary, no extension ($M)", 1.0, MONEY, False,
     "Renewal near the minimum. Excludes the pre-arbitration bonus pool, whose survival past the CBA is unknown."),
    ("Arbitration 1 share of open market value", 0.25, PCT, False, "2028. Conventional 25/40/60 arbitration ladder."),
    ("Arbitration 2 share of open market value", 0.40, PCT, False, "2029."),
    ("Arbitration 3 share of open market value", 0.60, PCT, False, "2030."),
    ("Hypothetical free agent deal, length in years", 8, '0', False, "Signed after 2030, covering ages 29 through 36."),
    ("Share of projected value an elite free agent captures", 1.00, PCT, True,
     "1.00 means he signs for exactly his projected value. Above 1.00 means the top of the market pays a premium."),
]
r = 11
for label, val, fmt, key, src in inputs:
    a[f"A{r}"] = label
    a[f"A{r}"].font = CALC
    a[f"B{r}"] = val
    a[f"B{r}"].font = INPUT
    a[f"B{r}"].number_format = fmt
    if key:
        a[f"B{r}"].fill = YELLOW
    a[f"C{r}"] = src
    a[f"C{r}"].font = NOTE
    r += 1

a["A22"] = "Aging curve: WAR added to true talent, by age"
a["A22"].font = BOLD
a["C22"] = "Peak at 26 and 27, then decline. Steeper than a slugger's curve because this player's value leans on defense and speed."
a["C22"].font = NOTE
a["A23"] = "Age"
a["B23"] = "Delta WAR"
a["A23"].font = BOLD
a["B23"].font = BOLD
curve = {25: 0.0, 26: 0.3, 27: 0.3, 28: -0.1, 29: -0.7, 30: -1.4,
         31: -2.1, 32: -2.8, 33: -3.5, 34: -4.2, 35: -4.9, 36: -5.6}
r = 24
for age, d in curve.items():
    a[f"A{r}"] = age
    a[f"A{r}"].font = CALC
    a[f"A{r}"].number_format = '0'
    a[f"B{r}"] = d
    a[f"B{r}"].font = INPUT
    a[f"B{r}"].number_format = '0.0'
    r += 1

a.column_dimensions["A"].width = 48
a.column_dimensions["B"].width = 13
a.column_dimensions["C"].width = 105

TAL = "Assumptions!$B$11"
DPW = "Assumptions!$B$12"
INF = "Assumptions!$B$13"
DISC = "Assumptions!$B$14"
PREARB = "Assumptions!$B$15"
A1S, A2S, A3S = "Assumptions!$B$16", "Assumptions!$B$17", "Assumptions!$B$18"
FALEN = "Assumptions!$B$19"
CAP = "Assumptions!$B$20"
BONUS = "Assumptions!$B$6"
BASEYR = "Assumptions!$B$8"
CURVE = "Assumptions!$A$24:$B$35"

# ============================ FREE AGENT DEAL ============================
f = wb.create_sheet("FA deal")
f.sheet_view.showGridLines = False
f["A1"] = "Counterfactual free agent contract he would have signed after 2030"
f["A1"].font = TITLE
f["A2"] = ("Absent the extension he reaches free agency at 28. A long deal's annual value is set by the whole term, "
           "including the decline years, so the 2031 and 2032 counterfactual is this deal's average annual value, not a single season's worth.")
f["A2"].font = NOTE

hdr = ["Year", "Age", "Projected WAR", "$ per win ($M)", "Market value ($M)"]
for i, h in enumerate(hdr, start=1):
    c = f.cell(row=4, column=i, value=h)
    c.font = HEAD
    c.fill = NAVY
    c.alignment = Alignment(horizontal="center", wrap_text=True)

for i in range(8):
    row = 5 + i
    f[f"A{row}"] = 2031 + i
    f[f"A{row}"].number_format = '0'
    f[f"A{row}"].font = CALC
    f[f"B{row}"] = f"=29+A{row}-2031"
    f[f"B{row}"].number_format = '0'
    f[f"C{row}"] = f"=MAX(0,{TAL}+INDEX({CURVE},MATCH(B{row},Assumptions!$A$24:$A$35,0),2))"
    f[f"C{row}"].number_format = NUM
    f[f"D{row}"] = f"={DPW}*(1+{INF})^(A{row}-2027)"
    f[f"D{row}"].number_format = MONEY
    f[f"E{row}"] = f"=C{row}*D{row}"
    f[f"E{row}"].number_format = MONEY
    for col in "ABCDE":
        f[f"{col}{row}"].font = CALC

f["A13"] = "Term (years)"
f["B13"] = f"={FALEN}"
f["B13"].font = LINK
f["B13"].number_format = '0'
f["A14"] = "Total projected value over the term ($M)"
f["B14"] = "=SUM(E5:E12)"
f["B14"].number_format = MONEY
f["A15"] = "Share of that value actually captured"
f["B15"] = f"={CAP}"
f["B15"].font = LINK
f["B15"].number_format = PCT
f["A16"] = "Average annual value used for 2031 and 2032 ($M)"
f["A16"].font = BOLD
f["B16"] = "=B14*B15/B13"
f["B16"].font = Font(name="Arial", size=10, bold=True)
f["B16"].number_format = MONEY
f["B16"].fill = GREYF
for rr in (13, 14, 15, 16):
    pass
f["A17"] = "Note: the term only runs eight years because WAR goes to zero on this curve. Lengthen it and the average annual value falls."
f["A17"].font = NOTE
f.column_dimensions["A"].width = 46
for col in "BCDE":
    f.column_dimensions[col].width = 17

FAAAV = "'FA deal'!$B$16"

# ============================ MODEL ============================
m = wb.create_sheet("Model")
m.sheet_view.showGridLines = False
m["A1"] = "Year by year build, 2027 through 2032"
m["A1"].font = TITLE
m["A2"] = ("Surplus value asks what he produced against what he was paid. Savings asks what the extension changed "
           "against the control years the Cubs already held. They are different questions with different answers.")
m["A2"].font = NOTE

cols = ["Year", "Age", "Status", "Projected WAR", "$ per win ($M)", "Market value ($M)",
        "Salary paid ($M)", "Cost with no extension ($M)", "Surplus value ($M)",
        "Savings vs no extension ($M)", "Discount factor", "PV of surplus ($M)", "PV of savings ($M)"]
for i, h in enumerate(cols, start=1):
    c = m.cell(row=4, column=i, value=h)
    c.font = HEAD
    c.fill = NAVY
    c.alignment = Alignment(horizontal="center", wrap_text=True, vertical="center")
m.row_dimensions[4].height = 44

sched = {2027: 10.0, 2028: 10.0, 2029: 10.0, 2030: 20.0, 2031: 30.0, 2032: 30.0}
status = {2027: "pre-arb", 2028: "arb1", 2029: "arb2", 2030: "arb3",
          2031: "free agent", 2032: "free agent"}

for i, yr in enumerate(sorted(sched)):
    row = 5 + i
    m[f"A{row}"] = yr
    m[f"A{row}"].number_format = '0'
    m[f"B{row}"] = f"=25+A{row}-2027"
    m[f"B{row}"].number_format = '0'
    m[f"C{row}"] = status[yr]
    m[f"D{row}"] = f"=MAX(0,{TAL}+INDEX({CURVE},MATCH(B{row},Assumptions!$A$24:$A$35,0),2))"
    m[f"D{row}"].number_format = NUM
    m[f"E{row}"] = f"={DPW}*(1+{INF})^(A{row}-2027)"
    m[f"E{row}"].number_format = MONEY
    m[f"F{row}"] = f"=D{row}*E{row}"
    m[f"F{row}"].number_format = MONEY
    m[f"G{row}"] = sched[yr]
    m[f"G{row}"].font = INPUT
    m[f"G{row}"].number_format = MONEY
    m[f"H{row}"] = (f'=IF(C{row}="pre-arb",{PREARB},'
                    f'IF(C{row}="free agent",{FAAAV},'
                    f'IF(C{row}="arb1",{A1S},IF(C{row}="arb2",{A2S},{A3S}))*F{row}))')
    m[f"H{row}"].number_format = MONEY
    m[f"I{row}"] = f"=F{row}-G{row}"
    m[f"I{row}"].number_format = MONEY
    m[f"J{row}"] = f"=H{row}-G{row}"
    m[f"J{row}"].number_format = MONEY
    m[f"K{row}"] = f"=1/(1+{DISC})^(A{row}-{BASEYR})"
    m[f"K{row}"].number_format = '0.000'
    m[f"L{row}"] = f"=I{row}*K{row}"
    m[f"L{row}"].number_format = MONEY
    m[f"M{row}"] = f"=J{row}*K{row}"
    m[f"M{row}"].number_format = MONEY
    for ci in range(1, 14):
        cell = m.cell(row=row, column=ci)
        if cell.font.color is None or cell.font.color.rgb != "000000FF":
            cell.font = CALC

trow = 11
m[f"A{trow}"] = "Total"
m[f"A{trow}"].font = BOLD
for col in ["D", "F", "G", "H", "I", "J", "L", "M"]:
    c = m[f"{col}{trow}"]
    c.value = f"=SUM({col}5:{col}10)"
    c.font = BOLD
    c.number_format = NUM if col == "D" else MONEY
    c.border = THIN

m["A13"] = "Signing bonus paid in 2026 ($M), an extra cost that exists only because the extension exists"
m["B13"] = f"=-{BONUS}"
m["B13"].font = LINK
m["B13"].number_format = MONEY
m["A13"].font = CALC
m.column_dimensions["A"].width = 10
m.column_dimensions["B"].width = 8
m.column_dimensions["C"].width = 13
for col in "DEFGHIJKLM":
    m.column_dimensions[col].width = 15

# ============================ SUMMARY ============================
s = wb.create_sheet("Summary", 0)
s.sheet_view.showGridLines = False
s["A1"] = "Pete Crow-Armstrong, six years and $115 million: what it is actually worth"
s["A1"].font = TITLE
s["A2"] = "All figures in millions of dollars, present value as of 2026. Change anything on the Assumptions tab and these move."
s["A2"].font = NOTE

def block(row, label, formula, note, bold=False):
    s[f"A{row}"] = label
    s[f"A{row}"].font = BOLD if bold else CALC
    s[f"B{row}"] = formula
    s[f"B{row}"].number_format = MONEY
    s[f"B{row}"].font = Font(name="Arial", size=10, bold=bold, color="008000")
    s[f"C{row}"] = note
    s[f"C{row}"].font = NOTE

s["A4"] = "What the Cubs pay"
s["A4"].font = BOLD
block(5, "Guarantee, nominal", "=SUM(Model!G5:G10)+Assumptions!B6", "Six salaries plus the signing bonus.")
block(6, "Guarantee, present value at 2026", "=SUMPRODUCT(Model!G5:G10,Model!K5:K10)+Assumptions!B6",
      "The schedule is backloaded, which is worth real money and is invisible in the average annual value.")
block(7, "Average annual value", "=SUM(Model!G5:G10)/6+Assumptions!B6/6",
      "A competitive balance tax concept, not an economic one.")

s["A9"] = "Question A: was he worth it?"
s["A9"].font = BOLD
block(10, "Market value of projected production", "=SUM(Model!F5:F10)", "Projected WAR times the market rate per win.")
block(11, "Surplus value, present value", "=SUM(Model!L5:L10)-Assumptions!B6",
      "Value produced minus salary paid. This is the number that makes every young star's deal look like a steal.", bold=True)

s["A13"] = "Question B: was the extension itself a good decision?"
s["A13"].font = BOLD
block(14, "Cost with no extension, present value", "=SUMPRODUCT(Model!H5:H10,Model!K5:K10)",
      "What the Cubs would have paid anyway through the control years, plus a free agent deal for 2031 and 2032.")
block(15, "Savings from the extension, present value", "=SUM(Model!M5:M10)-Assumptions!B6",
      "The only number that measures the decision the front office actually made.", bold=True)
block(16, "   of which the control years, 2027 to 2030", "=SUM(Model!M5:M8)-Assumptions!B6",
      "Arbitration, where most of the value turns out to be.")
block(17, "   of which the bought out free agent years, 2031 and 2032", "=SUM(Model!M9:M10)",
      "The part every write-up leads with.")

s["A19"] = "The gap between line 11 and line 15 is the whole argument."
s["A19"].font = BOLD
s["A20"] = ("Both are correct. The first says he is producing far more than he is paid, which is true of nearly every "
            "pre-free-agency star and says little about the front office. The second says what the Cubs gained by signing "
            "in March 2026 rather than waiting, which is the decision under review.")
s["A20"].font = NOTE
s["A22"] = ("Not modeled: the MVP escalators on the 2031 and 2032 bases, which run off 2027 through 2031 voting only, so the 2026 "
            "award triggers nothing. The $1 million assignment bonus on any trade. The pre-arbitration bonus pool. Off-field revenue. "
            "And the largest omission of all, a salary cap, which would reset both the market rate per win and the free agent "
            "counterfactual at once.")
s["A22"].font = NOTE
s.column_dimensions["A"].width = 52
s.column_dimensions["B"].width = 14
s.column_dimensions["C"].width = 100

wb.save("PCA_Extension_Model.xlsx")
print("saved")
