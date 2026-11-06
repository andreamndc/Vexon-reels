# Vexon Med · Ad #1 · CapCut rebuild kit (20 s, cut to the @asrpromedia sound)

This kit rebuilds the finished ad (`../VexonMed_Ad1_GymRegular_9x16.mp4`, one folder up; also in `reference/` in the zip) as an editable CapCut timeline.
It works in CapCut desktop and mobile. `timeline.csv` lists every item with its exact start and end time, as seconds plus frame number at 30 fps.

## Music: "original sound" by @asrpromedia (the reference TikTok)
The edit is cut to that sound's beat grid:
- **Tempo:** 118 BPM, with a beat every 0.508 s and a bar every 2.03 s.
- **Structure:** the first beat is at **00:00.50**. Full energy runs to 16.26 s, where the outro begins, and the sound ends at 20.2 s.

The ad is **20.0 s**. Every cut sits on a beat or half-beat: 3.80, 5.58, 7.11, 7.87, 8.63, 9.39, 10.16, 10.92, 12.95, 14.22 (the downbeat after the break), 16.26 (outro, fade to navy), 17.53 and 18.80 s.

The sound is **not included**: it belongs to the TikTok creator. On TikTok, use *Use this sound* on the reference video. In CapCut, import it and start it at 0:00. Check that the fade to navy lands exactly where the outro starts (16.26 s).

## What's in the kit
| folder | contents |
|---|---|
| `clips/` | 11 shots, each already trimmed, graded, reframed to 9:16 and speed-ramped, at the exact frame length it runs in the ad. There is no text and no transitions. Clips 12–14 are navy (`#0b1525`) PNGs: two text cards and the empty logo slot. |
| `layers/` | Transparent 1080×1920 PNGs of every text card and callout, in the exact Vexon styling, pre-positioned inside the Instagram ad safe zone. |
| `timeline.csv` | Every item: track, start, end, file, transition, in/out animation. |

## Build it in CapCut (about 15 minutes)
1. **New project, ratio 9:16, 30 fps.** Set the canvas background to navy `#0b1525`.
2. **Main track:** import `clips/01` to `clips/14`, in order. Set the navy PNGs to 1.27 s, 1.27 s and 1.20 s (38, 38 and 36 frames), so the timeline ends at 20.00 s.
3. **Music:** add the @asrpromedia sound from 0:00.
4. **Overlays:** for each `layers/*.png`, use *Overlay → Add overlay*. Set it to fill the canvas (already 1080×1920) and place it at the times in `timeline.csv`. Positions are baked in.
5. **Hook (one sentence):** line 1 is on screen from the first frame. Lines 2–4 land on the first three beats (0.50, 1.00 and 1.51 s), and the whole sentence holds until 3.80 s. Use a quick zoom-out "slam" in-animation (about 0.2 s).
6. **Other overlays:** set the *In* and *Out* animations from `timeline.csv`. If a CapCut preset name differs in your version, pick the closest one.
7. **Transitions:** keep them short (≤0.3 s). CapCut overlaps clips during transitions, so re-check that every cut still sits on the beat.
   - The five indicator shots are 0.76 s each, so keep transitions there at ≤0.2 s.
   - For the cut into Reaction time (10.16 s), use no transition. Instead, add the *Shake* effect for about 0.2 s.
   - Into the first navy card (16.26 s), use a ~0.45 s dissolve. Its text starts at 16.47 s.
8. **End cards:** "THIS IS FUNCTIONAL CAPACITY." (16.26–17.53 s) and "THIS IS VEXON MED." (17.53–18.80 s) on navy, with orange boxes on the key words.
9. **Logo:** add the official Vexon Med logo over the empty navy slot (18.80–20.00 s).
10. **Export:** 1080p, 30 fps.

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
