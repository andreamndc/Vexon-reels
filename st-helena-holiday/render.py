"""St. Helena holiday reel - clean 9:16 edit (no text; overlays are added by the client's editor).
Usage: python3 render.py <footage_dir> <music.wav> <out.mp4> [--stills t1,t2,...]
Shots are cut on a 160 BPM grid (1 bar = 1.5 s) to match music/holiday_track.wav."""
import glob, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS, TOTAL = 1080, 1920, 30, 25.0
FOOT, MUSIC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
STILLS = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')] if '--stills' in sys.argv else None

def src(key):
    return glob.glob(os.path.join(FOOT, f'*{key}*'))[0]

SHELF, SKINLAB, SETUP, TREAT = '2_15_05', '2_16_57', '3_32_46', '3_34_32_PM.'
HOLD, TRAY, PICK = '2_16_39', '2_01_25', '2_15_30'   # hand holding product box; treatment tray pan ending on Elf on the Shelf
# t0, t1, source, start, speed, zoom [from, to], crop centre (cx, cy), transition-in, sparkle
SHOTS = [
    # 0-3  hook: Dr. Strunck treating a patient
    (0.0, 3.0, TREAT, 0.0, 1.0, (1.00, 1.08), (.50, .40), 'fadein', True),
    # 3-7.5  Strunck b-roll + treatment (cuts on the bar)
    (3.0, 4.5, SETUP, 1.8, 1.0, (1.00, 1.05), (.50, .45), 'cut', False),
    (4.5, 6.0, TREAT, 5.0, 1.0, (1.35, 1.42), (.45, .33), 'cut', False),
    (6.0, 7.5, SETUP, 3.3, 1.0, (1.30, 1.36), (.60, .62), 'cut', False),
    # 7.5-12  with patient / treatment room
    (7.5, 9.0, SETUP, 0.0, 1.0, (1.00, 1.04), (.50, .50), 'dissolve', False),
    (9.0, 12.0, TREAT, 2.8, 0.8, (1.12, 1.20), (.42, .45), 'cut', False),
    # 12-16.5  SkinLab shelves & products
    (12.0, 13.5, SHELF, 0.3, 1.0, (1.05, 1.10), (.50, .45), 'dissolve', False),
    (13.5, 14.25, PICK, 0.9, 1.0, (1.10, 1.14), (.45, .45), 'cut', False),  # hand picks a serum
    (14.25, 15.0, HOLD, 2.0, 1.0, (1.00, 1.04), (.50, .50), 'cut', False),
    (15.0, 16.5, TRAY, 2.4, 1.0, (1.00, 1.05), (.55, .50), 'cut', False),   # lands on the Elf on the Shelf
    # 16.5-21  more Dr. Strunck
    (16.5, 18.0, SETUP, 4.6, 1.0, (1.05, 1.10), (.45, .45), 'dissolve', False),
    (18.0, 19.5, TREAT, 1.0, 1.0, (1.40, 1.46), (.35, .28), 'cut', False),
    (19.5, 21.0, TREAT, 0.0, 1.0, (1.25, 1.30), (.55, .62), 'cut', False),
    # 21-25  end card (blurred SkinLab shelf, light cream wash, room for both logos)
    (21.0, 25.0, SKINLAB, 2.2, 0.5, (1.10, 1.14), (.50, .50), 'dissolve', True),
]
XF = {'dissolve': 0.35, 'fadein': 0.4}

_cache = {}
def frames(key, start, n, speed):
    """Decode n output frames starting at `start` (source seconds) at the given speed."""
    ck = (key, start, n, speed)
    if ck in _cache: return _cache[ck]
    dur = n / FPS * speed + 0.2
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-ss', str(start), '-t', str(dur), '-i', src(key),
           '-vf', f'setpts=PTS/{speed},fps={FPS},scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    arr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    if len(arr) < n: arr = np.concatenate([arr, np.repeat(arr[-1:], n - len(arr), 0)])
    _cache[ck] = arr[:n]
    return _cache[ck]

def framed(img, z, cx, cy):
    """Sub-pixel crop/zoom so push-ins are perfectly smooth."""
    cw, ch = W / z, H / z
    x0 = min(max(cx * W - cw / 2, 0), W - cw); y0 = min(max(cy * H - ch / 2, 0), H - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

def ease(u): return u * u * (3 - 2 * u)

random.seed(7)
SPARKS = [dict(x=random.uniform(0, W), y=random.uniform(0, H), r=random.uniform(4, 16),
               vy=random.uniform(18, 55), ph=random.uniform(0, 6.28), a=random.uniform(.25, .7))
          for _ in range(46)]
def sparkle(img, t, strength):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for s in SPARKS:
        y = (s['y'] + s['vy'] * t) % H; x = s['x'] + 14 * math.sin(t * .8 + s['ph'])
        a = int(255 * s['a'] * strength * (.55 + .45 * math.sin(t * 3 + s['ph'])))
        r = s['r'] * 2.2; d.ellipse([x - r, y - r, x + r, y + r], fill=(236, 180, 90, a))
    glow = layer.filter(ImageFilter.GaussianBlur(9))
    core = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(core)
    for s in SPARKS:
        y = (s['y'] + s['vy'] * t) % H; x = s['x'] + 14 * math.sin(t * .8 + s['ph'])
        a = int(255 * min(1, s['a'] * 1.4) * strength * (.55 + .45 * math.sin(t * 3 + s['ph'])))
        r = s['r'] * .35; dc.ellipse([x - r, y - r, x + r, y + r], fill=(255, 248, 225, a))
    core = core.filter(ImageFilter.GaussianBlur(1.2))
    out = Image.alpha_composite(img.convert('RGBA'), glow)
    return Image.alpha_composite(out, core).convert('RGB')

def shot_frame(i, t):
    t0, t1, key, ss, sp, zz, (cx, cy), _, spark = SHOTS[i]
    n_total = int(round((t1 - t0 + 0.5) * FPS))
    fr = frames(key, ss, n_total, sp)
    k = min(int((t - t0) * FPS), n_total - 1)
    u = min(max((t - t0) / (t1 - t0), 0), 1)
    img = framed(Image.fromarray(fr[k]), zz[0] + (zz[1] - zz[0]) * ease(u), cx, cy)
    if i == len(SHOTS) - 1:                       # end card treatment
        img = img.filter(ImageFilter.GaussianBlur(22))
        img = Image.blend(img, Image.new('RGB', (W, H), (253, 248, 238)), 0.68)
    if spark:
        s = 1.0 if i == len(SHOTS) - 1 else max(0.0, 1 - max(0, t - 2.2) / 0.8)
        if s > 0: img = sparkle(img, t, s * (1.0 if i == len(SHOTS) - 1 else 0.75))
    return img

def render_at(t):
    i = max(j for j, s in enumerate(SHOTS) if s[0] <= t)
    img = shot_frame(i, t)
    tin = SHOTS[i][7]
    if tin in XF and t - SHOTS[i][0] < XF[tin]:
        a = ease((t - SHOTS[i][0]) / XF[tin])
        prev = shot_frame(i - 1, t) if i > 0 else Image.new('RGB', (W, H), (255, 250, 242))
        img = Image.blend(prev, img, a)
    return img

GRADE = ('eq=contrast=1.05:saturation=1.08:brightness=0.015,'
         'colorbalance=rm=0.03:gm=0.0:bm=-0.03:rh=0.02:bh=-0.02,vignette=PI/6')

if STILLS:
    for t in STILLS:
        p = f'{OUT}_{t:05.2f}.png'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                        '-i', '-', '-vf', GRADE, p], input=render_at(t).tobytes(), check=True)
        print(p)
    sys.exit()

enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                        '-r', str(FPS), '-i', '-', '-i', MUSIC, '-vf', GRADE, '-map', '0:v', '-map', '1:a',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '256k', '-t', str(TOTAL), '-movflags', '+faststart', OUT],
                       stdin=subprocess.PIPE)
for f in range(int(TOTAL * FPS)):
    enc.stdin.write(render_at(f / FPS).tobytes())
    if f % 150 == 0: print(f'{f / FPS:.0f}s', flush=True)
enc.stdin.close(); enc.wait()
print('done', OUT)
