#!/usr/bin/env python3
"""Render the photo history reel from plan.json.

Usage:
  python3 render.py plan.json out.mp4                 # full render with voiceover
  python3 render.py plan.json stills --stills 1,9.5   # PNG stills at given seconds
  python3 render.py plan.json board.png --storyboard  # one frame per shot, labelled

Every photo fills a 1080x1920 frame. Landscape photos fill the height and pan
left to right; portrait photos get a slow push-in. Transitions copy the inspo
reel: zoomblur (quick blurred push), whip (sideways slide with motion blur),
burst (strong radial zoom blur with a brief flash) and cut.
"""
import json, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageFilter, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
HALF = {"cut": 0.0, "zoomblur": 0.17, "whip": 0.18, "burst": 0.24}

_cache = {}
def load(name):
    """Source photo, pre-scaled with Lanczos (and sharpened if upscaled) so it covers the frame at zoom 1."""
    if name in _cache:
        return _cache[name]
    im = Image.open(os.path.join(HERE, "photos", name + ".jpg")).convert("RGB")
    w, h = im.size
    landscape = w > h
    s = H / h if landscape else max(W / w, H / h)
    s *= 1.0 if landscape else 1.02
    nw, nh = max(W, round(w * s)), max(H, round(h * s))
    big = im.resize((nw, nh), Image.LANCZOS)
    if s > 1.3:
        big = big.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
    arr = np.asarray(big).astype(np.float32)
    _cache[name] = (arr, landscape)
    return _cache[name]

def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)

def place(shot, p, extra_zoom=1.0, dx=0.0):
    """Frame of a shot at motion progress p (0..1)."""
    src, landscape = load(shot["img"])
    sh, sw = src.shape[:2]
    if landscape and "z" not in shot:
        # fill height, travel from the left edge to the right edge
        z = 1.0 * extra_zoom
        travel = sw * z - W
        x0 = -travel * (0.04 + 0.92 * ease(p * 0.9 + 0.05))
        y0 = (H - sh * z) / 2
    else:
        z0, z1 = shot.get("z", [1.0, 1.08])
        z = (z0 + (z1 - z0) * ease(p)) * extra_zoom
        cx, cy = shot.get("cx", 0.5), shot.get("cy", 0.5)
        x0 = W / 2 - sw * z * cx + (sw * z - W) * 0  # anchor point to centre
        y0 = H / 2 - sh * z * cy
        x0 = min(0, max(W - sw * z, x0)) if sw * z >= W else (W - sw * z) / 2
        y0 = min(0, max(H - sh * z, y0)) if sh * z >= H else (H - sh * z) / 2
    if extra_zoom != 1.0:
        # zoom around frame centre
        x0 = W / 2 - (W / 2 - x0)
        y0 = H / 2 - (H / 2 - y0)
    M = np.float32([[z, 0, x0 + dx], [0, z, y0]])
    return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def zoom_frame(img, k):
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, k)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def radial_blur(img, strength, n=7):
    if strength <= 0.002:
        return img
    acc = np.zeros_like(img)
    for i in range(n):
        acc += zoom_frame(img, 1 + strength * i / (n - 1))
    return acc / n

def hblur(img, k):
    k = int(k)
    return img if k < 3 else cv2.blur(img, (k, 1))

# grade: warm, gentle contrast, vignette, grain
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIG = (1 - 0.22 * np.clip(_r - 0.45, 0, 1) ** 1.6)[..., None].astype(np.float32)
_rng = np.random.default_rng(7)
GRAIN = [_rng.normal(0, 4.0, (H, W, 1)).astype(np.float32) for _ in range(6)]
WARM = np.float32([1.035, 1.0, 0.955])

def grade(img, fi):
    img = (img - 128) * 1.05 + 128
    img = img * WARM * VIG + GRAIN[fi % len(GRAIN)]
    return np.clip(img, 0, 255).astype(np.uint8)

def frame_at(plan, t, fi=0):
    shots = plan["shots"]
    ends = [s["t"] for s in shots[1:]] + [plan["end"]]
    i = max(j for j, s in enumerate(shots) if s["t"] <= t + 1e-9)
    s, e = shots[i]["t"], ends[i]

    def prog(j, tt):
        a, b = shots[j]["t"], ends[j]
        hin, hout = HALF[shots[j]["tin"]], HALF[shots[j + 1]["tin"]] if j + 1 < len(shots) else 0
        return (tt - (a - hin)) / ((b + hout) - (a - hin))

    # which transition window are we in?
    nxt = i + 1 if i + 1 < len(shots) else None
    if nxt is not None and t >= e - HALF[shots[nxt]["tin"]]:
        cut_j, before = nxt, True          # approaching the next cut
    elif t < s + HALF[shots[i]["tin"]] and i > 0:
        cut_j, before = i, False           # just after this shot's cut
    else:
        return place(shots[i], prog(i, t))

    kind, h, c = shots[cut_j]["tin"], HALF[shots[cut_j]["tin"]], shots[cut_j]["t"]
    out_j, in_j = cut_j - 1, cut_j
    if kind == "whip":
        u = ease((t - (c - h)) / (2 * h))
        a = place(shots[out_j], prog(out_j, t), dx=-u * W)
        b = place(shots[in_j], prog(in_j, t), dx=(1 - u) * W)
        mask = np.zeros((H, W, 1), np.float32)
        edge = int(round((1 - u) * W))
        mask[:, edge:] = 1
        img = a * (1 - mask) + b * mask
        return hblur(img, 170 * np.sin(np.pi * u))
    amt = 0.55 if kind == "burst" else 0.22
    if before:
        k = (t - (c - h)) / h                # 0 -> 1 into the cut
        img = place(shots[out_j], prog(out_j, t), extra_zoom=1 + amt * 0.6 * k * k)
        img = radial_blur(img, amt * 0.5 * k)
        if kind == "burst":
            img = img + 70 * k * k
        return img
    k = 1 - (t - c) / h                      # 1 -> 0 out of the cut
    img = place(shots[in_j], prog(in_j, t), extra_zoom=1 + amt * 0.6 * k * k)
    img = radial_blur(img, amt * 0.5 * k)
    if kind == "burst":
        img = img + 70 * k * k
    return img

def main():
    plan = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    if "--stills" in sys.argv:
        os.makedirs(out, exist_ok=True)
        for ts in sys.argv[sys.argv.index("--stills") + 1].split(","):
            t = float(ts)
            Image.fromarray(grade(frame_at(plan, t), 0)).save(os.path.join(out, f"t{t:06.2f}.png"))
        return
    if "--storyboard" in sys.argv:
        shots, ends = plan["shots"], [s["t"] for s in plan["shots"][1:]] + [plan["end"]]
        tw, th, cols = 216, 384, 7
        rows = -(-len(shots) // cols)
        board = Image.new("RGB", (cols * tw, rows * (th + 92)), (18, 16, 14))
        d = ImageDraw.Draw(board)
        try:
            f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except OSError:
            f = ImageFont.load_default()
        for n, (sh, e) in enumerate(zip(shots, ends)):
            mid = (sh["t"] + e) / 2
            im = Image.fromarray(grade(frame_at(plan, mid), 0)).resize((tw, th))
            x, y = (n % cols) * tw, (n // cols) * (th + 92)
            board.paste(im, (x, y))
            d.text((x + 6, y + th + 4), f"{n+1}. {sh['t']:.2f}s  [{sh['tin']}]", fill=(240, 200, 120), font=f)
            words, line, ly = sh["say"].split(), "", y + th + 22
            for w_ in words:
                if len(line + w_) > 30:
                    d.text((x + 6, ly), line, fill=(230, 230, 230), font=f); ly += 15; line = ""
                line += w_ + " "
            d.text((x + 6, ly), line, fill=(230, 230, 230), font=f)
        board.save(out)
        return
    n = int(round(plan["end"] * FPS))
    audio = os.path.join(HERE, plan["audio"])
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-af", "apad", "-t", f"{plan['end']:.3f}",
           "-movflags", "+faststart", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(n):
        ff.stdin.write(grade(frame_at(plan, fi / FPS), fi).tobytes())
        if fi % 300 == 0:
            print(f"frame {fi}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done", out)

if __name__ == "__main__":
    main()
