"""GSD St. George reel v3 - photo edit with beat-synced multi-photo layouts and transitions (no text; the client
adds text). 9:16, 25 s, 138.04 BPM grid (beat 0.4346 s, bar 1.7384 s) from the TikTok sound
@mayoutfitofficial/7308589082270027013. Sound starts at 0:04.1 (4.01 s); first downbeat lands at 1.421 s, bass enters at 10.113 s.
Exported silent: add the sound in-app starting at 0:04.1.

Layouts: full photo (push-in + 2-beat pulse), 3 vertical strips (slide up on 8th notes, middle strip expands to
full screen), 2x2 grid (panels pop in on beats, then the grid zooms into one panel), top/bottom split (halves
slide in from opposite sides on consecutive beats). Transitions: whip pan with motion blur, zoom punch, dissolve.

Usage: python3 render_fx.py <out.mp4> [--stills t1,t2,...]"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageFilter

W, H, FPS, TOTAL = 1080, 1920, 30, 25.0
BEAT = 0.4346; BAR = 4 * BEAT
OUT = sys.argv[1]
STILLS = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')] if '--stills' in sys.argv else None
HERE = os.path.dirname(os.path.abspath(__file__))
NAVY = (14, 30, 66); GAP = 10

OFF = 0.216 + 12 * BEAT - 4.01     # song beat grid (phase 0.216 s) seen from a 4.01 s start = 1.4212 s
def b(n): return 0.0 if n == 0 else round(OFF + (n - 1) * BAR, 4)   # b(1) = first downbeat
def P(name, z=(1.0, 1.06), c=(.5, .5), c1=None): return (name, z, c, c1 or c)

EXAM_WIDE = P('exam_room', (1.0, 1.06), (.62, .55), (.64, .55))
HALL_PUSH = P('hallway', (1.30, 1.42), (.45, .50))
EXTERIOR = P('exterior', (1.0, 1.12), (.45, .55), (.55, .55))
SHOTS = [
    # 0-3.16  location: exterior push-in (intro), whip to the window signage on the first downbeat
    dict(t0=b(0), t1=b(1), kind='full', p=P('exterior', (1.0, 1.08), (.42, .55), (.40, .55)), tin='cut'),
    dict(t0=b(1), t1=b(2), kind='full', p=P('exterior', (1.45, 1.55), (.33, .47), (.31, .47)), tin='whip'),
    # 3.16-6.64  interior: 3 strips slide up on 8th notes, middle (exam room) expands on the last beat
    dict(t0=b(2), t1=b(4), kind='strips', ps=[P('hallway', (1.0, 1.05), (.48, .55)), EXAM_WIDE,
                                               P('reception', (1.0, 1.05), (.5, .55))], tin='punch'),
    # 6.64-11.85  medical: exam room, whip to the equipment, grid pops in on the bass entry (10.11) and zooms into the hallway
    dict(t0=b(4), t1=b(5), kind='full', p=EXAM_WIDE, tin='cut'),
    dict(t0=b(5), t1=b(6), kind='full', p=P('exam_room', (1.55, 1.62), (.70, .42)), tin='whip'),
    dict(t0=b(6), t1=b(7), kind='grid', step=BEAT / 2, ps=[P('exam_room', (1.45, 1.50), (.50, .48)),
                                            P('exam_room', (1.25, 1.30), (.20, .62)),
                                            P('reception', (1.35, 1.42), (.5, .60)), HALL_PUSH],
         zoomto=3, tin='punch'),
    # 11.85-17.07  availability: hallway, split screen, reception
    dict(t0=b(7), t1=b(8), kind='full', p=HALL_PUSH, tin='cut'),
    dict(t0=b(8), t1=b(9), kind='split', ps=[P('reception', (1.0, 1.05), (.5, .45)),
                                             P('exam_room', (1.15, 1.2), (.30, .62))], tin='cut'),
    dict(t0=b(9), t1=b(10), kind='full', p=P('reception', (1.12, 1.0), (.5, .55)), tin='whip'),
    # 17.07-20.54  recap grid of the whole clinic, zoom into the exterior, then the exterior
    dict(t0=b(10), t1=b(11), kind='grid', step=BEAT / 2, ps=[EXTERIOR, P('reception', (1.0, 1.04)), P('hallway', (1.0, 1.04)),
                                              P('exam_room', (1.0, 1.04), (.62, .55))], zoomto=0, tin='punch'),
    dict(t0=b(11), t1=b(12), kind='full', p=EXTERIOR, tin='cut'),
    # 20.54-25  end card: blurred exterior with navy wash, clear for logo + CTA
    dict(t0=b(12), t1=TOTAL, kind='end', p=P('exterior', (1.05, 1.10), (.45, .55)), tin='dissolve'),
]

# ---------------------------------------------------------------------------------------------
_photos = {}
def photo(name):
    if name not in _photos:
        im = Image.open(os.path.join(HERE, 'photos', name + '.jpg')).convert('RGB')
        s = 2600 / max(im.size)
        if s > 1: im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        _photos[name] = im
    return _photos[name]

def ease(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)
def eout(u): u = min(max(u, 0), 1); return 1 - (1 - u) ** 3

def view(spec, u, w, h, extra=1.0):
    """Crop of a photo spec at shot progress u (0-1), sized w x h; same framing at any output size."""
    name, (z0, z1), (x0, y0), (x1, y1) = spec
    img = photo(name); e = ease(u)
    z = (z0 + (z1 - z0) * e) * extra; cx = x0 + (x1 - x0) * e; cy = y0 + (y1 - y0) * e
    a = w / h
    bw, bh = (img.height * a, img.height) if img.width / img.height > a else (img.width, img.width / a)
    cw, ch = bw / z, bh / z
    l = min(max(cx * img.width - cw / 2, 0), img.width - cw); tp = min(max(cy * img.height - ch / 2, 0), img.height - ch)
    return img.resize((w, h), Image.BICUBIC, box=(l, tp, l + cw, tp + ch))

def pulse(t, t0):
    """Small zoom bump every 2 beats."""
    k = (t - t0) % (2 * BEAT)
    return 1 + 0.025 * math.exp(-k / 0.12)

def frame(s, t):
    t0, t1 = s['t0'], s['t1']; u = (t - t0) / (t1 - t0)
    if s['kind'] == 'full':
        return view(s['p'], u, W, H, pulse(t, t0))
    if s['kind'] == 'end':
        img = view(s['p'], u, W, H).filter(ImageFilter.GaussianBlur(14))
        return Image.blend(img, Image.new('RGB', (W, H), NAVY), 0.45)
    out = Image.new('RGB', (W, H), NAVY)
    if s['kind'] == 'strips':
        sw = W // 3
        exp = ease((t - (t1 - BEAT)) / BEAT)               # middle strip expands over the last beat
        for j, sp in enumerate(s['ps']):
            full = view(sp, u, W, H)
            if j == 1:
                l = round(sw * (1 - exp)); r = round(2 * sw + (W - 2 * sw) * exp)
                out.paste(full.crop((l, 0, r, H)), (l, 0)); continue
            # side strips slide up on 8th notes, then slide away as the middle one expands
            y = round(H * (1 - eout((t - t0 - j * BEAT / 2) / 0.28)))
            dx = round((-1 if j == 0 else 1) * sw * exp)
            x = j * sw + dx
            out.paste(full.crop((j * sw, 0, (j + 1) * sw, H)), (x + (GAP // 2 if j == 2 else 0), y))
        if exp <= 0:   # middle strip also slides up on its 8th note
            yy = round(H * (1 - eout((t - t0 - BEAT / 2) / 0.28)))
            mid = view(s['ps'][1], u, W, H).crop((sw, 0, 2 * sw, H))
            out.paste(Image.new('RGB', (sw, H), NAVY), (sw, 0)); out.paste(mid, (sw + GAP // 2, yy))
        return out
    if s['kind'] == 'grid':
        pw, ph = (W - GAP) // 2, (H - GAP) // 2
        for j, sp in enumerate(s['ps']):
            k = (t - t0 - j * s.get('step', BEAT)) / 0.18  # panel j pops in on beat (or 8th note) j
            if k < 0: continue
            sc = 0.7 + 0.3 * eout(k)
            tile = view(sp, u, pw, ph)
            if sc < 1: tile = tile.resize((max(1, round(pw * sc)), max(1, round(ph * sc))), Image.BICUBIC)
            x = (j % 2) * (pw + GAP) + (pw - tile.width) // 2; y = (j // 2) * (ph + GAP) + (ph - tile.height) // 2
            out.paste(tile, (x, y))
        if 'zoomto' in s:                                  # zoom into the chosen panel over the last beat
            z = ease((t - (t1 - BEAT)) / BEAT)
            if z > 0:
                j = s['zoomto']; px, py = (j % 2) * (pw + GAP), (j // 2) * (ph + GAP)
                box = (px * z, py * z, W + (px + pw - W) * z, H + (py + ph - H) * z)
                out = out.resize((W, H), Image.BICUBIC, box=box)
        return out
    if s['kind'] == 'split':
        ph = (H - GAP) // 2
        top = view(s['ps'][0], u, W, ph); bot = view(s['ps'][1], u, W, ph)
        xt = round(-W * (1 - eout((t - t0) / 0.25))); xb = round(W * (1 - eout((t - t0 - BEAT) / 0.25)))
        out.paste(top, (xt, 0)); out.paste(bot, (xb, ph + GAP))
        return out

def whip(a, c, p):
    """Horizontal whip: a exits left, c enters from the right, with motion blur."""
    A, C = np.asarray(a, np.float32), np.asarray(c, np.float32)
    acc = np.zeros_like(A); n = 7
    for k in range(n):
        off = int(round((p + (k - n // 2) * 0.035) * W)); off = min(max(off, 0), W)
        fr = np.empty_like(A)
        fr[:, :W - off] = A[:, off:]; fr[:, W - off:] = C[:, :off]
        acc += fr
    return Image.fromarray((acc / n).astype(np.uint8))

def picture(t):
    i = max(j for j, s in enumerate(SHOTS) if s['t0'] <= t)
    s = SHOTS[i]; img = frame(s, t)
    # whip spans 0.12 s either side of the cut
    for j in (i, i + 1):
        if 0 < j < len(SHOTS) and SHOTS[j]['tin'] == 'whip':
            T = SHOTS[j]['t0']
            if T - 0.12 <= t < T + 0.12:
                return whip(frame(SHOTS[j - 1], t), frame(SHOTS[j], t), ease((t - (T - 0.12)) / 0.24))
    if s['tin'] == 'punch' and t - s['t0'] < 0.2:
        z = 1 + 0.15 * (1 - eout((t - s['t0']) / 0.2))
        img = img.resize((W, H), Image.BICUBIC, box=(W * (1 - 1 / z) / 2, H * (1 - 1 / z) / 2,
                                                     W - W * (1 - 1 / z) / 2, H - H * (1 - 1 / z) / 2))
    if s['tin'] == 'dissolve' and t - s['t0'] < 0.3:
        img = Image.blend(frame(SHOTS[i - 1], t), img, ease((t - s['t0']) / 0.3))
    return img

GRADE = 'eq=contrast=1.05:saturation=1.08,colorbalance=rh=0.01:bh=-0.01,vignette=PI/7'
if STILLS:
    for t in STILLS:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-i', '-',
                        '-vf', GRADE, f'{OUT}_{t:05.2f}.png'], input=picture(t).tobytes(), check=True)
    sys.exit()
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                        '-i', '-', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-vf', GRADE, '-map', '0:v', '-map', '1:a',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
                        '-t', str(TOTAL), '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for f in range(int(TOTAL * FPS)):
    enc.stdin.write(picture(f / FPS).tobytes())
enc.stdin.close(); enc.wait(); print('done', OUT)
