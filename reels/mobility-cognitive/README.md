# VEXON Med · "Mobility isn't just muscle" reel

9:16 · 29.4 s · 30 fps · cut to **"Salgo Pa' la Calle" (Daddy Yankee)** at ~95 BPM (1 beat = 0.632 s).
Built with the vexon-reel-editor skill (house style v6). Exported with a silent audio track: add the sound in-app.

## Adding the sound
Start the song on a strong downbeat (the first kick after the intro) at 0:00. Key hits land on these beats:

| time | beat | moment |
|---|---|---|
| 0.00 | 0 | Hook: "MOBILITY ISN'T" |
| 0.63 | 1 | "JUST MUSCLE." |
| 1.89 | 3 | Whip pan to the tablet + "IT'S" |
| 2.21 | 3.5 | "COGNITIVE," (orange) |
| 3.79 | 6 | Flash into "Most longevity-focused organizations..." |
| 6.32 | 10 | Cutout into "But how well you move..." |
| 8.21 | 13 | Whip into "how your brain processes information," |
| 10.11 | 16 | Cutout into "coordinates movement, and responds to your environment." |
| 12.32 | 19.5 | Indicators: scan wipes every 1.5 beats (01-04) |
| 16.11 | 25.5 | Flash into "These signals matter, too." |
| 18.00 | 28.5 | Cutout into "We look at the physical and beyond." |
| 19.89 | 31.5 | Whip into "We incorporate neurocognitive testing" |
| 21.47 | 34 | Cut into "into a more comprehensive view..." |
| 24.32 | 38.5 | Zoom punch into the CTA |
| 27.79 | 44 | Fade to the navy logo slot (1.6 s; add the logo here) |

## Re-render
Put the raw clips in `footage/` (1101.mp4, IMG_0038.MP4, IMG_0043.MP4, IMG_0047.MP4), then:

```bash
python3 scripts/storyboard.py plan.json out/storyboard.png
python3 scripts/render_reel.py plan.json out/render.mp4
bash scripts/finalize.sh out/render.mp4 out/VexonMed_Mobility_Cognitive_Reel.mp4
```

## Renderer additions (on top of the skill's render_reel.py)
- `"tin": "scan"`: an orange scan line wipes down to reveal the next shot (calm, no shake). Used for the four indicators.
- `"tin": "fade"`: a soft dissolve, used into the end slot.
- `fx.kind = "neural"`: a subtle node network whose links draw in, with soft pulses travelling along them.
- `box_beats`: when the orange highlight box wipes in. Short shots get it earlier automatically.
