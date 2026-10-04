#!/usr/bin/env python3
"""Photo cover options for wrigley-season-tickets-2026, built with tools/compose_cover.py.

P1: Matt's own photo from his seats (figures/raw/photo-pennant-night.png, 1276x708) as the
    background, the draft's H1 set in the dark sky at the upper left.
P2: P1 plus his 2016 World Series ticket as a small tilted inset at the lower right. The
    barcode and the code under it are pixelated before the inset is placed; the tier,
    aisle, row, seat and price stay legible. The crop stops above the red label band.

Both options use the headline from cover-options/cover.json (the fal.ai option A record,
seed 4201, kept here with its cover-prompt.md) and pass the same draft check. Every output is written with -strip, so no EXIF or other metadata survives.
The raw photos live in figures/raw/, which is gitignored. Outputs go to this folder; P2 was chosen
and copied to figures/cover-1200x630.png and figures/cover-1080x1080.png.

Run from the repo root:  python3 wrigley-season-tickets-2026/figures/cover-options/build_photo_options.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FIGURES = os.path.dirname(HERE)
PIECE = os.path.dirname(FIGURES)
REPO = os.path.dirname(PIECE)
sys.path.insert(0, os.path.join(REPO, "tools"))
import compose_cover as C  # noqa: E402

PHOTO = os.path.join(FIGURES, "raw", "photo-pennant-night.png")
TICKET = os.path.join(FIGURES, "raw", "photo-ws-ticket.png")
# Ticket photo, 1290x1704. The inset is the lower part, from the GAME 4 line to the price
# row, with the perspective-skewed right edge cropped off. Boxes are x, y, w, h in photo px.
TICKET_CROP = (40, 1040, 1152, 520)      # GAME 4 line through the seat row; stops above the red label band,
                                          # which carried a screenshot icon that overlapped the E in PRICE
BARCODE_BOX = (95, 1235, 650, 140)
CODE_BOX = (270, 1378, 300, 50)
INSET_WIDTH = {"wide": 320, "square": 400}
INSET_TILT = -6

cfg = json.load(open(os.path.join(HERE, "cover.json")))     # seed 4201's record, kept here
cfg = {"headline": cfg["headline"], "square_crop_x": 0.30,
       "formats": {
           # type in the dark sky, scrim only over that corner, zone only where the type is
           "wide": {"headline_max_width": 0.40, "headline_max_size": 0.09, "anchor": ["top", 0.13],
                    "scrim_x": [0.34, 0.70], "scrim_y": [0.30, 0.56],
                    "zones": [[0.04, 0.06, None, 0.44, "band"]]},
           "square": {"headline_max_width": 0.80, "headline_max_size": 0.062, "anchor": ["top", 0.11],
                      "scrim_x": None, "scrim_y": [0.34, 0.60],
                      "zones": [[0.04, 0.06, None, 0.46, "band"]]},
       }}
paths = C.piece_paths(PIECE)
C.check_against_draft(paths, cfg, ["wide", "square"])
print("headline passes the draft check")


def pixelate(src, dst, boxes, work):
    """Pixelate each box so nothing in it can be read, then crop the inset."""
    args = [src]
    for i, (x, y, w, h) in enumerate(boxes):
        args += ["(", "+clone", "-crop", "%dx%d+%d+%d" % (w, h, x, y), "+repage",
                 "-scale", "4%", "-scale", "%dx%d!" % (w, h), ")",
                 "-geometry", "+%d+%d" % (x, y), "-compose", "Over", "-composite"]
    x, y, w, h = TICKET_CROP
    args += ["-crop", "%dx%d+%d+%d" % (w, h, x, y), "+repage", "-strip", dst]
    C.magick(*args)


def inset(background, dst, size, fmt_name, work):
    """Tilt the ticket crop, add a shadow, and place it at the lower right over the crowd."""
    w, h = size
    width = round(INSET_WIDTH[fmt_name] * w / (1200 if fmt_name == "wide" else 1080))
    ticket = os.path.join(work, "ticket.png")
    pixelate(TICKET, ticket, [BARCODE_BOX, CODE_BOX], work)
    tilted = os.path.join(work, "tilted.png")
    C.magick(ticket, "-resize", "%dx" % width, "-bordercolor", "white", "-border", "6",
             "-background", "none", "-rotate", str(INSET_TILT), tilted)
    tw, th = C.image_size(tilted)
    x, y = w - tw - round(0.035 * w), h - th - round(0.06 * h)
    shadow = os.path.join(work, "inset-shadow.png")
    C.magick(tilted, "-alpha", "extract", "-blur", "0x14", "-evaluate", "multiply", "0.6",
             "(", "-size", "%dx%d" % (tw, th), "xc:black", ")", "+swap",
             "-alpha", "off", "-compose", "CopyOpacity", "-composite", shadow)
    C.magick(background, shadow, "-geometry", "+%d+%d" % (x + 6, y + 10), "-compose", "Over", "-composite",
             tilted, "-geometry", "+%d+%d" % (x, y), "-composite", dst)


def build(option, with_inset):
    for name in ("wide", "square"):
        fmt, text = C.piece_format(name, cfg)
        with tempfile.TemporaryDirectory() as work:
            background = C.prepare_source(fmt, PHOTO, cfg, work)
            size = C.image_size(background)
            strength, met, before, after = C.solve_scrim(fmt, background, size)
            print(C.describe(f"{option} {name}", strength, met, before, after))
            mean, p95 = C.wordmark_stats(fmt, background, size, strength)
            print("%-11s behind the wordmark %5.1f/%3.0f   %s" % ("", mean, p95, "ok" if p95 <= C.BAND_TARGET[1] else "TOO BRIGHT"))
            scrimmed, layer = os.path.join(work, "scrimmed.png"), os.path.join(work, "type.png")
            composed = os.path.join(work, "composed.png")
            C.apply_scrim(fmt, background, scrimmed, strength, size, work)
            if with_inset:
                with_ticket = os.path.join(work, "with-ticket.png")
                inset(scrimmed, with_ticket, size, name, work)
                scrimmed = with_ticket
            C.render_type(fmt, layer, size, text)
            C.composite_type(scrimmed, layer, composed, size, work)
            final = os.path.join(HERE, f"cover-{option}-{fmt['out_size'][0]}x{fmt['out_size'][1]}.png")
            C.magick(composed, "-resize", "%dx%d!" % fmt["out_size"], "-strip", "-depth", "8", final)
            C.magick(final, "-resize", "600x", "-strip", final[:-4] + "-600.png")
            print("wrote", os.path.relpath(final, REPO), f"(source {size[0]}x{size[1]})")


build("P1", with_inset=False)
build("P2", with_inset=True)
