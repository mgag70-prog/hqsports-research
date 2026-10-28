#!/usr/bin/env python3
"""Full-bleed cover options for mlb-2027-cap-2026. Nothing is installed; figures/cover-fal-*.png is untouched.

Backgrounds come from fal.ai through the request code in tools/compose_cover.py, with a louder style
line in place of the still-life house style and the same no-text, no-logo, no-people rules appended.
Every option carries the cover line "Over the cap. Before the offseason.", the wordmark, a bottom
gradient scrim in deep navy and a red rule; the wide format is checked against the X-card safe zone.

Files, all under figures/:
  raw/cover-options/option-{A,B,C,D}-background.png   fal.ai output as returned (raw/ is gitignored)
  cover-options/prompts.md                            prompt, model, seed, request id, date per option
  cover-options/option-{A,B,C,D}-1200x630.png         wide
  cover-options/option-{A,B,C,D}-1080x1080.png        square crop of the same background
  cover-options/contact-sheet.png                     all eight, labeled (gitignored, 12 MB)
  cover-options/README.md                             the ranking, written by hand after looking

Usage, from anywhere:
  python3 build_options.py generate [A B C D]   # fal.ai, needs FAL_KEY in the environment, $0.15 each
  python3 build_options.py build [A B C D]      # scrim, type, safe-zone check; also writes the sheet
  python3 build_options.py sheet
  python3 build_options.py cover                # rebuild figures/cover-fal-*.png from cover.json once one is installed
"""
import base64
import os
import sys
import tempfile
import time
import urllib.request
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
PIECE = os.path.dirname(os.path.dirname(HERE))
REPO = os.path.dirname(PIECE)
sys.path.insert(0, os.path.join(REPO, "tools"))
import compose_cover as cc  # noqa: E402

RAW_DIR = os.path.join(PIECE, "figures", "raw", "cover-options")
RECORD = os.path.join(HERE, "prompts.md")
DRAFT = os.path.join(PIECE, "draft.md")

COVER_LINE = ["Over the cap.", "Before the offseason."]
DEEP_RGB = (10, 19, 38)
COST_PER_IMAGE = 0.15

STYLE = (
    "Cinematic editorial photograph for a publication about the money in sport, lit like a film "
    "poster still: high contrast, one hard dramatic key light, deep black shadows, rich dark navy "
    "blue tones throughout, and one bold accent of brick red somewhere in the scene. Fine film "
    "grain, polished and intense, full-bleed with no empty panel."
)
COMPOSITION = (
    "Wide 16:9 frame, the scene filling the whole image. The lower third of the frame stays darker "
    "and simpler than the rest, with no small objects in it, so a caption can sit over it."
)
OPTIONS = {
    "A": {"seed": 5101, "square_crop_x": 0.30, "subject": (
        "A tall clear glass tank filled far past a thick brick red line painted around it near the top, worn "
        "baseballs spilling over the rim and tumbling down the sides onto a dark polished floor, one hard "
        "spotlight from above, glints on the glass.")},
    "B": {"seed": 5102, "square_crop_x": 0.30, "wide": {"headline_max_width": 0.36}, "subject": (
        "A towering pile of plain unmarked gold ingots stacked on dark infield dirt at night, rising well above "
        "a taut brick red rope stretched straight across the frame at waist height, floodlight glare and haze "
        "behind, the gold blazing in the light.")},
    "C": {"seed": 5103, "square_crop_x": 0.30, "subject": (
        "A baseball smashing upward through a thick brick red painted wooden beam, splinters and red paint "
        "chips frozen in midair, stadium floodlights flaring behind, deep night sky, extreme high speed photograph.")},
    "D": {"seed": 5104, "square_crop_x": 0.30, "subject": (
        "An empty batting cage at night, its dark netting bulging and sagging under a heap of worn baseballs "
        "piled far above a brick red top rail, balls spilling through the gaps onto bare ground, one floodlight "
        "raking across from the side.")},
}

# Full-bleed formats: type bottom-left, scrim rising from the bottom and fading rightward, plus a
# top-left corner so the wordmark lands on dark ground too.
FORMATS = {
    "wide": {"out_size": (1200, 630), "safe_box": cc.X_CARD_BOX, "margin_x": 96 / 1200,
             "bottom": 0.83, "headline_max_width": 0.76, "headline_max_size": 0.175,
             "scrim_y": (0.98, 0.30), "scrim_x": (0.84, 1.00), "corner": 1.0,
             "corner_y": (0.18, 0.36), "corner_x": (0.40, 0.68)},
    "square": {"out_size": (1080, 1080), "safe_box": None, "margin_x": 0.07,
               "bottom": 0.905, "headline_max_width": 0.86, "headline_max_size": 0.105,
               "scrim_y": (0.98, 0.50), "scrim_x": None, "corner": 1.0,
               "corner_y": (0.18, 0.30), "corner_x": (0.42, 0.76)},
}
RULE = (0.012, 0.11, 0.55)   # red rule: height and width as fractions of frame height, gap above the headline in cap heights


def out_path(letter: str, fmt_name: str) -> str:
    w, h = FORMATS[fmt_name]["out_size"]
    return os.path.join(HERE, "option-%s-%dx%d.png" % (letter, w, h))


def background_path(letter: str) -> str:
    return os.path.join(RAW_DIR, "option-%s-background.png" % letter)


# --- prompt and generation -------------------------------------------------

EDIT_URL = "https://queue.fal.run/" + cc.MODEL + "/edit"


def option_prompt(letter: str) -> str:
    subject = OPTIONS[letter]["subject"]
    problems = cc.lint_subject(subject)
    if problems:
        sys.exit("option %s subject breaks the cover rules:\n  %s" % (letter, "\n  ".join(problems)))
    if OPTIONS[letter].get("edit_of"):
        return subject + " " + cc.RULES
    return " ".join((STYLE, "Subject: " + subject, COMPOSITION, cc.RULES))


def image_data_uri(path: str, workdir: str) -> str:
    """The background as a full-size JPEG data URI, the input image for the edit endpoint."""
    jpeg = os.path.join(workdir, "input.jpg")
    cc.magick(path, "-quality", "92", jpeg)
    with open(jpeg, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


def submit(letter: str, key: str) -> dict:
    seed = OPTIONS[letter]["seed"]
    prompt = option_prompt(letter)
    source = OPTIONS[letter].get("edit_of")
    if source:
        with tempfile.TemporaryDirectory() as work:
            payload = {"prompt": prompt, "seed": seed, "image_urls": [image_data_uri(background_path(source), work)],
                       **cc.MODEL_PARAMS}
            submitted = cc.fal_request(EDIT_URL, key, payload)
    else:
        submitted = cc.fal_request(cc.QUEUE_URL, key, {"prompt": prompt, "seed": seed, **cc.MODEL_PARAMS})
    print("option %s: submitted %s, seed %d%s" % (letter, submitted["request_id"], seed,
                                                   ", edit of %s" % source if source else ""), flush=True)
    return {"letter": letter, "prompt": prompt, "seed": seed, "submitted": submitted}


def collect(job: dict, key: str) -> dict:
    deadline = time.time() + cc.POLL_LIMIT_SECONDS
    while True:
        status = cc.fal_request(job["submitted"]["status_url"], key)["status"]
        if status == "COMPLETED":
            break
        if status not in ("IN_QUEUE", "IN_PROGRESS"):
            raise RuntimeError("option %s: fal.ai request ended with status %s" % (job["letter"], status))
        if time.time() > deadline:
            raise RuntimeError("option %s: still %s after %ds" % (job["letter"], status, cc.POLL_LIMIT_SECONDS))
        time.sleep(cc.POLL_SECONDS)
    result = cc.fal_request(job["submitted"]["response_url"], key)
    images = result.get("images") or []
    if not images:
        raise RuntimeError("option %s: fal.ai returned no image" % job["letter"])
    os.makedirs(RAW_DIR, exist_ok=True)
    dst = background_path(job["letter"])
    with urllib.request.urlopen(images[0]["url"], timeout=120) as response, open(dst, "wb") as f:
        f.write(response.read())
    job["size"] = cc.image_size(dst)
    print("option %s: wrote %s (%dx%d)" % (job["letter"], os.path.relpath(dst, PIECE), *job["size"]), flush=True)
    return job


def write_record(jobs: list[dict]) -> None:
    params = ", ".join("%s %s" % (k, v) for k, v in cc.MODEL_PARAMS.items())
    new = not os.path.exists(RECORD)
    with open(RECORD, "a") as f:
        if new:
            f.write("# Cover option prompts: mlb-2027-cap-2026\n\n")
            f.write("- Model: %s (generation), %s/edit (edits)\n- Parameters: %s\n- Cost: $%.2f per image\n"
                    "- Cover line on every option: %s\n\n" % (cc.MODEL, cc.MODEL, params, COST_PER_IMAGE, " ".join(COVER_LINE)))
        for job in jobs:
            letter = job["letter"]
            source = OPTIONS[letter].get("edit_of")
            f.write("## Option %s%s\n\n- Date: %s\n- Endpoint: %s\n- Seed: %d\n- Request: %s\n- Background: %s, %dx%d\n- Cost: $%.2f\n\n"
                    % (letter, " (edit of option %s's background)" % source if source else "", date.today().isoformat(),
                       cc.MODEL + ("/edit" if source else ""), job["seed"], job["submitted"]["request_id"],
                       os.path.relpath(background_path(letter), PIECE), *job["size"], COST_PER_IMAGE))
            f.write("### Subject\n\n%s\n\n### Prompt as sent\n\n%s\n\n" % (OPTIONS[letter]["subject"], job["prompt"]))
    print("wrote", os.path.relpath(RECORD, PIECE))


def generate(letters: list[str]) -> None:
    key = os.environ.get("FAL_KEY")
    if not key:
        sys.exit("FAL_KEY is not set")
    for letter in letters:
        if os.path.exists(background_path(letter)):
            sys.exit("option %s already has a background at %s; delete it to regenerate" % (letter, background_path(letter)))
    jobs = [submit(letter, key) for letter in letters]
    jobs = [collect(job, key) for job in jobs]
    write_record(jobs)
    print("look at each background for stray lettering, marks or a recognizable place before building")


# --- checks against the piece ----------------------------------------------

def draft_report() -> list[str]:
    """Overlay text not found verbatim in draft.md. Reported, not fatal: these are options."""
    with open(DRAFT) as f:
        draft = cc.normalize(f.read())
    text = " ".join(COVER_LINE)
    missing = [] if cc.normalize(text) in draft else [text]
    for figure in cc.NUMBER.findall(text):
        if cc.normalize(figure) not in draft:
            missing.append("figure " + figure)
    return missing


# --- scrim -----------------------------------------------------------------

def alpha_at(fmt: dict, x: float, y: float, strength: float) -> float:
    main = cc.falloff(y, *fmt["scrim_y"]) * (cc.falloff(x, *fmt["scrim_x"]) if fmt["scrim_x"] else 1.0)
    corner = fmt["corner"] * cc.falloff(y, *fmt["corner_y"]) * cc.falloff(x, *fmt["corner_x"])
    return strength * max(main, corner)


def zone_stats(fmt: dict, grid: list[list[int]], zone: tuple, strength: float, rgb: tuple) -> tuple[float, float]:
    x0, y0, x1, y1 = zone
    rows, cols = len(grid), len(grid[0])
    luma = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    values = []
    for r, row in enumerate(grid):
        y = y0 + (y1 - y0) * (r + 0.5) / rows
        for c, v in enumerate(row):
            a = alpha_at(fmt, x0 + (x1 - x0) * (c + 0.5) / cols, y, strength)
            values.append(v * (1.0 - a) + luma * a)
    values.sort()
    return sum(values) / len(values), values[int(len(values) * 0.95)]


def solve_scrim(fmt: dict, path: str, size: tuple[int, int], zones: list, rgb: tuple) -> tuple:
    grids = [(zone, target, cc.zone_grid(path, size, zone)) for zone, target in zones]
    stats = lambda s: [zone_stats(fmt, grid, zone, s, rgb) for zone, _, grid in grids]
    meets = lambda result: all(m <= t[0] and p <= t[1] for (m, p), (_, t, _) in zip(result, grids))
    strength = cc.SCRIM_FLOOR
    while strength < cc.SCRIM_CEILING and not meets(stats(strength)):
        strength = round(strength + cc.SCRIM_STEP, 4)
    return strength, meets(stats(strength)), stats(0.0), stats(strength)


def band_luma(path: str, size: tuple[int, int], zone: tuple) -> tuple[float, float]:
    grid = cc.zone_grid(path, size, zone)
    values = sorted(v for row in grid for v in row)
    return sum(values) / len(values), values[int(len(values) * 0.95)]


def darken_band(src: str, dst: str, size: tuple[int, int], zone: tuple, rgb: tuple, workdir: str) -> tuple:
    """Lay a feathered local scrim over the headline zone, at the smallest strength that meets the ceiling.

    Returns (strength, met, (mean, p95)). The mask is the zone padded by 4% of the frame and blurred."""
    w, h = size
    x0, y0, x1, y1 = zone
    pad_x, pad_y = int(w * 0.04), int(h * 0.04)
    rect = "rectangle %d,%d %d,%d" % (int(w * x0) - pad_x, int(h * y0) - pad_y, int(w * x1) + pad_x, int(h * y1) + pad_y)
    mask = os.path.join(workdir, "band-mask.png")
    for step in range(2, 20):
        strength = step * 0.05
        cc.magick("-size", "%dx%d" % (w, h), "xc:black", "-fill", "white", "-draw", rect,
                  "-blur", "0x%d" % max(1, int(h * 0.03)), "-evaluate", "multiply", "%.3f" % strength, mask)
        cc.magick(src, "(", "-size", "%dx%d" % (w, h), "xc:rgb(%d,%d,%d)" % rgb, mask,
                  "-alpha", "off", "-compose", "CopyOpacity", "-composite", ")", "-compose", "Over", "-composite", dst)
        mean, p95 = band_luma(dst, size, zone)
        if mean <= cc.BAND_TARGET[0] and p95 <= cc.BAND_TARGET[1]:
            return strength, True, (mean, p95)
    return strength, False, (mean, p95)


def apply_scrim(fmt: dict, src: str, dst: str, strength: float, size: tuple[int, int], rgb: tuple, workdir: str) -> None:
    w, h = size
    mask = os.path.join(workdir, "mask.pgm")
    with open(mask, "wb") as f:
        f.write(b"P5\n%d %d\n255\n" % (w, h))
        for y in range(h):
            f.write(bytes(int(round(255 * alpha_at(fmt, (x + 0.5) / w, (y + 0.5) / h, strength))) for x in range(w)))
    cc.magick(src, "(", "-size", "%dx%d" % (w, h), "xc:rgb(%d,%d,%d)" % rgb, mask,
              "-alpha", "off", "-compose", "CopyOpacity", "-composite", ")", "-compose", "Over", "-composite", dst)


# --- type ------------------------------------------------------------------

def headline_px(fmt: dict, size: tuple[int, int], lines: list[str]) -> int:
    limit = size[0] * fmt["headline_max_width"]
    widest = max(cc.text_extent(cc.FONT_HEADLINE, 100, 0, line)[0] for line in lines)
    return min(int(size[1] * fmt["headline_max_size"]), int(100 * limit / widest))


def headline_block(fmt: dict, size: tuple[int, int], lines: list[str]) -> dict:
    """Pixel positions of the wordmark, red rule and the headline lines, bottom-anchored."""
    w, h = size
    px = headline_px(fmt, size, lines)
    cap = cc.text_extent(cc.FONT_HEADLINE, px, 0, "H")[1]
    pitch = cc.HEADLINE_LEADING * cap
    baselines = [h * fmt["bottom"] - pitch * (len(lines) - 1 - i) for i in range(len(lines))]
    rule_h, rule_w, rule_gap = RULE
    rule_y1 = baselines[0] - cap - cap * rule_gap
    return {"x": int(w * fmt["margin_x"]), "px": px, "cap": cap, "baselines": baselines,
            "rule": (int(w * fmt["margin_x"]), round(rule_y1 - h * rule_h), round(h * rule_w), round(h * rule_h))}


def render_type(fmt: dict, dst: str, size: tuple[int, int], lines: list[str] = COVER_LINE) -> dict:
    w, h = size
    lay = headline_block(fmt, size, lines)
    x = lay["x"]
    wordmark_px = max(1, round(h * cc.WORDMARK_SIZE))
    rx, ry, rw, rh = lay["rule"]
    args = ["-size", "%dx%d" % (w, h), "xc:none",
            "-font", cc.FONT_SUPPORT, "-pointsize", str(wordmark_px),
            "-kerning", str(round(wordmark_px * cc.WORDMARK_TRACKING, 2)),
            "-fill", cc.RED, "-annotate", "+%d+%d" % (x, round(h * cc.WORDMARK_BASELINE)), cc.WORDMARK,
            "-fill", cc.RED, "-draw", "rectangle %d,%d %d,%d" % (rx, ry, rx + rw, ry + rh),
            "-font", cc.FONT_HEADLINE, "-pointsize", str(lay["px"]), "-kerning", "0"]
    for line, y, fill in zip(lines, lay["baselines"], [cc.PAPER] + [cc.RED] * (len(lines) - 1)):
        args += ["-fill", fill, "-annotate", "+%d+%d" % (x, round(y)), line]
    cc.magick(*args, dst)
    return lay


def type_zones(fmt: dict, size: tuple[int, int], lay: dict) -> list:
    """The headline block and the wordmark strip, each paired with the house luminance ceiling."""
    w, h = size
    x0 = fmt["margin_x"] - 0.01
    top = (lay["rule"][1] - 4) / h
    bottom = min(1.0, (lay["baselines"][-1] + lay["cap"] * 0.35) / h)
    right = min(0.99, fmt["margin_x"] + fmt["headline_max_width"] + 0.02)
    word = (x0, cc.WORDMARK_BASELINE - 0.04, fmt["margin_x"] + 0.30, cc.WORDMARK_BASELINE + 0.02)
    return [((x0, top, right, bottom), cc.BAND_TARGET), (word, cc.BAND_TARGET)]


def safe_check(fmt: dict, layer: str, size: tuple[int, int]) -> None:
    zone = cc.safe_zone(fmt, size)
    if not zone:
        return
    bx0, by0, bx1, by1 = cc.type_bounds(layer)
    zx0, zy0, zx1, zy1 = zone
    scale = fmt["out_size"][0] / size[0]
    inside = bx0 >= zx0 and by0 >= zy0 and bx1 <= zx1 and by1 <= zy1
    print("         type %d,%d to %d,%d in the X-card safe zone %d,%d to %d,%d (output px)   %s"
          % (bx0 * scale, by0 * scale, bx1 * scale, by1 * scale,
             zx0 * scale, zy0 * scale, zx1 * scale, zy1 * scale, "ok" if inside else "TYPE OUTSIDE THE SAFE ZONE"), flush=True)
    if not inside:
        sys.exit("type falls outside the X-card safe zone")


# --- builds ----------------------------------------------------------------

def crop_source(fmt: dict, src: str, crop_x: float, workdir: str) -> str:
    return cc.prepare_source({"out_size": fmt["out_size"]}, src, {"square_crop_x": crop_x}, workdir)


def compose(src: str, opt: dict, label: str, out_for) -> None:
    """Scrim and type over a background for both formats; opt gives square_crop_x, flip and per-format overrides."""
    for name, fmt in FORMATS.items():
        with tempfile.TemporaryDirectory() as work:
            source = src
            if opt.get("flip"):   # mirrored so the subject clears the wordmark; no text in the image to reverse
                source = os.path.join(work, "flipped.png")
                cc.magick(src, "-flop", source)
            cropped = crop_source(fmt, source, opt["square_crop_x"], work)
            size = cc.image_size(cropped)
            layer = os.path.join(work, "type.png")
            override = opt.get(name, {})          # per-format: "lines", "headline_max_width"
            fmt = {**fmt, **{k: v for k, v in override.items() if k != "lines"}}
            lay = render_type(fmt, layer, size, override.get("lines", COVER_LINE))
            zones = type_zones(fmt, size, lay)
            strength, met, before, after = solve_scrim(fmt, cropped, size, zones, DEEP_RGB)
            print(cc.describe("%s %s" % (label, name), strength, met, before, after), flush=True)
            safe_check(fmt, layer, size)
            scrimmed, composed = os.path.join(work, "scrimmed.png"), os.path.join(work, "composed.png")
            apply_scrim(fmt, cropped, scrimmed, strength, size, DEEP_RGB, work)
            if not met and opt.get("band_boost"):
                boosted = os.path.join(work, "boosted.png")
                s2, met2, (m2, p2) = darken_band(scrimmed, boosted, size, zones[0][0], DEEP_RGB, work)
                print("         band darkened locally at %.2f -> %5.1f/%3.0f   %s" % (s2, m2, p2, "ok" if met2 else "TARGET NOT MET"), flush=True)
                scrimmed = boosted
            cc.composite_type(scrimmed, layer, composed, size, work)
            final = out_for(name)
            cc.magick(composed, "-resize", "%dx%d!" % fmt["out_size"], "-strip", "-depth", "8", final)
            print("         wrote", os.path.relpath(final, PIECE))


def build_photo(letter: str) -> None:
    src = background_path(letter)
    if not os.path.exists(src):
        sys.exit("option %s has no background; run generate first" % letter)
    compose(src, OPTIONS[letter], letter, lambda name: out_path(letter, name))


def build_cover() -> None:
    """Rebuild the installed cover, figures/cover-fal-*.png, from figures/cover.json and raw/cover-background.png."""
    paths = cc.piece_paths(PIECE)
    cfg = cc.load_config(paths)
    if cfg.get("builder") != "cover-options":
        sys.exit("figures/cover.json is not a cover-options cover; use tools/compose_cover.py build")
    if cfg.get("headline") != COVER_LINE:
        sys.exit("cover.json headline differs from this script's cover line: %r" % cfg.get("headline"))
    cc.check_against_draft(paths, cfg, list(cc.FORMATS))
    if not os.path.exists(paths["background"]):
        sys.exit("no background at %s" % paths["background"])
    opt = {**cfg, **cfg.get("formats", {})}
    compose(paths["background"], opt, "cover", lambda name: os.path.join(paths["figures"], cc.FORMATS[name]["out_name"]))


def contact_sheet() -> None:
    tiles = []
    for letter in OPTIONS:
        for name in FORMATS:
            path = out_path(letter, name)
            if not os.path.exists(path):
                sys.exit("missing %s; build it first" % os.path.relpath(path, PIECE))
            tiles += ["-label", "%s  %s" % (letter, os.path.basename(path)), path]
    sheet = os.path.join(HERE, "contact-sheet.png")
    cc.magick("montage", *tiles, "-font", cc.FONT_SUPPORT, "-pointsize", "22", "-fill", "#16284A",
              "-background", cc.PAPER, "-tile", "2x%d" % len(OPTIONS), "-geometry", "600x600>+18+14", sheet)
    print("wrote", os.path.relpath(sheet, PIECE))


def build(letters: list[str]) -> None:
    missing = draft_report()
    for letter in letters:
        build_photo(letter)
    if sorted(letters) == sorted(OPTIONS):
        contact_sheet()
    if missing:
        print("NOT VERBATIM IN draft.md (compose_cover would stop on these if one is installed):")
        for m in missing:
            print("  ", m)


def main(argv: list[str]) -> None:
    if not argv or argv[0] not in ("generate", "build", "sheet", "cover"):
        sys.exit(__doc__)
    letters = [a.upper() for a in argv[1:]] or list(OPTIONS)
    if any(x not in OPTIONS for x in letters):
        sys.exit(__doc__)
    if argv[0] == "cover":
        build_cover()
    elif argv[0] == "generate":
        generate(letters)
    elif argv[0] == "build":
        build(letters)
    else:
        contact_sheet()


if __name__ == "__main__":
    main(sys.argv[1:])
