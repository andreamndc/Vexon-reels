# Grand Opening recap reel

9:16, 22.45 s. Cut on the exact cut points of the reference TikTok
(https://www.tiktok.com/@bonsoirindonesia/video/7600338656771034388, ~103 BPM), so the edit lines up when
that sound is added in TikTok/Instagram **starting at 0:00**. The song is copyrighted, so the files are
exported with a silent audio track; add the sound in-app.

Outputs (`out/`):
- `GrandOpening_v1_text.mp4`: with text ("Welcome to our Grand Opening", "We're so glad to be here for you!",
  "Thank you for coming out!"), white Cinzel with a navy outline plus Great Vibes script (both OFL, in `fonts/`).
- `GrandOpening_v1_clean.mp4`: same edit, no text.

Render: `python3 render.py <media_dir> out/GrandOpening_v1` (writes both). `--stills 1.0,5.5` renders frames to check.
`<media_dir>` holds the uploaded .MOV clips plus the HEIC photos converted to JPG (pillow-heif) and the wide
ribbon-cutting photo saved as `ribbon_wide.jpg`. The shot list is `SHOTS` in render.py (one line per cut).

| time | shot |
|---|---|
| 0–2.33 | door with balloons swings open → Welcome sign (quiet intro, title) |
| 2.33 (white flash on the beat drop) – 4.70 | ribbon scissors photo → ribbon-cutting group |
| 4.70–5.90 | 4-panel grid (products, waiting room, orchid tray, doctor's portrait), panels pop in on 8th notes |
| 5.90–10.00 | one-beat detail cuts: champagne, glasses, gift bags, products, catering, reception |
| 10.00–14.70 | guests and staff, doctor greeting guests ("We're so glad…" 10.00–12.83) |
| 14.70–15.77 | split: wide ribbon-cutting photo / guests |
| 15.77–20.63 | doctor's portrait, display, reception table, snacks, staff, towels, welcome table |
| 20.63–22.45 | end on the Welcome sign ("Thank you for coming out!") |
