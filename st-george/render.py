"""GSD St. George reel - 9:16, 25 s, built from location photos.
Format follows the client's new-location reel (instagram.com/reel/DecLJHPOYEJ): bold italic white serif with a navy
outline, words revealed one at a time, quick dissolves between sections, GSD logo on the end card.
Timing follows the TikTok sound (@mayoutfitofficial 7308589082270027013, 138.04 BPM, bar = 1.7384 s) used from
0:14.12 (where the bass enters): cuts on the bar, words on the beat. Exported with a silent track (copyrighted
song) - add the sound in-app starting at 0:14.1.

Usage: python3 render.py <out.mp4> [--stills t1,t2,...] [--logo path/to/white_logo.png]"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, TOTAL = 1080, 1920, 30, 25.0
BEAT = 0.4346; BAR = 4 * BEAT
OUT = sys.argv[1]
STILLS = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')] if '--stills' in sys.argv else None
NOTEXT = '--notext' in sys.argv
LOGO = sys.argv[sys.argv.index('--logo') + 1] if '--logo' in sys.argv else None
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = '/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf'   # Times-style bold italic

def b(n): return round(n * BAR, 3)          # bar n start time

# (t0, t1, photo, zoom from->to, centre from->to, transition-in)
SHOTS = [
    # 0-3.5  ST. GEORGE, UTAH!  /  Looking for a dermatologist?
    (b(0), b(1), 'exterior', (1.00, 1.10), ((.42, .55), (.40, .55)), 'cut'),
    (b(1), b(2), 'exterior', (1.45, 1.55), ((.33, .47), (.31, .47)), 'cut'),      # window signage
    # 3.5-7  EXPERT DERMATOLOGIC CARE, CLOSE TO HOME.
    (b(2), b(3), 'reception', (1.00, 1.08), ((.50, .55), (.50, .55)), 'dissolve'),
    (b(3), b(4), 'hallway', (1.00, 1.14), ((.48, .55), (.47, .56)), 'cut'),       # push down the corridor
    # 7-12.2  MEDICAL & PEDIATRIC DERMATOLOGY
    (b(4), b(5), 'exam_room', (1.00, 1.06), ((.62, .55), (.64, .55)), 'dissolve'),
    (b(5), b(6), 'exam_room', (1.55, 1.62), ((.70, .42), (.70, .42)), 'cut'),     # wall-mounted equipment
    (b(6), b(7), 'exam_room', (1.45, 1.50), ((.50, .48), (.52, .48)), 'cut'),     # counter, supplies
    # 12.2-17.4  GREAT AVAILABILITY. / CARE FOR THE WHOLE FAMILY.
    (b(7), b(8), 'hallway', (1.30, 1.42), ((.45, .50), (.45, .50)), 'dissolve'),  # tighter push down the corridor
    (b(8), b(9), 'reception', (1.35, 1.42), ((.50, .62), (.50, .60)), 'cut'),
    (b(9), b(10), 'exam_room', (1.25, 1.30), ((.20, .62), (.22, .62)), 'cut'),    # chairs + artwork
    # 17.4-20.9  GET THE CARE YOU NEED, WHEN YOU NEED IT.
    (b(10), b(11), 'reception', (1.12, 1.00), ((.50, .55), (.50, .55)), 'dissolve'),
    (b(11), b(12), 'exterior', (1.15, 1.22), ((.70, .55), (.72, .55)), 'cut'),
    # 20.9-25  end card: blurred exterior, logo + CTA
    (b(12), TOTAL, 'exterior', (1.05, 1.10), ((.45, .55), (.45, .55)), 'dissolve'),
]
XF = 0.3

# text cards: (t0, t1, words with their beat offsets, centre y, font size)
def card(t0, t1, text, y, size, step=1):
    words = text.split(' ')
    return (t0, t1, [(w, t0 + i * step * BEAT) for i, w in enumerate(words)], y, size)
TEXT = [
    card(b(0) + .05, b(1) + 2 * BEAT, 'ST. GEORGE, UTAH!', 560, 132, 1),
    card(b(1) + 2 * BEAT, b(2), 'Looking for a dermatologist?', 560, 92, .5),
    card(b(2) + .1, b(4), 'EXPERT DERMATOLOGIC CARE, CLOSE TO HOME.', 820, 96, .5),
    card(b(4) + .1, b(7), 'MEDICAL & PEDIATRIC DERMATOLOGY', 820, 112, 1),
    card(b(7) + .1, b(8) + 2 * BEAT, 'GREAT AVAILABILITY.', 820, 112, 1),
    card(b(8) + 2 * BEAT, b(10), 'CARE FOR THE WHOLE FAMILY.', 820, 104, .5),
    card(b(10) + .1, b(12), 'GET THE CARE YOU NEED, WHEN YOU NEED IT.', 820, 96, .5),
    card(b(12) + .2, TOTAL, 'SCHEDULE YOUR VISIT IN ST. GEORGE.', 1160, 92, .5),
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

def crop(img, z, cx, cy):
    a = W / H
    bw, bh = (img.height * a, img.height) if img.width / img.height > a else (img.width, img.width / a)
    cw, ch = bw / z, bh / z
    x0 = min(max(cx * img.width - cw / 2, 0), img.width - cw); y0 = min(max(cy * img.height - ch / 2, 0), img.height - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

def ease(u): return u * u * (3 - 2 * u)

def shot(i, t):
    t0, t1, name, (z0, z1), ((x0, y0), (x1, y1)), _ = SHOTS[i]
    u = ease(min(max((t - t0) / (t1 - t0), 0), 1))
    img = crop(photo(name), z0 + (z1 - z0) * u, x0 + (x1 - x0) * u, y0 + (y1 - y0) * u)
    if i == len(SHOTS) - 1:                      # end card: soft blur, navy wash so a white logo reads
        img = img.filter(ImageFilter.GaussianBlur(14))
        img = Image.blend(img, Image.new('RGB', (W, H), (14, 30, 66)), 0.45)
    return img

def picture(t):
    i = max(j for j, s in enumerate(SHOTS) if s[0] <= t)
    img = shot(i, t)
    if SHOTS[i][5] == 'dissolve' and i > 0 and t - SHOTS[i][0] < XF:
        img = Image.blend(shot(i - 1, t), img, ease((t - SHOTS[i][0]) / XF))
    return img

def wrap(words, fnt, maxw):
    lines, cur = [], []
    for w in words:
        if cur and fnt.getlength(' '.join(cur + [w])) > maxw: lines.append(cur); cur = [w]
        else: cur.append(w)
    lines.append(cur)
    # balance: avoid a lone last word
    if len(lines) > 1 and len(lines[-1]) == 1 and len(lines[-2]) > 2: lines[-1].insert(0, lines[-2].pop())
    return lines

def overlay(img, t):
    img = img.convert('RGBA')
    for t0, t1, words, cy, size in ([] if NOTEXT else TEXT):
        if not (t0 <= t < t1): continue
        fnt = ImageFont.truetype(FONT, size)
        lines = wrap([w for w, _ in words], fnt, 900)
        lh = size * 1.08; y = cy - lh * len(lines) / 2
        fade = ease(min(1, (t1 - t) / 0.18)) if t1 < TOTAL - .01 else 1
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fg = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ds, df = ImageDraw.Draw(sh), ImageDraw.Draw(fg); k = 0
        for line in lines:
            full = ' '.join(line); x = W / 2 - fnt.getlength(full) / 2
            for w in line:
                ts = words[k][1]; k += 1
                if t >= ts:
                    a = ease(min(1, (t - ts) / 0.12)) * fade; pop = 1 + 0.12 * (1 - ease(min(1, (t - ts) / 0.15)))
                    al = int(255 * a)
                    ds.text((x + 4, y + 6), w, font=fnt, fill=(5, 15, 40, int(170 * a)), stroke_width=9, stroke_fill=(5, 15, 40, int(170 * a)))
                    df.text((x, y - (pop - 1) * 40), w, font=fnt, fill=(255, 255, 255, al), stroke_width=5, stroke_fill=(16, 36, 92, al))
                x += fnt.getlength(w + ' ')
            y += lh
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(8)))
        img = Image.alpha_composite(img, fg)
    if LOGO and t >= SHOTS[-1][0]:
        lg = Image.open(LOGO).convert('RGBA'); s = 520 / lg.width; lg = lg.resize((520, round(lg.height * s)), Image.LANCZOS)
        a = ease(min(1, (t - SHOTS[-1][0]) / 0.4)); lg.putalpha(lg.getchannel('A').point(lambda v: int(v * a)))
        img.alpha_composite(lg, (W // 2 - 260, 860 - lg.height))
    return img.convert('RGB')

GRADE = 'eq=contrast=1.05:saturation=1.08,colorbalance=rh=0.01:bh=-0.01,vignette=PI/7'
if STILLS:
    for t in STILLS:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-i', '-',
                        '-vf', GRADE, f'{OUT}_{t:05.2f}.png'], input=overlay(picture(t), t).tobytes(), check=True)
    sys.exit()
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                        '-i', '-', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-vf', GRADE, '-map', '0:v', '-map', '1:a',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
                        '-t', str(TOTAL), '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for f in range(int(TOTAL * FPS)):
    enc.stdin.write(overlay(picture(f / FPS), f / FPS).tobytes())
enc.stdin.close(); enc.wait(); print('done', OUT)
