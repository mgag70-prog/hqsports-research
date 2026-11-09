# Cover options: lockout-countdown-2026, week 1

Three full-bleed options generated on November 4, 2026 by `build_options.py` (fal-ai/nano-banana-pro, seeds 7101 to 7103), three images at $0.15, $0.45 in all. Prompts, seeds and request ids are in `prompts.md`.

**C is installed** as `figures/cover-fal-*.png` as of November 5, 2026, recorded in `figures/cover.json` (seed 7103, request 01a1aa05-b82a-7650-b251-e68d9093521d) and `figures/cover-prompt.md`. `build_options.py cover` reproduces both files byte for byte (md5 fa316d4b… wide, 162630de… square). Every option carries the cover line "26 days. Same lines." (verbatim in draft.md, "Same lines, nearly the same clubs"), composited in code, with the wordmark at top left, a red rule, the first line in paper and the second in red, and a bottom gradient scrim in deep navy. The "26" is house type, not model output. All six files met the house luminance ceiling under the type (headline band p95 at most 78), and the wide type is inside the X-card safe zone on all three.

## Ranking

1. **C, the hourglass.** A huge hourglass in a pool of light on the infield, red sand running out onto a white baseball, with chalk lines running off both sides. "26 days" reads before you've read anything, and the chalk lines carry "Same lines." It's the flashiest of the three and the square is the best file in the set. The wide headline had to come down to 33% of the frame width (scrim 0.81) to stay left of the glass, so it's the smallest type of the three in that format. The prompt asked for a pitcher's mound and the model drew something closer to home plate; nobody will mind, but it isn't a mound. Seed 7103.
2. **A, the chained door.** A blank brick-red door at the end of a concrete tunnel, chain and brass padlock, hard dawn light, a white baseball on a ledge. It's the plainest picture of a lockout, and the type sits on dark floor at full size. It says "locked" more than "countdown", so it leans on the headline for the 26 days, and the wide scrim (0.70) dims the left half of the door. Seed 7101.
3. **B, the dying light bank.** A wall of stadium bulbs mostly dead, a few still burning red and white, sparks falling. It's the countdown-light idea without a single digit, and the sparks are the loudest thing in the set. But the wordmark lands on the bulb frame and loses contrast in both formats, and the picture is the hardest of the three to read at thumbnail size. Seed 7102.

## What was checked

- Full-resolution crops on November 4: no letters, numbers, faces or engraving. A's door, padlock and ledge are blank. B's lit bulbs are scattered and form no digit or shape. C's glass and bases carry nothing. No people, no logos, no recognizable real venue.
- The two baseballs (A, C) are white leather with red stitching, round and unmarked. B has no ball.
- Red appears only as house brick red (door, sand, bulbs); no team's color scheme is suggested.
- `build_options.py build` reported no overlay text missing from draft.md.
- `contact-sheet.png` and `figures/raw/` are in `.gitignore` by explicit path, because the repo's one-level rules don't reach a piece two folders down.

## Settings

- Square crops (`square_crop_x`): 0.22 on all three.
- Wide headline for C: `headline_max_width` 0.33, `headline_max_size` 0.12. At the default width the headline ran over the hourglass and missed the ceiling with the scrim at its 0.96 cap. A and B keep the default.
