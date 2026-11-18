# Cover options: cbb-revenue-share-2026

Three full-bleed options generated on November 17, 2026 by `build_options.py` (fal-ai/nano-banana-pro, fresh generations, no edits), seeds 9201 to 9203, $0.15 each, $0.45 in all. Prompts, seeds and request ids are in `prompts.md`. The style line is the poster one from pca-mvp-award-2026 with a basketball line in place of the baseball one (plain orange ball, black seams, no printing; plain hardwood with no painted center emblem) and the house no-text, no-logo, no-people rules appended.

**Option A is installed** (November 17, Matt's pick) as `figures/cover-fal-1200x630.png` and `figures/cover-fal-1080x1080.png`, built by `build_options.py cover` from `figures/cover.json`; both files are byte-identical to `option-A-*.png`. The record is in `figures/cover-prompt.md`.

**Lining figures.** Georgia Bold has only old-style figures (no lnum feature), so its "0" read like a lowercase "o". `build_options.py` now sets digits in Charter Bold, which has lining figures, scaled to the height of Georgia Bold's "O", and A was rebuilt that way and checked at 600px. B and C were built before the change and still show the old-style zero; rerun `build_options.py build B C` if either is ever wanted.

Every option carries the cover line "$0 for the median player." (verbatim in draft.md, end of the second paragraph of "Who got paid in men's basketball"), composited in code: wordmark top left, red rule, the first line in paper and the second in red, a bottom gradient scrim in deep navy. The "$0" is house type, not model output. All six files met the house luminance ceiling under the type (headline band p95 at most 78), and the wide type sits inside the X-card safe zone on all three.

## Ranking

1. **C, the ball through the net with gold coins.** An orange ball dropping through a white net, blank gold coins spilling through with it, a red glow behind a plain glass backboard. It's the loudest of the three and reads at thumbnail size. It's mirrored so the hoop sits right of the type (nothing in the image to reverse), and the mirrored spotlight landed on the wordmark, so the wide corner darkening is boosted. Wide headline width 0.36, size cap 0.11, so the wide type is small; square crop x 0.21, where a couple of coins sit just above "$0 for the". Seed 9203.
2. **A, the empty bench.** A row of empty folding chairs along a dark sideline, one ball under the last chair, red-lit upper deck behind. It's the closest picture to the cover line (a roster's worth of seats, nobody paid to sit in them), the type sits on the cleanest ground of the set, and it runs the largest headline. The cost: it's the darkest and quietest of the three, and the ball is small. House defaults, no overrides. Seed 9201.
3. **B, gold on half the court.** Coins pouring through a beam of light onto one side of the floor, the ball at the edge of the pile. The idea fits the piece best on paper (some of the roster gets money, the rest doesn't), but the bright floor sits where the type goes: it's mirrored, the wide headline is held to 0.40 of the frame width, and both formats needed the type band darkened locally after the scrim alone missed the ceiling. Square crop x 0.40. Seed 9202.

## What was checked

- Full-resolution crops on November 17: no letters, numbers, faces or logos. The coins in B and C have blank faces. The balls are orange with black seams and no printing.
- A's upper-left arena wall has a dark scoreboard-like panel with a few soft blurred blobs on it; nothing in it reads as characters at full resolution, and it falls under the wordmark corner darkening.
- C's backboard carries the standard white shooter's square and B's floor shows a plain painted circle and lines; neither is a mark or text.
- Colors are navy, gold, orange and brick red; no team or conference colors are meant, and there are no marks.
- No people and no recognizable real arena.
- `build_options.py build` reported no overlay text missing from draft.md.
- `contact-sheet.png` is in `.gitignore`; `figures/raw/` is covered by the repo-wide `*/figures/raw/` rule.
