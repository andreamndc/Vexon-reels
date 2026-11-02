#!/usr/bin/env python3
"""Build the CapCut rebuild kit (clips, overlay PNGs, timeline.csv) from a plan + its clean render.
Usage: build_kit.py plan.json clean.mp4 kitdir"""
import copy, csv, json, math, os, shutil, subprocess, sys
from PIL import Image
plan, clean, kit = sys.argv[1:4]
RR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skill', 'scripts', 'render_reel.py')
P = json.load(open(plan)); BEAT = 60 / P['bpm']
for d in ('clips', 'layers'): shutil.rmtree(os.path.join(kit, d), ignore_errors=True); os.makedirs(os.path.join(kit, d))
F = lambda x: math.ceil(x * 30 - 1e-6)
def render(p, out, mode, times):
    json.dump(p, open('_kit_plan.json', 'w'))
    subprocess.run(['python3', RR, '_kit_plan.json', out, '--layers', mode, '--at', ','.join(f'{t:.3f}' for t in times)], check=True, capture_output=True)
    return [f'{out}_{round(t * 30) / 30:05.2f}.png' if False else f'{out}_{t:05.2f}.png' for t in times]
def slug(s): return ''.join(c if c.isalnum() else '_' for c in s.upper()).strip('_')

TRANS = {'cut': '-', 'flash': 'White flash (0.2s)', 'whip': 'Whip pan left (0.25s)', 'vwhip': 'Whip pan down (0.25s)',
         'zoom': 'Zoom in / pull in with blur (0.2s)', 'punch': 'Zoom in punch (0.2s)', 'panels': 'Slide down / blinds (0.3s)',
         'cutout': 'Torn paper / rip (0.3s)', 'hit': 'Hard cut + Shake effect 0.2s', 'fade': 'Dissolve / mix'}
rows = []; t = 0; vi = 0
shots = P['shots']
for k, s in enumerate(shots):
    s['t0'] = t; t += s['sec']; s['t1'] = t
END = t
# ---- clips
for k, s in enumerate(shots):
    f0, f1 = F(s['t0']), F(s['t1']); vi += 1
    name = f"{vi:02d}_{slug(s['name']).lower()}"
    if s.get('src'):
        fn = f'clips/{name}.mp4'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', clean, '-vf', f"select='between(n,{f0},{f1 - 1})',setpts=N/30/TB", '-r', '30',
                        '-frames:v', str(f1 - f0), '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-maxrate', '20M', '-bufsize', '40M',
                        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', os.path.join(kit, fn)], check=True)
    else:
        fn = f'clips/{name}_navy_0b1525.png'; Image.new('RGB', (1080, 1920), (11, 21, 37)).save(os.path.join(kit, fn))
    tr = TRANS.get(s['tin'], s['tin']) + (f" ({s.get('fade', 0.6)}s)" if s['tin'] == 'fade' else '')
    rows.append(['VIDEO', s['t0'], s['t1'], fn, tr, '-', '-', s.get('note', '')])
# ---- overlays
def tc(x): f = F(x); return f"{int(f // 1800):02d}:{(f / 30) % 60:05.2f} (frame {f})"
def ov(a, b, fn, ai, ao, note=''): rows.append(['OVERLAY', a, b, fn, '-', ai, ao, note])
for k, s in enumerate(shots):
    if s.get('cont'): continue
    span_end = shots[k + s.get('text_span', 1) - 1]['t1'] if s.get('text_span') else s['t1']
    s.setdefault('kind', 'line' if s.get('text') else 'plain')
    if s['kind'] == 'title':
        Q = copy.deepcopy(P); Q['shots'][k]['title_words'] = []
        src = render(Q, os.path.join(kit, 'layers', '_b'), 'text', [s['t0'] + 1.0])[0]
        os.rename(src, os.path.join(kit, 'layers', 'hook_0_band.png'))
        ov(s['t0'], span_end, 'layers/hook_0_band.png', 'Fade in 0.25s', 'Fade out 0.13s', 'Soft dark band behind the hook')
        for i, w in enumerate(s['title_words']):
            Q = copy.deepcopy(P); ww = dict(w); ww['beat'] = 0; ww.pop('until', None); Q['shots'][k]['title_words'] = [ww]
            src = render(Q, os.path.join(kit, 'layers', '_h'), 'nob', [s['t0'] + 1.0])[0]
            fn = f"layers/hook_{i + 1}_{slug(w['text'])}.png"; os.rename(src, os.path.join(kit, fn))
            a = s['t0'] + w['beat'] * BEAT; b = s['t0'] + w['until'] * BEAT if 'until' in w else span_end
            ov(a, b, fn, 'Zoom out (shrink) 0.2s', 'Fade out 0.13s', 'Lands on a song hit')
    elif s.get('text'):
        n = slug(s['name']).lower(); bx = s.get('box_at', BEAT if s['kind'] == 'cta' else 2 * BEAT)
        tin = s.get('text_in', 0.32); out_s = s.get('text_out_f', 5) / 30
        if bx > 0.2:  # plain state, then boxed state
            Q = copy.deepcopy(P); Q['shots'][k]['box_at'] = 99
            src = render(Q, os.path.join(kit, 'layers', '_p'), 'text', [min(s['t0'] + 1.0, span_end - out_s - 0.05)])[0]
            os.rename(src, os.path.join(kit, 'layers', f'text_{n}_plain.png'))
            ov(s['t0'], s['t0'] + bx, f'layers/text_{n}_plain.png', f'Wipe / slide up {tin:.2f}s', '-')
            src = render(P, os.path.join(kit, 'layers', '_x'), 'text', [min(s['t0'] + bx + 0.4, span_end - out_s - 0.03)])[0]
            os.rename(src, os.path.join(kit, 'layers', f'text_{n}_boxed.png'))
            ov(s['t0'] + bx, span_end, f'layers/text_{n}_boxed.png', '-', f'Fade out {out_s:.2f}s', 'Orange box(es) appear here')
        else:
            src = render(P, os.path.join(kit, 'layers', '_x'), 'text', [min(s['t0'] + 0.4, span_end - out_s - 0.03)])[0]
            os.rename(src, os.path.join(kit, 'layers', f'text_{n}.png'))
            ov(s['t0'], span_end, f'layers/text_{n}.png', f'Slide up {tin:.2f}s', f'Fade out {out_s:.2f}s')
for k, s in enumerate(shots):
    if s.get('fx'):
        n = slug(s['name']).lower(); at = s['fx'].get('at', BEAT)
        src = render(P, os.path.join(kit, 'layers', '_f'), 'fx', [min(s['t0'] + at + 0.4, s['t1'] - 0.2)])[0]
        fn = f"layers/fx_{n}_{s['fx']['kind']}.png"; os.rename(src, os.path.join(kit, fn))
        ov(s['t0'] + at, s['t1'], fn, 'Zoom out (shrink) 0.3s' if s['fx']['kind'] != 'rings' else 'Zoom in 0.3s (optional loop: Pulse)', 'Fade out 0.15s')
rows.append(['AUDIO', 0, END, P.get('audio_label', 'Music'), '-', '-', '-', P.get('music_note', '')])
for f in os.listdir(os.path.join(kit, 'layers')):
    if f.startswith('_'): os.remove(os.path.join(kit, 'layers', f))
os.remove('_kit_plan.json')
order = {'VIDEO': 0, 'OVERLAY': 1, 'AUDIO': 2}
rows.sort(key=lambda r: (order[r[0]], r[1]))
with open(os.path.join(kit, 'timeline.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['track', 'start', 'end', 'file', 'transition_in', 'animation_in', 'animation_out', 'notes'])
    for r in rows: w.writerow([r[0], tc(r[1]), tc(r[2])] + r[3:])
print('kit built', END, len(rows), 'rows')
