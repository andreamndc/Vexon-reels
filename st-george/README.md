# GSD St. George reel

**v3 (current): `out/StGeorge_v3_clean.mp4`** — no text; beat-synced layouts and transitions (`render_fx.py`).
Same section timings as v1/v2. Client asked to use the song from 4:01 (beyond the 1:22 TikTok sound, so not analysed
here); the cut keeps the 138.04 BPM bar grid, so start the sound at 4:01 and nudge it until the first whip (1.74 s)
lands on a downbeat.
| time | layout |
|---|---|
| 0–1.74 | exterior push-in |
| 1.74 | whip → window signage |
| 3.48 | zoom punch → 3 strips slide up on 8th notes (hallway, exam room, reception); exam room expands on the last beat |
| 6.95 | exam room full |
| 8.69 | whip → 2×2 grid, panels pop in on beats (equipment, counter, chairs, hallway); zooms into the hallway panel |
| 12.17 | hallway full |
| 13.91 | split screen: reception slides in from the left, exam-room chairs from the right on the next beat |
| 15.65 | whip → reception |
| 17.38 | zoom punch → recap grid (exterior, reception, hallway, exam room); zooms into the exterior |
| 19.12 | exterior full |
| 20.86 | dissolve → end card (blurred exterior, navy wash) for logo + CTA |


9:16, 25.0 s, built from location photos (`photos/`). Format follows the client's new-location reel
(instagram.com/reel/DecLJHPOYEJ): bold italic white serif text with a navy outline, words revealed one at a time,
quick dissolves between sections, slow push-ins on every photo, blurred navy-washed end card for the GSD logo.

Music: cut to the TikTok sound @mayoutfitofficial/7308589082270027013 (138.04 BPM, bar 1.738 s), segment from
0:14.12 where the bass enters. Cuts land on the bar, words appear on the beat. The video is exported with a
silent track (copyrighted song): add the sound in-app starting at 0:14.1.

**v2 (current): `out/StGeorge_v2_clean.mp4` — no text (client adds text); same cut.** Render with `--notext`.

Render: `python3 render.py out/StGeorge_v1.mp4 [--logo white_logo.png] [--notext]` (`--stills 1.5,8.0` for frame checks).

| time | photo | text |
|---|---|---|
| 0–3.48 | exterior, then push to the window signage | ST. GEORGE, UTAH! / Looking for a dermatologist? |
| 3.48–6.95 | reception, hallway push | EXPERT DERMATOLOGIC CARE, CLOSE TO HOME. |
| 6.95–12.17 | exam room: wide, equipment, counter | MEDICAL & PEDIATRIC DERMATOLOGY |
| 12.17–17.38 | hallway, reception, exam-room chairs | GREAT AVAILABILITY. / CARE FOR THE WHOLE FAMILY. |
| 17.38–20.86 | reception pull-out, exterior | GET THE CARE YOU NEED, WHEN YOU NEED IT. |
| 20.86–25.0 | end card (blurred exterior) | logo slot + SCHEDULE YOUR VISIT IN ST. GEORGE. |
