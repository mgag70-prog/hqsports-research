# Cover prompt: pca-mvp-award-2026

Installed November 13, 2026: option A, the pool full of gold (all three options are in `figures/cover-options/`). The background is A as generated, with no edit.

Built by `python3 figures/cover-options/build_options.py cover` from `figures/cover.json` and `raw/cover-background.png`, the same way lockout-countdown-2026/week-02's cover was. `tools/compose_cover.py` was not used for the composition: its panel layout would not reproduce it, and its build refuses this piece because `cover.json` names another builder.

- **Model:** fal-ai/nano-banana-pro (generation, not an edit).
- **Parameters:** aspect_ratio 16:9, resolution 2K, num_images 1, output_format png.
- **Seed and request:** 9101, 01a1d4dc-8585-78d1-8580-695c6c487c94.
- **Background:** raw/cover-background.png, 2752x1536, md5 4867a707…, a copy of raw/cover-options/option-A-background.png.
- **Cost:** $0.15 for this image; the three options cost $0.45 together. Installing generated nothing new.
- **Prompt:** the subject and the full prompt as sent are under Option A in `cover-options/prompts.md`.
- **Cover line:** $894,000. Most Valuable.
  - Two lines in both formats, verbatim in draft.md at the end of "What the award pays, and who pays it". The "$894,000" is composited type, not model output.
- **Composition:**
  - Full-bleed, with a bottom gradient scrim in deep navy and the wordmark top left.
  - Red rule; the first line in paper and the second in red.
  - The wide headline may run to 56% of the frame width (size cap 0.16), since the pool deck's lower third is empty.
  - The square is cropped from x 0.22.
  - The scrim solved to the 0.25 floor in both formats (wide headline band p95 43, square 12).
- **Checked:**
  - **Marks:** at full resolution there are no letters, numbers, faces or engraving; the coins have blank faces. No recognizable real venue.
  - **Baseball:** white leather with red stitching, unmarked.
  - **Colors:** navy, gold and a brick red glow at the far end of the pool; no team marks.
  - **Safe zone:** the wide type runs from 96,89 to 768,525, inside the X-card safe zone of 93,84 to 1103,548.
  - **Match:** both installed files are byte-identical to `cover-options/option-A-*.png`.

The ball is small in the frame and the picture is dark, so A is the quietest of the three at thumbnail size (see the ranking in `cover-options/README.md`).
