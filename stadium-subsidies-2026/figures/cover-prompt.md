# Cover prompt: stadium-subsidies-2026

Installed October 31, 2026: option A, the stadium on a pile of gold (the four options are in `figures/cover-options/`). The background is A as generated, with no edit step.

Built by `python3 figures/cover-options/build_options.py cover` from `figures/cover.json` and `raw/cover-background.png`. `tools/compose_cover.py` was not used for the composition: its panel layout would not reproduce it, and its build and generate commands refuse this piece because cover.json names the cover-options builder.

- **Model:** fal-ai/nano-banana-pro (generation).
- **Parameters:** aspect_ratio 16:9, resolution 2K, num_images 1, output_format png.
- **Background:** raw/cover-background.png, 2752x1536, md5 17d278f0…, a copy of raw/cover-options/option-A-background.png.
- **Cost:** one image at $0.15. The four options cost $0.60 together.
- **Cover line:** Public money. Private stadium.
  - Two lines in both formats, verbatim in draft.md under "Who keeps the gains".
- **Composition:**
  - Full-bleed, with a bottom gradient scrim in deep navy and a top-left corner.
  - Red rule; the first line in paper and the second in red.
  - The wide headline is held to 46% of the frame width (size cap 0.12) so it sits over the dark foreground, not the gold.
  - The square is cropped from x 0.22.
  - The scrim solved to 0.84 in the wide format (headline band p95 78, at the ceiling of 78) and 0.25 in the square (the floor).
- **Checked:**
  - **Marks:** at full resolution there are no letters, numbers, faces or engraving. The gold ingots are plain, the facade carries no signage, and the stadium is generic, not a recognizable venue.
  - **Colors:** the red is the house brick red on the roof arches; no team's color scheme.
  - **Safe zone:** the wide type runs from 96,89 to 648,524, inside the X-card safe zone of 93,84 to 1103,548.
- **Reproduced:** `build_options.py cover` rebuilds both files byte for byte (md5 d3453142… wide, d10de0a9… square).

## Option A: generation, seed 6101 (installed)

- Date: 2026-10-31
- Request: 01a19210-37f7-7553-8434-d79382f42872

### Prompt as sent

Cinematic editorial photograph for a publication about the money in sport, lit like a film poster still: high contrast, one hard dramatic key light, deep black shadows, rich dark navy blue tones throughout, and one bold accent of brick red somewhere in the scene. Any baseball is a plain white leather ball with red stitching. Fine film grain, polished and intense, full-bleed with no empty panel. Subject: A gleaming modern stadium at night rising on top of a colossal heap of plain unmarked gold ingots that forms its whole foundation, the gold blazing under floodlights, brick red steel trusses in the roof, low heroic angle from below, deep night sky. Wide 16:9 frame, the scene filling the whole image. The lower third of the frame stays darker and simpler than the rest, with no small objects in it, so a caption can sit over it. The image contains no text of any kind: no letters, words, numbers, digits, captions, signage, scoreboards, labels or watermarks, and every surface that would normally carry writing is blank. No logos, no team marks, no mascots, no team colors or insignia. No people and no faces.
