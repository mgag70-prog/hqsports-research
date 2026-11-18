# Cover prompt: lockout-countdown-2026, week 3

Installed November 18, 2026: option A, the last grains (both options are in `figures/cover-options/`). The background is A as returned by the edit endpoint, with no further edit.

Built by `python3 figures/cover-options/build_options.py cover` from `figures/cover.json` and `raw/cover-background.png`, the same way weeks 1 and 2 were. `tools/compose_cover.py` was not used for the composition: its panel layout would not reproduce it, and its build refuses this piece because `cover.json` names another builder.

- **Model:** fal-ai/nano-banana-pro/edit, editing week 2's installed background (`week-02/figures/raw/cover-background.png`).
- **Parameters:** aspect_ratio 16:9, resolution 2K, num_images 1, output_format png.
- **Seed and request:** 7301, 01a1ecba-ef79-7d41-8bd9-df9168926a98.
- **Background:** raw/cover-background.png, 2752x1536, md5 45c1bf1b…, a copy of raw/cover-options/option-A-background.png.
- **Cost:** one edit at $0.15. The two options cost $0.30 together.
- **Prompt:** the subject and the full prompt as sent are under Option A in `cover-options/prompts.md`.
- **Cover line:** 13 days. 5.13 times.
  - Two lines in both formats, verbatim in draft.md under "Checking Sword's claim". The "13" and "5.13" are composited type, not model output.
  - Numerals are Charter Bold (lining figures), scaled to Georgia Bold's "O"; Georgia Bold's old-style figures would mix heights in "5.13". The words stay in Georgia Bold.
- **Composition:** week 2's settings for this background.
  - Full-bleed, with a bottom gradient scrim in deep navy and the wordmark top left.
  - Red rule; the first line in paper and the second in red.
  - The wide headline is held to 33% of the frame width (size cap 0.12) so it stays left of the hourglass.
  - The square is cropped from x 0.22.
  - The scrim solved to 0.82 in the wide format (headline band p95 78, at the ceiling of 78) and 0.25 in the square (the floor; p95 70).
- **Checked:**
  - **Marks:** at full resolution there are no letters, numbers, faces or engraving. The faint red disc inside the top of the glass is the sand reflection carried over from weeks 1 and 2. The field is generic, not a recognizable venue.
  - **Baseball:** white leather with red stitching, unmarked.
  - **Colors:** the red is the house brick red in the sand; no team's color scheme.
  - **Safe zone:** the wide type runs from 96,89 to 488,524, inside the X-card safe zone of 93,84 to 1103,548.
  - **Match:** both installed files are pixel-identical to `cover-options/option-A-*.png`.
