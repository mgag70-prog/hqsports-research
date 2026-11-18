# Cover prompt: cbb-revenue-share-2026

Installed November 17, 2026: option A, the empty bench (all three options are in `figures/cover-options/`). The background is A as generated, with no edit.

Built by `python3 figures/cover-options/build_options.py cover` from `figures/cover.json` and `raw/cover-background.png`, the same way pca-mvp-award-2026's cover was. `tools/compose_cover.py` was not used for the composition: its panel layout would not reproduce it, and its build refuses this piece because `cover.json` names another builder.

- **Model:** fal-ai/nano-banana-pro (generation, not an edit).
- **Parameters:** aspect_ratio 16:9, resolution 2K, num_images 1, output_format png.
- **Seed and request:** 9201, 01a1ea0b-aeeb-7961-b0fc-aa442a8d9119.
- **Background:** raw/cover-background.png, 2752x1536, md5 dc98e404…, a copy of raw/cover-options/option-A-background.png.
- **Cost:** $0.15 for this image; the three options cost $0.45 together. Installing generated nothing new.
- **Prompt:** the subject and the full prompt as sent are under Option A in `cover-options/prompts.md`.
- **Cover line:** $0 for the median player.
  - Two lines in both formats ("$0 for the" / "median player."), verbatim in draft.md in "Who got paid in men's basketball". The "$0" is composited type, not model output.
- **Figures:** Georgia Bold, the house headline face, has only old-style figures (its GSUB has aalt and locl, no lnum), so its "0" reads like a lowercase "o". The digits are set in Charter Bold (face 3 of the macOS Charter.ttc, copied out to a temp file at build time), which has lining figures, scaled 1.058 times so the zero is as tall as Georgia Bold's "O". The "$" and the rest of the line stay in Georgia Bold; runs are placed by hb-shape advance widths. Checked at 600px wide in both formats: "$0" reads as a dollar sign and a zero, clearly taller than the "o" in "for".
- **Composition:**
  - Full-bleed, with a bottom gradient scrim in deep navy and the wordmark top left.
  - Red rule; the first line in paper and the second in red.
  - House layout defaults, no per-format overrides; the square is cropped from x 0.22.
  - Scrim strength 0.74 wide (headline band p95 78, at the ceiling), 0.27 square (p95 78).
- **Checked:**
  - **Marks:** at full resolution there are no letters, numbers, faces or logos. A dark scoreboard-like panel on the upper-left wall has a few soft blurred blobs; none reads as a character, and it sits under the wordmark corner darkening.
  - **Basketball:** orange with black seams, unmarked.
  - **Colors:** navy, orange and a brick red glow on the upper deck; no team or conference marks.
  - **Safe zone:** the wide type runs from 96,89 to 938,547, inside the X-card safe zone of 93,84 to 1103,548.
  - **Match:** both installed files are byte-identical to `cover-options/option-A-*.png`.

A is the darkest of the three options and its ball is small, so it's the quietest at thumbnail size (see the ranking in `cover-options/README.md`).
