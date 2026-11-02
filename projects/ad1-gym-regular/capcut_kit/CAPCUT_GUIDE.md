# Vexon Med · Ad #1 · CapCut rebuild kit (cut to “Baboon”)

This kit rebuilds the finished ad (`../VexonMed_Ad1_GymRegular_9x16.mp4`, one folder up; also in `reference/` in the zip) as an editable CapCut timeline.
It works in CapCut desktop and mobile. `timeline.csv` lists every item with its exact start and end time, as seconds plus frame number at 30 fps.

## Music: "Baboon" (Rj Pasin), as used in the reference TikTok
The edit is cut to that track's beat grid:
- **Tempo:** 165 BPM.
- **Accents:** each bar is 2.9085 s, with accents in a 3+3+2 pattern.
- **Drop:** the main drop is at **00:03.01**.

Every cut lands on an accent: 3.01, 4.83, 7.01, 7.73, 8.82, 9.91, 10.64, 11.73, 13.55, 15.73 and 17.55 s. The ad ends on the bar line at 19.37 s.

The song is **not included**; it's copyrighted. Add it in CapCut, TikTok or Instagram, and start it at the same point the reference TikTok does (its first hit at about 0.1 s and the drop at 3.01 s). The quickest way on TikTok is *Use this sound* on the reference video. Check that the drop hits exactly on the cut from boxing to rowing.

## What's in the kit
| folder | contents |
|---|---|
| `clips/` | 11 shots, each already trimmed, graded, reframed to 9:16 and speed-ramped, at the exact frame length it runs in the ad. There is no text and no transitions. Shot 12 is the navy logo slot as a PNG. |
| `layers/` | Transparent 1080×1920 PNGs of every text card and callout, in the exact Vexon styling, pre-positioned inside the Instagram ad safe zone. |
| `timeline.csv` | Every item: track, start, end, file, transition, in/out animation. |

## Build it in CapCut (about 15 minutes)
1. **New project, ratio 9:16, 30 fps.** Set the canvas background to navy `#0b1525`.
2. **Main track:** import `clips/01` to `clips/11` and the navy PNG (`12`), in order. Set the PNG's length to 1.83 s (55 frames).
3. **Music:** add "Baboon" from 0:00, aligned as above.
4. **Overlays:** for each `layers/*.png`, use *Overlay → Add overlay*. Set it to fill the canvas (already 1080×1920) and place it at the times in `timeline.csv`. Positions are baked in.
5. **Hook (one sentence):** the four hook lines build the sentence on the song's intro hits (0.10, 0.46, 0.83 and 1.19 s). All four stay on screen together until the drop at 3.01 s. Use a quick zoom-out "slam" in-animation (about 0.2 s).
6. **Other overlays:** set the *In* and *Out* animations from `timeline.csv`. If a CapCut preset name differs in your version, pick the closest one.
7. **Transitions:** keep them short (≤0.3 s). CapCut overlaps clips during transitions, so re-check that every cut still sits on the beat.
   - For the strength cut (7.01 s), use no transition. Instead, add the *Shake* effect for about 0.2 s.
8. **Logo:** add the official Vexon Med logo over the navy slot (17.55–19.37 s).
9. **Export:** 1080p, 30 fps.

## Native, editable text (optional)
- **Font:** Oswald SemiBold in ALL CAPS (free on Google Fonts). Use Public Sans for tags.
- **Colours:** cream `#fbf7ef`, orange `#ff7a1a` (highlight boxes and the hook's orange lines), navy `#0b1525` (text on orange).
- **Highlight boxes:** for per-word boxes, put the highlighted words on their own text layer with an orange background.
- **Shadow:** black, about 60% opacity, blur about 12.
- **Safe zone:** keep all text within x 65–1015 and y 270–1250.

## Not carried over 1:1
- **Hook font flicker:** the brief font flicker on the hook can't be reproduced with PNGs. Use a short *Flicker* / *Glitch* in-animation, or skip it.
- **Animated callouts:** the line scan and pulsing rings are still images here. A *Pulse* loop on the rings adds movement.
- **Camera shake:** the shake and colour split on hard transitions are not in the clean clips. Use CapCut's *Shake* effect.
