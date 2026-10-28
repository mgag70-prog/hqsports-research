#!/usr/bin/env python3
"""Email header for "The Ledger", the weekly Ledger & Whistle Substack Note.

Three background options from fal.ai nano-banana-pro at 21:9, the widest aspect it completes
(its schema also lists 4:1 and 8:1, which are Nano Banana 2 ratios; both returned
"Downstream service error" on October 27, 2026), cropped to 5:1, then the house navy scrim and type from tools/compose_cover.py. The model
never draws a letter; every word is set here in Georgia, as on the covers.

Usage, from the repo root:
  python3 notes/the-ledger/header/build_header.py prompt              # print the prompt, send nothing
  python3 notes/the-ledger/header/build_header.py generate [A B C]    # call fal.ai (FAL_KEY from env)
  python3 notes/the-ledger/header/build_header.py build [A B C]       # scrim, type, checks, PNGs
  python3 notes/the-ledger/header/build_header.py sheet               # contact sheet of the built options

Writes, next to this script:
  raw/option-X-background.png      the image as fal.ai returned it
  raw/option-X-request.json        seed, request id, size, date
  option-X-1100x220.png            the header
  option-X-2200x440.png            the same at 2x
  option-X-550-preview.png         the 1100 header shown at 550 wide, as many email clients do
  contact-sheet.png
"""
import json
import os
import sys
import tempfile
import time
import urllib.request
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import compose_cover as cc  # noqa: E402  house scrim, shadow, magick and fal.ai helpers

RAW = os.path.join(HERE, "raw")
MODEL_PARAMS = {"aspect_ratio": "21:9", "resolution": "2K", "num_images": 1, "output_format": "png"}
COST_PER_IMAGE = 0.15          # fal.ai list price for nano-banana-pro below 4K, October 2026

OPTIONS = {                    # crop_y: top of the full-width 5:1 window, as a fraction of the spare height
    "A": {"seed": 5101, "crop_y": 0.42},
    "B": {"seed": 5102, "crop_y": 0.46},
    "C": {"seed": 5104, "crop_y": 0.34},   # 5103 rejected: a person in frame, the word "Tick" written on the page
}

PROMPT = (
    "Dramatic, dark, cinematic close-up photograph for a publication about the money in sport. "
    "Subject: an open accounting ledger book lying on a dark wood desk. Its ruled columns are filled "
    "with handwritten-style tick marks and small red check marks in ink, and nothing else is written "
    "on the pages. A referee's whistle on a lanyard and a single baseball rest on the open pages. "
    "Warm desk-lamp light falls from the right; everything else sinks into deep navy shadow. "
    "Fine film grain, shallow depth of field, matte surfaces, a palette of dark navy blue and warm "
    "amber with one small accent of brick red. "
    "Composition: a wide 21:9 frame that will be cropped to a thin 5:1 banner through its vertical "
    "middle, so the ledger, the whistle and the baseball all sit inside the middle third of the frame "
    "height, in the right 40 percent of the frame width. The left 60 percent is calm, dark, out-of-focus desk "
    "surface fading into navy shadow, with no objects, no bright spots and no detail in it. "
    "The image contains no text of any kind: no letters, words, numbers, digits, dates, captions, "
    "labels or watermarks; the ledger pages carry only ruled lines, tick marks and check marks. "
    "No logos, no brand names, no team marks or insignia. No people and no faces."
)

# --- frame and type, in 1x pixels (everything is drawn at 2x) -----------------------------------
OUT = (1100, 220)
SCALE = 2
PAD = 40                       # minimum clear space to every edge of the inked type
MARGIN_X = 48
TITLE = "THE LEDGER"
TAGLINE = "Every call on the record. Graded weekly."
TITLE_CAP = 50                 # cap height of the title
TITLE_TRACKING = 0.03          # em
TITLE_MAX_W = 0.50             # title may not run past this fraction of the width
WORDMARK_PX = 18                # 16 put the caps at 5.5px when shown at 550 wide
TAGLINE_PX = 21
GAP_WORDMARK = 22              # wordmark baseline to title cap top
GAP_RULE = 14                  # title baseline to rule top
RULE = (64, 3)                 # length, thickness
GAP_TAGLINE = 13               # rule bottom to tagline cap top
TAGLINE_FILL = cc.PAPER_MUTED  # as the covers' sub-line

# Scrim: navy from the left edge, full on x 0 to 0.42, gone by 0.72. Zones checked against the
# house ceilings: the type band at the cover band target, the calm left 55 percent at the
# cover band target too (the cover "left" target is for a 40 percent column with no type over it).
FMT = {"scrim_x": (0.42, 0.72), "scrim_y": None,
       "zones": [((0.00, 0.00, 0.55, 1.00), cc.BAND_TARGET), ((0.03, 0.12, 0.52, 0.88), cc.BAND_TARGET)]}
ZONE_NAMES = ("left 55%", "type band")


def px(v: float) -> int:
    return int(round(v * SCALE))


# --- generate --------------------------------------------------------------------------------

def generate(letters: list[str]) -> None:
    key = os.environ.get("FAL_KEY")
    if not key:
        sys.exit("FAL_KEY is not set")
    os.makedirs(RAW, exist_ok=True)
    for letter in letters:
        seed = OPTIONS[letter]["seed"]
        submitted = cc.fal_request(cc.QUEUE_URL, key, {"prompt": PROMPT, "seed": seed, **MODEL_PARAMS})
        rid = submitted["request_id"]
        print("%s: submitted %s, seed %d" % (letter, rid, seed), flush=True)
        deadline = time.time() + cc.POLL_LIMIT_SECONDS
        while True:
            status = cc.fal_request(submitted["status_url"], key)["status"]
            if status == "COMPLETED":
                break
            if status not in ("IN_QUEUE", "IN_PROGRESS") or time.time() > deadline:
                raise RuntimeError("request %s ended %s" % (rid, status))
            time.sleep(cc.POLL_SECONDS)
        result = cc.fal_request(submitted["response_url"], key)
        images = result.get("images") or []
        if not images:
            raise RuntimeError("no image for %s: %s" % (rid, json.dumps(result)[:400]))
        dst = os.path.join(RAW, "option-%s-background.png" % letter)
        with urllib.request.urlopen(images[0]["url"], timeout=120) as r, open(dst, "wb") as f:
            f.write(r.read())
        size = cc.image_size(dst)
        with open(os.path.join(RAW, "option-%s-request.json" % letter), "w") as f:
            json.dump({"letter": letter, "seed": seed, "request_id": rid, "model": cc.MODEL,
                       "params": MODEL_PARAMS, "size": size, "date": date.today().isoformat(),
                       "cost_usd": COST_PER_IMAGE * (2 if MODEL_PARAMS["resolution"] == "4K" else 1),
                       "prompt": PROMPT}, f, indent=1)
        print("%s: wrote %s (%dx%d)" % (letter, os.path.relpath(dst, REPO), *size), flush=True)


# --- build -----------------------------------------------------------------------------------

def crop_to_5x1(src: str, dst: str, crop_y: float) -> None:
    w, h = cc.image_size(src)
    cw = min(w, h * OUT[0] // OUT[1])
    ch = cw * OUT[1] // OUT[0]
    left = (w - cw) // 2
    top = int(round((h - ch) * crop_y))
    cc.magick(src, "-crop", "%dx%d+%d+%d" % (cw, ch, left, top), "+repage",
              "-filter", "Lanczos", "-resize", "%dx%d!" % (OUT[0] * SCALE, OUT[1] * SCALE), dst)


def type_layout() -> dict:
    """Pixel positions (2x) of every element, the block centred vertically between the pads."""
    title_probe = 100
    probe_cap = cc.text_extent(cc.FONT_HEADLINE, title_probe, 0, "H")[1]
    title_px = int(round(title_probe * px(TITLE_CAP) / probe_cap))
    tracking = round(title_px * TITLE_TRACKING, 2)
    title_w = cc.text_extent(cc.FONT_HEADLINE, title_px, tracking, TITLE)[0]
    limit = OUT[0] * SCALE * TITLE_MAX_W - px(MARGIN_X)
    if title_w > limit:
        title_px = int(title_px * limit / title_w)
        title_w = cc.text_extent(cc.FONT_HEADLINE, title_px, tracking, TITLE)[0]
    title_cap = cc.text_extent(cc.FONT_HEADLINE, title_px, 0, "H")[1]
    wm_px, tag_px = px(WORDMARK_PX), px(TAGLINE_PX)
    wm_cap = cc.text_extent(cc.FONT_SUPPORT, wm_px, 0, "H")[1]
    tag_cap = cc.text_extent(cc.FONT_SUPPORT, tag_px, 0, "H")[1]
    block = wm_cap + px(GAP_WORDMARK) + title_cap + px(GAP_RULE) + px(RULE[1]) + px(GAP_TAGLINE) + tag_cap
    top = (OUT[1] * SCALE - block) / 2 - px(2)   # a touch high: the tagline's descenders sit below
    lay = {"x": px(MARGIN_X), "wm_px": wm_px, "title_px": title_px, "title_tracking": tracking,
           "tag_px": tag_px, "title_w": title_w}
    lay["wm_y"] = top + wm_cap
    lay["title_y"] = lay["wm_y"] + px(GAP_WORDMARK) + title_cap
    lay["rule_y"] = lay["title_y"] + px(GAP_RULE)
    lay["tag_y"] = lay["rule_y"] + px(RULE[1]) + px(GAP_TAGLINE) + tag_cap
    return lay


def element_args(lay: dict) -> dict:
    """magick drawing arguments per element, so each can be rendered alone for its own checks."""
    x = lay["x"]
    return {
        "wordmark": ["-font", cc.FONT_SUPPORT, "-pointsize", str(lay["wm_px"]),
                     "-kerning", str(round(lay["wm_px"] * cc.WORDMARK_TRACKING, 2)), "-fill", cc.RED,
                     "-annotate", "+%d+%d" % (x, round(lay["wm_y"])), cc.WORDMARK],
        "title": ["-font", cc.FONT_HEADLINE, "-pointsize", str(lay["title_px"]),
                  "-kerning", str(lay["title_tracking"]), "-fill", cc.PAPER,
                  "-annotate", "+%d+%d" % (x, round(lay["title_y"])), TITLE],
        "rule": ["-fill", cc.RED, "-draw", "rectangle %d,%d %d,%d" % (
            x, round(lay["rule_y"]), x + px(RULE[0]) - 1, round(lay["rule_y"]) + px(RULE[1]) - 1)],
        "tagline": ["-font", cc.FONT_SUPPORT, "-pointsize", str(lay["tag_px"]), "-kerning", "0",
                    "-fill", TAGLINE_FILL, "-annotate", "+%d+%d" % (x, round(lay["tag_y"])), TAGLINE],
    }


def render(dst: str, size: tuple[int, int], parts: list[list[str]]) -> None:
    cc.magick("-size", "%dx%d" % size, "xc:none", *[a for p in parts for a in p], dst)


def srgb_to_linear(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rel_lum(rgb) -> float:
    r, g, b = (srgb_to_linear(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def contrast_under(bg: str, layer: str, fill: tuple, alpha: float, work: str) -> tuple[float, float]:
    """WCAG contrast of an element against the background pixels beneath its ink, dilated 2px.

    Returns (worst, median): worst uses the 95th-percentile brightest background pixel."""
    w, h = cc.image_size(bg)
    mask = os.path.join(work, "mask.gray")
    cc.magick(layer, "-alpha", "extract", "-morphology", "Dilate", "Disk:2", "-threshold", "10%",
              "-depth", "8", "gray:" + mask)
    rgb = cc.magick(bg, "-depth", "8", "rgb:-", capture=True)
    with open(mask, "rb") as f:
        m = f.read()
    lums = sorted(rel_lum(rgb[3 * i:3 * i + 3]) for i in range(w * h) if m[i] > 127)
    out = []
    for bg_l in (lums[int(len(lums) * 0.95)], lums[len(lums) // 2]):
        # text drawn at alpha over the background: blend in linear light
        fg_l = rel_lum(fill) * alpha + bg_l * (1 - alpha)
        hi, lo = max(fg_l, bg_l), min(fg_l, bg_l)
        out.append((hi + 0.05) / (lo + 0.05))
    return out[0], out[1]


def build(letters: list[str]) -> list[dict]:
    lay = type_layout()
    parts = element_args(lay)
    size = (OUT[0] * SCALE, OUT[1] * SCALE)
    results = []
    for letter in letters:
        src = os.path.join(RAW, "option-%s-background.png" % letter)
        if not os.path.exists(src):
            sys.exit("no background for %s; run generate first" % letter)
        r = {"letter": letter}
        with tempfile.TemporaryDirectory() as work:
            bg = os.path.join(work, "crop.png")
            crop_to_5x1(src, bg, OPTIONS[letter]["crop_y"])
            strength, met, before, after = cc.solve_scrim(FMT, bg, size)
            r.update(strength=strength, met=met, before=before, after=after)
            scrimmed = os.path.join(work, "scrimmed.png")
            cc.apply_scrim(FMT, bg, scrimmed, strength, size, work)

            layer = os.path.join(work, "type.png")
            render(layer, size, list(parts.values()))
            x0, y0, x1, y1 = cc.type_bounds(layer)
            r["ink_1x"] = tuple(round(v / SCALE, 1) for v in (x0, y0, x1, y1))
            r["pad_1x"] = (round(x0 / SCALE, 1), round(y0 / SCALE, 1),
                           round(OUT[0] - x1 / SCALE, 1), round(OUT[1] - y1 / SCALE, 1))
            r["pad_ok"] = min(r["pad_1x"][0], r["pad_1x"][1], r["pad_1x"][3]) >= PAD
            r["title_right_frac"] = round(x1 / size[0], 3)

            fills = {"wordmark": (hex_rgb(cc.RED), 1.0), "title": (hex_rgb(cc.PAPER), 1.0),
                     "rule": (hex_rgb(cc.RED), 1.0), "tagline": (hex_rgb(cc.PAPER), 0.78)}
            r["contrast"] = {}
            for name, args in parts.items():
                el = os.path.join(work, name + ".png")
                render(el, size, [args])
                r["contrast"][name] = contrast_under(scrimmed, el, *fills[name], work)

            composed = os.path.join(work, "composed.png")
            cc.composite_type(scrimmed, layer, composed, size, work)
            out2 = os.path.join(HERE, "option-%s-2200x440.png" % letter)
            out1 = os.path.join(HERE, "option-%s-1100x220.png" % letter)
            prev = os.path.join(HERE, "option-%s-550-preview.png" % letter)
            cc.magick(composed, "-strip", "-depth", "8", out2)
            cc.magick(composed, "-filter", "Lanczos", "-resize", "%dx%d!" % OUT, "-strip", "-depth", "8", out1)
            cc.magick(out1, "-filter", "Lanczos", "-resize", "550x110!", "-strip", "-depth", "8", prev)
            r["sizes"] = [cc.image_size(p) for p in (out1, out2, prev)]
        results.append(r)
        report(r, lay)
    with open(os.path.join(HERE, "checks.json"), "w") as f:
        json.dump({"layout_2x": lay, "options": results}, f, indent=1, default=list)
    return results


def report(r: dict, lay: dict) -> None:
    z = "   ".join("%s %5.1f/%3.0f -> %5.1f/%3.0f" % (n, *b, *a)
                   for n, b, a in zip(ZONE_NAMES, r["before"], r["after"]))
    print("%s  scrim %.2f %s   %s" % (r["letter"], r["strength"], "ok" if r["met"] else "TARGET NOT MET", z))
    print("   ink 1x %s, clear space L/T/R/B %s  %s" % (r["ink_1x"], r["pad_1x"], "ok" if r["pad_ok"] else "UNDER 40px"))
    print("   contrast (worst p95 / median): " + ", ".join(
        "%s %.1f/%.1f" % (k, *v) for k, v in r["contrast"].items()))
    print("   wrote %s" % ", ".join("%dx%d" % s for s in r["sizes"]))


def sheet() -> None:
    rows = []
    with tempfile.TemporaryDirectory() as work:
        for letter in OPTIONS:
            one = os.path.join(HERE, "option-%s-1100x220.png" % letter)
            prev = os.path.join(HERE, "option-%s-550-preview.png" % letter)
            if not os.path.exists(one):
                continue
            row = os.path.join(work, letter + ".png")
            cc.magick("(", one, ")", "(", "-size", "24x220", "xc:#0c1424", ")",
                      "(", prev, "-background", "#0c1424", "-gravity", "north", "-extent", "550x220", ")",
                      "+append", "-background", "#0c1424", "-gravity", "north", "-splice", "0x34",
                      "-font", cc.FONT_SUPPORT, "-pointsize", "18", "-fill", "#c9ccd3",
                      "-gravity", "northwest", "-annotate", "+0+8",
                      "Option %s   seed %d   1100x220, and at 550 wide" % (letter, OPTIONS[letter]["seed"]), row)
            rows.append(row)
        if not rows:
            sys.exit("nothing built yet")
        cc.magick(*rows, "-background", "#0c1424", "-splice", "0x16", "-append",
                  "-bordercolor", "#0c1424", "-border", "24", os.path.join(HERE, "contact-sheet.png"))
    print("wrote contact-sheet.png")


def main(argv: list[str]) -> None:
    if not argv or argv[0] not in ("prompt", "generate", "build", "sheet"):
        sys.exit(__doc__)
    letters = argv[1:] or list(OPTIONS)
    if any(l not in OPTIONS for l in letters):
        sys.exit("options are " + " ".join(OPTIONS))
    {"prompt": lambda: print(PROMPT), "generate": lambda: generate(letters),
     "build": lambda: build(letters), "sheet": sheet}[argv[0]]()


if __name__ == "__main__":
    main(sys.argv[1:])
