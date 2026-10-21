# Cover prompt: mlb-floor-2026

Installed October 20, 2026, after Matt chose option F of the six in `figures/cover-options/` (A to D generated, E and F edits).
Built by `python3 figures/cover-options/build_options.py cover` from `figures/cover.json` and `raw/cover-background.png` (the F image below). `tools/compose_cover.py` was not used for the composition; its panel layout would not reproduce it, and its build and generate commands refuse this piece because cover.json names the cover-options builder.

- Model: fal-ai/nano-banana-pro (generation), fal-ai/nano-banana-pro/edit (edits)
- Parameters: aspect_ratio 16:9, resolution 2K, num_images 1, output_format png
- Background: raw/cover-background.png, 2752x1536, the output of step F
- Cost: three images in this chain at $0.15: $0.45 (the six options together cost $0.90)
- Cover line: Under the floor. In the World Series. (two lines in both formats; verbatim in draft.md)
- Composition: full-bleed, bottom gradient scrim in deep navy with a top-left corner, red rule, first line paper and the second red, square crop from x 0.42; wide headline at 56% width so the second line clears the helmets and the ball stack; wide scrim 0.86 (headline band p95 78, the ceiling), square scrim 0.62
- Checked: no logos, letters, numbers or marks on the four helmets at full resolution; bats plain wood; no recognizable ballpark; wide type 96,89 to 768,524 inside the X-card safe zone 93,84 to 1103,548

## Step B: generation, seed 4902

- Date: 2026-10-19
- Request: 01a156d8-06aa-7a33-8cdf-43b6a575250d

### Prompt as sent

Cinematic editorial photograph for a publication about the money in sport, lit like a film poster still: high contrast, one hard dramatic key light, deep black shadows, rich dark navy blue tones throughout, and one bold accent of brick red somewhere in the scene. Fine film grain, polished and intense, full-bleed with no empty panel. Subject: An empty dugout at night, its concrete floor wet and reflective, a painted brick red stripe running straight across the floor, a row of plain wooden bats leaning in the rack and a single glove on the bench, floodlight glare from the field beyond. Wide 16:9 frame, the scene filling the whole image. The lower third of the frame stays darker and simpler than the rest, with no small objects in it, so a caption can sit over it. The image contains no text of any kind: no letters, words, numbers, digits, captions, signage, scoreboards, labels or watermarks, and every surface that would normally carry writing is blank. No logos, no team marks, no mascots, no team colors or insignia. No people and no faces.

## Step E: edit of B, seed 4905

- Date: 2026-10-19
- Request: 01a156fa-e7c8-7df1-900d-eca51aec7867

### Prompt as sent

Edit this photograph. Keep the camera angle, framing, lighting, the wet reflective floor with its painted brick red stripe, the rack of plain wooden bats, the glove on the bench and the lit field beyond exactly as they are. Add a neat pyramid of worn baseballs stacked on the dugout floor in the open space in front of the bench, to the right of the bat rack, lit by the same light. Paint one thick brick red line straight across the dugout's back wall above the bench, well above the top of the stack. The image contains no text of any kind: no letters, words, numbers, digits, captions, signage, scoreboards, labels or watermarks, and every surface that would normally carry writing is blank. No logos, no team marks, no mascots, no team colors or insignia. No people and no faces.

## Step F: edit of E, seed 4906 (installed)

- Date: 2026-10-19
- Request: 01a15700-b313-7ae0-ac16-7a1d42ef1002

### Prompt as sent

Edit this photograph. Keep the dugout, the wet floor with its painted brick red stripe, the rack of plain wooden bats, the glove, the pyramid of baseballs, the red line on the back wall and the lighting exactly as they are, and keep the left side of the frame dark and empty. Add four plain batting helmets in solid colors with no markings of any kind: one all royal blue helmet sitting on the bench, and on the floor beside the pyramid of baseballs, below the red wall line, three navy helmets, one with a gold brim, one with a light blue brim and one with a red brim. The image contains no text of any kind: no letters, words, numbers, digits, captions, signage, scoreboards, labels or watermarks, and every surface that would normally carry writing is blank. No logos, no team marks, no mascots, no team colors or insignia. No people and no faces.
