# Cover options: lockout-countdown-2026, week 2

Two full-bleed options generated on November 11, 2026 by `build_options.py`. Both are edits of week 1's installed hourglass background (`week-01/figures/raw/cover-background.png`) through fal-ai/nano-banana-pro/edit, seeds 7201 and 7202, at $0.15 each, $0.30 in all. Prompts, seeds and request ids are in `prompts.md`.

**Option B is installed** (November 11) as `figures/cover-fal-1200x630.png` and `figures/cover-fal-1080x1080.png`, built by `build_options.py cover` from `figures/cover.json`; the record is in `figures/cover-prompt.md`. Both options carry the cover line "20 days. $11 million." (verbatim in draft.md, "The money that has moved this time"), composited in code the way week 1's was: wordmark top left, red rule, the first line in paper and the second in red, a bottom gradient scrim in deep navy, and week 1's settings for this background (square crop at x 0.22; wide headline held to 33% of the frame width, size cap 0.12). The "20" and "$11" are house type, not model output. All four files met the house luminance ceiling under the type (headline band p95 78 wide, 67 to 68 square), and the wide type runs from 96,89 to 493,533, inside the X-card safe zone on both.

## Ranking

1. **B, the top bulb mostly drained.** This is the one that does what the series needs. Set beside week 1, the top sand sits clearly lower and the bottom bulb is much fuller, so a reader who saw last week's cover can tell time has passed without reading anything. The scene, floodlight, haze, home-plate chalk and glass held. The ball rests on top of the pile, fully visible, at about week 1's size. The one flaw: the bottom sand is a tilted flat slope rather than a cone under the stream, which is physically a bit off. You notice it at full size, not at thumbnail. Wide scrim 0.83. Seed 7202.
2. **A, the deeper pile.** The bottom bulb filled up and the ball sank into a proper cone, which looks more natural than B's. But the top bulb barely changed. Its sand line sits only a little below week 1's, so the prompt's main ask (noticeably less on top) isn't met, and side by side with week 1 the cover reads as "more sand" rather than "less time". The model also widened the bottom bulb slightly. Wide scrim 0.82. Seed 7201.

If B's slope bothers you, the next step would be one more edit of B's background asking for a conical pile, at $0.15, then `build_options.py cover` again. I haven't run it.

## What was checked

- Full-resolution crops of the glass on November 11, compared with week 1's background: no letters, numbers, faces or engraving. The faint red disc inside the top of the glass is a reflection of the sand, carried over from week 1. No people, no logos, no recognizable real venue.
- The baseball is white leather with red stitching, unmarked, in both.
- Red appears only as house brick red in the sand.
- `build_options.py build` reported no overlay text missing from draft.md.
- `contact-sheet.png` and `figures/raw/` are covered by the lockout-countdown rules in the repo's `.gitignore` (lines 41 and 42).
