# Vexon Med · Ad #1 · CapCut rebuild kit

This kit rebuilds the finished ad (`../VexonMed_Ad1_GymRegular_9x16.mp4`, one folder up) as an editable CapCut timeline.
It works in CapCut desktop and mobile. `timeline.csv` lists every item with its exact start and end time.

## What's in the kit
| folder | contents |
|---|---|
| `clips/` | 11 shots, each already trimmed, graded, reframed to 9:16 and speed-ramped, at the exact length it runs in the ad. There is no text and no transitions, so you add those in CapCut. Shot 12 is the navy logo slot as a PNG. |
| `layers/` | Transparent 1080×1920 PNGs of every text card and callout graphic, in the exact Vexon styling: Oswald, cream text, orange boxes with navy text, soft shadow and dark legibility band. Each one is pre-positioned inside the Instagram ad safe zone. |
| `audio/` | Original score (120 BPM, 19.5 s), royalty-free. |
| `reference/` | The finished render and storyboard, so you can match it (in the zip; in the repo they sit one folder up). |
| `timeline.csv` | Every item: track, start, end, file, transition, in/out animation. |

## Build it in CapCut (about 15 minutes)
1. **New project, ratio 9:16.** Set the canvas background to navy `#0b1525`.
2. **Main track:** import `clips/01` to `clips/11` and the navy PNG (`12`), in order. Set the PNG's length to 1.5 s.
   The clips butt together at 0, 4, 6, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 14.5, 16.5 and 18 s.
3. **Music:** add `audio/VexonMed_Ad1_score_120bpm.wav` at 0:00. The cuts sit on the beat, so the score's hits land on them.
4. **Overlays:** for each `layers/*.png` file, use *Overlay → Add overlay*. Scale it to fill the canvas (it is already 1080×1920, so just "fit"). Then place it at the times in `timeline.csv`. All positions are baked in, so you don't need to move anything.
5. **Animations:** on each overlay, set the *In* and *Out* animations listed in `timeline.csv`. CapCut renames its presets between versions; if a name differs, pick the closest one:
   - The hook lines use a quick zoom-out "slam" (≈0.2 s).
   - Other text cards slide or wipe up (≈0.3 s).
6. **Transitions:** add the transitions from `timeline.csv` between clips, keeping them short (≤0.3 s; 0.6 s into the logo slot).
   - In CapCut, transitions overlap the clips. After adding them, check that cuts still line up with the music at the times above.
   - For the reaction-time cut, use no transition. Instead, add the *Shake* video effect for about 0.2 s at 11.5 s.
7. **Logo:** add the official Vexon Med logo over the navy slot (18.0–19.5 s).
8. **Export:** 1080p, 30 fps.

## If you'd rather type the text natively in CapCut (editable)
The PNGs match the ad exactly. If you need to edit wording, use native text with these settings:
- **Font:** Oswald SemiBold, ALL CAPS. It's free from Google Fonts; on desktop install it, on mobile use *Text → Font → Import*. Body tags use Public Sans.
- **Colours:** cream `#fbf7ef` (text), orange `#ff7a1a` (highlight boxes and the hook's orange lines), navy `#0b1525` (text on orange).
- **Highlight boxes:** CapCut's text background applies to the whole text box. For per-word boxes, put the highlighted words in a separate text layer with background orange `#ff7a1a` at 100% opacity and navy text.
- **Shadow:** black, about 60% opacity, blur about 12. Also keep `hook_0_band.png` (or a soft black gradient) behind text for legibility.
- **Safe zone:** keep all text within x 65–1015 and y 270–1250 on the 1080×1920 canvas.

## What can't be carried over 1:1
- **Hook font flicker:** the brief font flicker on the hook (4 frames cycling serif / sans before locking to Oswald) can't be reproduced with PNGs.
  - Closest CapCut option: a short *Flicker* / *Glitch* in-animation.
  - Or skip it; the zoom-out slam carries the moment.
- **Animated callouts:** the line scan and pulsing rings are animated in the original render. In the kit they are still frames. Add a *Pulse* loop animation to `fx_cardio_rings.png` for movement.
- **Camera shake:** the shake and colour split on hard transitions are not in the clean clips. Use CapCut's *Shake* effect where you want impact.
