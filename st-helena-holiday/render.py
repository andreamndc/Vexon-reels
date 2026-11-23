"""St. Helena holiday reel v4 - clean 9:16 edit (no text; overlays/logos added by the client's editor).
Usage: python3 render.py <footage_dir> <music> <out.mp4> [--stills t1,t2,...]
Cut to "Christmas In My Heart (Instrumental)" (Loving Caliber, Epidemic Sound): 134.02 BPM, beat B = 0.4477 s.
The track plays from MUSIC_OFFSET = 147.51 s to its real ending (final hit at 171.68 s = 24.17 s in the edit).
Strong accents fall at 0.895 + n * 1.791 s in the edit; every section change sits on one."""
import glob, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

B = 0.4477
W, H, FPS = 1080, 1920, 30
TOTAL = 25.0
MUSIC_OFFSET, FADE = 147.51, 0.5
FOOT, MUSIC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
STILLS = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')] if '--stills' in sys.argv else None

def src(key):
    return glob.glob(os.path.join(FOOT, f'*{key}*'))[0]

SHELF, SKINLAB, SETUP, TREAT = '2_15_05', '2_16_57', '3_32_46', '3_34_32_PM.'
HOLD, TRAY, PICK, WALK = '2_16_39', '2_01_25', '2_15_30', '2ff1841e'   # hand holding product box; treatment tray pan ending on Elf on the Shelf; office walk
LASER, CLOSE, CONSULT, FACE = '3_40_53', '3_42_57', '8ec49a6e', '3_31_23'   # wide laser treatment; handpiece close-up (landscape); consultation
LANDSCAPE_CX = {CLOSE: 0.5}    # horizontal clips: centre-crop to 9:16 at this x position
def acc(n): return round(0.895 + n * 4 * B, 3)    # accent n: 0.895, 2.686, 4.477, 6.268, 8.059 ...
# t0, t1, source, start, speed, zoom [from, to], crop centre (cx, cy), transition-in
SHOTS = [
    # hook: Dr. Strunck walking through the office
    (0.0, acc(1), WALK, 0.0, 1.0, (1.00, 1.05), (.50, .42), 'cut'),
    # 20% off cosmetic: treatment + Strunck b-roll
    (acc(1), acc(2), TREAT, 0.3, 1.0, (1.00, 1.05), (.50, .40), 'snow'),
    (acc(2), acc(3), LASER, 3.0, 1.0, (1.00, 1.05), (.55, .45), 'cut'),       # laser treatment, wide
    (acc(3), acc(4), TREAT, 4.9, 1.0, (1.35, 1.42), (.45, .33), 'cut'),
    # consultation / with patient / treatment room
    (acc(4), acc(5), FACE, 1.0, 1.0, (1.00, 1.05), (.45, .42), 'star'),       # Dr. Strunck treating the patient's face (3:31:23 PM)
    (acc(5), acc(6), TREAT, 3.0, 0.8, (1.12, 1.20), (.42, .45), 'cut'),
    # 20% off skincare: shelves, serum pick-up, product box, tray + Elf on the Shelf
    (acc(6), acc(6) + 2 * B, SHELF, 0.5, 1.0, (1.05, 1.08), (.50, .45), 'ribbon'),
    (acc(6) + 2 * B, acc(7), PICK, 0.9, 1.0, (1.10, 1.13), (.45, .45), 'cut'),
    (acc(7), acc(8), HOLD, 1.5, 1.0, (1.00, 1.04), (.50, .50), 'cut'),
    (acc(8), acc(9), TRAY, 2.2, 1.0, (1.00, 1.05), (.55, .50), 'cut'),
    # holiday savings: more Dr. Strunck
    (acc(9), acc(9) + 2 * B, LASER, 1.0, 1.0, (1.05, 1.09), (.55, .40), 'star'),     # Dr. Strunck, laser treatment
    (acc(9) + 2 * B, acc(10), CLOSE, 2.0, 1.0, (1.00, 1.04), (.50, .50), 'cut'),     # handpiece close-up
    (acc(10), acc(11), CONSULT, 10.5, 1.0, (1.22, 1.28), (.50, .36), 'cut'),       # consultation, tighter, later moment
    # end card: blurred SkinLab shelf, light cream wash, room for logos + CTA; song's final hit at 24.17 s
    (acc(11), TOTAL, SKINLAB, 2.2, 0.5, (1.10, 1.14), (.50, .50), 'snow'),
]
XF = {'snow': 0.8, 'star': 0.6, 'ribbon': 0.6}   # transition length, centred on the cut
PRE = 0.45                                         # pre-roll decoded before each shot for transitions

_cache = {}
def frames(key, start, n, speed):
    """Decode n output frames starting at `start` (source seconds) at the given speed."""
    ck = (key, start, n, speed)
    if ck in _cache: return _cache[ck]
    dur = n / FPS * speed + 0.2
    fit = (f'scale=-2:{H},crop={W}:{H}:(iw-{W})*{LANDSCAPE_CX[key]}:0' if key in LANDSCAPE_CX else f'scale={W}:{H}')
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-ss', str(start), '-t', str(dur), '-i', src(key),
           '-vf', f'setpts=PTS/{speed},fps={FPS},{fit}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
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
                        '-af', f'volume=-3dB,alimiter=limit=0.8:level=false:attack=1:release=50,afade=t=in:d=0.12,afade=t=out:st={TOTAL - FADE}:d={FADE}', '-map', '0:v', '-map', '1:a',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '256k', '-t', str(TOTAL), '-movflags', '+faststart', OUT],
                       stdin=subprocess.PIPE)
for f in range(int(round(TOTAL * FPS))):
    enc.stdin.write(render_at(f / FPS).tobytes())
    if f % 150 == 0: print(f'{f / FPS:.0f}s', flush=True)
enc.stdin.close(); enc.wait()
print('done', OUT)
