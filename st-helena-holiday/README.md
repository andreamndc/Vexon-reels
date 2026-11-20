# St. Helena Holiday Promo — Dr. Strunck reel ad (Duncan Dermatology & SkinLab)

9:16, 25 s, no voiceover. Text overlays are added by the client's editor, so the
render is a clean cut with music. Footage goes in `footage/`.

## Music — `music/holiday_track.wav` (25.0 s, -14 LUFS)
Original arrangement of "Jingle Bells" (James Lord Pierpont, 1857: public domain),
written in `music/make_song.py` and rendered with the FluidR3_GM soundfont (MIT licence).
No third-party recording or sample library, so it is royalty-free for paid ads.
Rebuild: `python3 make_song.py song.mid && fluidsynth -ni -g 0.6 -r 48000 -F raw.wav FluidR3_GM.sf2 song.mid`

160 BPM: 1 bar = 1.5 s. Drums enter with a crash at 3.0 s; more crashes at 6.0, 12.0, 18.0 s;
brass lift from 18.0 s; final hit at 24.0 s, ring-out to 25.0 s.

## v3 render — `out/StHelena_Holiday_Reel_v3.mp4` (24.27 s, current)
Same as v2, but opens on Dr. Strunck walking through the office (`1120.mp4`, 0–3.37 s); the treatment shot moves to the beat drop (3.37–4.72 s) and the laser set-up shot is shortened (4.72–6.07 s).

## v2 render — `out/StHelena_Holiday_Reel_v2.mp4` (24.27 s)
Music: client-supplied "A Lofi Wonderland" by Mizlo (Epidemic Sound) — place the WAV at
`music/ES_A_Lofi_Wonderland_-_Mizlo.wav` (not committed; licensed asset). 88.99 BPM, beat 0.6742 s; the track starts
at 7.402 s so its beat drop lands at 3.37 s; -1 dB, 1 s fade-out (the track ends abruptly).
Section changes (all on beats): 3.37 snow sweep · 8.76 star iris · 12.81 candy-cane ribbon · 16.86 star iris ·
20.90 snow sweep into the end card. No sparkle/lights. Cuts inside sections land on kicks.
`python3 render.py <footage_dir> music/ES_A_Lofi_Wonderland_-_Mizlo.wav out/StHelena_Holiday_Reel_v2.mp4`

## v1 render — `out/StHelena_Holiday_Reel_v1.mp4`
`python3 render.py <footage_dir> music/holiday_track.wav out/StHelena_Holiday_Reel_v1.mp4` (shot list is `SHOTS` in render.py;
`--stills 1.0,12.5` renders single frames for quick checks). Clean picture, no text; warm grade, sub-pixel push-ins,
cuts on the bar, 0.35 s dissolves at section changes, gold sparkle on the opener and end card.
Footage used (Nov 12 clips): 3:34:32 PM treatment, 3:32:46 PM laser setup, 2:15:05 PM shelf pan, 2:15:30 PM serum pick-up,
2:16:39 PM product box, 2:01:25 PM tray + Elf on the Shelf, 2:16:57 PM SkinLab shelf (blurred end card).
Not used: 3:34:32 PM_1 (duplicate), 2:15:17 PM (horizontal duplicate of shelf pan), 2:01:14 PM / 2:16:21 PM (spares).

## Cut map (brief sections snapped to the bar grid)
| time | bars | visuals | brief text (added later) |
|---|---|---|---|
| 0.0–3.0 | 1–2 (light intro) | Dr. Strunck hero shot, walking/working in clinic | ST. HELENA, YOUR HOLIDAY SAVINGS ARE HERE! |
| 3.0–7.5 | 3–5 (drums in) | Strunck b-roll + treatments, cut every 1.5 s | 20% OFF COSMETIC SERVICES … |
| 7.5–12.0 | 6–8 | Consultation, Strunck with patient, treatment room | THINKING ABOUT A COSMETIC TREATMENT? … |
| 12.0–16.5 | 9–11 (crash) | SkinLab shelves, product close-ups, application | 20% OFF SKINCARE … |
| 16.5–21.0 | 12–14 (brass lift at 18) | More Strunck b-roll, clinic details | HOLIDAY SAVINGS IN ST. HELENA |
| 21.0–25.0 | 15–16 + final hit | End card: GSD/Duncan Dermatology + SkinLab logos | BOOK YOUR CONSULTATION. SHOP SKINLAB. |
