"""St. Helena holiday reel v2 - clean 9:16 edit (no text; overlays/logos added by the client's editor).
Usage: python3 render.py <footage_dir> <music.wav> <out.mp4> [--stills t1,t2,...]
Cut to "A Lofi Wonderland" (Mizlo, Epidemic Sound): 88.99 BPM, beat B = 0.6742 s. The track starts at
MUSIC_OFFSET so its beat drop lands at 3.37 s; every cut and Christmas transition sits on a beat."""
import glob, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

B = 0.6742
W, H, FPS = 1080, 1920, 30
TOTAL = round(36 * B, 3)          # 24.27 s
MUSIC_OFFSET, FADE = 7.402, 1.0
FOOT, MUSIC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
STILLS = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')] if '--stills' in sys.argv else None

def src(key):
    return glob.glob(os.path.join(FOOT, f'*{key}*'))[0]

SHELF, SKINLAB, SETUP, TREAT = '2_15_05', '2_16_57', '3_32_46', '3_34_32_PM.'
HOLD, TRAY, PICK, WALK = '2_16_39', '2_01_25', '2_15_30', '2ff1841e'   # hand holding product box; treatment tray pan ending on Elf on the Shelf
def k(n): return round(n * B, 3)
# t0, t1, source, start, speed, zoom [from, to], crop centre (cx, cy), transition-in
SHOTS = [
    # hook (quiet intro): Dr. Strunck walking through the office
    (0.0, k(5), WALK, 0.0, 1.0, (1.00, 1.06), (.50, .42), 'cut'),     # Dr. Strunck walking through the office
    # beat drop -> 20% off cosmetic: Strunck b-roll + treatment
    (k(5), k(7), TREAT, 0.3, 1.0, (1.00, 1.05), (.50, .40), 'snow'),
    (k(7), k(9), SETUP, 2.4, 1.0, (1.00, 1.05), (.50, .45), 'cut'),
    (k(9), k(11), TREAT, 5.0, 1.0, (1.35, 1.42), (.45, .33), 'cut'),
    (k(11), k(13), SETUP, 4.6, 1.0, (1.30, 1.36), (.60, .62), 'cut'),
    # consultation / with patient / treatment room
    (k(13), k(17), SETUP, 0.0, 0.67, (1.00, 1.04), (.50, .50), 'star'),
    (k(17), k(19), TREAT, 3.0, 0.8, (1.12, 1.20), (.42, .45), 'cut'),
    # 20% off skincare: shelves, serum pick-up, product box, tray + Elf on the Shelf
    (k(19), k(20), SHELF, 0.5, 1.0, (1.05, 1.08), (.50, .45), 'ribbon'),
    (k(20), k(21), PICK, 1.0, 1.0, (1.10, 1.13), (.45, .45), 'cut'),
    (k(21), k(23), HOLD, 2.0, 1.0, (1.00, 1.04), (.50, .50), 'cut'),
    (k(23), k(25), TRAY, 2.5, 1.0, (1.00, 1.05), (.55, .50), 'cut'),
    # holiday savings: more Dr. Strunck
    (k(25), k(27), TREAT, 1.0, 0.8, (1.40, 1.46), (.35, .28), 'star'),
    (k(27), k(29), SETUP, 2.6, 0.7, (1.25, 1.30), (.38, .35), 'cut'),
    (k(29), k(31), TREAT, 4.1, 1.0, (1.30, 1.35), (.50, .62), 'cut'),
    # end card: blurred SkinLab shelf, light cream wash, room for logos + CTA
    (k(31), TOTAL, SKINLAB, 2.2, 0.5, (1.10, 1.14), (.50, .50), 'snow'),
]
XF = {'snow': 0.8, 'star': 0.6, 'ribbon': 0.6}   # transition length, centred on the cut
PRE = 0.45                                         # pre-roll decoded before each shot for transitions

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

# ---- Christmas transitions ---------------------------------------------------------------
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
DIAG = (XX / W * 0.45 + YY / H * 0.55)            # 0 top-left -> 1 bottom-right
random.seed(11)
FLAKES = [(random.uniform(-.15, 1.15), random.uniform(-.2, .2), random.uniform(16, 42), random.uniform(0, 6.28))
          for _ in range(150)]

def flake(d, x, y, r, rot, a):
    for j in range(3):                              # six-armed snowflake
        ang = rot + j * math.pi / 3; dx, dy = r * math.cos(ang), r * math.sin(ang)
        d.line([x - dx, y - dy, x + dx, y + dy], fill=(255, 255, 255, a), width=max(2, int(r / 6)))
        for sgn in (-1, 1):                         # little branches
            bx, by = x + sgn * dx * .55, y + sgn * dy * .55
            for bang in (ang + .6, ang - .6):
                ex, ey = r * .3 * math.cos(bang) * sgn, r * .3 * math.sin(bang) * sgn
                d.line([bx, by, bx + ex, by + ey], fill=(255, 255, 255, a), width=max(1, int(r / 9)))
    d.ellipse([x - r * .15, y - r * .15, x + r * .15, y + r * .15], fill=(255, 255, 255, a))

def tr_snow(prev, nxt, p):
    """A snow flurry sweeps diagonally across, swapping the shots behind its white front."""
    f = -0.2 + p * 1.4
    m = np.clip((f - DIAG) / 0.015 + 0.5, 0, 1)[..., None]
    band = np.exp(-((DIAG - f) / 0.085) ** 2)[..., None] * 0.97
    out = np.asarray(prev, np.float32) * (1 - m) + np.asarray(nxt, np.float32) * m
    out = out * (1 - band) + 255 * band
    img = Image.fromarray(out.clip(0, 255).astype(np.uint8)).convert('RGBA')
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for (u, v, r, ph) in FLAKES:
        sd = f + v                                  # flake rides near the front
        # position on the diagonal line DIAG == sd, spread along it by u
        x = u * W; y = (sd - 0.45 * u) / 0.55 * H
        a = int(255 * max(0, 1 - abs(v) / .2) * min(1, 4 * p, 4 * (1 - p)))
        if -40 < y < H + 40 and a > 8:
            flake(d, x, y, r, ph + p * 2.5, a)
    img = Image.alpha_composite(img, lay.filter(ImageFilter.GaussianBlur(0.8)))
    return img.convert('RGB')

def star_poly(cx, cy, R, rot):
    pts = []
    for j in range(10):
        rr = R if j % 2 == 0 else R * 0.45
        ang = rot - math.pi / 2 + j * math.pi / 5
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return pts

def tr_star(prev, nxt, p):
    """Star-shaped iris opens from the centre with a white edge, revealing the next shot."""
    q = p ** 1.6; R = 160 + q * 2500; rot = q * 0.6
    pts = star_poly(W / 2, H * 0.40, R, rot)
    mask = Image.new('L', (W, H), 0); ImageDraw.Draw(mask).polygon(pts, fill=255)
    out = Image.composite(nxt, prev, mask.filter(ImageFilter.GaussianBlur(2)))
    edge = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(edge).line(pts + [pts[0]], fill=(255, 255, 255, int(255 * min(1, 3 * (1 - p)))),
                              width=18, joint='curve')
    return Image.alpha_composite(out.convert('RGBA'), edge.filter(ImageFilter.GaussianBlur(1.5))).convert('RGB')

STRIPE = ((((XX + YY) // 70) % 2) == 0)[..., None]
CANE = np.where(STRIPE, np.array([196, 28, 42], np.float32), np.array([252, 250, 246], np.float32))
def tr_ribbon(prev, nxt, p):
    """Candy-cane striped ribbon sweeps up the frame like gift wrap; next shot is underneath."""
    hb = 560; top = H - ease(p) * (H + hb + 80)     # band top edge moves from bottom to above frame
    yy = YY[..., None]
    out = np.where(yy < top, np.asarray(prev, np.float32), np.asarray(nxt, np.float32))
    inb = (yy >= top) & (yy < top + hb)
    shade = np.clip(1 - (np.abs(yy - top - hb / 2) / (hb / 2)) ** 6 * .25, 0, 1)   # subtle roundness
    shift = (p * 300) % 140                          # stripes scroll for motion
    stripe = (((XX[..., None] + yy + shift) // 70) % 2) == 0
    cane = np.where(stripe, np.array([196, 28, 42], np.float32), np.array([252, 250, 246], np.float32))
    out = np.where(inb, cane * shade, out)
    shadow = np.exp(-((yy - top - hb) / 25) ** 2) * (yy > top + hb) * 0.35
    out = out * (1 - shadow)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))

TRANS = {'snow': tr_snow, 'star': tr_star, 'ribbon': tr_ribbon}

def shot_frame(i, t):
    t0, t1, key, ss, sp, zz, (cx, cy), _ = SHOTS[i]
    pre = min(PRE, ss / sp)                         # how much earlier footage exists
    n_total = int(round((t1 - t0 + pre + 0.5) * FPS))
    fr = frames(key, ss - pre * sp, n_total, sp)
    k = min(max(int((t - t0 + pre) * FPS), 0), n_total - 1)
    u = min(max((t - t0) / (t1 - t0), 0), 1)
    img = framed(Image.fromarray(fr[k]), zz[0] + (zz[1] - zz[0]) * ease(u), cx, cy)
    if i == len(SHOTS) - 1:                       # end card treatment
        img = img.filter(ImageFilter.GaussianBlur(22))
        img = Image.blend(img, Image.new('RGB', (W, H), (253, 248, 238)), 0.68)
    return img

def render_at(t):
    i = max(j for j, s in enumerate(SHOTS) if s[0] <= t)
    # inside a transition window centred on a cut?
    for j in (i, i + 1):
        if 0 < j < len(SHOTS) and SHOTS[j][7] in XF:
            d = XF[SHOTS[j][7]]; T = SHOTS[j][0]
            if T - d / 2 <= t < T + d / 2:
                return TRANS[SHOTS[j][7]](shot_frame(j - 1, t), shot_frame(j, t), (t - (T - d / 2)) / d)
    return shot_frame(i, t)

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
                        '-r', str(FPS), '-i', '-', '-ss', str(MUSIC_OFFSET), '-i', MUSIC, '-vf', GRADE,
                        '-af', f'volume=-1dB,afade=t=in:d=0.05,afade=t=out:st={TOTAL - FADE}:d={FADE}', '-map', '0:v', '-map', '1:a',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '256k', '-t', str(TOTAL), '-movflags', '+faststart', OUT],
                       stdin=subprocess.PIPE)
for f in range(int(round(TOTAL * FPS))):
    enc.stdin.write(render_at(f / FPS).tobytes())
    if f % 150 == 0: print(f'{f / FPS:.0f}s', flush=True)
enc.stdin.close(); enc.wait()
print('done', OUT)
