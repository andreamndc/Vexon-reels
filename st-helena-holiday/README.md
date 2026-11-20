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

## Cut map (brief sections snapped to the bar grid)
| time | bars | visuals | brief text (added later) |
|---|---|---|---|
| 0.0–3.0 | 1–2 (light intro) | Dr. Strunck hero shot, walking/working in clinic | ST. HELENA, YOUR HOLIDAY SAVINGS ARE HERE! |
| 3.0–7.5 | 3–5 (drums in) | Strunck b-roll + treatments, cut every 1.5 s | 20% OFF COSMETIC SERVICES … |
| 7.5–12.0 | 6–8 | Consultation, Strunck with patient, treatment room | THINKING ABOUT A COSMETIC TREATMENT? … |
| 12.0–16.5 | 9–11 (crash) | SkinLab shelves, product close-ups, application | 20% OFF SKINCARE … |
| 16.5–21.0 | 12–14 (brass lift at 18) | More Strunck b-roll, clinic details | HOLIDAY SAVINGS IN ST. HELENA |
| 21.0–25.0 | 15–16 + final hit | End card: GSD/Duncan Dermatology + SkinLab logos | BOOK YOUR CONSULTATION. SHOP SKINLAB. |
