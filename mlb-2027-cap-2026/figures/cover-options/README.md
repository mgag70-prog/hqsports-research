# Cover options: mlb-2027-cap-2026

Four full-bleed options generated on October 28, 2026 by `build_options.py` (fal-ai/nano-banana-pro, seeds 5101 to 5104), plus C2, an edit of C's background. That's five images at $0.15, $0.75 in all. Prompts, seeds and request ids are in `prompts.md`.

**C2 is installed** as `figures/cover-fal-*.png` as of October 28, 2026, replacing C, which was installed earlier the same day. It's recorded in `figures/cover.json` (edit chain C, seed 5103, to C2, seed 5113) and `figures/cover-prompt.md`. `build_options.py cover` reproduces both files byte for byte (md5 71efc7bd… wide, 80eec45f… square). Every option carries the cover line "Over the cap. Before the offseason." (verbatim in draft.md, "Everyone over the line"), with the wordmark at top left, a red rule, the first line in paper and the second in red, and a bottom gradient scrim in deep navy. Every format met the house luminance ceiling, and the wide type is inside the X-card safe zone on all five.

## C2: C with a white ball (installed)

- **The edit:** C's background run through `fal-ai/nano-banana-pro/edit` (seed 5113, request 01a183b5-31f1-7771-8128-210c03132700). It was told to change only the ball, to a normal white leather baseball with red stitching lit by the same floodlights, and to keep the beam, debris, floodlights, sky and composition.
- **The ball:** at full resolution it's white with red stitching, round, undistorted and unmarked, so no retry was needed.
- **The rest of the frame:** I compared it with C pixel by pixel. Outside the ball, 0.7% of pixels differ by more than 12%. They're fine texture across the beam's paint, the splinters and the dust, with the same shapes in the same places.
- **The type:** same cover line, square crop and settings as C, and the scrim solved to the same values (0.59 wide, 0.25 square). The wide type is inside the X-card safe zone.
- **Why:** this addresses the risk noted for C below. The ball no longer reads heavy against the sky at thumbnail size.


1. **C, the ball through the red beam.** A baseball smashing up through a thick red-painted beam, splinters and paint chips frozen in the air, floodlights at both edges. It's the loudest of the four and the cover line drawn literally: the ball is going over, and through, the line. The lower half is almost empty dark field, so the type needed the least help (scrim 0.59 wide, 0.25 square, the floor), and the beam's red picks up the red rule and the second line. The square crop keeps the ball and the break centered. Risk: a dark ball on a dark sky reads a touch heavy at thumbnail size, and the beam could read as a fence rail rather than a ceiling. Seed 5103.
2. **A, the overflowing glass tank.** A clear tank under a single spotlight, packed past a red line painted round it near the top, balls spilling over the rim and across the floor. The most exact picture of the argument, money already past the line with more still coming. Quieter than C, and in the wide format the tank is small in the middle of a lot of black; the square is the stronger crop. Seed 5101.
3. **B, the gold ingots and the red rope.** A pile of plain gold ingots on infield dirt at night, a red rope stretched across in front, fog and a floodlight behind. The gold makes the money explicit and it's the most cinematic image, but the rope crosses the pile low, so the picture says "behind a barrier" as much as "over the cap." The wide headline runs at 36% width so line one ends before the pile; it's smaller than on the other three. Flag: the out-of-focus stadium boards at left and right carry blurred shapes that look like lettering. Nothing is readable at full resolution, and the left boards sit under the scrim, but it's the one option that comes close to the no-text rule. Seed 5102.
4. **D, the batting cage.** Netting sagging under a heap of balls piled above a low red rail, balls spilling through onto the dirt. Handsome and the most baseball-specific, but the red rail is a low brick wall, so "over" reads weakly, and it's the least flashy of the four. Seed 5104.

## What was checked

- Full-resolution crops on October 28: C's ball shows stitching only; B's background boards are blurred, with no readable letters or numbers; A's and D's balls show stitching only. No logos, uniforms, people or numbers in any image, and no recognizable real ballpark (B, C and D are generic).
- `build_options.py build` reported no overlay text missing from draft.md.
- `contact-sheet.png` (now ten tiles, C2 last) is in `.gitignore`, as for the other pieces.

## How C, then C2, was installed, for the record

Copied option C's two PNGs to `figures/cover-fal-1200x630.png` and `-1080x1080.png`, put its background at `figures/raw/cover-background.png`, and wrote `figures/cover.json` with `"builder": "cover-options"`, the cover line as `headline`, and the option's `square_crop_x`, then added `figures/cover-prompt.md`, as the floor piece did. `python3 figures/cover-options/build_options.py cover` then reproduces it.

C2 replaced it the same way. Its two PNGs were copied over `figures/cover-fal-*.png` and its background over `figures/raw/cover-background.png`; C's own background stays at `figures/raw/cover-options/option-C-background.png`. `cover.json` gained an `edits` list (step C2, endpoint, `edit_of` C, seed, request, date), as the Illinois cover records its A > A2 > A3 chain, and `cover-prompt.md` was rewritten with both steps.
