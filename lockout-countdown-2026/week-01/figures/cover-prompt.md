# Cover prompt: lockout-countdown-2026, week 1

Installed November 5, 2026: option C, the hourglass (the three options are in `figures/cover-options/`). The background is C as generated, with no edit step.

Built by `python3 figures/cover-options/build_options.py cover` from `figures/cover.json` and `raw/cover-background.png`. `tools/compose_cover.py` was not used for the composition: its panel layout would not reproduce it, and its build refuses this piece because `cover.json` names another builder.

- **Model:** fal-ai/nano-banana-pro (generation).
- **Parameters:** aspect_ratio 16:9, resolution 2K, num_images 1, output_format png.
- **Seed and request:** 7103, 01a1aa05-b82a-7650-b251-e68d9093521d.
- **Background:** raw/cover-background.png, 2752x1536, md5 66d8ed3b…, a copy of raw/cover-options/option-C-background.png.
- **Cost:** one image at $0.15. The three options cost $0.45 together.
- **Cover line:** 26 days. Same lines.
  - Two lines in both formats, verbatim in draft.md under "Same lines, nearly the same clubs". The "26" is composited type, not model output.
- **Composition:**
  - Full-bleed, with a bottom gradient scrim in deep navy and a top-left corner.
  - Red rule; the first line in paper and the second in red.
  - The wide headline is held to 33% of the frame width (size cap 0.12) so it stays left of the hourglass.
  - The square is cropped from x 0.22.
  - The scrim solved to 0.81 in the wide format (headline band p95 78, at the ceiling of 78) and 0.25 in the square (the floor).
- **Checked:**
  - **Marks:** at full resolution there are no letters, numbers, faces or engraving. The glass and bases carry nothing, and the field is generic, not a recognizable venue.
  - **Baseball:** white leather with red stitching, unmarked.
  - **Colors:** the red is the house brick red in the sand; no team's color scheme.
  - **Safe zone:** the wide type runs from 96,89 to 492,524, inside the X-card safe zone of 93,84 to 1103,548.

The prompt asked for a pitcher's mound; the model drew something closer to home plate.
