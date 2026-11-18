#!/usr/bin/env python3
"""American Heritage Chocolate reel renderer (own style; not the VEXON kit).

  python3 render.py plan.json out.mp4                 full render (silent audio track)
  python3 render.py plan.json out.png --storyboard    storyboard sheet
  python3 render.py plan.json outdir --stills 1.0,9.5 single frames
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
FONTS = os.path.join(ROOT, 'brand', 'fonts')
BROWN = (0x59, 0x2d, 0x2b)
CREAM = (0xf3, 0xed, 0xe3)
WHITE = (255, 255, 255)
GRADE = 'eq=contrast=1.04:saturation=1.06,colorbalance=rs=0.025:bs=-0.03:rm=0.02:bm=-0.025'


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONTS, f'Montserrat-{weight}.ttf'), size)


def src_path(key):
    return os.path.normpath(os.path.join(BASE, P['sources'][key]))


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ---------- timeline ----------
t = 0.0
for s in P['shots']:
    s['start'] = t
    t += s['dur']
TOTAL = t
NFRAMES = int(round(TOTAL * FPS))


def shot_at(gt):
    for s in P['shots']:
        if s['start'] <= gt < s['start'] + s['dur'] - 1e-9:
            return s
    return P['shots'][-1]


# ---------- video decoding ----------
def decode(src, ss, dur, w, h, frames=None):
    """Decode a clip segment scaled to cover w x h (no crop), graded. Returns list of HxWx3 arrays."""
    n = frames or max(1, int(round(dur * FPS)))
    vf = f'fps={FPS},scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,{GRADE}'
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{ss:.3f}', '-i', src, '-t', f'{dur + 0.5:.3f}',
           '-vf', vf, '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    # output size after cover-scale
    probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                            'stream=width,height:stream_side_data=rotation', '-of', 'json', src],
                           capture_output=True, text=True).stdout
    st = json.loads(probe)['streams'][0]
    sw, sh = st['width'], st['height']
    if any(abs(d.get('rotation', 0)) == 90 for d in st.get('side_data_list', [])):
        sw, sh = sh, sw
    k = max(w / sw, h / sh)
    ow, oh = int(math.ceil(sw * k / 2) * 2) if False else None, None
    # replicate ffmpeg rounding: the forced dimension is exact, the other rounds
    if w / sw >= h / sh:
        ow, oh = w, int(round(sh * w / sw))
    else:
        ow, oh = int(round(sw * h / sh)), h
    fsz = ow * oh * 3
    got = len(raw) // fsz
    if got == 0:
        raise RuntimeError(f'no frames from {src} @ {ss}')
    arr = np.frombuffer(raw[:got * fsz], np.uint8).reshape(got, oh, ow, 3)
    out = [arr[min(i, got - 1)] for i in range(n)]
    return out


def crop_zoom(img, z, cx, cy, w, h, zmax):
    """img is cover-scaled to (w,h)*zmax. Crop window for zoom z, then resize to w x h."""
    ih, iw = img.shape[:2]
    cw, ch = w * zmax / z, h * zmax / z
    cw, ch = min(cw, iw), min(ch, ih)
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    im = Image.fromarray(img)
    return im.resize((w, h), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def shot_frames(s, local_times=None):
    """Yield PIL frames for a video shot; local_times (seconds from shot start) for stills."""
    zmax = max(s['z'])
    sp = s.get('speed', 1.0)
    cx, cy = s.get('cx', 0.5), s.get('cy', 0.5)
    cw, chh = int(round(W * zmax)), int(round(H * zmax))
    if local_times is None:
        n = int(round(s['dur'] * FPS))
        frames = decode(src_path(s['src']), s['ss'], s['dur'] * sp, cw, chh, n)
        lts = [i / FPS for i in range(n)]
    else:
        frames, lts = [], local_times
        for lt in lts:
            frames += decode(src_path(s['src']), s['ss'] + lt * sp, 0.1, cw, chh, 1)
    for f, lt in zip(frames, lts):
        u = ease(lt / s['dur'])
        z = s['z'][0] + (s['z'][1] - s['z'][0]) * u
        yield crop_zoom(f, z, cx, cy, W, H, zmax)


def collage_frames(s, local_times=None):
    gap = 10
    bh = (H - 2 * gap) // 3
    bands = []
    for b in s['bands']:
        n = int(round(s['dur'] * FPS))
        if local_times is None:
            fr = decode(src_path(b['src']), b['ss'], s['dur'], W, H, n)
        else:
            fr = [decode(src_path(b['src']), b['ss'] + lt, 0.1, W, H, 1)[0] for lt in local_times]
        bands.append(fr)
    lts = local_times if local_times is not None else [i / FPS for i in range(int(round(s['dur'] * FPS)))]
    for i, lt in enumerate(lts):
        canvas = Image.new('RGB', (W, H), CREAM)
        for k, (b, fr) in enumerate(zip(s['bands'], bands)):
            img = fr[min(i, len(fr) - 1)]
            ih = img.shape[0]
            z = 1.0 + 0.04 * ease(lt / s['dur'])
            ch = bh / z
            cw = W / z
            y0 = min(max(b['cy'] * ih - ch / 2, 0), ih - ch)
            x0 = (W - cw) / 2
            band = Image.fromarray(img).resize((W, bh), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
            canvas.paste(band, (0, k * (bh + gap)))
        yield canvas


# ---------- end card ----------
_END = None


def paper():
    rng = np.random.default_rng(7)
    base = np.ones((H, W, 3), np.float32) * np.array(CREAM, np.float32)
    n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    n = np.array(Image.fromarray(((n * 20) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
                 .filter(ImageFilter.GaussianBlur(3)), np.float32) - 128
    fine = rng.normal(0, 3.0, (H, W)).astype(np.float32)
    base += (n * 0.35 + fine)[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.07 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    base *= v[..., None]
    return Image.fromarray(base.clip(0, 255).astype(np.uint8))


def swirl(img):
    """Thin brown hand-drawn line with a loop, like the brand's 'Did you know?' cards."""
    pts = []
    for i in range(400):
        u = -1.2 + i / 399 * (2 * math.pi + 2.0)
        x = 70 * u - 95 * math.sin(u)
        y = -80 * math.cos(u)
        pts.append((x, y))
    ang = math.radians(-18)
    out = []
    for x, y in pts:
        xr, yr = x * math.cos(ang) - y * math.sin(ang), x * math.sin(ang) + y * math.cos(ang)
        out.append((640 + xr * 1.0, 1640 + yr * 1.0))
    layer = Image.new('RGBA', (W * 2, H * 2), (0, 0, 0, 0))
    ImageDraw.Draw(layer).line([(x * 2, y * 2) for x, y in out], fill=BROWN + (235,), width=8, joint='curve')
    layer = layer.resize((W, H), Image.LANCZOS)
    img.paste(layer, (0, 0), layer)


def endcard_base():
    global _END
    if _END is None:
        e = P['endcard']
        bg = paper().convert('RGBA')
        swirl(bg)
        logo = Image.open(os.path.normpath(os.path.join(BASE, e['logo']))).convert('RGBA')
        lw = e['logo_w']
        lh = int(logo.height * lw / logo.width)
        logo = logo.resize((lw, lh), Image.LANCZOS)
        cta = text_layer(e['cta'], 'plain', e['cta_size'])
        _END = (bg, logo, cta)
    return _END


def endcard_frame(lt):
    e = P['endcard']
    bg, logo, cta = endcard_base()
    im = bg.copy()
    a1 = ease((lt - 0.1) / 0.5)
    a2 = ease((lt - 0.55) / 0.45)
    lg = logo.copy()
    lg.putalpha(Image.eval(lg.getchannel('A'), lambda v: int(v * a1)))
    im.alpha_composite(lg, ((W - lg.width) // 2, e['logo_y'] - lg.height // 2 + int(14 * (1 - a1))))
    c = cta.copy()
    c.putalpha(Image.eval(c.getchannel('A'), lambda v: int(v * a2)))
    im.alpha_composite(c, ((W - c.width) // 2, e['cta_y'] - c.height // 2 + int(18 * (1 - a2))))
    return im.convert('RGB')


# ---------- text ----------
_TXT = {}


def text_layer(text, style, size):
    key = (text, style, size)
    if key in _TXT:
        return _TXT[key]
    lines = text.split('\n')
    if style == 'box':
        f = font('SemiBold', size)
        fill, stroke, sw = WHITE, None, 0
    elif style == 'plain':
        f = font('SemiBold', size)
        fill, stroke, sw = BROWN, None, 0
    else:
        f = font('Bold', size)
        fill, stroke, sw = WHITE, BROWN, max(4, size // 12)
    lh = int(size * 1.22)
    widths = [f.getlength(l) for l in lines]
    tw = int(max(widths)) + 2 * sw
    th = lh * len(lines) + 2 * sw
    padx, pady = (int(size * 0.85), int(size * 0.6)) if style == 'box' else (24, 24)
    lw, lhh = tw + 2 * padx, th + 2 * pady
    layer = Image.new('RGBA', (lw, lhh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if style == 'box':
        d.rectangle([0, 0, lw - 1, lhh - 1], fill=BROWN + (255,))
        ins = 9
        d.rectangle([ins, ins, lw - 1 - ins, lhh - 1 - ins], outline=(0xc9, 0xa8, 0x98, 255), width=2)
    else:
        # soft shadow for legibility on busy footage
        sh = Image.new('RGBA', (lw, lhh), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        for i, l in enumerate(lines):
            x = (lw - widths[i]) / 2
            sd.text((x, pady + sw + i * lh + 3), l, font=f, fill=(40, 15, 10, 110), stroke_width=sw + 2, stroke_fill=(40, 15, 10, 110))
        layer = Image.alpha_composite(layer, sh.filter(ImageFilter.GaussianBlur(6)))
        d = ImageDraw.Draw(layer)
    for i, l in enumerate(lines):
        x = (lw - widths[i]) / 2
        y = pady + sw + i * lh
        if stroke:
            d.text((x, y), l, font=f, fill=fill + (255,), stroke_width=sw, stroke_fill=stroke + (255,))
        else:
            d.text((x, y), l, font=f, fill=fill + (255,))
    _TXT[key] = layer
    return layer


def overlay_text(img, gt):
    im = img.convert('RGBA')
    for tx in P['texts']:
        if not (tx['t0'] <= gt < tx['t1']):
            continue
        a = min(ease((gt - tx['t0']) / 0.3), ease((tx['t1'] - gt) / 0.25))
        rise = int(22 * (1 - ease((gt - tx['t0']) / 0.35)))
        lay = text_layer(tx['text'], tx['style'], tx['size'])
        if a < 1:
            lay = lay.copy()
            lay.putalpha(Image.eval(lay.getchannel('A'), lambda v, a=a: int(v * a)))
        im.alpha_composite(lay, ((W - lay.width) // 2, tx['y'] - lay.height // 2 + rise))
    return im.convert('RGB')


# ---------- frame access ----------
def frames_for_shot(s, lts=None):
    kind = s.get('kind', 'video')
    if kind == 'collage':
        return collage_frames(s, lts)
    if kind == 'endcard':
        times = lts if lts is not None else [i / FPS for i in range(int(round(s['dur'] * FPS)))]
        return (endcard_frame(lt) for lt in times)
    return shot_frames(s, lts)


def still(gt):
    s = shot_at(gt)
    lt = gt - s['start']
    img = next(iter(frames_for_shot(s, [lt])))
    img = overlay_text(img, gt)
    # dissolve into end card
    if s.get('kind') == 'endcard' and lt < s.get('fade_in', 0):
        prev = P['shots'][P['shots'].index(s) - 1]
        pimg = overlay_text(next(iter(frames_for_shot(prev, [prev['dur'] - 1 / FPS]))), s['start'] - 1 / FPS)
        img = Image.blend(pimg, img, ease(lt / s['fade_in']))
    return img


def render(out):
    enc = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                            '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out],
                           stdin=subprocess.PIPE)
    fi = 0
    last = None
    for s in P['shots']:
        n = int(round((s['start'] + s['dur']) * FPS)) - fi
        lts = [(fi + i) / FPS - s['start'] for i in range(n)]
        fr = list(frames_for_shot(s, None))
        for i, lt in enumerate(lts):
            img = fr[min(i, len(fr) - 1)]
            gt = (fi + i) / FPS
            img = overlay_text(img, gt)
            if s.get('kind') == 'endcard' and lt < s.get('fade_in', 0) and last is not None:
                img = Image.blend(last, img, ease(lt / s['fade_in']))
            enc.stdin.write(img.tobytes())
            if s.get('kind') != 'endcard':
                last = img
        fi += n
        print(f"  {s['scene']:<24} {s.get('src', s.get('kind'))} done ({fi}/{NFRAMES})", flush=True)
    enc.stdin.close()
    enc.wait()


def storyboard(out):
    tw, th = 270, 480
    cols = 6
    cells = []
    for i, s in enumerate(P['shots']):
        # pick a moment where any overlapping text is fully visible
        cand = s['start'] + s['dur'] * 0.6
        for tx in P['texts']:
            if tx['t0'] < s['start'] + s['dur'] and tx['t1'] > s['start']:
                cand = min(max(cand, tx['t0'] + 0.45), tx['t1'] - 0.3, s['start'] + s['dur'] - 0.05)
                cand = max(cand, s['start'])
        if s.get('kind') == 'endcard':
            cand = s['start'] + s['dur'] - 0.1
        cells.append((s, still(cand).resize((tw, th), Image.LANCZOS)))
    rows = math.ceil(len(cells) / cols)
    capf, small, head = font('SemiBold', 17), font('Medium', 14), font('Bold', 30)
    cw_, ch_ = tw + 24, th + 110
    sheet = Image.new('RGB', (cols * cw_ + 24, rows * ch_ + 110), CREAM)
    d = ImageDraw.Draw(sheet)
    d.text((24, 26), P['title'], font=head, fill=BROWN)
    d.text((24, 66), f"{TOTAL:.1f}s · 1080×1920 · {P['music_note']}", font=small, fill=BROWN)
    for i, (s, im) in enumerate(cells):
        x, y = 24 + (i % cols) * cw_, 100 + (i // cols) * ch_
        sheet.paste(im, (x, y))
        d.rectangle([x - 1, y - 1, x + tw, y + th], outline=BROWN)
        d.text((x, y + th + 8), f"{i + 1:02d} · {s['start']:.1f}–{s['start'] + s['dur']:.1f}s · {s['scene']}", font=capf, fill=BROWN)
        words, line, ly = s.get('note', '').split(), '', y + th + 34
        for w_ in words:
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
