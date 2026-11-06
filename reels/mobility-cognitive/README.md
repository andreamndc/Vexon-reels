# VEXON Med · "Functional capacity isn't just muscle" reel

9:16 · 29.95 s · 30 fps · cut to the supplied **"Salgo Pa' la Calle"** clip (Daddy Yankee):
**90.02 BPM** (1 beat = 0.6665 s), first downbeat **0.355 s** into the clip. The video starts with a 0.355 s
lead-in, so the sound starts at **0:00** of the video.

Two exports:
- `..._WITH_MUSIC.mp4`: the supplied clip is 20.0 s long, so it is extended by jumping from bar 7 (19.02 s)
  back to bar 3 (8.35 s). Both bars share the song's 2-bar chord cycle, so the jump sits on a downbeat.
  Loudness is normalised to -14 LUFS, with a 0.8 s fade-out.
- `..._SILENT.mp4`: for adding the sound in the Instagram app. Start it at the same point as the clip (0:00).

## Beat sheet (music time = video time)

| time | beat | moment |
|---|---|---|
| 0.36 | 0 | Downbeat: "FUNCTIONAL" slams in |
| 1.02 / 1.69 | 1 / 2 | "CAPACITY ISN'T" / "JUST MUSCLE." |
| 3.02 | 4 | Bar 2: whip pan to the tablet + "IT'S"; "COGNITIVE," on 4.5 |
| 5.02 | 7 | Flash into "Most longevity-focused organizations..." |
| 7.69 | 11 | Cutout into "But how well you move also involves" |
| 9.69 | 14 | Whip into "how your brain processes information," |
| 11.69 | 17 | Cutout into "coordinates movement, and responds to your environment." |
| 13.69 | 20 | Bar 5 downbeat: indicators begin (scan wipe every 1.5 beats) |
| 17.68 | 26 | Flash into "These signals matter, too." |
| 19.68 | 29 | Cutout into "We look at the physical and beyond." |
| 21.68 | 32 | Bar 8 downbeat: whip into "We incorporate neurocognitive testing" |
| 23.35 | 34.5 | Cut into "into a more comprehensive view of performance and functional healthspan." |
| 26.35 | 39 | Zoom punch into the CTA: "Book an assessment with Vexon Med." |
| 28.35 | 42 | Fade to the navy logo slot (1.6 s) |

## Re-render
Put the raw clips in `footage/` (1101.mp4, IMG_0038.MP4, IMG_0043.MP4, IMG_0047.MP4), then:

```bash
python3 scripts/storyboard.py plan.json out/storyboard.png
python3 scripts/render_reel.py plan.json out/render.mp4
bash scripts/finalize.sh out/render.mp4 out/VexonMed_FunctionalCapacity_Reel_SILENT.mp4
bash scripts/finalize.sh out/render.mp4 out/VexonMed_FunctionalCapacity_Reel_WITH_MUSIC.mp4 path/to/music_bed.wav 0
```

## Safe zone
All text sits inside **x 90–960, y 270–1350**. That keeps it clear of the Instagram top bar, the caption/username
area at the bottom and the Like/Comment/Share buttons on the right. Check any change with:

```bash
python3 scripts/render_reel.py plan.json x --audit
```

## Renderer additions (on top of the skill's render_reel.py)
- `"tin": "scan"`: an orange scan line wipes down to reveal the next shot (calm, no shake). Used for the four indicators.
- `"tin": "fade"`: a soft dissolve, used into the end slot.
- `fx.kind = "neural"`: a subtle node network whose links draw in, with soft pulses travelling along them.
- `beat_offset` (top level, in seconds): the music's first downbeat. The beat pulse locks to it.
- `box_beats`: when the orange highlight box wipes in. Short shots get it earlier automatically.
