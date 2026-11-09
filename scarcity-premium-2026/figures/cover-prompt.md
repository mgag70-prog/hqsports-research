# Cover prompt: scarcity-premium-2026

Installed November 5, 2026: option C, the baseball outweighing the gold (the three options are in `figures/cover-options/`). The background is C as generated, with no edit step, mirrored at composition.

Built by `python3 figures/cover-options/build_options.py cover` from `figures/cover.json` and `raw/cover-background.png`. `tools/compose_cover.py` was not used for the composition: its panel layout would not reproduce it, and its build refuses this piece because `cover.json` names another builder.

- **Model:** fal-ai/nano-banana-pro (generation).
- **Parameters:** aspect_ratio 16:9, resolution 2K, num_images 1, output_format png.
- **Seed and request:** 8103, 01a1abf2-3140-7862-bdd0-829c450f541f.
- **Background:** raw/cover-background.png, 2752x1536, md5 58bc67d9…, a copy of raw/cover-options/option-C-background.png.
- **Cost:** one image at $0.15. The options cost $0.60 together, with option B generated twice.
- **Cover line:** Sold above the estimate.
  - Two lines in both formats, verbatim in draft.md under "The answer".
- **Composition:**
  - Full-bleed, with a bottom gradient scrim in deep navy and a top-left corner.
  - Red rule; the first line in paper and the second in red.
  - Mirrored (`flip`) so the ball clears the headline.
  - The wide headline is held to 44% of the frame width (size cap 0.12).
  - The square is cropped from x 0.22, and its wordmark sits at a baseline of 4.3% of the frame height, above the scale's beam, because no crop keeps both pans in frame and clears the chain at the default position.
  - The scrim solved to 0.71 in the wide format and 0.25 in the square (the floor).
- **Checked:**
  - **Marks:** at full resolution there are no letters, numbers, faces or engraving. The ingots and scale are unmarked.
  - **Baseball:** white leather with red stitching, unmarked.
  - **Colors:** the red is the house brick red in the curtain; no team's color scheme.
  - **Safe zone:** the wide type runs from 96,89 to 593,524, inside the X-card safe zone of 93,84 to 1103,548.
