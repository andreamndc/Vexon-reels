"""Grand Opening recap reel - 9:16, 22.45 s, cut on the exact cut points of the reference TikTok
(@bonsoirindonesia 7600338656771034388, ~103 BPM) so the edit lines up when that sound is added in-app at 0:00.
The video is exported WITHOUT the song (copyrighted); a text and a clean (no text) version are written.

Usage: python3 render.py <media_dir> <out_prefix> [--stills t1,t2,...]
<media_dir> holds the uploaded clips (*.MOV) and the photos converted to JPG (*.jpg)."""
import glob, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, TOTAL = 1080, 1920, 30, 22.45
MEDIA, OUT = sys.argv[1], sys.argv[2]
STILLS = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')] if '--stills' in sys.argv else None
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, 'fonts', 'GreatVibes-Regular.ttf')
SERIF = os.path.join(HERE, 'fonts', 'Cinzel-VariableFont.ttf')

def find(key):
    return glob.glob(os.path.join(MEDIA, f'*{key}*'))[0]

# clips
SHELF, WALK, BAR, GUESTS, RECEP, PORTRAIT, DOOR = 'IMG_2627', 'IMG_3993', 'IMG_3992', 'IMG_2681', 'IMG_2663', 'IMG_2629', 'IMG_2601'
# photos
P_SCISSORS, P_RIBBON, P_GIFTS, P_ROOM, P_STAFF, P_DR, P_WIDE = (
    'IMG_2672', 'IMG_2697', 'IMG_2660', 'IMG_2617', 'IMG_2665', 'IMG_2676', 'ribbon_wide')

def v(key, ss, z=(1.0, 1.05), c=(.5, .5), sp=1.0): return ('v', key, ss, sp, z, c)
def p(key, z=(1.0, 1.08), c=(.5, .5)): return ('p', key, 0, 1, z, c)

# shot boundaries = the reference's cut points (s)
SHOTS = [
    (0.00, 1.20, v(DOOR, 0.0, (1.00, 1.06), (.5, .45))),          # door with balloons swings open
    (1.20, 2.33, v(BAR, 5.0, (1.05, 1.12), (.5, .45))),           # Welcome / Grand Opening sign
    (2.33, 3.60, p(P_SCISSORS, (1.0, 1.07), (.5, .42))),          # beat kicks in: ribbon scissors
    (3.60, 4.70, p(P_RIBBON, (1.0, 1.06), (.5, .5))),             # ribbon-cutting group
    (4.70, 5.90, ('grid', [v(SHELF, 0.5), v(WALK, 2.0), v(WALK, 14.0), v(PORTRAIT, 1.0)])),
    (5.90, 6.17, v(BAR, 0.2, (1.1, 1.12))),                       # champagne
    (6.17, 6.43, v(BAR, 1.7, (1.1, 1.12))),                       # glasses
    (6.43, 7.03, v(WALK, 0.0)),                                   # balloons + gift bags
    (7.03, 7.60, v(SHELF, 0.3)),                                  # products
    (7.60, 8.23, p(P_GIFTS, (1.05, 1.1))),
    (8.23, 8.83, v(WALK, 6.8)),                                   # catering
    (8.83, 9.50, p(P_ROOM, (1.0, 1.06))),
    (9.50, 10.00, v(WALK, 15.8)),                                 # reception counter
    (10.00, 10.53, v(RECEP, 3.2)),                                # staff at the welcome table
    (10.53, 11.43, v(GUESTS, 0.0, (1.08, 1.12), (.45, .40))),       # guests arriving
    (11.43, 12.30, p(P_STAFF, (1.0, 1.06), (.5, .55))),
    (12.30, 12.83, v(GUESTS, 2.8)),
    (12.83, 13.47, p(P_DR, (1.0, 1.06), (.6, .5))),
    (13.47, 14.70, v(GUESTS, 4.3, (1.05, 1.1), (.5, .45))),       # doctor with guests
    (14.70, 15.77, ('split', [p(P_WIDE, (1.0, 1.05), (.5, .55)), v(GUESTS, 1.5, (1.0, 1.04), (.5, .45))])),
    (15.77, 16.97, v(PORTRAIT, 0.5, (1.0, 1.08))),
    (16.97, 17.53, v(WALK, 17.2)),                                # glass display + balloons
    (17.53, 18.10, v(DOOR, 2.4)),                                 # reception table
    (18.10, 18.70, v(WALK, 12.0)),                                # snacks
    (18.70, 19.27, v(RECEP, 4.0)),                                # staff smiling
    (19.27, 19.83, v(SHELF, 3.5)),
    (19.83, 20.63, v(BAR, 3.2)),                                  # welcome table
    (20.63, 22.45, v(BAR, 5.3, (1.0, 1.08), (.5, .45))),          # end on the welcome sign
]
FLASH = [2.33]          # white flash on the beat drop

TEXT = [  # (t0, t1, lines[(text, font, size)], centre y)
    (0.15, 2.33, [('WELCOME TO OUR', SERIF, 52), ('Grand Opening', SCRIPT, 190)], 1300),
    (10.00, 12.83, [("We're so glad", SERIF, 84), ('to be here', SERIF, 84), ('for you!', SERIF, 84)], 500),
    (20.63, 22.45, [('Thank you', SCRIPT, 200), ('for coming out!', SERIF, 74)], 1320),
]

# ---------------------------------------------------------------------------------------------
_vcache, _pcache = {}, {}
def vframes(key, start, n, speed):
    ck = (key, start, n, speed)
    if ck not in _vcache:
        cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-ss', str(start), '-t', str(n / FPS * speed + 0.3), '-i', find(key),
               '-vf', f'setpts=PTS/{speed},fps={FPS},scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
        arr = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.uint8).reshape(-1, H, W, 3)
        if len(arr) < n: arr = np.concatenate([arr, np.repeat(arr[-1:], n - len(arr), 0)])
        _vcache[ck] = arr[:n]
    return _vcache[ck]

def photo(key):
    if key not in _pcache:
        im = Image.open(find(key)).convert('RGB')
        s = 2400 / max(im.size); _pcache[key] = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return _pcache[key]

def crop(img, w, h, z, cx, cy):
    """Sub-pixel crop of the largest w:h window (zoomed by z, centred at cx, cy), resized to w x h."""
    a = w / h
    bw, bh = (img.height * a, img.height) if img.width / img.height > a else (img.width, img.width / a)
    cw, ch = bw / z, bh / z
    x0 = min(max(cx * img.width - cw / 2, 0), img.width - cw); y0 = min(max(cy * img.height - ch / 2, 0), img.height - ch)
    return img.resize((w, h), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

def ease(u): return u * u * (3 - 2 * u)

def source(spec, t0, t1, t, w, h):
    kind, key, ss, sp, (z0, z1), (cx, cy) = spec
    u = min(max((t - t0) / (t1 - t0), 0), 1); z = z0 + (z1 - z0) * ease(u)
    if kind == 'p':
        img = photo(key)
    else:
        n = int(round((t1 - t0 + 0.3) * FPS)); fr = vframes(key, ss, n, sp)
        img = Image.fromarray(fr[min(int((t - t0) * FPS), n - 1)])
    return crop(img, w, h, z, cx, cy)

def picture(t):
    t0, t1, spec = next(s for s in SHOTS if s[0] <= t < s[1]) if t < TOTAL else SHOTS[-1]
    if spec[0] == 'grid':                                   # 2 x 2 panels with thin white gutters
        out = Image.new('RGB', (W, H), (250, 248, 244)); g = 8; pw, ph = (W - g) // 2, (H - g) // 2
        for j, sub in enumerate(spec[1]):
            # panels pop in one after another on 8th notes
            if t - t0 < j * 0.145: continue
            out.paste(source(sub, t0, t1, t, pw, ph), ((j % 2) * (pw + g), (j // 2) * (ph + g)))
        return out
    if spec[0] == 'split':                                  # top / bottom halves
        out = Image.new('RGB', (W, H), (250, 248, 244)); g = 8; ph = (H - g) // 2
        out.paste(source(spec[1][0], t0, t1, t, W, ph), (0, 0))
        if t - t0 >= 0.29: out.paste(source(spec[1][1], t0, t1, t, W, ph), (0, ph + g))
        return out
    img = source(spec, t0, t1, t, W, H)
    for f in FLASH:
        if 0 <= t - f < 0.2:
            img = Image.blend(img, Image.new('RGB', (W, H), (255, 255, 255)), 0.85 * (1 - (t - f) / 0.2))
    return img

_fonts = {}
def font(path, size):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
        if path == SERIF: _fonts[k].set_variation_by_name('Bold')
    return _fonts[k]

def overlay(img, t):
    for t0, t1, lines, cy in TEXT:
        if not (t0 <= t < t1): continue
        a_in = ease(min(1, (t - t0) / 0.3)); a_out = ease(min(1, (t1 - t) / 0.25)) if t1 < TOTAL else 1
        a = a_in * a_out; rise = (1 - a_in) * 30
        sizes = [font(f, s).getbbox(txt) for txt, f, s in lines]
        hts = [int(s * (0.9 if f == SCRIPT else 1.25)) for txt, f, s in lines]
        y = cy - sum(hts) / 2 + rise
        shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fg = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ds, df = ImageDraw.Draw(shadow), ImageDraw.Draw(fg)
        for (txt, f, s), hh in zip(lines, hts):
            fnt = font(f, s); x = W / 2
            stroke = 0 if f == SCRIPT else max(2, s // 22)
            ds.text((x + 3, y + hh / 2 + 5), txt, font=fnt, anchor='mm', fill=(10, 25, 60, int(200 * a)),
                    stroke_width=stroke + 4, stroke_fill=(10, 25, 60, int(200 * a)))
            df.text((x, y + hh / 2), txt, font=fnt, anchor='mm', fill=(255, 255, 255, int(255 * a)),
                    stroke_width=stroke, stroke_fill=(18, 38, 84, int(255 * a)))
            y += hh
        img = Image.alpha_composite(img.convert('RGBA'), shadow.filter(ImageFilter.GaussianBlur(10)))
        img = Image.alpha_composite(img, fg).convert('RGB')
    return img

GRADE = ('eq=contrast=1.06:saturation=1.06:brightness=0.005,'
         'colorbalance=rm=0.025:bm=-0.03:rh=0.015:bh=-0.02,vignette=PI/7')
def encoder(path):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                             '-r', str(FPS), '-i', '-', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                             '-vf', GRADE, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow',
                             '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', '-t', str(TOTAL),
                             '-movflags', '+faststart', path], stdin=subprocess.PIPE)

if STILLS:
    for t in STILLS:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-i', '-',
                        '-vf', GRADE, f'{OUT}_{t:05.2f}.png'], input=overlay(picture(t), t).tobytes(), check=True)
    sys.exit()

clean, text = encoder(f'{OUT}_clean.mp4'), encoder(f'{OUT}_text.mp4')
for f in range(int(round(TOTAL * FPS))):
    t = f / FPS; img = picture(t)
    clean.stdin.write(img.tobytes()); text.stdin.write(overlay(img, t).tobytes())
    if f % 150 == 0: print(f'{t:.0f}s', flush=True)
for e in (clean, text): e.stdin.close(); e.wait()
print('done')
