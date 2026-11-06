# Vexon Med · Ad #1 · "Gym regular"

- **Deliverable:** `VexonMed_Ad1_GymRegular_9x16.mp4` (1080×1920, 30 fps, **20.0 s**, H.264). It's exported **silent**: add the music in the app.
- **Music:** cut to the **"original sound" on @asrpromedia's TikTok** (video 7421228470077754667).
  - **Grid:** 118 BPM (beat 0.508 s, bar 2.03 s), first beat at 0.50 s; outro from 16.26 s; the sound ends at 20.2 s.
  - **Cuts:** every cut sits on a beat or half-beat: 3.80, 5.58, 7.11, 7.87, 8.63, 9.39, 10.16, 10.92, 12.95, 14.22, 16.26 (fade to navy on the outro), 17.53, 18.80.
  - **Licensing:** the sound belongs to the TikTok creator and is not embedded. For a *paid* ad, use audio cleared for commercial use.
- **Copy:**
  - Hook: *I CAN'T BELIEVE I SCORED AS LOW AS I DID AS A GYM REGULAR.*, one sentence on one continuous boxing take, on screen from the first frame.
  - Body: problem line, five indicators, question, solution.
  - End cards on navy: *THIS IS FUNCTIONAL CAPACITY.* then *THIS IS VEXON MED.*
- **Pacing:** text runs at ≈3–3.6 words/s at most; each indicator word holds 0.76 s.
- **Safe zone:** all text stays inside x 65–1015, y 270–1250 (Meta Reels-ad guidance). Every frame is checked (0 violations).
- **Logo:** 18.80–20.00 s is an empty navy slot (`#0b1525`). Add the official logo there.
- **CapCut:** `capcut_kit/` holds the clean clips, transparent text/callout overlays, navy card PNGs and `timeline.csv` (frame-accurate). See `capcut_kit/CAPCUT_GUIDE.md`.
- **Rebuild:** `source/ad1.plan.json` with `source/render_reel.patched.py`. `source/build_kit.py` regenerates the CapCut kit and `source/beat_grid.py` does the tempo analysis. The previous 14.23 s "Baboon" cut is kept as `source/ad1_baboon_14s.plan.json`.

| time (s) | section | footage | transition in |
|---|---|---|---|
| 0.00–3.80 | Hook (one sentence) | one boxing take, speed ramp, punch-in on the bar at 2.02 | — |
| 3.80–7.11 | Problem | rowing → outdoor machine push | whip, zoom blur |
| 7.11–10.92 | Indicators (0.76 s each) | grip, VO2 bike, squat, force-plate feet, reaction tablet | flash, whip, cutout, vertical whip, hit |
| 10.92–12.95 | Question | 3D body scan, slow pull-out | zoom punch |
| 12.95–16.26 | Solution | body-composition test → decision-speed results | flash, panels |
| 16.26–17.53 | "This is functional capacity." | navy | dissolve |
| 17.53–18.80 | "This is Vexon Med." | navy | — |
| 18.80–20.00 | Logo slot | navy (empty) | — |
