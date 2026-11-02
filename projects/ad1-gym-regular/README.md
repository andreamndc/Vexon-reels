# Vexon Med · Ad #1 · "Gym regular"

- **Deliverable:** `VexonMed_Ad1_GymRegular_9x16.mp4` (1080×1920, 30 fps, **14.23 s**, H.264). It's exported **silent**: add the music in the app.
- **Music:** cut to **"Baboon" (Rj Pasin)**, as used in the reference TikTok (@quincy.visuals).
  - **Grid:** 165 BPM, bars of 2.9085 s with 3+3+2 accents, main drop at 3.007 s.
  - **Cuts:** every cut sits on the song's accents and 8th-note pulses: 3.01 (drop), 4.83, 5.92, 6.46, 7.19, 7.73, 8.28, 8.82, 10.28, 11.73, 12.82. The ad ends at 14.23 to fit the music.
  - **Alignment:** start the song where the reference TikTok starts it, so the drop hits the boxing→rowing cut.
  - **Licensing:** the song is copyrighted and not embedded. For a *paid* ad, the track must be cleared for commercial use (e.g. TikTok/Meta commercial music library or a licence).
- **Hook:** one sentence, *I CAN'T BELIEVE I SCORED AS LOW AS I DID AS A GYM REGULAR.*, on one continuous boxing take. Its lines land on the song's intro hits.
- **Safe zone:** all text stays inside x 65–1015, y 270–1250 (Meta Reels-ad guidance). Every frame is checked (0 violations).
- **Logo:** 12.82–14.23 s is a blank navy slot (`#0b1525`). Add the official logo there.
- **CapCut:** `capcut_kit/` holds the clean shot clips, the transparent text/callout overlays and `timeline.csv` (frame-accurate). See `capcut_kit/CAPCUT_GUIDE.md`.
- **Rebuild:** `source/ad1.plan.json` with `source/render_reel.patched.py`, which adds `sec` durations, `beat_offset`, speed `ramp`, `kicks`, `until`, `box_at`, safe-zone enforcement, `text_in` / `text_out_f`, `--layers`, and the `zoom` / `vwhip` / `fade` transitions. `source/beat_grid.py` is the tempo analysis and `source/build_kit.py` regenerates the CapCut kit from the plan.

| time (s) | section | footage | transition in |
|---|---|---|---|
| 0.00–3.01 | Hook (one sentence) | one boxing take, speed ramp, punch-in on 1.92 | — |
| 3.01–5.92 | Problem | rowing → outdoor machine push | flash on the drop, zoom blur on 4.83 |
| 5.92–8.82 | Indicators (0.5–0.7 s each) | grip, VO2 bike, squat, force-plate feet, reaction tablet | hit, whip, hit, vertical whip, zoom blur |
| 8.82–10.28 | Question | 3D body scan, slow pull-out | zoom punch |
| 10.28–12.82 | Solution | body-composition test → decision-speed results | flash, panels |
| 12.82–14.23 | Logo slot | navy | fade |
