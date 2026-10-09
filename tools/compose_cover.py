#!/usr/bin/env python3
"""Cover art for Ledger & Whistle. Covers only; in-article figures stay code-built.

Three steps per cover. ImageMagick (`magick`) must be on PATH.

  1. Background: a no-text image from fal.ai, prompted with the house style below plus
     one subject line for the piece. The request and its seed are recorded in the
     piece's figures/cover-prompt.md.
  2. Scrim: a navy gradient over the type zone, with its strength solved per cover so
     the type lands on the same dark field every time.
  3. Type: wordmark, headline and sub-line set in Georgia by this script. The model
     never draws a letter or a number.

Rules for every prompt: no text, numbers, logos, team marks, mascots or real people.
The subject line is linted for digits, quotation marks, proper nouns and a short list
of words that invite lettering; the house rules are appended to every prompt. Any
headline or figure on the cover comes from the overlay step and has to appear in the
piece's draft.md, or the build stops.

Each piece supplies figures/cover.json:

  {"subject": "one or two sentences, no names, no numbers",
   "seed": 4101,
   "headline": ["line one", "line two"],
   "sub": ["optional line"],
   "eyebrow": "OPTIONAL SMALL LINE ABOVE THE HEADLINE",
   "square_crop_x": 0.42,
   "formats": {"wide": {"headline_max_width": 0.31},
               "square": {"anchor": ["bottom", 0.94], "headline": ["other", "line breaks"]}}}

"formats" is optional. It overrides any FORMATS setting for this piece's image, and
may give a format its own headline, sub or eyebrow lines; "skip": true drops a format.

and gets back, in the same folder:

  raw/cover-background.png   the image as fal.ai returned it; figures/raw/ is gitignored
  cover-prompt.md            prompt, model, seed, date
  cover-fal-1200x630.png     wide cover, type left-middle, scrim from the left edge
  cover-fal-1080x1080.png    square crop of the same background, type upper-left by default

Usage, from the repo root:
  python3 tools/compose_cover.py prompt PIECE            # print the full prompt, send nothing
  python3 tools/compose_cover.py generate PIECE          # call fal.ai (needs FAL_KEY), write the record
  python3 tools/compose_cover.py build PIECE [format]    # scrim and type; format is wide or square
  python3 tools/compose_cover.py measure PIECE [format]  # darkness and the X-card safe-zone check, no files written
"""
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_NAME = "cover.json"
BACKGROUND_NAME = os.path.join("raw", "cover-background.png")
RECORD_NAME = "cover-prompt.md"
FONT_HEADLINE = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
FONT_SUPPORT = "/System/Library/Fonts/Supplemental/Georgia.ttf"

# --- brand -----------------------------------------------------------------
NAVY = (22, 40, 74)                # #16284A
RED = "#D4553D"
PAPER = "#F7F5F0"
PAPER_MUTED = "rgba(247,245,240,0.78)"
WORDMARK = "LEDGER & WHISTLE"

# --- prompt ----------------------------------------------------------------
MODEL = "fal-ai/nano-banana-pro"
MODEL_PARAMS = {"aspect_ratio": "16:9", "resolution": "2K", "num_images": 1, "output_format": "png"}
QUEUE_URL = "https://queue.fal.run/" + MODEL
POLL_SECONDS, POLL_LIMIT_SECONDS = 3, 300

HOUSE_STYLE = (
    "Editorial still-life photograph for a publication about the money in sport. "
    "One plain physical object or one empty place stands for the story, and nothing else "
    "competes with it. Low directional light from the upper right, deep soft shadows. "
    "A restrained palette: dark navy blue, warm off-white paper tones, and one small accent "
    "of muted brick red. Matte surfaces, fine film grain, shallow depth of field, eye-level "
    "medium-format camera. Quiet and exact, like a plate in a printed annual report; not "
    "glossy, not a sports poster, no lens flare, no motion blur."
)
COMPOSITION = (
    "Wide 16:9 frame. The subject sits in the right half. The left 45 percent of the frame "
    "is empty, dark, out-of-focus navy background with no objects in it."
)
RULES = (
    "The image contains no text of any kind: no letters, words, numbers, digits, captions, "
    "signage, scoreboards, labels or watermarks, and every surface that would normally carry "
    "writing is blank. No logos, no team marks, no mascots, no team colors or insignia. "
    "No people and no faces."
)
SUBJECT_BANNED_WORDS = (
    "logo", "mascot", "jersey", "uniform", "scoreboard", "banner", "sign", "signage", "newspaper",
    "headline", "lettering", "caption", "numeral", "number", "word", "text", "portrait", "crowd",
)

# --- scrim -----------------------------------------------------------------
SCRIM_RGB = NAVY
SCRIM_FLOOR = 0.25                 # every cover gets at least this much
SCRIM_CEILING = 0.96
SCRIM_STEP = 0.01
GRID = (64, 48)                    # zones are sampled down to this grid for measuring
# Luminance ceilings (0-255, gamma-encoded) after the scrim: (mean, 95th percentile).
# The scrim pulls a zone toward navy, luminance 38.6, so no ceiling can sit below that.
LEFT_TARGET = (46.0, 60)
BAND_TARGET = (50.0, 78)

# --- type ------------------------------------------------------------------
HEADLINE_LEADING = 1.62            # baseline pitch in cap heights; Georgia is set in mixed case
SUB_SIZE_RATIO = 0.36              # sub-line size relative to the headline
SUB_LEADING = 1.95
EYEBROW_SIZE_RATIO = 0.24
EYEBROW_TRACKING_RATIO = 0.035     # tracking as a fraction of the headline size
GAP_EYEBROW = 0.70                 # gaps in headline cap heights
GAP_SUB = 0.80
WORDMARK_SIZE = 15 / 630           # fractions of frame height, from the code-built covers
WORDMARK_BASELINE = 100 / 630      # low enough to clear the X-card safe zone below
# Substack's X card does not keep the whole 1200x630 cover. Matching the twitter image Substack
# served (1600x800) against our cover on October 5, 2026 showed it keeps a centered 1088x544 box,
# x 54 to 1143 and y 44 to 588 in cover pixels: about a 0.907 zoom, then a 2:1 crop. All type has
# to sit inside that box with the margin below, so inside x 94 to 1103, y 84 to 548, or measure
# and build stop. Formats without a safe_box skip the check.
X_CARD_BOX = (54, 44, 1143, 588)   # x0, y0, x1, y1 in output pixels of the 1200x630 cover
SAFE_MARGIN_PX = 40
WORDMARK_TRACKING = 2.7 / 15       # fraction of the wordmark size
SHADOW = (0.010, 0.005, 0.55)      # blur and downward offset (fractions of height), strength

# Each format: output size, where the type sits, how the scrim falls off, which zones must be dark.
# anchor is (mode, fraction of height): the headline block's center, top or bottom edge.
# scrim_x / scrim_y are (plateau, end) fractions: full strength on the plateau side, none past
# end. plateau < end fades rightward or downward; plateau > end fades the other way. None
# means the scrim doesn't vary along that axis.
# Zones are (x0, y0, x1, y1) fractions paired with their (mean, p95) luminance ceilings. When a
# piece changes headline_max_width, the "band" zone's right edge moves to the edge of the new
# headline box; an x1 of None in a piece's own zones means the same thing.
ZONE_TARGETS = {"left": LEFT_TARGET, "band": BAND_TARGET}
HEADLINE_ZONE_PAD = 0.015
TEXT_KEYS = ("headline", "sub", "eyebrow")
FORMATS = {
    "wide": {
        "out_name": "cover-fal-1200x630.png", "out_size": (1200, 630), "safe_box": X_CARD_BOX,
        "margin_x": 96 / 1200, "anchor": ("center", 0.53),
        "headline_max_width": 0.46, "headline_max_size": 0.135,
        "scrim_x": (0.30, 0.64), "scrim_y": None,
        "zones": [((0.00, 0.00, 0.40, 1.00), "left"), ((0.04, 0.24, 0.52, 0.78), "band")],
    },
    "square": {
        "out_name": "cover-fal-1080x1080.png", "out_size": (1080, 1080), "safe_box": None,
        "margin_x": 0.06, "anchor": ("top", 0.21),
        "headline_max_width": 0.66, "headline_max_size": 0.085,
        "scrim_x": (0.66, 1.00), "scrim_y": (0.44, 0.70),
        "zones": [((0.04, 0.03, 0.74, 0.46), "band")],
    },
}


def magick(*args: str, capture: bool = False) -> bytes | None:
    result = subprocess.run(["magick", *args], capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError("magick failed: %s\n%s" % (" ".join(args[:6]), result.stderr.decode()[:600]))
    return result.stdout if capture else None


def image_size(path: str) -> tuple[int, int]:
    w, h = magick(path, "-format", "%w %h", "info:", capture=True).decode().split()
    return int(w), int(h)


# --- piece -----------------------------------------------------------------

def piece_paths(piece: str) -> dict[str, str]:
    root = piece if os.path.isabs(piece) else os.path.join(REPO, piece)
    figures = os.path.join(root, "figures")
    if not os.path.isdir(root):
        sys.exit("no such piece folder: %s" % root)
    return {"root": root, "figures": figures, "name": os.path.basename(os.path.normpath(root)),
            "config": os.path.join(figures, CONFIG_NAME), "draft": os.path.join(root, "draft.md"),
            "background": os.path.join(figures, BACKGROUND_NAME),
            "record": os.path.join(figures, RECORD_NAME)}


def load_config(paths: dict[str, str]) -> dict:
    if not os.path.exists(paths["config"]):
        sys.exit("missing %s (see the docstring for its fields)" % paths["config"])
    with open(paths["config"]) as f:
        cfg = json.load(f)
    if not cfg.get("subject", "").strip():
        sys.exit("%s has no subject" % paths["config"])
    return cfg


# --- prompt ----------------------------------------------------------------

def lint_subject(subject: str) -> list[str]:
    """Reasons this subject line breaks the house rules; empty when it is clean."""
    problems = []
    if re.search(r"\d", subject):
        problems.append("contains a digit")
    if re.search(r"[\"“”‘]", subject):
        problems.append("contains quotation marks, which invite lettering")
    words = re.findall(r"[A-Za-z']+", subject.lower())
    for banned in SUBJECT_BANNED_WORDS:
        if banned in words or banned + "s" in words:
            problems.append("uses the word '%s'" % banned)
    # A capitalized word that does not open a sentence is a name: a person, a team, a school.
    for sentence in re.split(r"(?<=[.!?])\s+", subject.strip()):
        for name in re.findall(r"(?<!^)\b[A-Z][a-z]+", sentence):
            problems.append("names something ('%s'); describe it without the name" % name)
    return problems


def full_prompt(cfg: dict) -> str:
    problems = lint_subject(cfg["subject"])
    if problems:
        sys.exit("subject breaks the cover rules:\n  " + "\n  ".join(problems))
    return " ".join((HOUSE_STYLE, "Subject: " + cfg["subject"].strip(), COMPOSITION, RULES))


def fal_request(url: str, key: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, method="POST" if data else "GET",
                                     headers={"Authorization": "Key " + key,
                                              "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as err:
        raise RuntimeError("fal.ai returned HTTP %d for %s: %s"
                           % (err.code, url, err.read().decode(errors="replace")[:600])) from None


def generate(piece: str) -> None:
    paths = piece_paths(piece)
    cfg = load_config(paths)
    prompt = full_prompt(cfg)
    key = os.environ.get("FAL_KEY")
    if not key:
        sys.exit("FAL_KEY is not set")
    seed = int(cfg["seed"]) if "seed" in cfg else random.randrange(1000, 10000)
    payload = {"prompt": prompt, "seed": seed, **MODEL_PARAMS}
    submitted = fal_request(QUEUE_URL, key, payload)
    print("submitted %s, seed %d" % (submitted["request_id"], seed), flush=True)
    deadline = time.time() + POLL_LIMIT_SECONDS
    while True:
        status = fal_request(submitted["status_url"], key)["status"]
        if status == "COMPLETED":
            break
        if status not in ("IN_QUEUE", "IN_PROGRESS"):
            raise RuntimeError("fal.ai request %s ended with status %s" % (submitted["request_id"], status))
        if time.time() > deadline:
            raise RuntimeError("fal.ai request %s still %s after %ds"
                               % (submitted["request_id"], status, POLL_LIMIT_SECONDS))
        time.sleep(POLL_SECONDS)
    result = fal_request(submitted["response_url"], key)
    images = result.get("images") or []
    if not images:
        raise RuntimeError("fal.ai returned no image: %s" % json.dumps(result)[:600])
    os.makedirs(os.path.dirname(paths["background"]), exist_ok=True)
    with urllib.request.urlopen(images[0]["url"], timeout=120) as response, \
            open(paths["background"], "wb") as f:
        f.write(response.read())
    size = image_size(paths["background"])
    write_record(paths, cfg, prompt, seed, submitted["request_id"], size)
    print("wrote %s (%dx%d) and %s" % (BACKGROUND_NAME, size[0], size[1], RECORD_NAME))
    print("look at the background for stray lettering or marks before building")


def write_record(paths: dict[str, str], cfg: dict, prompt: str, seed: int, request_id: str,
                 size: tuple[int, int]) -> None:
    params = ", ".join("%s %s" % (k, v) for k, v in MODEL_PARAMS.items())
    with open(paths["record"], "w") as f:
        f.write("# Cover prompt: %s\n\n" % paths["name"])
        f.write("- Date: %s\n- Model: %s\n- Seed: %d\n- Parameters: %s\n"
                % (date.today().isoformat(), MODEL, seed, params))
        f.write("- Request: %s\n- Background: %s, %dx%d\n\n"
                % (request_id, BACKGROUND_NAME, size[0], size[1]))
        f.write("## Subject\n\n%s\n\n## Prompt as sent\n\n%s\n" % (cfg["subject"].strip(), prompt))


# --- draft -----------------------------------------------------------------

NUMBER = re.compile(r"\$?\d[\d,]*(?:\.\d+)?(?:\s?(?:million|billion|percent|M|B|K|%))?")


def normalize(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", re.sub(r"[*_`]", "", text)).lower()


def piece_format(name: str, cfg: dict) -> tuple[dict, dict]:
    """A format's settings and its overlay text, with this piece's overrides applied."""
    override = cfg.get("formats", {}).get(name, {})
    fmt = {**FORMATS[name], **{k: v for k, v in override.items() if k not in TEXT_KEYS}}
    for key in ("anchor", "scrim_x", "scrim_y"):
        fmt[key] = tuple(fmt[key]) if fmt[key] else None
    right = fmt["margin_x"] + fmt["headline_max_width"] + HEADLINE_ZONE_PAD
    follow = "headline_max_width" in override and "zones" not in override
    zones = []
    for zone in fmt["zones"]:
        box, target = (zone[:4], zone[4]) if len(zone) == 5 else zone
        x0, y0, x1, y1 = box
        if x1 is None or (follow and target == "band"):
            x1 = right
        zones.append(((x0, y0, x1, y1), ZONE_TARGETS[target]))
    fmt["zones"] = zones
    text = {key: override.get(key, cfg.get(key, "" if key == "eyebrow" else [])) for key in TEXT_KEYS}
    return fmt, text


def check_against_draft(paths: dict[str, str], cfg: dict, format_names: list[str]) -> None:
    """Stop unless every format's headline and every figure in its overlay appear in draft.md."""
    texts = [piece_format(name, cfg)[1] for name in format_names]
    headlines = sorted({" ".join(text["headline"]) for text in texts})
    lines = sorted({line for text in texts for line in text["headline"] + text["sub"] + [text["eyebrow"]]})
    if not any(lines):
        return
    if not os.path.exists(paths["draft"]):
        sys.exit("no draft.md in %s, so the cover text can't be checked against it" % paths["root"])
    with open(paths["draft"]) as f:
        draft = normalize(f.read())
    missing = []
    for headline in headlines:
        if headline and normalize(headline) not in draft:
            missing.append("headline: %s" % headline)
    for line in lines:
        for figure in NUMBER.findall(line):
            if normalize(figure) not in draft:
                missing.append("figure: %s" % figure.strip())
    if missing:
        sys.exit("cover text not found in draft.md:\n  " + "\n  ".join(missing))


# --- scrim -----------------------------------------------------------------

def falloff(t: float, plateau: float, end: float) -> float:
    """1 on the plateau side, easing to 0 at end; runs either way along the axis."""
    u = (t - plateau) / (end - plateau)
    if u <= 0.0:
        return 1.0
    if u >= 1.0:
        return 0.0
    return 1.0 - u * u * (3.0 - 2.0 * u)


def scrim_alpha(fmt: dict, x_frac: float, y_frac: float, strength: float) -> float:
    """Scrim opacity at a point, both coordinates as fractions of the frame."""
    alpha = strength
    if fmt["scrim_x"]:
        alpha *= falloff(x_frac, *fmt["scrim_x"])
    if fmt["scrim_y"]:
        alpha *= falloff(y_frac, *fmt["scrim_y"])
    return alpha


def zone_grid(path: str, size: tuple[int, int], zone: tuple) -> list[list[int]]:
    """Luminance of a zone, sampled to GRID. Returns rows of 0-255 values."""
    w, h = size
    x0, y0, x1, y1 = zone
    crop = "%dx%d+%d+%d" % (int(w * (x1 - x0)), int(h * (y1 - y0)), int(w * x0), int(h * y0))
    raw = magick(path, "-crop", crop, "+repage", "-colorspace", "Gray",
                 "-resize", "%dx%d!" % GRID, "-depth", "8", "gray:-", capture=True)
    cols, rows = GRID
    return [list(raw[r * cols:(r + 1) * cols]) for r in range(rows)]


def zone_stats(fmt: dict, grid: list[list[int]], zone: tuple, strength: float) -> tuple[float, float]:
    """(mean, p95) luminance of a zone once a scrim of this strength is laid over it."""
    x0, y0, x1, y1 = zone
    rows, cols = len(grid), len(grid[0])
    scrim_luma = 0.2126 * SCRIM_RGB[0] + 0.7152 * SCRIM_RGB[1] + 0.0722 * SCRIM_RGB[2]
    values = []
    for r, row in enumerate(grid):
        y = y0 + (y1 - y0) * (r + 0.5) / rows
        for c, v in enumerate(row):
            a = scrim_alpha(fmt, x0 + (x1 - x0) * (c + 0.5) / cols, y, strength)
            values.append(v * (1.0 - a) + scrim_luma * a)
    values.sort()
    return sum(values) / len(values), values[int(len(values) * 0.95)]


def solve_scrim(fmt: dict, path: str, size: tuple[int, int]) -> tuple:
    """Smallest scrim strength that brings every zone of the format under target.

    Returns (strength, met, before, after); before/after are lists of
    (mean, p95) pairs, one per zone.
    """
    grids = [(zone, target, zone_grid(path, size, zone)) for zone, target in fmt["zones"]]

    def stats(strength):
        return [zone_stats(fmt, grid, zone, strength) for zone, _, grid in grids]

    def meets(result):
        return all(mean <= target[0] and p95 <= target[1]
                   for (mean, p95), (_, target, _) in zip(result, grids))

    strength = SCRIM_FLOOR
    while strength < SCRIM_CEILING and not meets(stats(strength)):
        strength = round(strength + SCRIM_STEP, 4)
    return strength, meets(stats(strength)), stats(0.0), stats(strength)


def apply_scrim(fmt: dict, src: str, dst: str, strength: float, size: tuple[int, int],
                workdir: str) -> None:
    """Composite the navy gradient scrim over src at the given strength."""
    w, h = size
    across = [falloff((x + 0.5) / w, *fmt["scrim_x"]) if fmt["scrim_x"] else 1.0 for x in range(w)]
    down = [falloff((y + 0.5) / h, *fmt["scrim_y"]) if fmt["scrim_y"] else 1.0 for y in range(h)]
    rows = {}
    mask = os.path.join(workdir, "scrim-mask.pgm")
    with open(mask, "wb") as f:
        f.write(b"P5\n%d %d\n255\n" % (w, h))
        for fy in down:
            if fy not in rows:
                rows[fy] = bytes(int(round(255 * strength * fy * fx)) for fx in across)
            f.write(rows[fy])
    magick(src, "(", "-size", "%dx%d" % (w, h), "xc:rgb(%d,%d,%d)" % SCRIM_RGB, mask,
           "-alpha", "off", "-compose", "CopyOpacity", "-composite", ")",
           "-compose", "Over", "-composite", dst)


# --- type ------------------------------------------------------------------

def text_extent(font: str, size: int, tracking: float, text: str) -> tuple[int, int]:
    """(width, height) in px of the inked area of a line of text."""
    out = magick("-font", font, "-pointsize", str(size), "-kerning", str(tracking),
                 "label:" + text, "-trim", "+repage", "-format", "%w %h", "info:", capture=True)
    w, h = out.decode().split()
    return int(w), int(h)


def headline_size(fmt: dict, size: tuple[int, int], headline: list[str]) -> int:
    """The largest headline size that fits every line, up to the format's cap."""
    limit = size[0] * fmt["headline_max_width"]
    probe = 100
    widest = max(text_extent(FONT_HEADLINE, probe, 0, line)[0] for line in headline)
    return min(int(size[1] * fmt["headline_max_size"]), int(probe * limit / widest))


def type_layout(fmt: dict, size: tuple[int, int], headline_px: int, text: dict) -> dict:
    """Sizes and baseline positions for the eyebrow, headline lines and sub lines."""
    h = size[1]
    headline, sub, eyebrow = text["headline"], text["sub"], text["eyebrow"]
    cap = text_extent(FONT_HEADLINE, headline_px, 0, "H")[1]
    sub_px, eyebrow_px = int(headline_px * SUB_SIZE_RATIO), int(headline_px * EYEBROW_SIZE_RATIO)
    sub_cap = text_extent(FONT_SUPPORT, sub_px, 0, "H")[1]
    eyebrow_cap = text_extent(FONT_SUPPORT, eyebrow_px, 0, "H")[1]
    head_pitch, sub_pitch = cap * HEADLINE_LEADING, sub_cap * SUB_LEADING
    block = cap + head_pitch * (len(headline) - 1)
    if eyebrow:
        block += eyebrow_cap + cap * GAP_EYEBROW
    if sub:
        block += cap * GAP_SUB + sub_cap + sub_pitch * (len(sub) - 1)
    mode, at = fmt["anchor"]
    top = h * at - {"center": block / 2, "top": 0, "bottom": block}[mode]
    layout = {"eyebrow_px": eyebrow_px, "sub_px": sub_px, "headline": [], "sub": []}
    y = top
    if eyebrow:
        layout["eyebrow_y"] = top + eyebrow_cap
        y = layout["eyebrow_y"] + cap * GAP_EYEBROW
    y += cap
    for i in range(len(headline)):
        layout["headline"].append(y + head_pitch * i)
    y = layout["headline"][-1] + cap * GAP_SUB + sub_cap
    for i in range(len(sub)):
        layout["sub"].append(y + sub_pitch * i)
    return layout


def render_type(fmt: dict, dst: str, size: tuple[int, int], text: dict) -> None:
    """Transparent layer holding the wordmark and, when the piece has one, the headline block."""
    w, h = size
    x = int(w * fmt["margin_x"])
    wordmark_px = max(1, round(h * WORDMARK_SIZE))
    args = ["-size", "%dx%d" % (w, h), "xc:none",
            "-font", FONT_SUPPORT, "-pointsize", str(wordmark_px),
            "-kerning", str(round(wordmark_px * WORDMARK_TRACKING, 2)),
            "-fill", RED, "-annotate", "+%d+%d" % (x, round(h * WORDMARK_BASELINE)), WORDMARK]
    headline = text["headline"]
    if headline:
        headline_px = headline_size(fmt, size, headline)
        lay = type_layout(fmt, size, headline_px, text)
        if text["eyebrow"]:
            args += ["-font", FONT_SUPPORT, "-pointsize", str(lay["eyebrow_px"]),
                     "-kerning", str(round(headline_px * EYEBROW_TRACKING_RATIO, 2)), "-fill", PAPER_MUTED,
                     "-annotate", "+%d+%d" % (x, round(lay["eyebrow_y"])), text["eyebrow"]]
        args += ["-font", FONT_HEADLINE, "-pointsize", str(headline_px), "-kerning", "0", "-fill", PAPER]
        for line, y in zip(headline, lay["headline"]):
            args += ["-annotate", "+%d+%d" % (x, round(y)), line]
        args += ["-font", FONT_SUPPORT, "-pointsize", str(lay["sub_px"]), "-fill", PAPER_MUTED]
        for line, y in zip(text["sub"], lay["sub"]):
            args += ["-annotate", "+%d+%d" % (x, round(y)), line]
    magick(*args, dst)


def render_shadow(layer: str, dst: str, size: tuple[int, int]) -> None:
    """Black shadow layer shaped by the type layer's alpha."""
    blur, offset_y, strength = SHADOW
    magick(layer, "-alpha", "extract", "-blur", "0x%d" % max(1, round(size[1] * blur)),
           "-roll", "+0+%d" % round(size[1] * offset_y), "-evaluate", "multiply", str(strength),
           "(", "-size", "%dx%d" % size, "xc:black", ")", "+swap",
           "-alpha", "off", "-compose", "CopyOpacity", "-composite", dst)


def composite_type(background: str, type_layer: str, dst: str, size: tuple[int, int],
                   workdir: str) -> None:
    """Lay the type over the background with its shadow beneath it."""
    shadow = os.path.join(workdir, "shadow.png")
    render_shadow(type_layer, shadow, size)
    magick(background, shadow, "-compose", "Over", "-composite", type_layer, "-composite", dst)


# --- commands --------------------------------------------------------------

def safe_zone(fmt: dict, size: tuple[int, int]) -> tuple[int, int, int, int] | None:
    """(x0, y0, x1, y1) in source pixels of the format's safe box inset by the margin, or None
    when the format has no safe box. The box is given in output pixels and scaled to the source."""
    if not fmt.get("safe_box"):
        return None
    sx, sy = size[0] / fmt["out_size"][0], size[1] / fmt["out_size"][1]
    x0, y0, x1, y1 = fmt["safe_box"]
    return (round((x0 + SAFE_MARGIN_PX) * sx), round((y0 + SAFE_MARGIN_PX) * sy),
            round((x1 - SAFE_MARGIN_PX) * sx), round((y1 - SAFE_MARGIN_PX) * sy))


def type_bounds(layer: str) -> tuple[int, int, int, int]:
    """(x0, y0, x1, y1) of the inked type on a transparent layer."""
    out = magick(layer, "-trim", "-format", "%w %h %X %Y", "info:", capture=True).decode().split()
    bw, bh, bx, by = (int(float(v)) for v in out)
    return bx, by, bx + bw, by + bh


def describe(name: str, strength: float, met: bool, before: list, after: list) -> str:
    zones = "   ".join("%5.1f/%3.0f -> %5.1f/%3.0f" % (b + a) for b, a in zip(before, after))
    return "%-8s scrim %.2f   %s   %s" % (name, strength, zones, "ok" if met else "TARGET NOT MET")


def wordmark_stats(fmt: dict, path: str, size: tuple[int, int], strength: float) -> tuple[float, float]:
    """(mean, p95) luminance behind the wordmark once the scrim is on."""
    zone = (fmt["margin_x"], WORDMARK_BASELINE - 0.04, fmt["margin_x"] + 0.34, WORDMARK_BASELINE + 0.02)
    return zone_stats(fmt, zone_grid(path, size, zone), zone, strength)


def prepare_source(fmt: dict, src: str, cfg: dict, workdir: str) -> str:
    """The background cropped to the format's shape: 1200:630 from the middle, or a square."""
    w, h = image_size(src)
    out_w, out_h = fmt["out_size"]
    cropped = os.path.join(workdir, "cropped.png")
    if out_w == out_h:
        left = min(int(w * cfg.get("square_crop_x", 0.40)), w - h)
        crop = "%dx%d+%d+0" % (h, h, left)
    else:
        crop_h = min(h, int(w * out_h / out_w))
        crop_w = min(w, int(crop_h * out_w / out_h))
        crop = "%dx%d+%d+%d" % (crop_w, crop_h, (w - crop_w) // 2, (h - crop_h) // 2)
    magick(src, "-crop", crop, "+repage", cropped)
    return cropped


def build(piece: str, format_names: list[str], measure_only: bool = False) -> None:
    paths = piece_paths(piece)
    cfg = load_config(paths)
    if not os.path.exists(paths["background"]):
        sys.exit("no background at %s; run generate first" % paths["background"])
    format_names = [n for n in format_names if not cfg.get("formats", {}).get(n, {}).get("skip")]
    if not measure_only:
        check_against_draft(paths, cfg, format_names)
    print("%s: zone figures are mean/p95 luminance (0-255), before -> after scrim" % paths["name"])
    for name in format_names:
        fmt, text = piece_format(name, cfg)
        with tempfile.TemporaryDirectory() as work:
            background = prepare_source(fmt, paths["background"], cfg, work)
            size = image_size(background)
            strength, met, before, after = solve_scrim(fmt, background, size)
            print(describe(name, strength, met, before, after), flush=True)
            mean, p95 = wordmark_stats(fmt, background, size, strength)
            print("%-8s behind the wordmark %5.1f/%3.0f   %s"
                  % ("", mean, p95, "ok" if p95 <= BAND_TARGET[1] else "TOO BRIGHT"), flush=True)
            layer = os.path.join(work, "type.png")
            render_type(fmt, layer, size, text)
            zone = safe_zone(fmt, size)
            if zone:
                bx0, by0, bx1, by1 = type_bounds(layer)
                zx0, zy0, zx1, zy1 = zone
                scale = fmt["out_size"][0] / size[0]
                inside = bx0 >= zx0 and by0 >= zy0 and bx1 <= zx1 and by1 <= zy1
                ox0, oy0, ox1, oy1 = fmt["safe_box"]
                print("%-8s type %d,%d to %d,%d in the X-card safe zone %d,%d to %d,%d (output px)   %s"
                      % ("", bx0 * scale, by0 * scale, bx1 * scale, by1 * scale,
                         ox0 + SAFE_MARGIN_PX, oy0 + SAFE_MARGIN_PX, ox1 - SAFE_MARGIN_PX, oy1 - SAFE_MARGIN_PX,
                         "ok" if inside else "TYPE OUTSIDE THE SAFE ZONE"), flush=True)
                if not inside:
                    sys.exit("%s: type falls outside the X-card safe zone; move or shrink it before building" % name)
            if measure_only:
                continue
            scrimmed, composed = os.path.join(work, "scrimmed.png"), os.path.join(work, "composed.png")
            apply_scrim(fmt, background, scrimmed, strength, size, work)
            composite_type(scrimmed, layer, composed, size, work)
            final = os.path.join(paths["figures"], fmt["out_name"])
            magick(composed, "-resize", "%dx%d!" % fmt["out_size"], "-strip", "-depth", "8", final)
            print("wrote", final)


def main(argv: list[str]) -> None:
    if len(argv) < 2 or argv[0] not in ("prompt", "generate", "build", "measure"):
        sys.exit(__doc__)
    command, piece, rest = argv[0], argv[1], argv[2:]
    if any(name not in FORMATS for name in rest) or (rest and command in ("prompt", "generate")):
        sys.exit(__doc__)
    if command == "prompt":
        print(full_prompt(load_config(piece_paths(piece))))
    elif command == "generate":
        generate(piece)
    else:
        build(piece, rest or list(FORMATS), measure_only=(command == "measure"))


if __name__ == "__main__":
    main(sys.argv[1:])
