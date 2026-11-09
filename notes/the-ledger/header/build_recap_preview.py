#!/usr/bin/env python3
"""Social preview for a Ledger monthly recap, built from header option B's background (seed 5102).

No generation: the image is raw/option-B-background.png, cropped. Type is set in the header's
house style (Georgia, from tools/compose_cover.py): the red "LEDGER & WHISTLE" wordmark top left,
"THE LEDGER" large in paper, a short red rule, the recap line in paper and the tagline in paper
at 78%. The navy scrim is solved per format against the house luminance ceilings, the wide type
is checked against the Substack X-card safe zone, and each element's contrast is measured
against the scrimmed pixels under its ink.

Usage, from the repo root:
  python3 notes/the-ledger/header/build_recap_preview.py ["October 2026 recap"] [slug]

Writes, next to this script:
  ledger-recap-2026-10-1200x630.png    the social preview
  ledger-recap-2026-10-1080x1080.png   the square
  ledger-recap-2026-10-checks.json
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, HERE)
import compose_cover as cc  # noqa: E402  house scrim, shadow and magick helpers
import build_header as bh  # noqa: E402  contrast measurement and element rendering helpers

SRC = os.path.join(HERE, "raw", "option-B-background.png")
SEED = 5102
RECAP_LINE = "October 2026 recap"
SLUG = "ledger-recap-2026-10"
SCALE = 2
PAD = 40                       # minimum clear space to every frame edge, as on the header
# Worst-case (p95 background) contrast floors. Paper type must reach 4.5. The red wordmark can't over
# any navy scrim (the house red on the house navy is about 3.6); header A shipped at 3.7, so it gets 3.0.
# The rule is decoration and isn't held to one.
MIN_CONTRAST = {"wordmark": 3.0, "title": 4.5, "recap": 4.5, "tagline": 4.5}

# crop: (left, top, width, height) as fractions of the 3168x1344 background.
# Type sizes and gaps in 1x output pixels. block_y: where the block below the wordmark is centred.
FORMATS = {
    "wide": {
        "out": (1200, 630), "crop": (0.192, 0.0, 0.808, 1.0), "safe_box": cc.X_CARD_BOX,
        # The book starts about a third of the way in, so the type sits top left over the dark wall
        # and the scrim fades both right and down, leaving the book, whistle and ball unveiled.
        "margin_x": 96, "wordmark_px": 18, "wordmark_baseline": 108,
        "title_cap": 48, "title_max_w": 0.42, "gap_rule": 14, "rule": (72, 4),
        "gap_recap": 18, "recap_px": 30, "gap_tag": 12, "tag_px": 21, "block_top": 136,
        "scrim_x": (0.40, 0.70), "scrim_y": (0.42, 0.66),
        "zones": [((0.00, 0.00, 0.30, 1.00), cc.LEFT_TARGET), ((0.04, 0.12, 0.50, 0.46), cc.BAND_TARGET)],
    },
    "square": {
        "out": (1080, 1080), "crop": (0.544, 0.0, 0.424, 1.0), "safe_box": None,
        "margin_x": 64, "wordmark_px": 18, "wordmark_baseline": 84,
        "title_cap": 52, "title_max_w": 0.62, "gap_rule": 16, "rule": (72, 4),
        "gap_recap": 20, "recap_px": 30, "gap_tag": 14, "tag_px": 21, "block_top": 128,
        "scrim_x": (0.70, 1.00), "scrim_y": (0.30, 0.52),
        "zones": [((0.03, 0.03, 0.70, 0.33), cc.BAND_TARGET)],
    },
}
ZONE_NAMES = {"wide": ("left 30%", "type band"), "square": ("type band",)}


def crop(fmt: dict, dst: str) -> None:
    w, h = cc.image_size(SRC)
    l, t, cw, ch = fmt["crop"]
    box = (round(w * cw), round(h * ch), round(w * l), round(h * t))
    out = fmt["out"]
    if abs(box[0] / box[1] - out[0] / out[1]) > 0.01:
        sys.exit("crop %s is not %dx%d in shape" % (fmt["crop"], *out))
    if box[2] + box[0] > w or box[3] + box[1] > h:
        sys.exit("crop runs off the background")
    cc.magick(SRC, "-crop", "%dx%d+%d+%d" % box, "+repage", "-filter", "Lanczos",
              "-resize", "%dx%d!" % (out[0] * SCALE, out[1] * SCALE), dst)


def layout(fmt: dict) -> dict:
    """2x pixel positions of every element."""
    s = SCALE
    probe = 100
    title_px = int(round(probe * fmt["title_cap"] * s / cc.text_extent(cc.FONT_HEADLINE, probe, 0, "H")[1]))
    tracking = round(title_px * bh.TITLE_TRACKING, 2)
    limit = fmt["out"][0] * s * fmt["title_max_w"]
    title_w = cc.text_extent(cc.FONT_HEADLINE, title_px, tracking, bh.TITLE)[0]
    if title_w > limit:
        title_px = int(title_px * limit / title_w)
        tracking = round(title_px * bh.TITLE_TRACKING, 2)
    cap = lambda font, size: cc.text_extent(font, size, 0, "H")[1]
    title_cap = cap(cc.FONT_HEADLINE, title_px)
    recap_px, tag_px, wm_px = fmt["recap_px"] * s, fmt["tag_px"] * s, fmt["wordmark_px"] * s
    recap_cap, tag_cap = cap(cc.FONT_SUPPORT, recap_px), cap(cc.FONT_SUPPORT, tag_px)
    block = (title_cap + (fmt["gap_rule"] + fmt["rule"][1] + fmt["gap_recap"]) * s + recap_cap
             + fmt["gap_tag"] * s + tag_cap)
    top = fmt["block_top"] * s if "block_top" in fmt else fmt["out"][1] * s * fmt["block_y"] - block / 2
    lay = {"x": fmt["margin_x"] * s, "wm_px": wm_px, "title_px": title_px, "title_tracking": tracking,
           "recap_px": recap_px, "tag_px": tag_px, "wm_y": fmt["wordmark_baseline"] * s}
    lay["title_y"] = top + title_cap
    lay["rule_y"] = lay["title_y"] + fmt["gap_rule"] * s
    lay["recap_y"] = lay["rule_y"] + (fmt["rule"][1] + fmt["gap_recap"]) * s + recap_cap
    lay["tag_y"] = lay["recap_y"] + fmt["gap_tag"] * s + tag_cap
    return lay


def elements(fmt: dict, lay: dict, recap_line: str) -> dict:
    x, s = lay["x"], SCALE
    text = lambda font, size, fill, y, words, kern="0": [
        "-font", font, "-pointsize", str(size), "-kerning", str(kern), "-fill", fill,
        "-annotate", "+%d+%d" % (x, round(y)), words]
    return {
        "wordmark": text(cc.FONT_SUPPORT, lay["wm_px"], cc.RED, lay["wm_y"], cc.WORDMARK,
                         round(lay["wm_px"] * cc.WORDMARK_TRACKING, 2)),
        "title": text(cc.FONT_HEADLINE, lay["title_px"], cc.PAPER, lay["title_y"], bh.TITLE, lay["title_tracking"]),
        "rule": ["-fill", cc.RED, "-draw", "rectangle %d,%d %d,%d" % (
            x, round(lay["rule_y"]), x + fmt["rule"][0] * s - 1, round(lay["rule_y"]) + fmt["rule"][1] * s - 1)],
        "recap": text(cc.FONT_SUPPORT, lay["recap_px"], cc.PAPER, lay["recap_y"], recap_line),
        "tagline": text(cc.FONT_SUPPORT, lay["tag_px"], cc.PAPER_MUTED, lay["tag_y"], bh.TAGLINE),
    }


FILLS = {"wordmark": (cc.RED, 1.0), "title": (cc.PAPER, 1.0), "rule": (cc.RED, 1.0),
         "recap": (cc.PAPER, 1.0), "tagline": (cc.PAPER, 0.78)}


def build_one(name: str, recap_line: str, slug: str) -> dict:
    fmt = FORMATS[name]
    out = fmt["out"]
    size = (out[0] * SCALE, out[1] * SCALE)
    fmt_cc = {"scrim_x": fmt["scrim_x"], "scrim_y": fmt["scrim_y"], "zones": fmt["zones"]}
    lay = layout(fmt)
    parts = elements(fmt, lay, recap_line)
    r = {"format": name, "size": list(out), "crop": fmt["crop"]}
    with tempfile.TemporaryDirectory() as work:
        bg = os.path.join(work, "crop.png")
        crop(fmt, bg)
        strength, met, before, after = cc.solve_scrim(fmt_cc, bg, size)
        r.update(scrim=strength, scrim_met=met, before=before, after=after)
        scrimmed = os.path.join(work, "scrimmed.png")
        cc.apply_scrim(fmt_cc, bg, scrimmed, strength, size, work)

        layer = os.path.join(work, "type.png")
        bh.render(layer, size, list(parts.values()))
        x0, y0, x1, y1 = (v / SCALE for v in cc.type_bounds(layer))
        r["ink_1x"] = [round(v, 1) for v in (x0, y0, x1, y1)]
        r["clear_1x"] = [round(x0, 1), round(y0, 1), round(out[0] - x1, 1), round(out[1] - y1, 1)]
        r["clear_ok"] = min(r["clear_1x"]) >= PAD
        if fmt["safe_box"]:
            bx0, by0, bx1, by1 = fmt["safe_box"]
            m = cc.SAFE_MARGIN_PX
            r["safe_zone"] = [bx0 + m, by0 + m, bx1 - m, by1 - m]
            r["safe_ok"] = x0 >= bx0 + m and y0 >= by0 + m and x1 <= bx1 - m and y1 <= by1 - m
        r["contrast"] = {}
        for el, args in parts.items():
            path = os.path.join(work, el + ".png")
            bh.render(path, size, [args])
            fill, alpha = FILLS[el]
            r["contrast"][el] = [round(v, 2) for v in bh.contrast_under(scrimmed, path, bh.hex_rgb(fill), alpha, work)]
        r["contrast_ok"] = all(r["contrast"][k][0] >= floor for k, floor in MIN_CONTRAST.items())

        composed = os.path.join(work, "composed.png")
        cc.composite_type(scrimmed, layer, composed, size, work)
        dst = os.path.join(HERE, "%s-%dx%d.png" % (slug, *out))
        cc.magick(composed, "-filter", "Lanczos", "-resize", "%dx%d!" % out, "-strip", "-depth", "8", dst)
        r["file"] = os.path.relpath(dst, REPO)
        r["written_size"] = list(cc.image_size(dst))
    report(r)
    return r


def report(r: dict) -> None:
    zones = "   ".join("%s %5.1f/%3.0f -> %5.1f/%3.0f" % (n, *b, *a)
                       for n, b, a in zip(ZONE_NAMES[r["format"]], r["before"], r["after"]))
    print("%-6s scrim %.2f %s   %s" % (r["format"], r["scrim"], "ok" if r["scrim_met"] else "TARGET NOT MET", zones))
    print("       ink 1x %s, clear space L/T/R/B %s %s" % (r["ink_1x"], r["clear_1x"], "ok" if r["clear_ok"] else "UNDER 40px"))
    if "safe_ok" in r:
        print("       X-card safe zone %s: %s" % (r["safe_zone"], "ok" if r["safe_ok"] else "TYPE OUTSIDE"))
    print("       contrast worst/median: " + ", ".join("%s %.1f/%.1f" % (k, *v) for k, v in r["contrast"].items())
          + ("  ok" if r["contrast_ok"] else "  UNDER FLOOR %s" % MIN_CONTRAST))
    print("       wrote %s %s" % (r["file"], "x".join(map(str, r["written_size"]))))


def main(argv: list[str]) -> None:
    recap_line = argv[0] if argv else RECAP_LINE
    slug = argv[1] if len(argv) > 1 else SLUG
    results = [build_one(n, recap_line, slug) for n in FORMATS]
    with open(os.path.join(HERE, "%s-checks.json" % slug), "w") as f:
        json.dump({"background": os.path.relpath(SRC, REPO), "seed": SEED, "recap_line": recap_line,
                   "formats": results}, f, indent=1)
    bad = [r["format"] for r in results
           if not (r["scrim_met"] and r["clear_ok"] and r.get("safe_ok", True) and r["contrast_ok"])]
    if bad:
        sys.exit("CHECKS FAILED: " + ", ".join(bad))
    print("ALL CHECKS PASS")


if __name__ == "__main__":
    main(sys.argv[1:])
