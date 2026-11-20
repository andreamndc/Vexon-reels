# GSD St. George reel

**v4 (current): `out/StGeorge_v4_clean.mp4`** — no text; beat-synced layouts and transitions (`render_fx.py`).
Sound starts at **0:04.1** of the TikTok sound. From that start the song's first downbeat is at 1.421 s and the bass
enters at 10.113 s; every cut sits on the bar grid 1.421 + n × 1.7384 s.
| time | layout |
|---|---|
| 0–1.42 | exterior push-in (intro) |
| 1.42 | whip → window signage |
| 3.16 | zoom punch → 3 strips slide up on 8th notes (hallway, exam room, reception); exam room expands on the last beat |
| 6.64 | exam room full |
| 8.38 | whip → equipment close-up |
| 10.11 | bass entry: zoom punch → 2×2 grid pops in on 8th notes (counter, chairs, reception, hallway); zooms into the hallway |
| 11.85 | hallway full |
| 13.59 | split screen: reception from the left, exam-room chairs from the right on the next beat |
| 15.33 | whip → reception |
| 17.07 | zoom punch → recap grid (exterior, reception, hallway, exam room); zooms into the exterior |
| 18.81 | exterior full |
| 20.54 | dissolve → end card (blurred exterior, navy wash) for logo + CTA |


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
