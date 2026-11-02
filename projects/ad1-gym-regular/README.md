# Vexon Med · Ad #1 · "Gym regular"

- **Deliverable:** `VexonMed_Ad1_GymRegular_9x16.mp4` (1080×1920, 30 fps, 19.5 s, H.264 + AAC, -14 LUFS)
- **Music:** `VexonMed_Ad1_score_120bpm.m4a`, an original instrumental composed for this ad (`source/score.py`, pure synthesis, no samples). It is royalty-free and cleared for paid social.
- **Logo:** 18.0–19.5 s is a blank navy slot (`#0b1525`). Add the official logo there.
- **Rebuild:** `source/ad1.plan.json` and `source/render_reel.patched.py`. The patched renderer is the vexon-reel-editor renderer plus speed `ramp`, hook words with `until`, `box_at`, and the `zoom` / `vwhip` / `fade` transitions. Clip keys map to the uploads 1102_11…15.

| time | section | footage | transition in |
|---|---|---|---|
| 0.0–4.0 | Hook (2 beats) | boxing, speed ramp → rowing | whip |
| 4.0–7.5 | Problem | rowing (match cut) → outdoor machine | cut, zoom blur |
| 7.5–12.5 | Indicators | grip, VO2 bike, squat, force-plate feet, reaction tablet | flash, whip, cutout, vertical whip, hit |
| 12.5–14.5 | Question | 3D body scan, slow-mo pull-out, music drops out | zoom punch |
| 14.5–18.0 | Solution | body-composition test → decision-speed results | flash, panels |
| 18.0–19.5 | Logo slot | navy | fade |
