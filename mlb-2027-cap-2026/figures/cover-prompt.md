# Cover prompt: mlb-2027-cap-2026

Installed October 28, 2026, after Matt chose option C of the four in `figures/cover-options/` (A to D generated, no edits).
Built by `python3 figures/cover-options/build_options.py cover` from `figures/cover.json` and `raw/cover-background.png` (option C's background as returned). `tools/compose_cover.py` was not used for the composition; its panel layout would not reproduce it, and its build and generate commands refuse this piece because cover.json names the cover-options builder.

- Model: fal-ai/nano-banana-pro (generation)
- Parameters: aspect_ratio 16:9, resolution 2K, num_images 1, output_format png
- Background: raw/cover-background.png, 2752x1536, md5 fbf4ef41…, the output of option C
- Cost: one image at $0.15 (the four options together cost $0.60)
- Cover line: Over the cap. Before the offseason. (two lines in both formats; verbatim in draft.md, "Everyone over the line")
- Composition: full-bleed, bottom gradient scrim in deep navy with a top-left corner, red rule, first line paper and the second red, square crop from x 0.30; wide scrim 0.59 (headline band p95 77, under the ceiling of 78), square scrim 0.25 (the floor)
- Checked: the ball shows stitching only at full resolution; the beam is plain painted wood; the floodlights are generic, with no recognizable ballpark; no letters, numbers or marks anywhere; wide type 96,89 to 1006,524 inside the X-card safe zone 93,84 to 1103,548
- Reproduced: `build_options.py cover` rebuilds both files byte for byte (md5 0bb118cc… wide, 727eff9a… square)

## Option C: generation, seed 5103

- Date: 2026-10-28
- Request: 01a1828a-7971-7221-b43c-b6e8ab7757b3

### Prompt as sent

Cinematic editorial photograph for a publication about the money in sport, lit like a film poster still: high contrast, one hard dramatic key light, deep black shadows, rich dark navy blue tones throughout, and one bold accent of brick red somewhere in the scene. Fine film grain, polished and intense, full-bleed with no empty panel. Subject: A baseball smashing upward through a thick brick red painted wooden beam, splinters and red paint chips frozen in midair, stadium floodlights flaring behind, deep night sky, extreme high speed photograph. Wide 16:9 frame, the scene filling the whole image. The lower third of the frame stays darker and simpler than the rest, with no small objects in it, so a caption can sit over it. The image contains no text of any kind: no letters, words, numbers, digits, captions, signage, scoreboards, labels or watermarks, and every surface that would normally carry writing is blank. No logos, no team marks, no mascots, no team colors or insignia. No people and no faces.
