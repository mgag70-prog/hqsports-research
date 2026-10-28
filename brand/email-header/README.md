# Email header: Ledger & Whistle masthead

This is the masthead banner for Ledger & Whistle Substack emails. `build_header.py` built it on October 28, 2026, the same way as `notes/the-ledger/header/`: one fal.ai background per concept, then the house navy scrim and the type, which is set in code with the helpers from `tools/compose_cover.py`. The model drew no letters.

There are three concepts, plus B2 (an edit of B), B3 (a fresh generation in B's look, laid out for 5:1), B4 (a 4:3 still life composited onto a navy banner in code) and B5 (B4's still life placed larger and further left, in code only). Each comes in three sizes:

| File | Size |
|---|---|
| `option-X-1100x220.png` | the header |
| `option-X-2200x440.png` | @2x |
| `option-X-550-preview.png` | the 1100 file scaled to 550 wide, as many email clients show it |

`contact-sheet.png` shows all seven at 1100 and at 550, in the order A, B, B2, B3, B4, B5, C.

Every banner carries the tagline. The no-tagline variants were dropped on October 28: the builder no longer makes them, and the old files are in `raw/superseded-notag/` (local only).

## Type

- **Wordmark:** "LEDGER & WHISTLE" in Georgia Bold, the house serif, in paper white #F7F5F0, with the "&" in red #D4553D.
  - The line is set once and only the "&" is recoloured in place, so spacing and kerning are those of the single line.
  - The width limit sets its size: it runs from x 48 to x 584.5, which is 53.1% of the width. Its cap height is 32px at 1x.
- **Rule:** 72x3 in red, 16px under the wordmark baseline.
- **Tagline:** "The business of sports, by the numbers." in Georgia at 26px, in paper at 78% (the covers' sub-line colour).

All of it is left-aligned. Clear space at 1x is at least 48px left and 64.5px top and bottom.

## Ranking

**B4, composited still life (seed 6231). Recommended.**
- It's the only option where the whole group is in the banner: the football, baseball and basketball, the whistle on its lanyard, and the green-and-red ruled paper, all whole, with clear navy around them.
- It isn't cropped from a wide frame. A 4:3 still life is scaled down into the banner and blended into plain navy on the left, so the composition doesn't depend on the model filling a 5:1 band, which it never managed.
- **The trade-off is size:** the group is 180px tall at 1x and sits at 73–93% of the width. At 550 the four objects are small but each one reads.
- **Two departures from the brief:**
  - The baseball sits lower and in front of the other two balls, not level with them.
  - The football's nose points away from the baseball; its other end rests against the basketball.

  Both are as the model drew them. Neither ball nor the whistle is cut, so the retry rule didn't apply.
- **The paper has tiny form-header squiggles** (see the checks). At the banner's scale they're about 1px tall and can't be seen.

**B5, B4's still life placed larger and further right of the type (code only, no new generation).**
- **Placement:** the same source image (seed 6231) and the same fade-to-navy blend, with two changes.
  - The group is 210px tall at 1x, 5px clear top and bottom (scale 0.3498 against B4's 0.2998).
  - Its left edge sits at x 625, 40px clear of the end of "LEDGER & WHISTLE" (x 584.5) and 125px right of the tagline's end (x 500): `gap_after_tagline` 125.
  - Against B4, the group is about 17% taller and starts about 176px further left. Nothing overlaps the type: the wordmark's worst-case contrast is 14.2:1, against B4's 14.4.
- **History:** a first B5 with `gap_after_tagline` 40 put the football under the "LE" of WHISTLE (wordmark worst 4.7:1), and was moved on October 28.
- **The right edge:** the still life no longer reaches the right edge. Its right side fades into navy matched to its own right-hand cloth, and the last 11% or so of the banner (x 974 to 1100 at 1x) is plain navy. Both fades pass the seam check.
- **The source's flaws carry over:** the baseball sits low and in front, the football's nose points away from the baseball, and the paper has the invisible form-header squiggles noted for B4.

The ranking of the first three concepts stands as written:

1. **B, still life (seed 6201).**
   - It's the only concept that shows the name: a referee's whistle, with a baseball, a basketball, the bottom of a football and a corner of green-and-red ruled accounting paper.
   - The navy cloth behind the type is already dark, so it needed only the minimum scrim (0.25). The objects come through unveiled.
   - The whistle and the baseball still read at 550.
   - The crop sits low (`crop_y` 0.72) so the whistle stays in. That costs most of the football, which shows only as a brown curve along the top edge.
2. **C, scoreboard bulbs (seed 6301).**
   - The moodiest of the three, and the most abstract: a grid of dark bulbs going soft to the left, with about a dozen lit red ones.
   - The lit bulbs are scattered across a diagonal band and form no letter, digit or shape that I can see at 2x. That's my judgment, so check it by eye too.
   - It has the best contrast for the red "&" of any option (4.5–4.6:1) and needed only the minimum scrim.
   - It says "scoreboard" more than "sports business", and it's the least specific to the brand.
3. **A, night stadium with a ledger grid (seed 6101).**
   - The most striking at 1100, and the idea (a stadium printed on ledger paper) is the cleverest.
   - At 550 the ruled grid almost vanishes, and the stadium crowds the type. The bright stands start right where "WHISTLE" ends, and a floodlight mast stands behind "TLE".
   - I pushed the scrim's full-strength zone out to 54% for this option (`scrim_x` 0.54–0.80) and it passes every check.
   - The field has faint generic lines but no numbers. The seat-row trim is brick red, and two yellow posts appear at the field edge. None of it matches a team that I can tell.

**B2, B edited (seed 6203). Not ranked, because it doesn't meet its brief.** B2 is option B's background run through `fal-ai/nano-banana-pro/edit`, with two asks: move the whistle down onto the accounting paper, and bring the football fully into view beside the baseball as a group of three.
- **What the edit did:**
  - The whistle now rests on the paper at the bottom right with its lanyard trailing.
  - The top sheets of paper are gone.
  - The football is whole, undistorted and unmarked, but it sits large and high, above and to the left of the baseball, not beside it at the same height.
- **Why the brief can't be met at 5:1:** in the source frame the football runs from 9% to 55% of the height and the whistle from 77% to 91%, while a 5:1 window holds 47%.
  - Even the three balls alone span 9% to 68%.
  - No crop shows both the football and the whistle, or even all three balls whole.
- **Where the crop sits:** `crop_y` 0.78. That keeps the whistle, the lanyard, the baseball and the basketball, but shows only the bottom of the football along the top edge.
  - The whistle's lower edge touches the frame.
  - The crop stops just above the paper squiggle (below), which is why it can't go lower.
- **Compared with B:** at 1100 this reads close to B with the whistle moved onto the paper. It is a usable banner, not the one asked for.

**B3, fresh generation (seed 6222). Not ranked, because it misses parts of its brief.** It's a text-to-image generation, not an edit, with B2's look and a layout written for the 5:1 band:
- football, baseball and basketball in a row at the same level, the football's nose pointing at the baseball;
- the whistle on the ruled paper below and in front of the baseball;
- everything inside the middle 45% of the height and the right 45% of the width, nothing cut.

What came back:
- **The objects are right and clean.** The football lies side-on with plain white laces and its nose toward the baseball, with a small gap. The basketball just touches the baseball. The whistle and lanyard rest on the paper at the lower right. Every shape reads, and none is distorted.
- **The group is still too tall for 5:1.** It runs from 13.5% (top of the basketball) to 75% (bottom of the whistle) of the frame height. The window holds 47%.
- **The crop:** at `crop_y` 0.56, the baseball, the whistle and the lanyard are whole. The crown of the football touches the top edge, and roughly the top fifth of the basketball is cut.
  - The alternative is `crop_y` 0.22, a one-number change. It keeps all three balls whole and drops the whistle entirely.
  - I kept the whistle.
- **It sits further left than asked.** The football starts at about 43% of the width, under the end of "WHISTLE" and of the tagline. The football is dark there, so the scrim stayed at the 0.25 minimum and the wordmark's worst-case contrast is 12.1:1, but image and type do overlap.
- **The paper has marks:** two tiny script-like marks near the top sheet's upper right corner, one of which looks almost like a word. They're inside the crop, about 3px tall at 1100. See the checks.

Getting here took four generations across two briefs, recorded below. Every one spread the group over 57–74% of the frame height, whatever the prompt asked.

**How B4 is built** (`composite_to_banner` in `build_header.py`):
B5 uses the same function with `group_margin` 5 and `gap_after_tagline` 125. Its still life ends inside the banner on the right, so it gets a second fill, taken from the still life's right edge (the two fills meet under the opaque middle of the photo), and a second fade from 16px past the group to the photo's right edge.

1. **Scale.** `group` is the box around the balls, paper, whistle and lanyard, as fractions of the source, measured by eye: x 0.17–0.785, y 0.18–0.85. The still life is scaled (0.2998) so that box is 440 − 2×40 = 360px tall at 2x, which leaves 20px clear above and below at 1x.
2. **Place.** It's set flush right, so it has no right-hand edge inside the banner, and its 537px height covers the full 440, so it has no top or bottom edge either.
3. **Fill.** Left of it, the canvas is filled row by row with the mean colour of the still life's leftmost 24 columns, lightly blurred, so the navy matches the cloth at every height.
4. **Fade.** The still life's alpha ramps (smoothstep) from 0 at its left edge (x 1480 at 2x) to 1 at x 1586, 16px short of the football.

Because the fill and the photo are the same colour at the photo's edge, and the photo is fully transparent there, there's no seam to see.

It's different from The Ledger header in every case: no open ledger book, no desk, no desk lamp.

## Seeds, requests and cost

Model `fal-ai/nano-banana-pro`, 21:9, resolution 2K, PNG, 3168x1344 returned. Each image is cropped full-width to 5:1, at `crop_y` per option in `build_header.py`, then scaled to 2200x440. B4 is the exception: 4:3, composited rather than cropped.

| Option | Seed | Request id | Crop y | Result | Cost |
|---|---|---|---|---|---|
| A | 6101 | 01a1833b-ce2e-7e93-a52f-7b7eab046758 | 0.25 | used | $0.15 |
| B | 6201 | 01a1833c-3db9-79b1-a1e9-47578a2e4701 | 0.72 | used | $0.15 |
| C | 6301 | 01a1833c-ac4b-7f91-8f49-9a3c44c8336a | 0.35 | used | $0.15 |
| B2 (first edit) | 6202 | 01a18367-5ada-7592-b430-fa18667b335c | n/a | rejected: the football didn't move, and the paper squiggle became glyph-like (close to "12"); kept in `raw/rejected/` | $0.15 |
| B2 | 6203 | 01a18368-4ee4-7d31-a127-3673d57803d4 | 0.78 | used | $0.15 |
| B3, first brief | 6211 | 01a18375-f7c6-7800-ae6d-6c9358f8846f | n/a | rejected: the group ran from 14% to 78% of the height | $0.15 |
| B3, first brief, retry | 6212 | 01a18376-a6a5-75a2-af07-220341f75586 | 0.57 | superseded: the group ran 20% to 77% and sat under the type (wordmark worst 5.5:1); PNGs in `raw/rejected/B3-seed6212-pngs/` | $0.15 |
| B3, second brief | 6221 | 01a1837b-24a6-7213-8c80-3998688ff7db | n/a | rejected: the group ran from 4% to 78%, and a brass lamp base appeared at the right edge | $0.15 |
| B3, second brief, retry | 6222 | 01a1837b-df4b-7c82-aaa9-fa6af7bf65d1 | 0.56 | used | $0.15 |
| B4 | 6231 | 01a18383-ca71-7ed2-ae3d-29ec31773388 | composited, 4:3, 2400x1792 | used, first try | $0.15 |
| B5 | 6231 (B4's image) | 01a18383-ca71-7ed2-ae3d-29ec31773388 | composited, placed in code | used | $0 |

**Total: $1.50.**
- **Text-to-image:** $0.45, three images at the $0.15 list price, which applies below 4K. There were no re-rolls.
- **B4:** $0.15, one text-to-image generation at 4:3, 2K, which returned 2400x1792. No retry: every ball and the whistle were whole.
- **B3:** $0.60, four text-to-image generations at 21:9, 2K, across two briefs, each with one retry.
  - The second brief placed objects by position in the frame: the top of the basketball below the 30% line, the bottom of the whistle above the 70% line, the basketball about a quarter of the frame tall.
  - Its retry, seed 6222, added a far-away, long-lens camera, "a thin strip about five times wider than tall", and no other objects. That brought the three balls inside 47% of the height, but not the whistle below them.
  - The B3 prompt as sent is in `raw/option-B3-request.json`. The earlier ones are in `raw/rejected/`.
- **B2 edits:** $0.30, two calls to `fal-ai/nano-banana-pro/edit`. I've assumed the edit endpoint has the same $0.15 price; I haven't checked it on the fal dashboard.
- **B2 source:** both edits were sent B's background, `raw/option-B-background.png` (md5 916a5848…), as a JPEG q95 data URI of 2.0 MB, because the 7.5 MB PNG is too big to inline. The output is 21:9, 2K, PNG, 3168x1344.
- **Retry rule:** retry once with a new seed. The second edit, seed 6203, used a tighter prompt (football to the left of the baseball at the same height; paper with ruled lines only). It moved the football but not into a 5:1 band, and the squiggle survived. The prompts as sent are in `raw/option-X-request.json`, and you can print them with `python3 brand/email-header/build_header.py prompt`.

## Checks

These are the numbers from `checks.json` after the last build.

**Luminance** is mean / p95 on a 0–255 scale, measured after the scrim. The ceiling is the house band target from `compose_cover.py`, 50 / 78. Two zones are checked:
- the left 55% of the frame;
- the type band, which is the inked type's box grown by 12px.

**Contrast** is WCAG 2.x, measured on the background pixels under each element's ink, dilated 2px. "Worst" uses the 95th-percentile brightest background pixel under the element; "median" uses the median.

| | A | B | B2 | B3 | B4 | B5 | C |
|---|---|---|---|---|---|---|---|
| Scrim strength (solved) | 0.28 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 |
| Left 55% | 29.5 / 78 ok | 26.3 / 41 ok | 27.4 / 42 ok | 34.6 / 46 ok | 34.3 / 43 ok | 35.0 / 43 ok | 25.5 / 48 ok |
| Type band | 28.7 / 64 ok | 27.0 / 40 ok | 28.1 / 39 ok | 33.9 / 44 ok | 36.6 / 43 ok | 37.0 / 43 ok | 25.8 / 49 ok |
| Wordmark (paper), worst / median | 10.6 / 16.5 | 12.7 / 15.9 | 13.1 / 15.8 | 12.1 / 14.7 | 14.4 / 15.3 | 14.2 / 15.3 | 12.0 / 16.3 |
| "&" (red) | 4.2 / 4.4 | 4.1 / 4.2 | 4.0 / 4.2 | 3.6 / 3.8 | 3.8 / 4.1 | 3.8 / 4.0 | 4.5 / 4.7 |
| Rule (red) | 4.4 / 4.5 | 4.4 / 4.6 | 4.4 / 4.5 | 4.0 / 4.1 | 3.5 / 3.5 | 3.5 / 3.5 | 4.3 / 4.6 |
| Tagline (78% paper) | 11.0 / 13.2 | 11.4 / 12.9 | 11.2 / 12.5 | 10.1 / 11.6 | 10.3 / 10.3 | 10.3 / 10.3 | 9.9 / 13.3 |

**B4 composite checks** (in `checks.json` under `composite`; `build` exits with an error if any fails):
- **Coverage:** the placed still life covers the full banner height (it's placed at y −57 and is 537px tall, at 2x). The group box sits at x 1602–2045 and y 40–399 at 2x, so it's whole, clear of the frame by 20px top and bottom at 1x, and entirely inside the right 45%.
- **Seam:** across the fade, the column-mean luminance never steps more than 0.32 levels (0–255) from one column to the next. The photo's own cloth in the same columns, unblended, steps 0.32, so the blend adds nothing measurable. The check fails at more than twice the cloth's own step.
- **By eye:** I looked at a 2x crop of the fade with its levels stretched (`raw/inspect/B4-fade-2x-stretched.png`). There's no edge or line, only the photo's cloth folds fading into the smooth fill.

**B5 composite checks:**
- **Coverage:** the still life is placed at x 1107, y −103 and is 840x627 at 2x, so it covers the full height. The group box is x 1250–1766, y 10–430 at 2x: 210px tall at 1x, 5px clear top and bottom. It starts at x 625 at 1x, 125px right of the tagline's end and 40.5px right of the wordmark's.
- **Seam, left fade (x 1107–1234 at 2x):** the largest column-to-column step is 0.32 levels, against 0.38 in the photo's own cloth over those columns.
- **Seam, right fade (x 1782–1947 at 2x, plus 60px of fill):** the largest step is 0.37, against 0.47 in the cloth.
- **By eye:** in a stretched 2x crop (`raw/inspect/B5-fades-2x-stretched.png`), neither fade shows an edge. The right-hand fill shows faint horizontal banding only with the levels stretched, from its row-by-row colour match.

**Legibility at 550 wide:**
- The wordmark is 23px type with 16px caps.
- The tagline is 13px type with 9px caps, and it reads cleanly in all seven previews.
- The red "&" can't reach 4.5:1 on navy in most of the options; red on navy tops out around 3.6–4.8 here. It clears 3:1 everywhere, which is the bar for large text, and at 23px bold at 550 it counts as large.

**Clear space:** 48px left, 65px top and 64.5px bottom of the inked type in all seven, and the type ends at 53.1% of the width, inside the dark left 55%. `build` exits with an error if any of these fails, or if any zone misses its target.

**Sizes:** checked with `magick identify`. Every `-1100x220.png` is exactly 1100x220, every `-2200x440.png` is exactly 2200x440, and every preview is 550x110.

**No text, logos, people or team marks:** I checked full-resolution crops of every background by eye. They're in `raw/inspect/`.
- **A:** blank boards, seats, field and lights. The tiny marks along the field wall are unreadable smudges.
- **B:** no printing on any ball. The lower accounting sheet has one script-like squiggle, unreadable, at about (2338, 1204) in the source. The B crop ends at y 1145, so it's outside every B file, and I confirmed that on the 2x crop.
- **C:** bulbs and a floodlight only.
- **B2:** no printing on any ball; the football has plain laces and seams only.
  - The edit kept B's squiggle on the lower sheet, now at about (2358, 1214) in the B2 source. B2's crop ends at y 1187, so it's outside every B2 file, which I confirmed on the 2x crop.
  - The rejected first edit made that squiggle more glyph-like, which is one reason it was rejected.
- **B3:** no printing on any ball; the football has plain laces and seams only. The whistle is plain chrome.
  - The top accounting sheet has two tiny script-like marks near its upper right corner, at about (2800, 868) and (2780, 885) in the source; one looks almost like a short word. Both sit inside the B3 crop (rows 398 to 1030), at about 3px tall in the 1100 file. They're the one rule break in B3, and fixing them would take another generation or an edit.
  - Nothing else is on the paper; the whistle and lanyard are plain.
  - The inspection crops are `raw/inspect/B3-*.png`.

- **B4:** no printing on any ball; the football has plain white laces and seams only, and the whistle and lanyard are plain.
  - The top accounting sheet has a row of tiny form-header squiggles along its top edge and over its right-hand columns, about seven in all. None is readable, but they look like small printed labels, which the brief rules out.
  - At the banner's scale (0.30 at 2x) each is about 2px tall in the 2200 file and about 1px in the 1100 file, so they can't be seen. Removing them would take an edit or a new generation.
  - The inspection crops are `raw/inspect/B4-*.png`.

## Rebuilding

```
python3 brand/email-header/build_header.py build    # all seven banners, checks.json; no fal.ai call
python3 brand/email-header/build_header.py sheet    # contact-sheet.png
```

`raw/` (about 95 MB) and `contact-sheet.png` (3.8 MB) are in `.gitignore`. So `build` reproduces the banners only on a machine that holds `raw/`; anywhere else, regenerate from the seeds above.
