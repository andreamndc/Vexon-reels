"""Original upbeat arrangement of "Jingle Bells" (J. Pierpont, 1857 - public domain).
160 BPM, 4/4, 16 bars of chorus + final hit = ~25 s. Bar = 1.5 s, beat = 0.375 s.
Writes song.mid; render with fluidsynth + FluidR3_GM (MIT licensed soundfont)."""
import mido, sys

BPM = 160
TPB = 480
mid = mido.MidiFile(ticks_per_beat=TPB)
events = {}  # channel -> list of (tick, msg)

def note(ch, start_beats, dur_beats, pitch, vel):
    s = int(start_beats * TPB); e = int((start_beats + dur_beats) * TPB) - 10
    events.setdefault(ch, []).append((s, mido.Message('note_on', channel=ch, note=pitch, velocity=vel)))
    events.setdefault(ch, []).append((e, mido.Message('note_off', channel=ch, note=pitch, velocity=0)))

# --- melody (in C), (pitch name, beats) per bar ------------------------------
N = {'C': 72, 'D': 74, 'E': 76, 'F': 77, 'G': 79, 'A': 81, 'B': 83, 'g': 67}
A = [[('E', 1), ('E', 1), ('E', 2)],
     [('E', 1), ('E', 1), ('E', 2)],
     [('E', 1), ('G', 1), ('C', 1.5), ('D', .5)],
     [('E', 4)],
     [('F', 1), ('F', 1), ('F', 1.5), ('F', .5)],
     [('F', 1), ('E', 1), ('E', 1), ('E', .5), ('E', .5)]]
melody = A + [[('E', 1), ('D', 1), ('D', 1), ('E', 1)], [('D', 2), ('G', 2)]] + \
         A + [[('G', 1), ('G', 1), ('F', 1), ('D', 1)], [('C', 4)]]
chords = ['C', 'C', 'C', 'C', 'F', 'C', 'D7', 'G7', 'C', 'C', 'C', 'C', 'F', 'C', 'G7', 'C']
CH = {'C': [48, 52, 55, 60, 64], 'F': [53, 57, 60, 65, 69], 'G7': [55, 59, 62, 65, 67],
      'D7': [50, 54, 57, 60, 66], 'Am': [57, 60, 64, 69]}
ROOT = {'C': 36, 'F': 41, 'G7': 43, 'D7': 38}
FIFTH = {'C': 43, 'F': 36, 'G7': 38, 'D7': 45}

# channels: 0 glockenspiel lead, 1 piano, 2 bass, 3 strings pad, 4 brass stabs, 5 celesta double, 9 drums
programs = {0: 9, 1: 0, 2: 33, 3: 48, 4: 61, 5: 8}
for bar, notes in enumerate(melody):
    t = bar * 4
    for name, d in notes:
        note(0, t, min(d, 1.2), N[name], 108)
        note(5, t, d * 0.95, N[name] - 12, 70)
        t += d

for bar, c in enumerate(chords):
    b0 = bar * 4
    # piano: bouncy off-beat chops ("oom-pah" pop feel)
    for k in range(4):
        note(1, b0 + k + .5, .4, CH[c][1], 62); note(1, b0 + k + .5, .4, CH[c][2], 62)
        note(1, b0 + k + .5, .4, CH[c][3], 60)
    # bass: root / fifth walking quarters
    for k, p in enumerate([ROOT[c], FIFTH[c], ROOT[c] + 12, FIFTH[c]]):
        note(2, b0 + k, .9, p, 96)
    # strings pad from bar 4
    if bar >= 4:
        for p in CH[c][1:4]:
            note(3, b0, 4, p + 12, 52)
    # brass stabs on the last phrase for a lift
    if bar >= 12:
        for p in CH[c][2:5]:
            note(4, b0, .5, p, 78); note(4, b0 + 2.5, .5, p, 70)

# --- drums ---------------------------------------------------------------------
KICK, SNARE, HAT, CRASH, TAMB, JINGLE, CLAP = 36, 38, 42, 49, 54, 83, 39
for bar in range(16):
    b0 = bar * 4
    for k in range(8):
        note(9, b0 + k * .5, .25, JINGLE, 92 if k % 2 == 0 else 70)   # sleigh bells on 8ths
    if bar < 2:                                                        # lighter intro
        note(9, b0, .5, KICK, 90); note(9, b0 + 2, .5, KICK, 90)
        continue
    for k in range(4):
        note(9, b0 + k, .5, KICK if k % 2 == 0 else SNARE, 100 if k % 2 == 0 else 88)
        if k % 2: note(9, b0 + k, .5, CLAP, 70)
    for k in range(8):
        note(9, b0 + k * .5 + .25 * 0, .2, HAT, 50)
    if bar in (2, 4, 8, 12):
        note(9, b0, 1, CRASH, 95)
    if bar in (3, 7, 11):          # little snare fill into the next phrase
        for k in range(4):
            note(9, b0 + 3 + k * .25, .2, SNARE, 70 + k * 8)
# final hit (bar 16)
end = 16 * 4
for p in CH['C']:
    note(1, end, 5, p, 90); note(3, end, 5, p + 12, 70); note(4, end, 1, p + 12, 85)
note(0, end, 3, 84, 110); note(5, end, 4, 72, 80); note(2, end, 5, 36, 100)
note(9, end, 2, CRASH, 110); note(9, end, 1, KICK, 110)
for k in range(4):
    note(9, end + k * .5, .25, JINGLE, 90 - k * 15)

for ch in sorted(events):
    tr = mido.MidiTrack(); mid.tracks.append(tr)
    if ch == min(events):
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM)))
    if ch != 9:
        tr.append(mido.Message('program_change', channel=ch, program=programs[ch]))
        tr.append(mido.Message('control_change', channel=ch, control=91, value=50))  # reverb
    last = 0
    for t, m in sorted(events[ch], key=lambda x: (x[0], x[1].type == 'note_on')):
        tr.append(m.copy(time=t - last)); last = t
mid.save(sys.argv[1] if len(sys.argv) > 1 else 'song.mid')
print('bars=16, seconds to final hit =', 16 * 4 * 60 / BPM)
