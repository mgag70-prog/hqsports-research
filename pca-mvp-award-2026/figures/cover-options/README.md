# Cover options: pca-mvp-award-2026

Three full-bleed options generated on November 13, 2026 by `build_options.py` (fal-ai/nano-banana-pro, fresh generations, no edits), seeds 9101 to 9103, $0.15 each, $0.45 in all. Prompts, seeds and request ids are in `prompts.md`. The style line is the louder poster one from scarcity-premium-2026, with the house no-text, no-logo, no-people rules appended.

**Option A is installed** (November 13, Matt's pick) as `figures/cover-fal-1200x630.png` and `figures/cover-fal-1080x1080.png`, built by `build_options.py cover` from `figures/cover.json`; both files are byte-identical to `option-A-*.png`. The record is in `figures/cover-prompt.md`.

Every option carries the cover line "$894,000. Most Valuable." (verbatim in draft.md, end of "What the award pays, and who pays it"), composited in code: wordmark top left, red rule, the first line in paper and the second in red, a bottom gradient scrim in deep navy. The "$894,000" is house type, not model output. All six files met the house luminance ceiling under the type (headline band p95 at most 78), and the wide type sits inside the X-card safe zone on all three.

## Ranking

1. **C, the ball on the coin tower.** A white baseball balanced on a leaning stack of blank gold coins, with more coins bursting outward against a red glow. It's the flashiest of the three, and it reads at thumbnail size: the ball sits on top of the money, which is the cover line in one picture. In the square, the ball rose into the wordmark, so the square moves the wordmark up to a baseline at 4.3% of the frame height (the same fix the scarcity cover used). Wide headline width 0.44, size cap 0.14; scrim 0.38 wide, 0.59 square. Seed 9103.
2. **A, the pool full of gold.** A swimming pool at night filled with blank coins, lit navy from below, the ball resting on the gold. It's the only option that draws the piece's actual subject, the pool, and its empty lower third gives the type the cleanest ground of the set (scrim at the 0.25 floor in both formats, and the wide headline can run larger, size cap 0.16). The cost: the ball is small and the picture is the darkest of the three, so it's the least loud at thumbnail, and the pun on "pool" only works for someone who's read the dek. Seed 9101.
3. **B, the trophy.** A plain gold cup with the ball in its mouth, on a black pedestal in front of a red curtain, confetti in a spotlight. It says "Most Valuable" most literally, but it looks like stock art, and the centered trophy fights the type. In the square, "$894,000." crosses the top of the pedestal and needed the heaviest scrim of the set (0.86); the wide headline is held to 0.34 of the frame width to stay left of it. Seed 9102.

## What was checked

- Full-resolution crops on November 13: no letters, numbers, faces or engraving. The coins in A and C have blank faces and edges; B's cup and pedestal are unengraved. No people, no logos, no recognizable real venue.
- All three baseballs are white leather with red stitching, unmarked.
- Colors are navy, gold and brick red. The red curtain in B and the red glow in C sit near Cubs colors, which you said is fine; there are no marks.
- `build_options.py build` reported no overlay text missing from draft.md.
- `contact-sheet.png` is in `.gitignore`; `figures/raw/` is covered by the repo-wide `*/figures/raw/` rule.
