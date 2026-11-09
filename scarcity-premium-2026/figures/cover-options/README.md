# Cover options: scarcity-premium-2026

Three full-bleed options generated on November 5, 2026 by `build_options.py` (fal-ai/nano-banana-pro). Four images at $0.15, $0.60 in all: option B was generated twice, because the first (seed 8102) drew a blueprint title block with fake lettering in the corner. Its record stays in `prompts.md`; the option here is seed 8104.

**C is installed** as `figures/cover-fal-*.png` as of November 5, 2026, recorded in `figures/cover.json` (seed 8103, request 01a1abf2-3140-7862-bdd0-829c450f541f) and `figures/cover-prompt.md`. `build_options.py cover` rebuilds both (md5 634fffed… wide, 2e7b42ca… square). The wide matches the option file byte for byte. The installed square moves the wordmark up, to a baseline at 4.3% of the frame height, so it clears the scale's chain; `option-C-1080x1080.png` keeps the old position. Every option carries the cover line "Sold above the estimate." (verbatim in draft.md, "The answer"), composited in code on two lines, with the wordmark at top left, a red rule, the first line in paper and the second in red, and a bottom gradient scrim in deep navy. All six files met the house luminance ceiling under the type (headline band p95 at most 78), and the wide type is inside the X-card safe zone on all three.

## Ranking

1. **C, the baseball outweighing the gold.** A brass balance scale with one white baseball pulling its pan down and a stack of gold lifted high. It's the only option that draws the cover line: the team is worth more than the figure on the other side. The red curtain gives it the most color at thumbnail size. In the option file's square the wordmark crosses the scale's chain, fixed on the installed cover, and in the wide the ball is fairly small. The background is mirrored (`flip`) so the ball clears the headline. Seed 8103.
2. **B, the gavel on the gold.** A gavel smashing into a stack of plain ingots over a blue stadium drawing, gold and red sparks everywhere. It's the flashiest of the three and the square is the loudest file in the set. It says "auction" more than "above the estimate", so the type carries the argument, and the wide needed the heaviest scrim (0.79). Seed 8104.
3. **A, the paddle on the lectern.** A blank wooden paddle and a baseball on a cushion in a dark saleroom with empty gilt frames. It has the cleanest type area, but the paddle reads a bit like a ping-pong bat and the picture is the quietest of the three. Seed 8101.

## What was checked

- Full-resolution crops on November 5: no letters, numbers, faces or engraving. A's paddle is bare wood and its frames are empty. C's ingots and scale are unmarked. B's ingots are plain, and the ruled box in the corner of the drawing has lines only, confirmed on a full-resolution crop, and falls outside the square crop. No people, no logos, no recognizable real venue.
- The two baseballs (A, C) are white leather with red stitching, round and unmarked. B has no ball.
- Red appears only as house brick red (curtains, sparks); no team's color scheme is suggested.
- `build_options.py build` reported no overlay text missing from draft.md.
- `contact-sheet.png` is in `.gitignore`; `figures/raw/` is covered by the repo-wide `*/figures/raw/` rule.

## Settings

- Square crops (`square_crop_x`): 0.22 on all three. C is mirrored before cropping.
- Wide headline: A and B `headline_max_width` 0.36, C 0.44, all `headline_max_size` 0.12, so the type stays clear of the subject.
