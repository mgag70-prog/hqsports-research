# Cover options: mlb-floor-2026

Six full-bleed options (A to D generated, E and F edits); **F is installed** as `figures/cover-fal-*.png` as of October 20, 2026, with the chain recorded in `figures/cover.json` and `figures/cover-prompt.md`. Cover line on all four: "Under the floor. In the World Series." (verbatim in draft.md, section 1). Wordmark top left, red rule, first line paper and second line red, bottom gradient scrim in deep navy, X-card safe zone checked on the wide format. Built October 19, 2026 by `build_options.py`; prompts, seeds and request ids in `prompts.md`. Four generations at $0.15: $0.60.

## Ranking

1. **D, the ball and the red tape line.** One baseball on a dark hardwood floor, a strip of red tape across the floor just above it. It's the cover line drawn literally: the ball sits under the line. Reads at thumbnail size, nothing competes with the type, and the red tape runs straight into the red rule above the headline. Seed 4904.
2. **A, the stack of baseballs under the painted line.** The outline's own idea. The red line on the wall sits well above the pyramid, so the metaphor holds, and the spotlight gives it the drama Matt asked for. Busier than D at small sizes; the stack is 15 or so balls and the stitching goes to texture on a phone. Seed 4901.
3. **C, the outfield wall at night.** Floodlights, mist, a red line along the padded wall. The most cinematic of the four and the type sits beautifully on the dark warning track, but the line reads as a wall stripe rather than a floor, so the picture carries less of the argument. Seed 4903.
4. **B, the empty dugout.** Wet concrete, a painted red stripe, a rack of plain bats and a glove, the field lit beyond. Handsome, and the stripe is a floor line, but the bats pull the eye from the type and the bright field at upper left needed the heaviest scrim of the four (0.60). Seed 4902.

## Option E: A combined into B (added October 19 at Matt's request)

An edit of B's background through the fal.ai edit endpoint, seed 4905, one more image at $0.15: the dugout as shot, with A's pyramid of baseballs added on the floor to the right of the bat rack and one red line painted across the back wall above the bench. The floor stripe, bats, glove and lit field are unchanged. On the wide format the headline runs three lines at 41% width so the stack stays clear of the type; the square keeps two lines under the stack. The wide headline band missed the house luminance ceiling (p95 87 against 78) even at the maximum scrim because of the wet floor's reflections; it reads fine to my eye, but it is the one option that didn't clear the automated check. If the dugout wins, E over B: the stack gives the picture the "under" the line needs.

## Option F: E plus four plain batting helmets (added October 19 at Matt's request)

An edit of E's background through the fal.ai edit endpoint, seed 4906, request 01a15700-b313-7ae0-ac16-7a1d42ef1002, one image at $0.15; the first seed was accepted, no retry needed. Added: an all-royal-blue helmet on the bench, and on the floor beside the ball stack, below the wall line, three navy helmets with a gold brim (left of the stack), a light blue brim and a red brim (right of it). Full-resolution crops of all four show solid color only: no logos, letters, numbers or marks. Dugout, bats, glove, balls, floor stripe, wall line and lighting unchanged; the left side stayed dark. Cover line on two lines in both formats; the wide headline runs at 56% width (type 96,89 to 768,524) so line two clears the gold-brim helmet and the stack, and the global scrim at 0.86 brought the headline band to p95 78, the ceiling, so the local band-darkening step wasn't needed. Square scrim 0.62, both zones met. Installed October 20, 2026: the option-F PNGs copied to `figures/cover-fal-1200x630.png` and `-1080x1080.png`, F's background to `figures/raw/cover-background.png`; `build_options.py cover` reproduces both files byte for byte (md5 58a74c11… wide, a16ce6a6… square).

## What was checked before installing

- No option carries readable text, numbers, logos or uniforms. The baseballs show stitching only; the bats in B are plain wood. Full-resolution crops of A's stack, B's bats and D's ball were checked on October 19.
- None of the four shows a recognizable real ballpark: A and D are interiors, B and C are generic.
- The outline's other idea, a scoreboard, was skipped: the house prompt rules ban scoreboards because they invite lettering.
- How F was installed, for the record: copy its two PNGs to `figures/cover-fal-1200x630.png` and `-1080x1080.png`, put its background at `figures/raw/cover-background.png`, and write `figures/cover.json` with `"builder": "cover-options"`, the cover line as `headline`, and the option's `square_crop_x`, as the Illinois piece did; then `python3 figures/cover-options/build_options.py cover` reproduces it and `tools/compose_cover.py build` refuses.
