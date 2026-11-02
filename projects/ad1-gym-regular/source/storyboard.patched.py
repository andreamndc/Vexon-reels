#!/usr/bin/env python3
"""Storyboard sheet from a plan: renders one real still per beat (mid-shot, after text is in) and
captions it with timecode, name, on-screen text and the shot's "note".
Usage: storyboard.py plan.json out.png [workdir]"""
import json, os, subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); FD = os.path.join(os.path.dirname(HERE), 'assets', 'fonts')
plan, out = sys.argv[1], sys.argv[2]; work = sys.argv[3] if len(sys.argv) > 3 else os.path.splitext(out)[0] + '_frames'
os.makedirs(work, exist_ok=True)
P = json.load(open(plan)); BEAT = 60 / P.get('bpm', 140); BAR = 4 * BEAT
t = 0; items = []; burst = None
for s in P['shots']:
    d = s['sec'] if 'sec' in s else (s['bars'] * BAR if 'bars' in s else s.get('beats', 1) * BEAT)
    if s.get('kind') == 'burst':
        if burst is None: burst = dict(s, name='DROP · burst', t0=t, t1=t + d, mid=t + d * 0.6); items.append(burst)
        else: burst['t1'] = t + d
    elif not s.get('cont'):
        items.append(dict(s, t0=t, t1=t + d, mid=min(t + d - 0.3, t + max(1.5, d * 0.6))))
    else: items[-1]['t1'] = t + d
    t += d
mids = ','.join(f"{i['mid']:.2f}" for i in items)
subprocess.run([sys.executable, os.path.join(HERE, 'render_reel.py'), plan, os.path.join(work, 'f'), '--stills', mids], check=True)
def f(n, s, v=None):
    x = ImageFont.truetype(os.path.join(FD, n), s)
    if v: x.set_variation_by_axes([v])
    return x
SI = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf', 21)
cols = 4; tw, th = 300, 533; cw = tw + 30; capH = 280; rows = (len(items) + cols - 1) // cols
im = Image.new('RGB', (cols * cw + 30, 150 + rows * (th + capH)), (11, 21, 37)); d = ImageDraw.Draw(im)
d.text((30, 24), P.get('title', 'VEXON reel · Storyboard'), font=f('Oswald.ttf', 44, 650), fill=(255, 122, 26))
d.text((30, 90), f"9:16 · {t:.1f}s · {P.get('bpm', 140)} BPM · {P.get('music_note', '')}"[:125], font=f('PublicSans.ttf', 20, 500), fill=(217, 210, 196))
for i, it in enumerate(items):
    x = 30 + (i % cols) * cw; y = 150 + (i // cols) * (th + capH)
    im.paste(Image.open(os.path.join(work, f"f_{it['mid']:05.2f}.png")).resize((tw, th)), (x, y))
    d.text((x, y + th + 10), f"{it['t0']:.1f}s – {it['t1']:.1f}s", font=f('PublicSans.ttf', 18, 600), fill=(138, 133, 120))
    d.text((x, y + th + 32), it.get('name', it.get('kind', '')).upper(), font=f('Oswald.ttf', 28, 600), fill=(247, 177, 55))
    yy = y + th + 72
    body = (f"“{it['text']}” " if it.get('text') else '') + it.get('note', '')
    for l in textwrap.wrap(body, 29)[:8]: d.text((x, yy), l, font=SI, fill=(251, 247, 239)); yy += 25
im.save(out); print(out, im.size)
