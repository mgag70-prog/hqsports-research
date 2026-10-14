# Cover prompt: illinois-revenue-sharing-2026

Installed October 14, 2026, replacing the ledger-stack cover (seed 4801) after Matt chose option A of four and asked for two edits.
Built by `python3 figures/cover-options/build_options.py cover` from `figures/cover.json` and `raw/cover-background.png` (the A3 image below). `tools/compose_cover.py` was not used for the composition; its panel layout would not reproduce it.

- Model: fal-ai/nano-banana-pro (generation), fal-ai/nano-banana-pro/edit (edits)
- Parameters: aspect_ratio 16:9, resolution 2K, num_images 1, output_format png
- Background: raw/cover-background.png, 2752x1536, the output of step A3
- Cost: three images at $0.15: $0.45
- Cover line: Six schools. Zero dollars by sport. (the wide format breaks it over three lines)
- Composition: full-bleed, bottom gradient scrim in deep navy with a top-left corner, red rule, first line paper and the rest red, square crop from x 0.30

## Step A: generation, seed 4811

- Date: 2026-10-14
- Request: 01a13a94-36d5-7dd0-9d9c-c5d43f97c8e4

### Prompt as sent

Cinematic editorial photograph for a publication about the money in sport, lit like a film poster still: high contrast, one hard dramatic key light, deep black shadows, rich dark navy blue tones throughout, and one bold accent of brick red somewhere in the scene. Fine film grain, polished and intense, full-bleed with no empty panel. Subject: A row of six tall dark steel lockers in an empty locker room, five of them shut with heavy padlocks, the sixth door ajar with bright warm light spilling out of it across the concrete floor. Wide 16:9 frame, the scene filling the whole image. The lower third of the frame stays darker and simpler than the rest, with no small objects in it, so a caption can sit over it. The image contains no text of any kind: no letters, words, numbers, digits, captions, signage, scoreboards, labels or watermarks, and every surface that would normally carry writing is blank. No logos, no team marks, no mascots, no team colors or insignia. No people and no faces.

## Step A2: edit of A, seed 4821

- Date: 2026-10-14
- Request: 01a13aa1-a60f-78a2-b0b8-7ad5fb4e4d94

### Prompt as sent

Edit this photograph. Keep the camera angle, framing, lighting, colors and the concrete floor exactly as they are. Make the row exactly six lockers: five shut with heavy padlocks and one standing open, with the same warm light spilling out of the open door across the floor. Inside the open locker, replace the gray shirt with a plain sleeveless basketball top on a hanger, navy or brick red, with nothing printed on it and no marks of any kind; keep the red gear if it fits. On the floor in front of the lockers, in the light from the open door, add a plain matte navy football helmet with no markings, a football and a basketball. The image contains no text of any kind: no letters, words, numbers, digits, captions, signage, scoreboards, labels or watermarks, and every surface that would normally carry writing is blank. No logos, no team marks, no mascots, no team colors or insignia. No people and no faces.

## Step A3: edit of A2, seed 4831 (installed)

- Date: 2026-10-14
- Request: 01a13aa2-ea85-7652-ae9b-9d75764060c0

### Prompt as sent

Edit this photograph. Keep the camera angle, framing, lighting, the open locker with its warm light, the hanging top, the red gear, the helmet and the two balls on the floor exactly as they are. Two changes only. First, remove the two shut lockers to the right of the open one, so the row is exactly six lockers: five shut with padlocks on the left, then the open one at the end of the row, with plain dark wall beyond it. Second, make the hanging sleeveless top deep navy blue, still with nothing printed on it and no marks of any kind. The image contains no text of any kind: no letters, words, numbers, digits, captions, signage, scoreboards, labels or watermarks, and every surface that would normally carry writing is blank. No logos, no team marks, no mascots, no team colors or insignia. No people and no faces.
