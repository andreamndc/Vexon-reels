#!/usr/bin/env python3
"""American Heritage Chocolate holiday reel renderer (own style; not the VEXON kit).

No burned-in text: the editor adds text and the logo in CapCut. This renders footage only,
with transitions, a warm holiday grade, soft bloom, light snowfall and a blank end card.

  python3 render.py plan.json out.mp4                  full render (silent audio track)
  python3 render.py plan.json out.jpg --storyboard     storyboard sheet
  python3 render.py plan.json outdir --stills 1.0,9.5  single frames
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PLAN_PATH = sys.argv[1]
P = json.load(open(PLAN_PATH))
BASE = os.path.dirname(os.path.abspath(PLAN_PATH))
ROOT = os.path.dirname(BASE)
W, H = P['size']
FPS = P['fps']
LOOK = P.get('look', {})
BROWN = (0x59, 0x2d, 0x2b)
CREAM = (0xf3, 0xed, 0xe3)
GRADE = LOOK.get('grade', 'eq=contrast=1.04:saturation=1.06')


def font(weight, size):
    return ImageFont.truetype(os.path.join(ROOT, 'brand', 'fonts', f'Montserrat-{weight}.ttf'), size)


def src_path(key):
    return os.path.normpath(os.path.join(BASE, P['sources'][key]))


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ---------- timeline ----------
SHOTS = P['shots']
t = 0.0
for i, s in enumerate(SHOTS):
    s['i'] = i
    s['start'] = t
    t += s['dur']
    s['end'] = t
for i, s in enumerate(SHOTS):
    tin = s.get('tin', {'type': 'cut', 'd': 0})
    s['tin'] = tin if i else {'type': 'cut', 'd': 0}
    s['pre'] = s['tin']['d'] / 2
    s['post'] = SHOTS[i + 1].get('tin', {'d': 0})['d'] / 2 if i + 1 < len(SHOTS) else 0
TOTAL = t
NFRAMES = int(round(TOTAL * FPS))

_DIMS = {}


def display_dims(src):
    if src not in _DIMS:
        st = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                        'stream=width,height:stream_side_data=rotation', '-of', 'json', src],
                                       capture_output=True, text=True).stdout)['streams'][0]
        w, h = st['width'], st['height']
        if any(abs(d.get('rotation', 0)) == 90 for d in st.get('side_data_list', [])):
            w, h = h, w
        _DIMS[src] = (w, h)
    return _DIMS[src]


_TRC = {}


def to_sdr(src):
    """Colour-accurate conversion to SDR BT.709. iPhone HDR (HLG / BT.2020) is tone-mapped the
    way a phone shows it in SDR; BT.709 sources pass through. No grading."""
    if src not in _TRC:
        _TRC[src] = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                    'stream=color_transfer', '-of', 'csv=p=0', src],
                                   capture_output=True, text=True).stdout.strip().split('\n')[0].strip(',')
    if _TRC[src] in ('arib-std-b67', 'smpte2084'):
        return ('zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:desat=0,'
                'zscale=t=bt709:m=bt709:r=tv,format=yuv420p')
    return 'null'


class Decoder:
    """Streams graded frames of src from time t0, cover-scaled to (w, h). Pads before 0 / after end."""

    def __init__(self, src, t0, w, h):
        sw, sh = display_dims(src)
        if w / sw >= h / sh:
            self.ow, self.oh = w, int(round(sh * w / sw))
        else:
            self.ow, self.oh = int(round(sw * h / sh)), h
        self.pad = max(0, int(round(-t0 * FPS)))
        vf = f'{to_sdr(src)},fps={FPS},scale={self.ow}:{self.oh}:flags=lanczos:in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24,{GRADE}'
        self.p = subprocess.Popen(stderr=subprocess.DEVNULL, args=['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{max(t0, 0):.3f}', '-i', src,
                                   '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                  stdout=subprocess.PIPE)
        self.fsz = self.ow * self.oh * 3
        self.last = None

    def next(self):
        if self.pad > 0 and self.last is not None:
            self.pad -= 1
            return self.last
        buf = self.p.stdout.read(self.fsz) if self.p else b''
        if len(buf) == self.fsz:
            self.last = np.frombuffer(buf, np.uint8).reshape(self.oh, self.ow, 3)
            if self.pad > 0:
                self.pad -= 1
        elif self.last is None:
            raise RuntimeError('decoder produced no frames')
        else:
            self.close()
        return self.last

    def close(self):
        if self.p:
            self.p.stdout.close()
            self.p.kill()
            self.p.wait()
            self.p = None


def crop_zoom(img, z, cx, cy, w, h, zmax):
    ih, iw = img.shape[:2]
    cw, ch = min(w * zmax / z, iw), min(h * zmax / z, ih)
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    return Image.fromarray(img).resize((w, h), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


class ShotStream:
    """Frames of one shot for global frame indices, including the transition overlap on both sides."""

    def __init__(self, s, f0):
        self.s = s
        self.f = f0
        kind = s.get('kind', 'video')
        lt0 = f0 / FPS - s['start']
        if kind == 'video':
            self.zmax = max(s['z'])
            sp = s.get('speed', 1.0)
            self.dec = Decoder(src_path(s['src']), s['ss'] + lt0 * sp, int(round(W * self.zmax)),
                               int(round(H * self.zmax)))
        elif kind == 'collage':
            self.decs = [Decoder(src_path(b['src']), b['ss'] + lt0, W, H) for b in s['bands']]

    def frame(self):
        s = self.s
        lt = self.f / FPS - s['start']
        self.f += 1
        kind = s.get('kind', 'video')
        if kind == 'video':
            img = self.dec.next()
            u = ease(lt / s['dur'])
            z = s['z'][0] + (s['z'][1] - s['z'][0]) * u
            return crop_zoom(img, z, s.get('cx', 0.5), s.get('cy', 0.5), W, H, self.zmax)
        if kind == 'collage':
            return collage(s, [d.next() for d in self.decs], lt)
        return endcard()

    def close(self):
        for d in ([self.dec] if hasattr(self, 'dec') else []) + getattr(self, 'decs', []):
            d.close()


# ---------- collage: bands slide in one after another ----------
def collage(s, imgs, lt):
    gap = 12
    bh = (H - 2 * gap) // 3
    canvas = Image.new('RGB', (W, H), CREAM)
    for k, (b, img) in enumerate(zip(s['bands'], imgs)):
        ih = img.shape[0]
        z = 1.0 + 0.05 * ease(lt / s['dur'])
        ch, cw = bh / z, W / z
        y0 = min(max(b['cy'] * ih - ch / 2, 0), ih - ch)
        band = Image.fromarray(img).resize((W, bh), Image.BILINEAR, box=((W - cw) / 2, y0, (W + cw) / 2, y0 + ch))
        p = ease((lt + s['pre'] - 0.12 * k) / 0.45) if s.get('stagger', True) else 1
        side = -1 if k % 2 == 0 else 1
        x = int(side * (1 - p) * W)
        canvas.paste(band, (x, k * (bh + gap)))
    return canvas


# ---------- end card: blank cream paper, space left for the logo ----------
_END = None


def endcard():
    global _END
    if _END is None:
        rng = np.random.default_rng(7)
        base = np.ones((H, W, 3), np.float32) * np.array(P.get('endcard', {}).get('color', CREAM), np.float32)
        n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
        n = np.array(Image.fromarray(((n * 20) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
                     .filter(ImageFilter.GaussianBlur(3)), np.float32) - 128
        base += (n * 0.35 + rng.normal(0, 3.0, (H, W)).astype(np.float32))[..., None]
        yy, xx = np.mgrid[0:H, 0:W]
        base *= (1 - 0.08 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2))[..., None]
        _END = Image.fromarray(base.clip(0, 255).astype(np.uint8))
    return _END


# ---------- transitions ----------
def hblur(img, k):
    """Cheap horizontal motion blur: squash then stretch."""
    if k < 1.5:
        return img
    return img.resize((max(8, int(W / k)), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)


LEAK = None


def light_leak(p):
    """Warm golden light sweeping across the frame (peak at p=0.5)."""
    global LEAK
    if LEAK is None:
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
        LEAK = (xx, yy)
    xx, yy = LEAK
    cx = (-0.3 + 1.6 * p) * W / 4
    cy = (0.25 + 0.3 * p) * H / 4
    r = np.sqrt(((xx - cx) / (W / 4 * 0.55)) ** 2 + ((yy - cy) / (H / 4 * 0.45)) ** 2)
    g = np.exp(-r ** 2 * 1.6) * math.sin(math.pi * p)
    col = np.array([255, 196, 120], np.float32) / 255
    leak = (g[..., None] * col * 255).astype(np.uint8)
    return Image.fromarray(leak).resize((W, H), Image.BICUBIC)


def screen(a, b, k=1.0):
    A = np.asarray(a, np.float32) / 255
    B = np.asarray(b, np.float32) / 255 * k
    return Image.fromarray(((1 - (1 - A) * (1 - B)) * 255).clip(0, 255).astype(np.uint8))


def transition(kind, A, B, p):
    e = ease(p)
    if kind == 'dissolve':
        return Image.blend(A, B, e)
    if kind == 'glow':
        out = Image.blend(A, B, ease((p - 0.2) / 0.6))
        out = screen(out, light_leak(p), 0.55)
        lift = math.sin(math.pi * p) * 0.07
        return Image.blend(out, Image.new('RGB', (W, H), (255, 236, 210)), lift)
    if kind == 'whip':
        k = 1 + 14 * math.sin(math.pi * p)
        off = int(e * W)
        out = Image.new('RGB', (W, H))
        out.paste(hblur(A, k), (-off, 0))
        out.paste(hblur(B, k), (W - off, 0))
        return out
    if kind == 'zoom':
        za = 1 + 0.25 * e
        zb = 1.2 - 0.2 * e
        def zf(img, z):
            cw, ch = W / z, H / z
            return img.resize((W, H), Image.BILINEAR, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
        a, b = zf(A, za), zf(B, zb)
        r = int(6 * math.sin(math.pi * p))
        out = Image.blend(a, b, e)
        return out.filter(ImageFilter.GaussianBlur(r)) if r else out
    return B if p >= 0.5 else A


# ---------- holiday finish: bloom + snow ----------
def bloom(img, k):
    if k <= 0:
        return img
    small = np.asarray(img.resize((W // 6, H // 6), Image.BILINEAR), np.float32)
    hi = np.clip(small - 170, 0, 255) * 2.2
    hi *= np.array([1.0, 0.86, 0.66], np.float32)
    glow = Image.fromarray(hi.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR)
    return screen(img, glow, k)


class Snow:
    def __init__(self, n, seed=3):
        rng = np.random.default_rng(seed)
        self.x0 = rng.uniform(0, W, n)
        self.y0 = rng.uniform(-40, H, n)
        depth = rng.uniform(0, 1, n) ** 1.6          # most flakes far away (small, slow, soft)
        self.size = 3 + depth * 13
        self.v = 50 + depth * 170                     # px / s
        self.sway = 10 + depth * 30
        self.freq = rng.uniform(0.3, 0.9, n)
        self.ph = rng.uniform(0, 2 * math.pi, n)
        self.alpha = 0.35 + depth * 0.5
        self.blur = 2.2 - depth * 1.6
        self.sprites = {}

    def sprite(self, d, b):
        d, b = float(int(d)), float(round(b, 1)); key = (d, b)
        if key not in self.sprites:
            s = int(d * 3) + 6
            im = Image.new('L', (s, s), 0)
            ImageDraw.Draw(im).ellipse([(s - d) / 2, (s - d) / 2, (s + d) / 2, (s + d) / 2], fill=255)
            self.sprites[key] = im.filter(ImageFilter.GaussianBlur(float(max(0.6, b * d / 6))))
        return self.sprites[key]

    def apply(self, img, t, amount):
        if amount <= 0:
            return img
        lay = Image.new('L', (W, H), 0)
        for i in range(len(self.x0)):
            y = (self.y0[i] + self.v[i] * t) % (H + 80) - 40
            x = (self.x0[i] + 18 * t + self.sway[i] * math.sin(self.freq[i] * 2 * math.pi * t + self.ph[i])) % W
            sp = self.sprite(self.size[i], self.blur[i])
            a = int(255 * self.alpha[i] * amount)
            lay.paste(Image.new('L', sp.size, a), (int(x - sp.width / 2), int(y - sp.height / 2)),
                      Image.composite(sp, Image.new('L', sp.size, 0), sp))
        white = Image.new('RGB', (W, H), (255, 252, 246))
        return Image.composite(white, img, lay)


SNOW = Snow(LOOK.get('snow_flakes', 110))


def vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = 1 - LOOK.get('vignette', 0.18) * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2
    return v[..., None].clip(0, 1)


VIG = vignette()


def finish(img, t, s):
    is_end = s.get('kind') == 'endcard'
    if not is_end:
        img = bloom(img, LOOK.get('bloom', 0.35))
        img = Image.fromarray((np.asarray(img, np.float32) * VIG).astype(np.uint8))
    snow = LOOK.get('snow', 0.8) * (LOOK.get('snow_on_endcard', 0.0) if is_end else 1.0)
    return SNOW.apply(img, t, snow)


# ---------- frame assembly ----------
def shot_index(t):
    for s in SHOTS:
        if t < s['end'] - 1e-9:
            return s['i']
    return len(SHOTS) - 1


def compose(f, streams):
    """streams: dict shot_i -> ShotStream positioned at frame f (created on demand)."""
    t = f / FPS
    i = shot_index(t)
    s = SHOTS[i]
    pair = None
    if i + 1 < len(SHOTS) and t >= s['end'] - s['post'] and s['post'] > 0:
        pair = (i, i + 1, SHOTS[i + 1])
    elif i > 0 and t < s['start'] + s['pre']:
        pair = (i - 1, i, s)
    need = [pair[0], pair[1]] if pair else [i]
    for k in need:
        if k not in streams:
            streams[k] = ShotStream(SHOTS[k], f)
    for k in list(streams):
        if k not in need and k < min(need):
            streams.pop(k).close()
    frames = {k: streams[k].frame() for k in need}
    if pair:
        a, b, nxt = pair
        d = nxt['tin']['d']
        p = (t - (nxt['start'] - d / 2)) / d
        img = transition(nxt['tin']['type'], frames[a], frames[b], p)
        owner = SHOTS[b] if p >= 0.5 else SHOTS[a]
    else:
        img, owner = frames[i], s
    return finish(img, t, owner)


def render(out):
    enc = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                            '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                            '-vf', 'scale=in_range=full:out_color_matrix=bt709:out_range=tv,format=yuv420p',
                            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '16',
                            '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out],
                           stdin=subprocess.PIPE)
    streams = {}
    for f in range(NFRAMES):
        enc.stdin.write(compose(f, streams).tobytes())
        if f % 90 == 0:
            print(f'  frame {f}/{NFRAMES}', flush=True)
    for st in streams.values():
        st.close()
    enc.stdin.close()
    enc.wait()


def still(t):
    f = int(round(t * FPS))
    streams = {}
    img = compose(f, streams)
    for st in streams.values():
        st.close()
    return img


def storyboard(out):
    tw, th, cols = 270, 480, 6
    cells = [(s, still(s['start'] + s['dur'] * 0.55).resize((tw, th), Image.LANCZOS)) for s in SHOTS]
    capf, small, head = font('SemiBold', 17), font('Medium', 14), font('Bold', 30)
    cw_, ch_ = tw + 24, th + 110
    rows = math.ceil(len(cells) / cols)
    sheet = Image.new('RGB', (cols * cw_ + 24, rows * ch_ + 110), CREAM)
    d = ImageDraw.Draw(sheet)
    d.text((24, 26), P['title'], font=head, fill=BROWN)
    d.text((24, 66), f"{TOTAL:.1f}s · 1080×1920 · {P['music_note']}", font=small, fill=BROWN)
    for i, (s, im) in enumerate(cells):
        x, y = 24 + (i % cols) * cw_, 100 + (i // cols) * ch_
        sheet.paste(im, (x, y))
        d.rectangle([x - 1, y - 1, x + tw, y + th], outline=BROWN)
        d.text((x, y + th + 8), f"{i + 1:02d} · {s['start']:.1f}–{s['end']:.1f}s · {s['scene']}", font=capf, fill=BROWN)
        tin = s['tin']
        note = (f"In: {tin['type']} {tin['d']:.2f}s. " if tin['d'] else '') + s.get('note', '')
        line, ly = '', y + th + 34
        for w_ in note.split():
            if small.getlength(line + ' ' + w_) > tw:
                d.text((x, ly), line.strip(), font=small, fill=(60, 40, 35)); ly += 18; line = ''
            line += ' ' + w_
        d.text((x, ly), line.strip(), font=small, fill=(60, 40, 35))
    sheet.save(out, quality=92)


if __name__ == '__main__':
    out = sys.argv[2]
    if '--storyboard' in sys.argv:
        storyboard(out)
    elif '--stills' in sys.argv:
        os.makedirs(out, exist_ok=True)
        for v in sys.argv[sys.argv.index('--stills') + 1].split(','):
            still(float(v)).save(os.path.join(out, f'still_{float(v):05.2f}.jpg'), quality=92)
    else:
        render(out)
    print('ok', out)
