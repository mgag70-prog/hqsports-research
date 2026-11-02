# Cover options: stadium-subsidies-2026

Four full-bleed options generated on October 31, 2026 by `build_options.py` (fal-ai/nano-banana-pro, seeds 6101 to 6104), four images at $0.15, $0.60 in all. Prompts, seeds and request ids are in `prompts.md`.

**A is installed** as `figures/cover-fal-*.png` as of October 31, 2026, recorded in `figures/cover.json` (seed 6101, request 01a19210-37f7-7553-8434-d79382f42872) and `figures/cover-prompt.md`. `build_options.py cover` reproduces both files byte for byte (md5 d3453142… wide, d10de0a9… square). Every option carries the cover line "Public money. Private stadium." (verbatim in draft.md, "Who keeps the gains"), with the wordmark at top left, a red rule, the first line in paper and the second in red, and a bottom gradient scrim in deep navy. All eight files meet the house luminance ceiling under the type (headline band p95 at most 78), and the wide type is inside the X-card safe zone on all four.

## Ranking

1. **A, the stadium on a pile of gold.** A big-roofed stadium at night with red steel arches, sitting on a glowing heap of plain gold ingots that runs the width of the frame. It's the cover line drawn literally: public money is the foundation, and the building on top is someone else's. It's the flashiest of the four and the square is the strongest crop of the set. Wide type had to come down to 46% of the frame width (scrim 0.84) because the gold runs right behind the headline; the line still reads clearly. Seed 6101.
2. **B, the locked gate.** Red-painted iron gate bars chained and padlocked, with a floodlit empty ballpark glowing behind them and a white baseball (red stitching) on the ground in front. The clearest picture of "private": you paid for it, you're on the wrong side of the gate. It doesn't show the money, so it leans on the type for "Public money." Needed the least scrim (0.25 in both formats). Seed 6102.
3. **D, the jar of coins behind a velvet rope.** A glass jar full of plain gold coins, a white baseball with red stitching on top, red velvet rope and stanchions, floodlights behind. Money and exclusion in one image, and the square works well. It reads a bit like a tip jar or a still life rather than a stadium story, and it's the only one where the headline runs full width in the wide format over a dark field. Seed 6104.
4. **C, the crane lowering a gold bar.** A tower crane lowering one huge gold ingot into a half-built concrete bowl, welding sparks, floodlights. Good drama, but the sparks and red beams sit behind the headline (wide scrim 0.75 at the reduced 46% width), and in the square the wordmark crosses the crane's jib. Seed 6103.

## What was checked

- Full-resolution crops on October 31: no letters, numbers, faces or engraving anywhere. B's stands and field are generic with no signage; D's coins are blank discs; C's crane cab and A's facade carry no marks. No people, no logos, no recognizable real venue.
- The two baseballs (B, D) are white leather with red stitching, round and unmarked, as the brief requires. A and C have no ball.
- Red appears only as the house brick red (gate bars, arches, beams, rope); no team's color scheme is suggested.
- `build_options.py build` reported no overlay text missing from draft.md.
- `contact-sheet.png` is in `.gitignore`, as for the other pieces; `figures/raw/` is already ignored by the repo-wide `*/figures/raw/` rule.

## Settings

- Square crops (`square_crop_x`, left edge as a fraction of the background width): A 0.22, B 0.22, C 0.30, D 0.00. D's crop sits hard left so the ball on the jar clears the wordmark.
- Wide headline for A, B and C: `headline_max_width` 0.46, `headline_max_size` 0.12. At the default 0.76 width the headline band ran over the bright subject and missed the ceiling (scrim at its 0.96 cap); D keeps the default.
