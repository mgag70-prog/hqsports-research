# Email header: The Ledger

Header image for *The Ledger*, the weekly Ledger & Whistle Substack Note. The Note keeps a prediction ledger: every call is on the record and graded. Built October 27, 2026 by `build_header.py`, with the house scrim, shadow and fal.ai helpers imported from `tools/compose_cover.py`. There are three options, each saved as `option-X-1100x220.png` (the header), `option-X-2200x440.png` (@2x) and `option-X-550-preview.png` (the 1100 file scaled to 550 wide, the way many email clients show it). `contact-sheet.png` shows all three at 1100 and at 550.

Type is composited and every word is set in Georgia, as on the covers:
- "THE LEDGER" is Georgia Bold in paper white #F7F5F0.
- A 64x3 red #D4553D rule sits under it.
- The tagline "Every call on the record. Graded weekly." is Georgia in paper at 78%, like the cover sub-lines.
- The "LEDGER & WHISTLE" wordmark is red, Georgia caps with the covers' tracking, top left.

The type is left-aligned at x 48, with at least 44.5px clear space on every side at 1x. The model drew no letters.

## Ranking

1. **B, seed 5102. Recommended.** The page is the cleanest of the three: ticks, red checks and ruling, nothing that looks like writing. The book sits low and to the right, so the dark desk and wall behind the type needed only the minimum scrim (0.25). The photo comes through almost unveiled, and the lamp glow at top right gives it warmth. It has the best contrast on every type element, and the whistle and ball read clearly at 550.
2. **A, seed 5101.** The most dramatic of the three. It's the tightest close-up, the ball and whistle are the largest of any option, and the lamp light on the page is the most cinematic. But the open ledger runs under the type, so it needed the heaviest scrim (0.86). The page under "THE LEDGER" becomes a navy veil, and the red wordmark drops to 3.7:1. There are faint grey smudges in the column headers at the top right, not readable.
3. **C, seed 5104.** A brass whistle and a softer page. Next to the whistle are a few handwriting-like squiggles. They spell nothing, but at 2x they look like script, which is the closest any option came to breaking the no-text rule. Scrim 0.60. It's fine as a spare; I wouldn't lead with it.

## Seeds, requests and cost

Model `fal-ai/nano-banana-pro`, 21:9, resolution 2K, PNG, 3168x1344 returned, then cropped full-width to 5:1 (`crop_y` per option in `build_header.py`).

| Option | Seed | Request id | Result | Cost |
|---|---|---|---|---|
| A | 5101 | 01a17d55-a42f-7440-8499-39bf2872a517 | used | $0.15 |
| B | 5102 | 01a17d56-9263-7390-9056-a5a668648e83 | used | $0.15 |
| C (first try) | 5103 | 01a17d57-012c-7d91-9a3d-b304eda5d6dd | rejected: a person's shoulder fills the left side, and the word "Tick" is written down the right page | $0.15 |
| C | 5104 | 01a17d57-a47e-7e72-ba3d-b9591f8f0e37 | used | $0.15 |
| A at 8:1 | 5101 | 01a17d54-1950-7182-b9ef-7a2777e0c1a6 | HTTP 500 "Downstream service error", no image | $0 expected |
| A at 4:1 | 5101 | 01a17d54-b44e-7022-8c79-1d5eb424d7ef | HTTP 500 "Downstream service error", no image | $0 expected |

**Total: $0.60** for four images at the $0.15 list price, which applies below 4K. The two failed requests returned no image; I expect fal not to bill them, but haven't confirmed it on the fal dashboard.

**Why 21:9 and not 8:1.** The brief asked for the widest aspect the model supports. Pro's API schema lists 4:1 and 8:1, but both failed. Pro's own model card lists ratios only up to 21:9, and the 4:1 / 8:1 entries match Nano Banana 2's schema, which says "Supports extreme ratios: 4:1, 1:4, 8:1, 1:8". So 21:9 is the widest Pro actually completes. Cropping 21:9 to 5:1 keeps the full width and 47% of the height, which is still 3168x634 before it is scaled to 2200x440.

The prompt as sent is in `raw/option-X-request.json` and `python3 notes/the-ledger/header/build_header.py prompt`.

## Checks

Luminance figures are mean/p95 (0–255) after the scrim. The ceiling is the house band target from `compose_cover.py`, 50 / 78. Contrast is WCAG 2.x, measured on the pixels under each element's ink: worst is the 95th-percentile brightest background pixel, median is the median.

| | A | B | C |
|---|---|---|---|
| Scrim strength (solved) | 0.86 | 0.25 | 0.60 |
| Type band x 3–52%, y 12–88% | 41.2 / 67 ok | 28.0 / 45 ok | 32.7 / 62 ok |
| Left 55% of the frame | 42.7 / 78 ok | 30.4 / 66 ok | 33.2 / 78 ok |
| "THE LEDGER", worst / median | 9.9 / 13.8 | 13.0 / 16.1 | 8.2 / 14.9 |
| Tagline (78% paper) | 10.7 / 11.0 | 12.1 / 13.1 | 11.7 / 12.0 |
| Wordmark (red) | 3.7 / 3.7 | 4.4 / 4.5 | 3.9 / 4.0 |
| Red rule | 3.7 / 3.8 | 4.5 / 4.5 | 4.1 / 4.1 |

- **Clear space at 1x:** the type's ink spans x 48 to 548.5 and y 44.5 to 175.5, which leaves 48 left, 44.5 top, 44.5 bottom and 551.5 right. The title ends at 49.9% of the width, inside the dark left 55%.
- **At 550 wide:** "THE LEDGER" is 33.5px type with a 23.5px cap height. The tagline is 10.5px type (caps 7.2px), the small end of readable, and it reads cleanly in the previews. The wordmark is the smallest element: 9px type with 6.2px caps. I raised it from 16 to 18px at 1x because at 16 its caps were 5.5px at 550.
- **Wordmark contrast:** red on navy is 3.6:1 at best (brand README), so the wordmark can never reach the 4.5:1 body-text bar on this ground. It clears the 3:1 bar in all three options. B gets closest to 4.5 (4.4) because its scrim sits on an already dark wall.
- **Sizes:** every `-1100x220.png` is exactly 1100x220 and every `-2200x440.png` exactly 2200x440, both checked with `magick identify`.
- **No text in the images:** full-resolution crops of every ledger page were checked by eye. A and B show ruling, ticks and checks only. C (5104) has the squiggles noted above. The rejected C (5103) had a readable word and a person in it. There are no logos or marks; the baseballs show stitching only and the whistles are plain metal.

## Files

- `build_header.py`: `prompt`, `generate [A B C]`, `build [A B C]` and `sheet`. `build` and `sheet` reproduce every PNG here from the raw backgrounds without calling fal.ai.
- `checks.json`: the layout and every number in the checks table.
- `raw/`: the backgrounds as returned, one request record each, review JPEGs, the inspection crops, and `rejected/` for seed 5103. `.gitignore` only covers `*/figures/raw/`, so this `raw/` folder (about 30 MB) is not ignored. If you commit this folder, add `notes/the-ledger/header/raw/` to `.gitignore` first.
