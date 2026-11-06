#!/usr/bin/env python3
"""Render a VEXON-style 9:16 reel from a plan JSON.

Usage:
  render_reel.py plan.json out.mp4                 # full render (video only, CRF 17 intermediate)
  render_reel.py plan.json stills_prefix --stills 0.5,4.9,12.0   # PNG stills at those seconds

Requires: ffmpeg on PATH, Python 3 with numpy + Pillow.
See SKILL.md and examples/*.plan.json for the plan format.
"""
import json, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)

# ---------------------------------------------------------------- config
plan_path, OUT = sys.argv[1], sys.argv[2]
STILLS = None
if '--stills' in sys.argv:
    STILLS = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')]
P = json.load(open(plan_path))
PLAN_DIR = os.path.dirname(os.path.abspath(plan_path))

W, H = P.get('size', [1080, 1920])
FPS = P.get('fps', 30)
BPM = P.get('bpm', 140)
BEAT = 60 / BPM
BAR = 4 * BEAT
OFFSET = P.get('beat_offset', 0.0)  # seconds from video start to the first downbeat of the music

def hex2rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
BR = {'orange': '#ff7a1a', 'gold': '#f7b137', 'cream': '#fbf7ef', 'navy': '#0b1525', 'white': '#ffffff'}
BR.update(P.get('brand_colors', {}))
COL = {k: hex2rgb(v) for k, v in BR.items()}
ORANGE, CREAM, NAVYD = COL['orange'], COL['cream'], COL['navy']
def color(name): return COL[name] if name in COL else hex2rgb(name)

FONT_DIR = P.get('fonts_dir') or os.path.join(SKILL, 'assets', 'fonts')
TITLE_FONT = os.path.join(FONT_DIR, P.get('title_font', 'Oswald.ttf'))
SUB_FONT = os.path.join(FONT_DIR, P.get('subtitle_font', 'PublicSans.ttf'))
SERIF = P.get('serif_font', '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf')

LOOK = {'grade': True, 'grain': True, 'beat_pulse': True, 'card_border': False}
LOOK.update(P.get('look', {}))

def src_path(key):
    if key is None: return None
    p = P['sources'].get(key, key)
    return p if os.path.isabs(p) else os.path.join(PLAN_DIR, p)

_fc = {}
def font(kind, size):
    k = (kind, size)
    if k in _fc: return _fc[k]
    spec = {'title': (TITLE_FONT, 650), 'title_bold': (TITLE_FONT, 700), 'sub': (SUB_FONT, 800),
            'sub_medium': (SUB_FONT, 600), 'sub_light': (SUB_FONT, 300), 'serif': (SERIF, None)}[kind]
    f = ImageFont.truetype(spec[0], size)
    if spec[1]:
        try: f.set_variation_by_axes([spec[1]])
        except Exception: pass
    _fc[k] = f
    return f

# ---------------------------------------------------------------- timeline
SHOTS = P['shots']
t = 0.0
for s in SHOTS:
    s['dur'] = s['bars'] * BAR if 'bars' in s else s.get('beats', 1) * BEAT
    s['t0'] = t; t += s['dur']; s['t1'] = t
    s.setdefault('tin', 'cut'); s.setdefault('kind', 'line' if 'text' in s else ('end' if s.get('src') is None else 'plain'))
    if 'text' in s:
        hl = [h.lower() for h in s.get('highlight', [])]
        s['_words'] = [(w, any(h in w.lower().strip('.,?!…') for h in hl)) for w in s['text'].split()]
TOTAL = t

# ---------------------------------------------------------------- footage
GRADE = ("eq=contrast=1.10:brightness={b}:saturation=0.88,"
         "colorbalance=rs=-0.04:bs=0.06:rm=0.03:bm=-0.02:rh=0.08:gh=0.02:bh=-0.07,"
         "vignette=angle=PI/4.5")

class Reader:
    """Streams graded, 9:16-cropped frames of one shot from ffmpeg."""
    def __init__(self, s): self.s = s; self.p = None; self.n = 0; self.last = None; self.base = 0
    def start(self, at=0):
        s = self.s; sp = s.get('speed', 1.0)
        nfr = int(round(s['dur'] * FPS)) + 3
        cx, cy = s.get('cx', 0.5), s.get('cy', 0.5)
        vf = ('transpose=2,' if s.get('rot') else '') + f"setpts=(PTS-STARTPTS)/{sp},fps={FPS}," + \
             f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos," + \
             f"crop={W}:{H}:(iw-{W})*{cx}:(ih-{H})*{cy}"
        if LOOK['grade']: vf += ',' + GRADE.format(b=s.get('bright', -0.02))
        self.base = at
        self.p = subprocess.Popen(['ffmpeg', '-v', 'quiet', '-ss', str(s['ss'] + at / FPS * sp), '-i', src_path(s['src']),
                                   '-an', '-vf', vf, '-frames:v', str(nfr), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                  stdout=subprocess.PIPE)
        self.n = at
    def frame(self, i):
        if self.p is None or i < self.base: self.start(i if STILLS else 0)
        while self.n <= i:
            b = self.p.stdout.read(W * H * 3)
            if len(b) < W * H * 3: break
            self.last = np.frombuffer(b, np.uint8).reshape(H, W, 3); self.n += 1
        if self.last is None: self.last = np.zeros((H, W, 3), np.uint8)
        return self.last

readers = [Reader(s) if s.get('src') else None for s in SHOTS]

def clamp(x): return min(max(x, 0.0), 1.0)
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def easeio(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x): x = clamp(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

HITS = ('flash', 'cutout', 'whip', 'panels', 'punch', 'hit')  # 'scan' and 'fade' are deliberately calm (no shake)

def shot_zoom(k, t):
    s = SHOTS[k]; lt = t - s['t0']
    z0, z1 = s.get('z', [1.04, 1.04])
    z = z0 + (z1 - z0) * easeio(lt / s['dur'])
    if s['kind'] == 'burst':
        z = 1.14 - 0.12 * ease(lt / s['dur'])
    elif LOOK['beat_pulse']:
        ph = ((t - OFFSET) % (2 * BEAT)) / BEAT
        z *= 1 + 0.022 * math.exp(-ph * 5)
    return z

def shot_image(k, t):
    s = SHOTS[k]; lt = t - s['t0']
    img = Image.fromarray(readers[k].frame(max(0, int(round(lt * FPS)))))
    z = shot_zoom(k, t); blur = 0
    nxt = SHOTS[k + 1] if k + 1 < len(SHOTS) else None
    if nxt and nxt['tin'] == 'punch':
        r = (lt - (s['dur'] - 5 / FPS)) / (5 / FPS)
        if r > 0: z *= 1 + 0.35 * r * r; blur = 14 * r
    if s['tin'] == 'punch':
        r = 1 - lt / (6 / FPS)
        if r > 0: z *= 1 + 0.25 * r * r; blur = max(blur, 14 * r)
    if abs(z - 1) > 1e-3:
        cw, ch = W / z, H / z; x0, y0 = (W - cw) / 2, (H - ch) / 2
        img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    if blur > 0.5: img = img.filter(ImageFilter.GaussianBlur(blur))
    return img, z

def xf(p, z): return ((p[0] - W / 2) * z + W / 2, (p[1] - H / 2) * z + H / 2)

# ---------------------------------------------------------------- transitions
JAG = {}
def jag_mask(step, nsteps, seed):
    key = (step, seed)
    if key in JAG: return JAG[key]
    rnd = random.Random(seed * 100 + step)
    level = H * (1.05 - 1.35 * ease((step + 1) / nsteps))
    pts = []; n = 14
    for j in range(n + 1):
        x = W * j / n + (rnd.uniform(-30, 30) if 0 < j < n else 0)
        pts.append((x, level + rnd.uniform(-220, 220) + 160 * math.sin(j * 0.9 + seed)))
    edge = [(-10, pts[0][1])] + pts[1:-1] + [(W + 10, pts[-1][1])]
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon([(0, H + 50)] + edge + [(W + 10, H + 50)], fill=255)
    o = Image.new('L', (W, H), 0); ImageDraw.Draw(o).line(edge, fill=255, width=9, joint='curve')
    JAG[key] = (np.asarray(m, np.float32)[..., None] / 255, np.asarray(o, np.float32)[..., None] / 255)
    return JAG[key]

def hblur(a, amt):
    if amt < 2: return a
    out = np.zeros_like(a)
    for j in range(7): out += np.roll(a, int((j - 3) * amt / 7), axis=1)
    return out / 7

def shift(a, dx):
    dx = int(dx); out = np.zeros_like(a)
    if 0 <= dx < W: out[:, dx:] = a[:, :W - dx]
    elif -W < dx < 0: out[:, :W + dx] = a[:, -dx:]
    return out

# ---------------------------------------------------------------- text
def layout(words, fnt, maxw):
    lines, cur = [], []; sp = fnt.getlength(' ')
    for w in words:
        test = cur + [w]
        if sum(fnt.getlength(x[0]) for x in test) + sp * (len(test) - 1) > maxw and cur:
            lines.append(cur); cur = [w]
        else: cur = test
    if cur: lines.append(cur)
    return lines

def text_block(layer, words, lt, span, cy, size, maxw, box_at):
    """Uppercase kinetic text: lines mask-wipe up; key words get an orange box wiping in behind them
    (trailing punctuation stays outside the box); lines are balanced so no word is left alone."""
    fnt = font('title', size)
    txt = [(w.upper(), h) for w, h in words]
    n0 = len(layout(txt, fnt, maxw)); mw = maxw
    while mw > 300 and len(layout(txt, fnt, mw - 10)) == n0: mw -= 10
    lines = layout(txt, fnt, mw)
    lh = int(size * 1.12); total = lh * len(lines); y0 = cy - total / 2
    sp = fnt.getlength(' ')
    out_r = ease((lt - (span - 5 / FPS)) / (5 / FPS))
    for li, line in enumerate(lines):
        lw = sum(fnt.getlength(w) for w, _ in line) + sp * (len(line) - 1)
        x = (W - lw) / 2; ly = y0 + li * lh
        r = ease((lt - li * 0.07) / 0.32)
        if r <= 0: continue
        CH = int(size * 1.5); lc = Image.new('RGBA', (W, CH), (0, 0, 0, 0)); ld = ImageDraw.Draw(lc)
        off = max((1 - r) * (lh + 10) - out_r * (lh + 10), -(lh + 10))
        bx = x
        for w, hl in line:
            ww = fnt.getlength(w)
            br = ease((lt - box_at) / 0.25) if hl else 0
            if br > 0:
                core = w.rstrip('.,?!…'); bw = fnt.getlength(core); bb = fnt.getbbox(core)
                ld.rectangle((bx - 12, 6 + bb[1] - 10, bx - 12 + (bw + 24) * br, 6 + bb[3] + 10), fill=ORANGE + (255,))
            ld.text((bx, 6), w, font=fnt, fill=CREAM + (255,))
            if br > 0:
                nv = Image.new('RGBA', lc.size, (0, 0, 0, 0)); ImageDraw.Draw(nv).text((bx, 6), w, font=fnt, fill=NAVYD + (255,))
                m = Image.new('L', lc.size, 0); ImageDraw.Draw(m).rectangle((bx - 12, 0, bx - 12 + (bw + 24) * br, CH), fill=255)
                lc.paste(nv, (0, 0), Image.composite(nv, Image.new('RGBA', lc.size, (0, 0, 0, 0)), m).getchannel('A'))
            bx += ww + sp
        sh = Image.new('RGBA', lc.size, (0, 0, 0, 0)); sh.paste(lc, (0, int(off)))
        layer.alpha_composite(sh, (0, int(ly - 6)))
    return y0, total

def numeral(layer, num, lt, span, ny):
    """Giant outlined number; slides in from the right and drifts (parallax)."""
    f = font('title_bold', 560)
    r = ease(lt / 0.45); out = ease((lt - (span - 5 / FPS)) / (5 / FPS))
    a = int(150 * r * (1 - out))
    if a <= 0: return
    x = W - 40 - f.getlength(num) + (1 - r) * 300 - lt * 25
    ImageDraw.Draw(layer).text((x, ny), num, font=f, fill=(0, 0, 0, 0), stroke_width=4, stroke_fill=CREAM + (a,))

def tag(d, x, y, text, a):
    f = font('sub', 30); w = f.getlength(text)
    d.rectangle((x, y, x + w + 36, y + 50), fill=ORANGE + (a,))
    d.text((x + 18, y + 7), text, font=f, fill=NAVYD + (a,))

def callout(layer, fx, lt, span, z):
    """Motion-graphic callouts locked to the footage: brackets / scan / rings (+ label tag)."""
    d = ImageDraw.Draw(layer)
    out = 1 - ease((lt - (span - 5 / FPS)) / (5 / FPS))
    if fx['kind'] in ('brackets', 'scan'):
        x0, y0 = xf(fx['box'][:2], z); x1, y1 = xf(fx['box'][2:], z)
        r = back((lt - BEAT) / 0.35)
        if r <= 0: return
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; s = 1 + 0.25 * (1 - r)
        x0, x1 = cx + (x0 - cx) * s, cx + (x1 - cx) * s; y0, y1 = cy + (y0 - cy) * s, cy + (y1 - cy) * s
        a = int(255 * clamp(r) * out); L = 70
        for (px, py, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
            d.line([(px, py + sy * L), (px, py), (px + sx * L, py)], fill=CREAM + (a,), width=7)
        if fx['kind'] == 'scan':
            ph = ((lt - BEAT) % (4 * BEAT)) / (4 * BEAT); sy = y0 + (y1 - y0) * ph
            d.rectangle((x0 + 12, sy - 2, x1 - 12, sy + 2), fill=ORANGE + (int(a * 0.9),))
            for g in range(1, 8):
                d.rectangle((x0 + 12, sy - 2 - g * 9, x1 - 12, sy - 2 - (g - 1) * 9), fill=ORANGE + (int(a * 0.12 * (8 - g) / 7),))
        tr = ease((lt - BEAT - 0.15) / 0.25)
        if tr > 0 and fx.get('tag'): tag(d, x0, y0 - 66 + (1 - tr) * 20, fx['tag'], int(255 * tr * out))
    elif fx['kind'] == 'neural':
        # subtle node network: links draw in, then soft pulses travel along them (information flow)
        rnd = random.Random(fx.get('seed', 7)); bx = fx['box']
        nodes = [(rnd.uniform(bx[0], bx[2]), rnd.uniform(bx[1], bx[3])) for _ in range(fx.get('n', 11))]
        edges = []
        for i, a_ in enumerate(nodes):
            near = sorted(range(len(nodes)), key=lambda j: (nodes[j][0] - a_[0]) ** 2 + (nodes[j][1] - a_[1]) ** 2)[1:3]
            for j in near:
                if (j, i) not in edges: edges.append((i, j))
        st = fx.get('start', 0.15)
        for ei, (i, j) in enumerate(edges):
            r = ease((lt - st - ei * 0.04) / 0.35)
            if r <= 0: continue
            p0 = xf(nodes[i], z); p1 = xf(nodes[j], z)
            pe = (p0[0] + (p1[0] - p0[0]) * r, p0[1] + (p1[1] - p0[1]) * r)
            d.line([p0, pe], fill=CREAM + (int(110 * out),), width=3)
            ph = ((lt - st) / (2 * BEAT) + ei * 0.37) % 1.0
            if r >= 1 and lt > st + 0.4:
                q = (p0[0] + (p1[0] - p0[0]) * ph, p0[1] + (p1[1] - p0[1]) * ph)
                d.ellipse((q[0] - 6, q[1] - 6, q[0] + 6, q[1] + 6), fill=ORANGE + (int(230 * out * math.sin(ph * math.pi)),))
        for ni, n_ in enumerate(nodes):
            r = back((lt - st - ni * 0.03) / 0.3)
            if r <= 0: continue
            c = xf(n_, z); rad = 9 * r
            d.ellipse((c[0] - rad, c[1] - rad, c[0] + rad, c[1] + rad), fill=CREAM + (int(220 * out),))
            d.ellipse((c[0] - rad - 8, c[1] - rad - 8, c[0] + rad + 8, c[1] + rad + 8), outline=ORANGE + (int(140 * out),), width=2)
        tr = ease((lt - st - 0.3) / 0.25)
        if tr > 0 and fx.get('tag'): tag(d, bx[0], bx[1] - 66 + (1 - tr) * 20, fx['tag'], int(255 * tr * out))
    elif fx['kind'] == 'rings':
        c = xf(fx['c'], z); st = BEAT
        if lt < st: return
        for k in range(3):
            v = (lt - st) / BEAT - k * 0.33
            if v < 0: continue
            ph = v % 1.0; rad = 70 + 230 * ease(ph)
            d.ellipse((c[0] - rad, c[1] - rad, c[0] + rad, c[1] + rad), outline=ORANGE + (int(220 * (1 - ph) * out),), width=6)
        r = back((lt - st) / 0.3)
        d.ellipse((c[0] - 14 * r, c[1] - 14 * r, c[0] + 14 * r, c[1] + 14 * r), fill=ORANGE + (int(255 * out),))
        tr = ease((lt - st - 0.15) / 0.25)
        if tr > 0 and fx.get('tag'):
            d.line([(c[0] + 14, c[1] - 14), (c[0] + 120, c[1] - 180)], fill=CREAM + (int(230 * tr * out),), width=4)
            tag(d, c[0] + 120, c[1] - 230 + (1 - tr) * 20, fx['tag'], int(255 * tr * out))

FLICK = ['serif', 'sub_light', 'title', 'serif', 'sub']
def hook_title(layer, words, lt, span):
    """Approved hook: each word group SLAMS in on its beat (scale 1.6 -> 1) with a 4-step font flicker
    (serif / Public Sans light / Oswald / serif / Public Sans), then locks to Oswald. No underline."""
    out = ease((lt - (span - 4 / FPS)) / (4 / FPS))
    for wd in words:
        bt = lt - wd['beat'] * BEAT
        if bt < 0: continue
        fi = int(bt * FPS)
        kind = FLICK[(fi // 2) % len(FLICK)] if fi < 8 else 'title'
        sz = int(wd['size'] * (1.0 if kind == 'title' else 0.82))
        f = font(kind, sz); tw = f.getlength(wd['text'])
        sc = 1 + 0.6 * (1 - ease(bt / 0.16))
        c = Image.new('RGBA', (int(tw + 40), int(sz * 1.5)), (0, 0, 0, 0))
        ImageDraw.Draw(c).text((20, 0), wd['text'], font=f, fill=color(wd.get('color', 'cream')) + (int(255 * clamp(bt / 0.08) * (1 - out)),))
        if sc > 1.01: c = c.resize((int(c.width * sc), int(c.height * sc)), Image.BICUBIC)
        layer.alpha_composite(c, (int((W - c.width) / 2), int(wd['y'] - c.height / 2)))

def band(cy, hgt, strength):
    ys = np.arange(H)
    return (np.clip(1 - np.abs(ys - cy) / hgt, 0, 1) ** 1.5 * strength).astype(np.float32)[:, None, None]

CARD = None
if LOOK['card_border']:  # rounded "film card" frame — OFF by default (client asked for clean full-bleed)
    cm = Image.new('L', (W * 2, H * 2), 0)
    ImageDraw.Draw(cm).rounded_rectangle((36, 36, W * 2 - 36, H * 2 - 36), 116, fill=255)
    CARD = np.asarray(cm.resize((W, H), Image.LANCZOS), np.float32)[..., None] / 255
rng = np.random.default_rng(3)
GRAIN = [rng.normal(0, 7, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1) for _ in range(6)]

def shot_at(t):
    for k, s in enumerate(SHOTS):
        if s['t0'] <= t < s['t1']: return k
    return len(SHOTS) - 1

def text_span(k):
    s = SHOTS[k]
    if s.get('cont'): return text_span(k - 1)
    if s['kind'] not in ('title', 'line', 'cta'): return None
    end = SHOTS[k + s.get('text_span', 1) - 1]['t1']
    return (k, s['t0'], end)

# ---------------------------------------------------------------- frame
def render_frame(fi):
    t = fi / FPS
    k = shot_at(t); s = SHOTS[k]; lt = t - s['t0']; fr = lt * FPS
    if s.get('src') is None:
        arr = np.zeros((H, W, 3), np.float32); arr[:] = color(s.get('fill', 'navy')); z = 1
    else:
        img, z = shot_image(k, t); arr = np.asarray(img, np.float32)

    def prev(): return np.asarray(shot_image(k - 1, s['t0'] - 1 / FPS)[0], np.float32)
    if s['tin'] == 'cutout' and fr < 10:
        m, o = jag_mask(int(fr) // 2, 5, k)
        arr = prev() * (1 - m) + arr * m; arr = arr * (1 - o) + 255 * o
    if s['tin'] == 'whip' and fr < 7:
        r = ease(fr / 7); off = int(-r * W); blur = 160 * (1 - r) + 20
        arr = shift(hblur(prev(), blur), off) + shift(hblur(arr, blur * (1 - r)), off + W)
    if s['tin'] == 'scan' and fr < 9:
        r = ease(fr / 9); yy = int(r * H); p_ = prev()
        arr = arr.copy(); arr[yy:] = p_[yy:]
        g = np.zeros((H, 1, 1), np.float32); ys = np.arange(H)
        g[:, 0, 0] = np.clip(1 - np.abs(ys - yy) / 60, 0, 1) ** 2
        arr = arr * (1 - 0.55 * g) + np.array(ORANGE, np.float32) * 0.55 * g
        arr[max(0, yy - 3):yy + 3] = ORANGE
    if s['tin'] == 'fade' and fr < 14:
        r = easeio(fr / 14); arr = prev() * (1 - r) + arr * r
    if s['tin'] == 'panels' and fr < 10:
        new = arr; arr = prev().copy(); n = 4; pw = W // n
        for j in range(n):
            r = ease((fr - j * 1.4) / 5)
            if r <= 0: continue
            dy = int((1 - r) * -H); seg = new[:, j * pw:(j + 1) * pw]
            if dy == 0: arr[:, j * pw:(j + 1) * pw] = seg
            else:
                arr[0:H + dy, j * pw:(j + 1) * pw] = seg[-dy:]
                arr[max(0, H + dy - 10):H + dy, j * pw:(j + 1) * pw] = ORANGE

    # camera shake + RGB split on hits
    hitr = max(0, 1 - fr / 6) if s['tin'] in HITS and s['kind'] != 'end' else 0
    if s['kind'] == 'burst': hitr = max(hitr, 0.8 * max(0, 1 - fr / 4))
    if hitr > 0:
        rr = random.Random(fi)
        dx = int(rr.uniform(-1, 1) * 22 * hitr); dy = int(rr.uniform(-1, 1) * 22 * hitr)
        arr = np.roll(arr, (dy, dx), axis=(0, 1))
        sp = int(14 * hitr)
        if sp:
            arr = arr.copy(); arr[..., 0] = np.roll(arr[..., 0], sp, 1); arr[..., 2] = np.roll(arr[..., 2], -sp, 1)

    if s.get('src') is not None:
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        span = text_span(k)
        if span:
            sk, a0, a1 = span; ts = SHOTS[sk]; tl = t - a0
            bf = min(1, tl / 0.25) * min(1, (a1 - t) / 0.2)
            if ts['kind'] == 'title':
                arr = arr * (1 - band(ts.get('band_y', 820), 560, 0.5) * bf)
                hook_title(layer, ts['title_words'], tl, a1 - a0)
            elif ts['kind'] == 'cta':
                cy = ts.get('ty', 900)
                arr = arr * (1 - band(cy + 50, 600, 0.55) * bf)
                text_block(layer, ts['_words'], tl, a1 - a0, cy, ts.get('size', 96), 900, ts.get('box_beats', 1) * BEAT)
            else:
                cy = ts.get('ty', 1130)
                arr = arr * (1 - band(cy, 520, 0.55) * bf)
                if ts.get('num'): numeral(layer, ts['num'], tl, a1 - a0, ts.get('num_y', 150))
                n = len(ts['_words']); size = ts.get('size', 92 if n <= 9 else (80 if n <= 14 else 70))
                text_block(layer, ts['_words'], tl, a1 - a0, cy, size, ts.get('maxw', P.get('text_maxw', 940)), ts['box_beats'] * BEAT if 'box_beats' in ts else min(2 * BEAT, 0.3 * (a1 - a0)))
        if s.get('fx'): callout(layer, s['fx'], lt, s['dur'], z)
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        sh.putalpha(layer.getchannel('A').filter(ImageFilter.GaussianBlur(12)).point(lambda v: min(255, int(v * 1.2))))
        la = np.asarray(Image.alpha_composite(sh, layer), np.float32); al = la[..., 3:4] / 255
        arr = arr * (1 - al) + la[..., :3] * al

    fl = 0
    if s['tin'] == 'flash': fl = max(fl, 1 - lt / (6 / FPS))
    if k + 1 < len(SHOTS) and SHOTS[k + 1]['tin'] == 'flash':
        r = (lt - (s['dur'] - 3 / FPS)) / (3 / FPS)
        if r > 0: fl = max(fl, r ** 1.5)
    if s['kind'] == 'burst' and fr < 1.5: fl = max(fl, 0.35)
    if fl > 0: arr = arr * (1 + 2.2 * fl) + 255 * 0.55 * fl

    if LOOK['grain']: arr = arr + GRAIN[fi % 6]
    if CARD is not None: arr = arr * CARD
    return np.clip(arr, 0, 255).astype(np.uint8)

# ---------------------------------------------------------------- main
if '--audit' in sys.argv:
    # Print each text block's bounding box in output pixels, so it can be checked against the IG safe zone.
    def lines_of(words, size, maxw):
        fnt = font('title', size); txt = [(w.upper(), h) for w, h in words]
        n0 = len(layout(txt, fnt, maxw)); mw = maxw
        while mw > 300 and len(layout(txt, fnt, mw - 10)) == n0: mw -= 10
        return fnt, layout(txt, fnt, mw)
    for s in SHOTS:
        if s['kind'] == 'title':
            for wd in s['title_words']:
                f = font('title', wd['size']); tw = f.getlength(wd['text']); bb = f.getbbox(wd['text'])
                print(f"{s['name'][:22]:<22} x {(W-tw)/2:5.0f}-{(W+tw)/2:5.0f}  y {wd['y']-wd['size']*0.75+bb[1]:5.0f}-{wd['y']-wd['size']*0.75+bb[3]:5.0f}  {wd['text']}")
        elif s['kind'] in ('line', 'cta'):
            cta = s['kind'] == 'cta'; n = len(s['_words'])
            size = s.get('size', 96 if cta else (92 if n <= 9 else (80 if n <= 14 else 70)))
            maxw = 900 if cta else s.get('maxw', P.get('text_maxw', 940)); cy = s.get('ty', 900 if cta else 1130)
            fnt, ls = lines_of(s['_words'], size, maxw); sp = fnt.getlength(' ')
            lh = int(size * 1.12); y0 = cy - lh * len(ls) / 2
            wmax = max(sum(fnt.getlength(w) for w, _ in l) + sp * (len(l) - 1) for l in ls)
            print(f"{s['name'][:22]:<22} x {(W-wmax)/2-12:5.0f}-{(W+wmax)/2+12:5.0f}  y {y0:5.0f}-{y0+lh*len(ls):5.0f}  " + ' / '.join(' '.join(w for w, _ in l) for l in ls))
    sys.exit()
if STILLS:
    for ts_ in STILLS:
        Image.fromarray(render_frame(int(round(ts_ * FPS)))).save(f'{OUT}_{ts_:05.2f}.png')
        for r in readers:
            if r: r.p = None
    sys.exit()

print(f'timeline {TOTAL:.2f}s @ {BPM} BPM')
for s in SHOTS: print(f"  {s['t0']:6.2f}-{s['t1']:6.2f}  {s.get('name', s['kind']):<20} in:{s['tin']}")
NF = int(round(TOTAL * FPS))
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                        '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', OUT],
                       stdin=subprocess.PIPE)
for fi in range(NF):
    enc.stdin.write(render_frame(fi).tobytes())
    if fi % 90 == 0: print(f'{fi / FPS:.1f}s', flush=True)
enc.stdin.close(); enc.wait(); print('done', OUT)
