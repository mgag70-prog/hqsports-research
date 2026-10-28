#!/usr/bin/env python3
"""Ledger & Whistle masthead banner for Substack email headers.

Three concepts, one fal.ai nano-banana-pro background each at 21:9 (the widest ratio Pro
completes; see notes/the-ledger/header/README.md), cropped full-width to 5:1, then the house
navy scrim and type from tools/compose_cover.py. B4 is the exception: a 4:3 still life scaled
onto the right of the banner over navy matched to its cloth (composite_to_banner). The model never draws a letter: the wordmark,
rule and tagline are set here in Georgia, the house serif. Every banner carries the tagline (the
no-tagline variants were dropped on October 28, 2026).

Usage, from the repo root:
  python3 brand/email-header/build_header.py prompt [A B B2 B3 B4 B5 C]      # print the prompts, send nothing
  python3 brand/email-header/build_header.py generate [A B B2 B3 B4 B5 C]    # call fal.ai (FAL_KEY from env)
  python3 brand/email-header/build_header.py build [A B B2 B3 B4 B5 C]       # scrim, type, checks, PNGs
  python3 brand/email-header/build_header.py sheet               # contact sheet of the built options

Writes, next to this script:
  raw/option-X-background.png            the image as fal.ai returned it
  raw/option-X-request.json              seed, request id, size, date, cost, prompt
  option-X-1100x220.png                  the header, with tagline
  option-X-2200x440.png                  the same at 2x
  option-X-550-preview.png               the 1100 header shown at 550 wide, as many email clients do
  checks.json, contact-sheet.png
"""
import base64
import hashlib
import json
import os
import sys
import tempfile
import time
import urllib.request
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools"))
import compose_cover as cc  # noqa: E402  house scrim, shadow, magick and fal.ai helpers

RAW = os.path.join(HERE, "raw")
MODEL_PARAMS = {"aspect_ratio": "21:9", "resolution": "2K", "num_images": 1, "output_format": "png"}
COST_PER_IMAGE = 0.15          # fal.ai list price for nano-banana-pro below 4K, October 2026

STYLE = (
    "Dark, cinematic, editorial photograph for a publication about the money in sport. "
    "Fine film grain, matte surfaces, a restrained palette of deep navy blue and warm amber light "
    "with small accents of brick red. Quiet and exact, not a sports poster, no lens flare."
)
COMPOSITION = (
    "Composition: a wide 21:9 frame that will be cropped to a thin 5:1 banner through its vertical "
    "middle, so the subject sits inside the middle third of the frame height. The interest sits in "
    "the right 45 percent of the frame width. The left 55 percent is darker and calmer: deep navy "
    "shadow with low, even detail and no bright spots, so type can sit over it."
)
RULES = (
    "The image contains no text of any kind: no letters, words, numbers, digits, dates, captions, "
    "signage, labels or watermarks, and every surface that would normally carry writing is blank. "
    "No logos, no brand names, no team marks, insignia or mascots, and no team colors: nothing that "
    "identifies a team, league or maker. No people and no faces."
)

SUBJECTS = {
    "A": (
        "Subject: a large open-air stadium at night seen from high above, almost straight down at a "
        "steep angle, the floodlights blazing on tall masts and throwing pools of warm light onto a "
        "plain green grass field with no painted lines, markings, numbers or logos on it. The stands "
        "are rows of empty seats in neutral charcoal grey. Every video board and scoreboard is switched "
        "off and blank black. Laid over the whole scene, as if the photograph were printed on an "
        "accountant's ledger paper, is a faint grid of thin, evenly spaced pale ruled lines, horizontal "
        "rows crossed by a few vertical column lines, very subtle, like the ruling of a ledger sheet. "
        "The stadium sits in the right part of the frame; the left part is the dark city at night "
        "around it, out of focus, with the ruled grid continuing faintly across it."
    ),
    "B": (
        "Subject: a still life on a dark navy surface. A plain chrome referee's whistle on a black "
        "lanyard lies beside an American football, a baseball and a basketball, grouped together. The "
        "balls are plain: natural brown leather with white laces, white leather with red stitching, "
        "and orange pebbled leather with black seams, with no printing, stamps or brand marks on any "
        "of them. Under and around them lie the edges of a few sheets of accounting paper, pale green "
        "with thin ruled green and red column lines and nothing written on them. Low, warm light "
        "comes from the right, leaving long soft shadows toward the left."
    ),
    "C": (
        "Subject: an extreme close-up macro of an old stadium scoreboard's bulb matrix: a dense, regular "
        "grid of small round incandescent bulbs in black sockets on a dark panel, almost all of them "
        "unlit and dark. A handful of bulbs, scattered irregularly at random positions on the right "
        "side, glow warm red; together they form no letter, no digit, no symbol and no shape. Shallow "
        "depth of field: the grid falls out of focus toward the left. Beyond the panel, at the top "
        "right, the soft haze of a stadium floodlight glows in the night air."
    ),
}

# crop_y: top of the full-width 5:1 window, as a fraction of the spare height.
# scrim_x: navy scrim at full strength from the left edge to the first fraction, gone by the second.
OPTIONS = {
    "A": {"seed": 6101, "crop_y": 0.25, "scrim_x": (0.54, 0.80)},   # the stands start under "WHISTLE"
    "B": {"seed": 6201, "crop_y": 0.72, "scrim_x": (0.48, 0.76)},   # low enough to keep the whistle
    "C": {"seed": 6301, "crop_y": 0.35, "scrim_x": (0.48, 0.76)},
}
# B2 is not generated from text: it is option B's background edited in place (see EDITS).
# Seed 6202 was rejected: the football did not move and the paper squiggle became glyph-like.
OPTIONS["B2"] = {"seed": 6203, "crop_y": 0.78, "scrim_x": (0.48, 0.76), "edit_of": "B"}
# B3 is a fresh generation with B's look, laid out for the 5:1 band (see SUBJECTS_B3 below).
# Earlier B3 prompts (seeds 6211, 6212) were rejected: the group ran 57 to 64 percent of the frame
# height, too tall for 5:1. This is the second B3 brief, laid out by position in the frame.
# Seed 6221 was rejected: the group ran from 4 to 78 percent of the height, and a brass lamp base
# appeared at the right edge.
OPTIONS["B3"] = {"seed": 6222, "crop_y": 0.56, "scrim_x": (0.48, 0.76)}
# B4 is composited, not cropped: a 4:3 still life is scaled to fit the banner height and placed on
# the right over plain navy matched to its cloth (see composite_to_banner). "group" is the box around
# the balls and whistle as fractions of the source, measured by eye from the returned image.
OPTIONS["B4"] = {"seed": 6231, "params": {"aspect_ratio": "4:3"}, "composite": True,
                 "group": (0.17, 0.18, 0.785, 0.85), "scrim_x": (0.48, 0.76)}
# B5 is B4's still life placed differently, in code only: the group 210px tall at 1x (5px clear top
# and bottom) and its left edge 125px right of the tagline's end, 40px clear of the wordmark (x 625).
OPTIONS["B5"] = {**OPTIONS["B4"], "source": "B4", "group_margin": 5, "gap_after_tagline": 125}
OPTIONS = {k: OPTIONS[k] for k in ("A", "B", "B2", "B3", "B4", "B5", "C")}  # contact-sheet order

EDIT_MODEL = "fal-ai/nano-banana-pro/edit"
EDIT_SOURCE_QUALITY = 95       # the source goes up as a JPEG data URI; the 7.5 MB PNG is too big to inline
EDITS = {
    "B2": (
        "Edit this photograph. Keep the lighting from the right, the dark navy cloth, the colors, the "
        "film grain, the camera angle, the basketball, the baseball and the dark, calm, empty left side "
        "of the frame exactly as they are. Make these changes. "
        "1. Take the American football away from where it lies now, above and behind the baseball, and "
        "put it down lower on the cloth, to the LEFT of the baseball, at the same height in the frame "
        "as the baseball, lying on its side with its plain white laces on top. The whole football is in "
        "view. It touches or nearly touches the baseball, the same small distance from the baseball as "
        "the basketball is on the other side, so the three balls sit in a tight row: football, baseball, "
        "basketball, reading clearly as one group in the middle band of the frame. Where the football "
        "used to be, show the pale accounting paper and dark cloth behind it. "
        "2. Move the chrome referee's whistle down and to the right so it rests near the bottom of the "
        "frame, on or just at the edge of the pale green ruled accounting paper with green and red "
        "column lines; its black lanyard trails from it naturally across the cloth. "
        "The accounting paper carries only ruled lines: remove any marks, scribbles or characters from "
        "it. The football is plain brown leather with plain white laces and no other markings. "
        "The image contains no text of any kind: no letters, words, numbers, digits, labels or "
        "watermarks, no logos, brand names, stamps or printing on any ball, and nothing written on the "
        "paper. No people and no faces."
    ),
}


def edit_source(letter: str) -> str:
    return os.path.join(RAW, "option-%s-background.png" % OPTIONS[letter]["edit_of"])


SUBJECTS["B3"] = (
    "Subject: a still life on a dark navy cloth, lit by low, warm light from the right that leaves "
    "soft shadows toward the left; the football and the basketball may fall partly into shadow, but "
    "their shapes read clearly. Three balls sit in a row at exactly the same level on the cloth: an "
    "American football on the left, lying on its side with its long axis horizontal and its pointed "
    "nose aimed at the baseball and nearly touching it, plain brown leather with plain white laces; a "
    "baseball in the middle, white leather with red stitching; and a basketball on the right, orange "
    "pebbled leather with black seams, just touching the baseball. A few sheets of pale green "
    "accounting paper, ruled with thin green and red column lines, lie at the lower right, and a plain "
    "chrome referee's whistle on a black lanyard rests on the ruled paper below and in front of the "
    "baseball, the whole whistle in view. The paper carries only ruled lines: no handwriting, script, "
    "scribbles, stamps or marks."
)
SUBJECTS["B4"] = (
    "Subject: a still life on a dark navy cloth, lit by low, warm light from the right that leaves "
    "soft shadows toward the left. Three balls sit in a row at exactly the same level on the cloth, all "
    "three whole: an American football on the left, lying on its side with its pointed nose nearly "
    "touching the baseball, plain brown leather with plain white laces; a baseball in the middle, white "
    "leather with red stitching; and a basketball on the right, orange pebbled leather with black "
    "seams, just touching the baseball on the other side. A few sheets of pale green accounting paper, "
    "ruled with thin green and red column lines, lie at the lower right, and a plain chrome referee's "
    "whistle on a black lanyard rests on the paper below and in front of the baseball, the whole "
    "whistle in view. The paper carries only ruled lines: no handwriting, script, scribbles, stamps or "
    "marks."
)
COMPOSITION_BY = {
    "B4": (
        "Composition: a 4:3 frame, camera low and nearly level. The group of balls, paper and whistle "
        "sits in the middle of the frame with a clear margin of plain dark navy cloth on every side of it: "
        "nothing touches or is cut by any edge of the frame. The cloth fills the whole background, "
        "evenly lit, with no other objects: no lamp, no trophy, no stand, no furniture."
    ),
    "B3": (
        "Composition: a wide 21:9 frame, shot from far away with a long lens and a low, nearly level "
        "camera, so the objects look small, as in a wide establishing shot of a tabletop, and line up "
        "side by side. The objects together form a thin horizontal strip across the middle of the frame, "
        "about five times wider than it is tall. The frame will be cropped "
        "to a thin 5:1 banner through its exact vertical middle, so every object sits inside the middle "
        "45 percent of the frame height: the top of the basketball is below the 30 percent line from the "
        "top of the frame and the bottom of the whistle is above the 70 percent line, with plain dark "
        "cloth filling the top 30 percent and the bottom 30 percent of the frame. The basketball, the "
        "largest object, is about one quarter of the frame height across. All the objects and the paper "
        "sit in the right 45 percent of the frame width. Nothing is cut off by the frame. The left 55 "
        "percent of the frame is plain, dark, calm navy cloth with no objects, no bright spots and no "
        "detail, so type can sit over it. There are no other objects in the scene: no lamp, no trophy, "
        "no stand, no furniture."
    ),
}


def prompt_for(letter: str) -> str:
    if letter in EDITS:
        return EDITS[letter]
    return " ".join((STYLE, SUBJECTS[letter], COMPOSITION_BY.get(letter, COMPOSITION), RULES))


# --- frame and type, in 1x pixels (everything is drawn at 2x) -----------------------------------
OUT = (1100, 220)
SCALE = 2
PAD = 40                       # minimum clear space to the left, top and bottom of the inked type
MARGIN_X = 48
WORDMARK = cc.WORDMARK         # "LEDGER & WHISTLE"
AMP = "&"
TAGLINE = "The business of sports, by the numbers."
TITLE_CAP = 50                 # cap height target; the width limit below wins
TITLE_TRACKING = 0.03          # em
TITLE_MAX_W = 0.53             # the wordmark may not run past this fraction of the width
TAGLINE_PX = 26               # 13px type at 550 wide
GAP_RULE = 16                  # wordmark baseline to rule top
RULE = (72, 3)                 # length, thickness
GAP_TAGLINE = 15               # rule bottom to tagline cap top
TAGLINE_FILL = cc.PAPER_MUTED  # as the covers' sub-line
TYPE_BAND_PAD = 12             # the type-band zone is the ink box grown by this much

VARIANTS = {"": True}                      # file suffix: with tagline? (no-tagline variants dropped October 28)
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
        if OPTIONS[letter].get("source"):
            sys.exit("%s reuses option %s's background; nothing to generate" % (letter, OPTIONS[letter]["source"]))
        seed, prompt = OPTIONS[letter]["seed"], prompt_for(letter)
        params = {**MODEL_PARAMS, **OPTIONS[letter].get("params", {})}
        payload, model, extra = {"prompt": prompt, "seed": seed, **params}, cc.MODEL, {}
        if letter in EDITS:
            src = edit_source(letter)
            jpg = cc.magick(src, "-quality", str(EDIT_SOURCE_QUALITY), "jpeg:-", capture=True)
            payload["image_urls"] = ["data:image/jpeg;base64," + base64.b64encode(jpg).decode()]
            model = EDIT_MODEL
            with open(src, "rb") as f:
                extra = {"source": os.path.relpath(src, HERE), "source_md5": hashlib.md5(f.read()).hexdigest(),
                         "source_sent_as": "JPEG q%d data URI, %d bytes" % (EDIT_SOURCE_QUALITY, len(jpg))}
        submitted = cc.fal_request("https://queue.fal.run/" + model, key, payload)
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
            json.dump({"letter": letter, "seed": seed, "request_id": rid, "model": model,
                       "params": params, "size": size, "date": date.today().isoformat(),
                       "cost_usd": COST_PER_IMAGE, **extra, "prompt": prompt}, f, indent=1)
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


GROUP_MARGIN = 20              # 1x clear space above and below the composited group
EDGE_SAMPLE = 24               # 2x columns at the still life's left edge that set the navy fill, row by row
FADE_GAP = 16                  # 2x: the fade ends this far short of the group's left edge


def smooth(u: float) -> float:
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def column_lum(path: str, x: int, y: int, w: int, h: int) -> list[float]:
    """Mean luminance (0-255) of each column of a box."""
    out = cc.magick(path, "-crop", "%dx%d+%d+%d" % (w, h, x, y), "+repage", "-colorspace", "Gray",
                    "-scale", "%dx1!" % w, "-depth", "16", "-endian", "MSB", "gray:-", capture=True)
    return [int.from_bytes(out[i:i + 2], "big") / 257 for i in range(0, len(out), 2)]


def max_step(values: list[float]) -> float:
    return round(max(abs(a - b) for a, b in zip(values, values[1:])), 2)


def composite_to_banner(src: str, dst: str, opt: dict, work: str, tagline_right: int) -> dict:
    """Place a still life on the right of the 2x banner over navy matched to its own cloth.

    The source is scaled so the group box is the banner height less the option's margin (default
    GROUP_MARGIN) top and bottom. By default it is set flush right; with "gap_after_tagline" the
    group's left edge sits that many 1x pixels right of the tagline's end. The canvas is filled row by
    row with the mean colour of the still life's left edge (and, when its right edge falls inside the
    banner, its right edge on that side), and the still life fades in from transparent at each edge
    inside the banner to opaque short of the group, so at an edge the two are the same pixels and
    there is nothing to make a seam."""
    W, H = OUT[0] * SCALE, OUT[1] * SCALE
    w, h = cc.image_size(src)
    gx0, gy0, gx1, gy1 = opt["group"]
    margin = opt.get("group_margin", GROUP_MARGIN)
    s = (H - 2 * px(margin)) / ((gy1 - gy0) * h)
    sw, sh = int(round(w * s)), int(round(h * s))
    if opt.get("gap_after_tagline") is None:
        ox = W - sw                                        # flush right: no right-hand edge to hide
    else:
        ox = tagline_right + px(opt["gap_after_tagline"]) - int(round(gx0 * sw))
    oy = int(round(H / 2 - s * h * (gy0 + gy1) / 2))       # group centred vertically
    group = (round(ox + gx0 * sw), round(oy + gy0 * sh), round(ox + gx1 * sw), round(oy + gy1 * sh))
    info = {"scale": round(s, 4), "placed": (ox, oy, sw, sh), "group_2x": group,
            "group_height_1x": round((group[3] - group[1]) / SCALE, 1),
            "tagline_right_2x": tagline_right, "gap_after_tagline_1x": round((group[0] - tagline_right) / SCALE, 1)}
    info["covers_height"] = oy <= 0 and oy + sh >= H
    min_left = W * 0.55 if opt.get("gap_after_tagline") is None else tagline_right
    info["group_inside"] = (group[1] >= px(margin) - 1 and group[3] <= H - px(margin) + 1
                            and group[0] >= min_left and group[2] <= W)
    right_inside = ox + sw < W
    scaled = os.path.join(work, "still.png")
    cc.magick(src, "-filter", "Lanczos", "-resize", "%dx%d!" % (sw, sh), "-depth", "8", scaled)

    # navy fill: per-row mean of the still life's edge columns, cropped to the banner rows, lightly smoothed
    fill = os.path.join(work, "fill.png")
    cc.magick(scaled, "-crop", "%dx%d+0+%d" % (EDGE_SAMPLE, H, -oy), "+repage", "-scale", "1x%d!" % H,
              "-blur", "0x6", "-scale", "%dx%d!" % (W, H), fill)
    if right_inside:
        rfill = os.path.join(work, "fill-right.png")
        split = ox + sw // 2                               # under the opaque middle of the photo
        cc.magick(scaled, "-crop", "%dx%d+%d+%d" % (EDGE_SAMPLE, H, sw - EDGE_SAMPLE, -oy), "+repage",
                  "-scale", "1x%d!" % H, "-blur", "0x6", "-scale", "%dx%d!" % (W - split, H), rfill)
        cc.magick(fill, rfill, "-geometry", "+%d+0" % split, "-compose", "Copy", "-composite", fill)

    # alpha mask over the scaled still life: 0 at each edge inside the banner, smoothstep to 1 short of the group
    fade_end = max(1, int(round(gx0 * sw)) - FADE_GAP)
    info["fade_2x"] = (ox, ox + fade_end)
    if right_inside:
        rstart = int(round(gx1 * sw)) + FADE_GAP
        info["fade_right_2x"] = (ox + rstart, ox + sw)
        row = bytes(int(round(255 * smooth(x / fade_end) * smooth((sw - x) / (sw - rstart)))) for x in range(sw))
    else:
        row = bytes(int(round(255 * smooth(x / fade_end))) for x in range(sw))
    mask = os.path.join(work, "fade.pgm")
    with open(mask, "wb") as f:
        f.write(b"P5\n%d %d\n255\n" % (sw, sh) + row * sh)
    placed = os.path.join(work, "placed.png")
    cc.magick(scaled, mask, "-alpha", "off", "-compose", "CopyOpacity", "-composite", placed)
    cc.magick(fill, placed, "-geometry", "%+d%+d" % (ox, oy), "-compose", "Over", "-composite",
              "-depth", "8", dst)

    # seam check: column-mean luminance across each fade, largest step between neighbouring columns,
    # set against the same statistic in the photograph's own cloth over the same columns, unblended
    lo = max(0, ox - 60)
    info["seam_max_step"] = max_step(column_lum(dst, lo, 0, ox + fade_end - lo, H))
    info["cloth_max_step"] = max_step(column_lum(scaled, 0, -oy, fade_end, H))
    ok = info["seam_max_step"] <= max(1.0, 2 * info["cloth_max_step"])
    if right_inside:
        hi = min(W, ox + sw + 60)
        info["seam_right_max_step"] = max_step(column_lum(dst, ox + rstart, 0, hi - ox - rstart, H))
        info["cloth_right_max_step"] = max_step(column_lum(scaled, rstart, -oy, sw - rstart, H))
        ok = ok and info["seam_right_max_step"] <= max(1.0, 2 * info["cloth_right_max_step"])
    info["seam_ok"] = ok
    return info


def type_layout(tagline: bool) -> dict:
    """Pixel positions (2x) of every element, the block centred vertically in the frame."""
    probe = 100
    probe_cap = cc.text_extent(cc.FONT_HEADLINE, probe, 0, "H")[1]
    title_px = int(round(probe * px(TITLE_CAP) / probe_cap))
    tracking = round(title_px * TITLE_TRACKING, 2)
    title_w = cc.text_extent(cc.FONT_HEADLINE, title_px, tracking, WORDMARK)[0]
    limit = OUT[0] * SCALE * TITLE_MAX_W - px(MARGIN_X)
    if title_w > limit:
        title_px = int(title_px * limit / title_w)
        tracking = round(title_px * TITLE_TRACKING, 2)
        title_w = cc.text_extent(cc.FONT_HEADLINE, title_px, tracking, WORDMARK)[0]
    title_cap = cc.text_extent(cc.FONT_HEADLINE, title_px, 0, "H")[1]
    tag_px = px(TAGLINE_PX)
    tag_cap = cc.text_extent(cc.FONT_SUPPORT, tag_px, 0, "H")[1]
    block = title_cap + px(GAP_RULE) + px(RULE[1])
    if tagline:
        block += px(GAP_TAGLINE) + tag_cap
    top = (OUT[1] * SCALE - block) / 2 - (px(2) if tagline else 0)   # tagline descenders sit below
    lay = {"x": px(MARGIN_X), "title_px": title_px, "title_tracking": tracking, "title_w": title_w,
           "title_cap": title_cap, "tag_px": tag_px, "tag_cap": tag_cap, "tagline": tagline}
    lay["title_y"] = top + title_cap
    lay["rule_y"] = lay["title_y"] + px(GAP_RULE)
    lay["tag_y"] = lay["rule_y"] + px(RULE[1]) + px(GAP_TAGLINE) + tag_cap
    return lay


def text_args(lay: dict, text: str, fill: str) -> list[str]:
    return ["-font", cc.FONT_HEADLINE, "-pointsize", str(lay["title_px"]),
            "-kerning", str(lay["title_tracking"]), "-fill", fill,
            "-annotate", "+%d+%d" % (lay["x"], round(lay["title_y"])), text]


def render(dst: str, size: tuple[int, int], parts: list[list[str]]) -> None:
    cc.magick("-size", "%dx%d" % size, "xc:none", *[a for p in parts for a in p], dst)


def first_ink_after(layer: str, x: int, size: tuple[int, int]) -> int:
    """First inked column of a type layer at or right of x."""
    w = size[0] - x
    out = cc.magick(layer, "-crop", "%dx%d+%d+0" % (w, size[1], x), "+repage", "-trim",
                    "-format", "%X", "info:", capture=True).decode()
    return x + int(float(out))


def amp_columns(lay: dict, size: tuple[int, int], work: str) -> tuple[int, int]:
    """Columns [x0, x1) of the "&" in the set wordmark.

    The wordmark is set once; the "&" is recoloured in place, so kerning and spacing are exactly
    those of the single line. Its columns come from setting the prefixes "LEDGER" and "LEDGER &"
    at the same origin: glyphs are laid left to right, so each prefix inks exactly the columns it
    inks in the full line. The cut sits halfway across each word space."""
    head, _, tail = WORDMARK.partition(" " + AMP + " ")
    edges = []
    for text in (head, head + " " + AMP, WORDMARK):
        p = os.path.join(work, "probe.png")
        render(p, size, [text_args(lay, text, "white")])
        edges.append(cc.type_bounds(p))
    r_right, amp_right = edges[0][2], edges[1][2]
    # first inked column of "WHISTLE": set the full line, blank everything up to the "&" edge
    p = os.path.join(work, "probe.png")
    render(p, size, [text_args(lay, WORDMARK, "white")])
    w_left = first_ink_after(p, amp_right, size)
    # first inked column of "&": set "LEDGER &", look past the end of "LEDGER"
    render(p, size, [text_args(lay, head + " " + AMP, "white")])
    a_left = first_ink_after(p, r_right, size)
    return (r_right + a_left) // 2, (amp_right + w_left) // 2


def element_layers(lay: dict, size: tuple[int, int], work: str) -> dict[str, str]:
    """One transparent PNG per element, so each can be measured alone and then stacked."""
    a0, a1 = amp_columns(lay, size, work)
    paper = os.path.join(work, "wm-paper.png")
    red = os.path.join(work, "wm-red.png")
    render(paper, size, [text_args(lay, WORDMARK, cc.PAPER)])
    render(red, size, [text_args(lay, WORDMARK, cc.RED)])
    layers = {"wordmark": os.path.join(work, "el-wordmark.png"), "amp": os.path.join(work, "el-amp.png"),
              "rule": os.path.join(work, "el-rule.png")}
    cut = ["(", "-size", "%dx%d" % size, "xc:none", "-fill", "white",
           "-draw", "rectangle %d,0 %d,%d" % (a0, a1 - 1, size[1]), ")"]
    cc.magick(paper, *cut, "-compose", "DstOut", "-composite", layers["wordmark"])
    cc.magick(red, *cut, "-compose", "DstIn", "-composite", layers["amp"])
    x = lay["x"]
    render(layers["rule"], size, [["-fill", cc.RED, "-draw", "rectangle %d,%d %d,%d" % (
        x, round(lay["rule_y"]), x + px(RULE[0]) - 1, round(lay["rule_y"]) + px(RULE[1]) - 1)]])
    if lay["tagline"]:
        layers["tagline"] = os.path.join(work, "el-tagline.png")
        render(layers["tagline"], size, [["-font", cc.FONT_SUPPORT, "-pointsize", str(lay["tag_px"]),
                                          "-kerning", "0", "-fill", TAGLINE_FILL, "-annotate",
                                          "+%d+%d" % (x, round(lay["tag_y"])), TAGLINE]])
    return layers


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
        fg_l = rel_lum(fill) * alpha + bg_l * (1 - alpha)     # text at alpha, blended in linear light
        hi, lo = max(fg_l, bg_l), min(fg_l, bg_l)
        out.append((hi + 0.05) / (lo + 0.05))
    return out[0], out[1]


FILLS = {"wordmark": (hex_rgb(cc.PAPER), 1.0), "amp": (hex_rgb(cc.RED), 1.0),
         "rule": (hex_rgb(cc.RED), 1.0), "tagline": (hex_rgb(cc.PAPER), 0.78)}


def build_one(letter: str, suffix: str, tagline: bool, src: str) -> dict:
    lay = type_layout(tagline)
    size = (OUT[0] * SCALE, OUT[1] * SCALE)
    r = {"name": letter + suffix, "layout_2x": lay}
    with tempfile.TemporaryDirectory() as work:
        layers = element_layers(lay, size, work)
        layer = os.path.join(work, "type.png")
        cc.magick(*layers.values(), "-background", "none", "-compose", "Over", "-flatten", layer)
        x0, y0, x1, y1 = cc.type_bounds(layer)
        r["ink_1x"] = tuple(round(v / SCALE, 1) for v in (x0, y0, x1, y1))
        r["pad_1x"] = (round(x0 / SCALE, 1), round(y0 / SCALE, 1),
                       round(OUT[0] - x1 / SCALE, 1), round(OUT[1] - y1 / SCALE, 1))
        r["pad_ok"] = min(r["pad_1x"][0], r["pad_1x"][1], r["pad_1x"][3]) >= PAD
        r["right_frac"] = round(x1 / size[0], 3)
        r["inside_left_55"] = r["right_frac"] <= 0.55
        g = TYPE_BAND_PAD * SCALE
        band = (max(0, x0 - g) / size[0], max(0, y0 - g) / size[1],
                min(size[0], x1 + g) / size[0], min(size[1], y1 + g) / size[1])
        r["type_band"] = tuple(round(v, 3) for v in band)
        fmt = {"scrim_x": OPTIONS[letter]["scrim_x"], "scrim_y": None,
               "zones": [((0.00, 0.00, 0.55, 1.00), cc.BAND_TARGET), (band, cc.BAND_TARGET)]}

        bg = os.path.join(work, "crop.png")
        if OPTIONS[letter].get("composite"):
            r["composite"] = composite_to_banner(src, bg, OPTIONS[letter], work,
                                                 cc.type_bounds(layers["tagline"])[2])
        else:
            crop_to_5x1(src, bg, OPTIONS[letter]["crop_y"])
        strength, met, before, after = cc.solve_scrim(fmt, bg, size)
        r.update(strength=strength, met=met, before=before, after=after)
        scrimmed = os.path.join(work, "scrimmed.png")
        cc.apply_scrim(fmt, bg, scrimmed, strength, size, work)

        r["contrast"] = {name: contrast_under(scrimmed, path, *FILLS[name], work)
                         for name, path in layers.items()}
        composed = os.path.join(work, "composed.png")
        cc.composite_type(scrimmed, layer, composed, size, work)
        stem = os.path.join(HERE, "option-%s%s" % (letter, suffix))
        out2, out1, prev = stem + "-2200x440.png", stem + "-1100x220.png", stem + "-550-preview.png"
        cc.magick(composed, "-strip", "-depth", "8", out2)
        cc.magick(composed, "-filter", "Lanczos", "-resize", "%dx%d!" % OUT, "-strip", "-depth", "8", out1)
        cc.magick(out1, "-filter", "Lanczos", "-resize", "550x110!", "-strip", "-depth", "8", prev)
        r["sizes"] = [cc.image_size(p) for p in (out1, out2, prev)]
        r["sizes_ok"] = r["sizes"] == [OUT, (OUT[0] * 2, OUT[1] * 2), (550, 110)]
    # at 550 wide the 2x drawing is shown at a quarter of its pixel size
    r["at_550"] = {"wordmark_cap": round(lay["title_cap"] / 4, 1), "wordmark_px": round(lay["title_px"] / 4, 1),
                   "tagline_cap": round(lay["tag_cap"] / 4, 1) if tagline else None,
                   "tagline_px": round(lay["tag_px"] / 4, 1) if tagline else None}
    report(r)
    return r


def build(letters: list[str]) -> list[dict]:
    results = []
    for letter in letters:
        src = os.path.join(RAW, "option-%s-background.png" % OPTIONS[letter].get("source", letter))
        if not os.path.exists(src):
            sys.exit("no background for %s; run generate first" % letter)
        for suffix, tagline in VARIANTS.items():
            results.append(build_one(letter, suffix, tagline, src))
    path = os.path.join(HERE, "checks.json")
    old = {}
    if os.path.exists(path):
        with open(path) as f:
            old = {o["name"]: o for o in json.load(f).get("options", [])}
    old.update({r["name"]: r for r in results})
    with open(path, "w") as f:
        json.dump({"options": [old[k] for k in sorted(old)]}, f, indent=1, default=list)
    bad = [r["name"] for r in results if not (r["met"] and r["pad_ok"] and r["sizes_ok"] and r["inside_left_55"])
           or ("composite" in r and not (r["composite"]["covers_height"] and r["composite"]["group_inside"] and r["composite"]["seam_ok"]))]
    if bad:
        sys.exit("CHECKS FAILED: " + ", ".join(bad))
    print("all checks ok")
    return results


def report(r: dict) -> None:
    z = "   ".join("%s %5.1f/%3.0f -> %5.1f/%3.0f" % (n, *b, *a)
                   for n, b, a in zip(ZONE_NAMES, r["before"], r["after"]))
    print("%-8s scrim %.2f %s   %s" % (r["name"], r["strength"], "ok" if r["met"] else "TARGET NOT MET", z))
    print("   ink 1x %s, clear space L/T/R/B %s  %s, right edge %.1f%% of width"
          % (r["ink_1x"], r["pad_1x"], "ok" if r["pad_ok"] else "UNDER 40px", 100 * r["right_frac"]))
    print("   contrast (worst p95 / median): " + ", ".join(
        "%s %.1f/%.1f" % (k, *v) for k, v in r["contrast"].items()))
    print("   at 550: %s   wrote %s" % (r["at_550"], ", ".join("%dx%d" % s for s in r["sizes"])))
    if "composite" in r:
        print("   composite: %s" % r["composite"])


def sheet() -> None:
    rows = []
    with tempfile.TemporaryDirectory() as work:
        for letter in OPTIONS:
            for suffix in VARIANTS:
                one = os.path.join(HERE, "option-%s%s-1100x220.png" % (letter, suffix))
                prev = os.path.join(HERE, "option-%s%s-550-preview.png" % (letter, suffix))
                if not os.path.exists(one):
                    continue
                row = os.path.join(work, letter + suffix + ".png")
                label = "Option %s%s   seed %d   1100x220, and at 550 wide" % (
                    letter, " (no tagline)" if suffix else "", OPTIONS[letter]["seed"])
                cc.magick("(", one, ")", "(", "-size", "24x220", "xc:#0c1424", ")",
                          "(", prev, "-background", "#0c1424", "-gravity", "north", "-extent", "550x220", ")",
                          "+append", "-background", "#0c1424", "-gravity", "north", "-splice", "0x34",
                          "-font", cc.FONT_SUPPORT, "-pointsize", "18", "-fill", "#c9ccd3",
                          "-gravity", "northwest", "-annotate", "+0+8", label, row)
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
    if argv[0] == "prompt":
        for l in letters:
            print("%s (seed %d):\n%s\n" % (l, OPTIONS[l]["seed"], prompt_for(l)))
    elif argv[0] == "generate":
        generate(letters)
    elif argv[0] == "build":
        build(letters)
    else:
        sheet()


if __name__ == "__main__":
    main(sys.argv[1:])
