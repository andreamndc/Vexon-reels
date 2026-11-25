#!/usr/bin/env python3
"""AI-upscale the small photos used in plan.json with Real-ESRGAN x4.

Usage: python3 upscale.py plan.json /path/to/RealESRGAN_x4plus.pth [min_enlargement]

Writes photos_upscaled/<name>.jpg for every photo in the plan that would be
enlarged by at least min_enlargement (default 2.0) to fill the 1080x1920 frame.
render.py uses the upscaled copy when one exists; the originals are untouched.
Weights: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
"""
import json, os, sys, time
import numpy as np, torch
from PIL import Image
from spandrel import ModelLoader

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920

def enlargement(w, h):
    return H / h if w > h else max(W / w, H / h)

def upscale(model, im, tile=256, pad=16):
    x = torch.from_numpy(np.asarray(im).astype(np.float32) / 255).permute(2, 0, 1)[None]
    _, _, h, w = x.shape
    out = torch.zeros(1, 3, h * 4, w * 4)
    with torch.inference_mode():
        for y0 in range(0, h, tile):
            for x0 in range(0, w, tile):
                ya, xa = max(0, y0 - pad), max(0, x0 - pad)
                yb, xb = min(h, y0 + tile + pad), min(w, x0 + tile + pad)
                r = model(x[:, :, ya:yb, xa:xb])
                ty, tx = (y0 - ya) * 4, (x0 - xa) * 4
                th, tw = min(tile, h - y0) * 4, min(tile, w - x0) * 4
                out[:, :, y0 * 4:y0 * 4 + th, x0 * 4:x0 * 4 + tw] = r[:, :, ty:ty + th, tx:tx + tw]
    arr = (out[0].permute(1, 2, 0).clamp(0, 1).numpy() * 255).round().astype(np.uint8)
    return Image.fromarray(arr)

def main():
    plan = json.load(open(sys.argv[1]))
    model = ModelLoader().load_from_file(sys.argv[2]).model.eval()
    lim = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    os.makedirs(os.path.join(HERE, "photos_upscaled"), exist_ok=True)
    for name in sorted({s["img"] for s in plan["shots"]}):
        dst = os.path.join(HERE, "photos_upscaled", name + ".jpg")
        im = Image.open(os.path.join(HERE, "photos", name + ".jpg")).convert("RGB")
        e = enlargement(*im.size)
        if e < lim or os.path.exists(dst):
            continue
        t = time.time()
        upscale(model, im).save(dst, quality=92)
        print(f"{name}: {im.size[0]}x{im.size[1]} -> x4 ({e:.1f}x needed) in {time.time()-t:.0f}s", flush=True)

if __name__ == "__main__":
    main()
