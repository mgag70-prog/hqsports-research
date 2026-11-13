# Cover prompt: lockout-countdown-2026, week 2

Installed November 11, 2026: option B, the drained hourglass (both options are in `figures/cover-options/`). The background is B as returned by the edit endpoint, with no further edit.

Built by `python3 figures/cover-options/build_options.py cover` from `figures/cover.json` and `raw/cover-background.png`, the same way week 1's cover was. `tools/compose_cover.py` was not used for the composition: its panel layout would not reproduce it, and its build refuses this piece because `cover.json` names another builder.

- **Model:** fal-ai/nano-banana-pro/edit, editing week 1's installed background (`week-01/figures/raw/cover-background.png`).
- **Parameters:** aspect_ratio 16:9, resolution 2K, num_images 1, output_format png.
- **Seed and request:** 7202, 01a1caa8-cbb5-7620-b6f1-5f906915ae04.
- **Background:** raw/cover-background.png, 2752x1536, md5 f12c3b71…, a copy of raw/cover-options/option-B-background.png.
- **Cost:** one edit at $0.15. The two options cost $0.30 together.
- **Prompt:** the subject and the full prompt as sent are under Option B in `cover-options/prompts.md`.
- **Cover line:** 20 days. $11 million.
  - Two lines in both formats, verbatim in draft.md under "The money that has moved this time". The "20" and "$11" are composited type, not model output.
- **Composition:** week 1's settings for this background.
  - Full-bleed, with a bottom gradient scrim in deep navy and the wordmark top left.
  - Red rule; the first line in paper and the second in red.
  - The wide headline is held to 33% of the frame width (size cap 0.12) so it stays left of the hourglass.
  - The square is cropped from x 0.22.
  - The scrim solved to 0.83 in the wide format (headline band p95 78, at the ceiling of 78) and 0.25 in the square (the floor; p95 68).
- **Checked:**
  - **Marks:** at full resolution there are no letters, numbers, faces or engraving. The faint red disc inside the top of the glass is a reflection of the sand, carried over from week 1. The field is generic, not a recognizable venue.
  - **Baseball:** white leather with red stitching, unmarked.
  - **Colors:** the red is the house brick red in the sand; no team's color scheme.
  - **Safe zone:** the wide type runs from 96,89 to 493,533, inside the X-card safe zone of 93,84 to 1103,548.
  - **Match:** both installed files are pixel-identical to `cover-options/option-B-*.png`.

The bottom sand is a tilted flat slope rather than a cone under the stream, which is physically a bit off; it shows at full size, not at thumbnail.
