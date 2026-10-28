# Cover prompt: mlb-2027-cap-2026

Installed October 28, 2026: option C2, an edit of option C (the four options are in `figures/cover-options/`). C was installed first; C2 replaced it the same day after Matt asked for C's near-black ball to be a normal white baseball, changing nothing else.

Built by `python3 figures/cover-options/build_options.py cover` from `figures/cover.json` and `raw/cover-background.png`, which is the C2 image below. `tools/compose_cover.py` was not used for the composition: its panel layout would not reproduce it, and its build and generate commands refuse this piece because cover.json names the cover-options builder.

- **Model:** fal-ai/nano-banana-pro (generation), fal-ai/nano-banana-pro/edit (edit).
- **Parameters:** aspect_ratio 16:9, resolution 2K, num_images 1, output_format png.
- **Background:** raw/cover-background.png, 2752x1536, md5 0f95d059…, the output of step C2.
  - C's background is unchanged at raw/cover-options/option-C-background.png (md5 fbf4ef41…).
  - The edit was sent C's image as a JPEG q92 data URI, the builder's standard edit input.
- **Cost:** two images at $0.15, $0.30: generation C and edit C2. The four options and the edit together cost $0.75.
- **Cover line:** Over the cap. Before the offseason.
  - Two lines in both formats, verbatim in draft.md under "Everyone over the line".
- **Composition:** unchanged from C.
  - Full-bleed, with a bottom gradient scrim in deep navy and a top-left corner.
  - Red rule; the first line in paper and the second in red.
  - The square is cropped from x 0.30.
  - The scrim solved to 0.59 in the wide format (headline band p95 77, under the ceiling of 78) and 0.25 in the square (the floor).
- **Checked:**
  - **The ball:** at full resolution it is white leather with red stitching, round and undistorted, with no printing, stamp, letters or numbers.
  - **What the edit touched:** I compared C and C2 pixel by pixel. Outside the ball, 0.7% of pixels differ by more than 12%. They are fine-texture differences across the beam's paint, the splinters and the dust, with the same shapes in the same places. The beam, debris layout, floodlights, sky and framing are unchanged.
  - **Marks:** no letters, numbers or marks anywhere, and the floodlights are generic, with no recognizable ballpark.
  - **Safe zone:** the wide type runs from 96,89 to 1006,524, inside the X-card safe zone of 93,84 to 1103,548.
- **Reproduced:** `build_options.py cover` rebuilds both files byte for byte (md5 71efc7bd… wide, 80eec45f… square).

## Step C: generation, seed 5103

- Date: 2026-10-28
- Request: 01a1828a-7971-7221-b43c-b6e8ab7757b3

### Prompt as sent

Cinematic editorial photograph for a publication about the money in sport, lit like a film poster still: high contrast, one hard dramatic key light, deep black shadows, rich dark navy blue tones throughout, and one bold accent of brick red somewhere in the scene. Fine film grain, polished and intense, full-bleed with no empty panel. Subject: A baseball smashing upward through a thick brick red painted wooden beam, splinters and red paint chips frozen in midair, stadium floodlights flaring behind, deep night sky, extreme high speed photograph. Wide 16:9 frame, the scene filling the whole image. The lower third of the frame stays darker and simpler than the rest, with no small objects in it, so a caption can sit over it. The image contains no text of any kind: no letters, words, numbers, digits, captions, signage, scoreboards, labels or watermarks, and every surface that would normally carry writing is blank. No logos, no team marks, no mascots, no team colors or insignia. No people and no faces.

## Step C2: edit of C, seed 5113 (installed)

- Date: 2026-10-28
- Request: 01a183b5-31f1-7771-8128-210c03132700

### Prompt as sent

Edit this photograph. Change only the ball: make it a normal white leather baseball with red stitching, its white leather lit brightly by the same floodlights, still smashing upward through the red painted wooden beam with exactly the same splinters, paint chips and debris flying around it. Keep the beam, the debris, the floodlights, the night sky, the framing and the composition exactly as they are. Nothing is printed or stamped on the ball. The image contains no text of any kind: no letters, words, numbers, digits, captions, signage, scoreboards, labels or watermarks, and every surface that would normally carry writing is blank. No logos, no team marks, no mascots, no team colors or insignia. No people and no faces.
