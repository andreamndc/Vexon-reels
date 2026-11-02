#!/usr/bin/env python3
"""Original instrumental score for VEXON MED Ad #1 (120 BPM, 19.5 s). Pure numpy synthesis -> WAV.
Sections (beats): hook 0-8 | problem 8-15 | indicators 15-25 | question 25-29 | solution 29-36 | end 36-39."""
import numpy as np, wave, sys

SR = 44100; BPM = 120; BEAT = 60 / BPM; TOTAL = 19.5 + 0.0
N = int(SR * TOTAL)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
def bt(b): return int(round(b * BEAT * SR))
def hz(m): return 440 * 2 ** ((m - 69) / 12)

def lowpass(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** 4), len(x))
def highpass(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * (f / fc) ** 2 / np.sqrt(1 + (f / fc) ** 4), len(x))
def add(sig, at, gl=1.0, gr=None, samples=False):
    gr = gl if gr is None else gr
    a = int(at) if samples else bt(float(at))
    if a >= N: return
    n = min(len(sig), N - a); L[a:a + n] += sig[:n] * gl; R[a:a + n] += sig[:n] * gr
def env(n, a=0.005, d=None, sus=1.0, rel=0.05):
    e = np.ones(n) * sus; na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na) * (1 if sus else 1)
    nr = max(1, int(rel * SR)); e[-nr:] *= np.linspace(1, 0, nr); return e

# ---------------- pad (detuned saws, soft low-pass, slow swell)
def saw(f, n, det=0.0):
    t = np.arange(n) / SR; ph = rng.random()
    return 2 * ((f * (1 + det) * t + ph) % 1) - 1
def pad(notes, b0, b1, cutoff=1400, vol=0.05, swell=0.4):
    n = bt(b1) - bt(b0) + int(0.6 * SR); sl = np.zeros(n); sr = np.zeros(n)
    for m in notes:
        for k, d in enumerate((-0.006, 0.0, 0.0065)):
            s = saw(hz(m), n, d); pan = (k - 1) * 0.6
            sl += s * (1 - pan) ; sr += s * (1 + pan)
    e = np.ones(n); na = int(swell * SR); e[:na] = np.linspace(0, 1, na) ** 2
    nr = int(0.6 * SR); e[-nr:] *= np.linspace(1, 0, nr)
    sl = lowpass(sl, cutoff) * e * vol / len(notes); sr = lowpass(sr, cutoff) * e * vol / len(notes)
    add(sl, b0, 1, 0); add(sr, b0, 0, 1)

# ---------------- sub bass pulse
def sub(m, b0, b1, step=0.5, vol=0.22, glide=False):
    b = b0
    while b < b1 - 1e-6:
        n = bt(step) ; t = np.arange(n) / SR
        s = np.sin(2 * np.pi * hz(m) * t) + 0.25 * np.sin(4 * np.pi * hz(m) * t)
        e = np.exp(-t * 6) * (1 - np.exp(-t * 400)); s = s * e
        add(s * vol, b); b += step

def kick(b, vol=0.55):
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 30); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7) + 0.25 * rng.normal(0, 1, n) * np.exp(-t * 120)
    add(s * vol, b)
def hat(b, vol=0.05, open_=False):
    n = int((0.18 if open_ else 0.05) * SR); t = np.arange(n) / SR
    s = highpass(rng.normal(0, 1, n), 7000) * np.exp(-t * (18 if open_ else 70))
    p = 0.3 * np.sin(b * 3.1)
    add(s * vol, b, 1 - p, 1 + p)
def clap(b, vol=0.12):
    n = int(0.25 * SR); t = np.arange(n) / SR
    s = lowpass(highpass(rng.normal(0, 1, n), 900), 5000)
    e = np.exp(-t * 22) + 0.6 * np.exp(-((t - 0.012) * 300) ** 2) + 0.5 * np.exp(-((t - 0.024) * 300) ** 2)
    add(s * e * vol, b)
def tick(b, vol=0.04):  # clean "clock" tick — science/measurement feel
    n = int(0.04 * SR); t = np.arange(n) / SR
    add(np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 160) * vol, b)
def bell(m, b, vol=0.07, dec=2.2, pan=0.0):
    n = int(1.6 * SR); t = np.arange(n) / SR; f = hz(m)
    s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t * 3) + 0.12 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 6))
    s *= np.exp(-t * dec) * (1 - np.exp(-t * 600))
    add(s * vol, b, 1 - pan, 1 + pan)
def impact(b, vol=0.6, bright=True):
    n = int(2.2 * SR); t = np.arange(n) / SR
    f = 38 + 70 * np.exp(-t * 14); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 2.2)
    nz = lowpass(rng.normal(0, 1, n), 2500 if bright else 900) * np.exp(-t * 5) * 0.35
    add((s + nz) * vol, b)
def riser(b0, b1, vol=0.10):
    n = bt(b1) - bt(b0); t = np.linspace(0, 1, n)
    nz = rng.normal(0, 1, n); X = np.fft.rfft(nz)
    # sweep: filter progressively by chunk
    out = np.zeros(n); ch = 2048
    for i in range(0, n, ch):
        seg = nz[i:i + ch]; fc = 400 + 7000 * t[min(i, n - 1)] ** 2
        out[i:i + ch] = lowpass(np.pad(seg, (0, ch - len(seg)))[:ch], fc)[:len(seg)]
    tone = np.sin(2 * np.pi * np.cumsum(220 + 660 * t ** 2) / SR) * 0.3
    add((out + tone) * t ** 2.2 * vol, b0)
def reverse_swell(b_end, length=1.5, vol=0.12, m=57):
    n = int(length * SR); t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * hz(m) * t) + 0.5 * np.sin(2 * np.pi * hz(m + 7) * t) + 0.3 * lowpass(rng.normal(0, 1, n), 3000))
    s *= (t / t[-1]) ** 3
    add(s * vol, bt(b_end) - n, samples=True)

# ---------------- arrangement (A minor -> F -> resolve to C)
Am9 = [45, 52, 57, 60, 64, 71]; Fmaj7 = [41, 53, 57, 60, 64]; Dm9 = [38, 50, 57, 60, 64, 65]; C = [36, 48, 55, 60, 64, 67, 74]; G = [43, 50, 55, 59, 62]; Esus = [40, 52, 57, 59, 64]

# HOOK 0-8: tension, curiosity
impact(0, 0.55); pad(Am9, 0, 4, cutoff=900, vol=0.06, swell=0.05)
pad(Am9, 4, 8, cutoff=1300, vol=0.06, swell=0.05)
for b in np.arange(0, 8, 0.25): tick(b, 0.03 if b % 1 else 0.05)
for b, m in [(0, 69), (1, 72), (2, 76), (3.5, 74)]: bell(m, b, 0.06, pan=-0.3)
reverse_swell(4, 1.2, 0.10); impact(4, 0.45)
for b, m in [(4, 76), (4.5, 79), (5, 76), (6, 72), (7, 74)]: bell(m, b, 0.055, pan=0.3)
sub(33, 4, 8, 0.5, 0.16)
# PROBLEM 8-15: groove enters
pad(Fmaj7, 8, 12, cutoff=1600, vol=0.055, swell=0.1); pad(G, 12, 15, cutoff=1700, vol=0.05, swell=0.1)
sub(29, 8, 12, 0.5, 0.2); sub(31, 12, 15, 0.5, 0.2)
for b in range(8, 15): kick(b, 0.45 if b % 2 == 0 else 0.3)
for b in np.arange(8, 15, 0.5): hat(b + 0.25 if False else b + 0.5, 0.045)
for b, m in [(8, 72), (9.5, 76), (10, 77), (12, 74), (13.5, 79), (14, 74)]: bell(m, b, 0.045, pan=-0.2)
# INDICATORS 15-25: energy, a hit on every keyword
impact(15, 0.4)
for i, (ch, root) in enumerate([(Am9, 33), (Fmaj7, 29), (C, 36), (G, 31), (Esus, 28)]):
    b0 = 15 + 2 * i; pad(ch, b0, b0 + 2, cutoff=2200, vol=0.05, swell=0.03); sub(root, b0, b0 + 2, 0.5, 0.22)
    kick(b0, 0.55); kick(b0 + 1, 0.45); clap(b0 + 1, 0.10)
    for h in np.arange(b0, b0 + 2, 0.25): hat(h, 0.05 if h % 0.5 else 0.03)
    bell([81, 84, 79, 83, 86][i], b0, 0.06, dec=3, pan=[-.4, .4, -.2, .2, 0][i])
riser(22.5, 25, 0.12)
# QUESTION 25-29: drop out, suspended, ticking clock
pad(Dm9, 25, 29, cutoff=800, vol=0.07, swell=0.02)
impact(25, 0.5, bright=False)
for b in np.arange(25, 29, 0.5): tick(b, 0.05)
bell(76, 25.5, 0.05, dec=1.5); bell(74, 27, 0.05, dec=1.5); bell(72, 28, 0.045, dec=1.5)
reverse_swell(29, 1.6, 0.14, m=60)
# SOLUTION 29-36: resolve and lift
impact(29, 0.65)
pad(C, 29, 33, cutoff=3000, vol=0.06, swell=0.02); pad(Fmaj7, 33, 36, cutoff=3000, vol=0.055, swell=0.05)
sub(36, 29, 33, 0.5, 0.22); sub(29, 33, 36, 0.5, 0.22)
for b in range(29, 36): kick(b, 0.5);
for b in range(30, 36, 2): clap(b, 0.11)
for b in np.arange(29, 36, 0.25): hat(b, 0.045 if b % 0.5 else 0.028)
for b, m in [(29, 79), (29.5, 84), (30, 83), (31, 79), (32, 76), (33, 77), (33.5, 81), (34, 84), (35, 83)]: bell(m, b, 0.05, pan=0.25 if b % 1 else -0.25)
# END 36-39: final chord rings out under the logo slot
impact(36, 0.45); pad(C, 36, 39, cutoff=1800, vol=0.06, swell=0.02); bell(84, 36, 0.07, dec=1.2); bell(79, 36, 0.05, dec=1.2)

# ---------------- reverb (stereo noise IR), master
def reverb(x, seed, sec=1.8):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = np.random.default_rng(seed).normal(0, 1, n) * np.exp(-t * 3.2); ir[0] = 0
    m = len(x) + n; F = 1 << (m - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
    return y / np.sqrt(np.sum(ir ** 2))
wl = L + 0.22 * reverb(highpass(L, 200), 1); wr = R + 0.22 * reverb(highpass(R, 200), 2)
st = np.stack([wl, wr], 1)
st = np.tanh(st * 1.6) / np.tanh(1.6)           # gentle glue/saturation
fi = int(0.02 * SR); st[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(1.2 * SR); st[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
st = st / np.max(np.abs(st)) * 0.89
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close(); print('wrote', sys.argv[1], TOTAL, 's')
