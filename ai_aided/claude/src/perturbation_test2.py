"""Second synthetic black-box test: context, shape, detail and position.

Edits (each changes ONE thing):
  original       unchanged
  blur           Gaussian blur (radius 3 px): same size, less detail
  squash         height halved: round galaxies become elongated, nothing else changes
  shift          galaxy moved 40 px right and 40 px down (off-centre)
  no_context     everything outside 40 px from the centre replaced by sky: removes neighbours
  add_neighbour  a small elliptical from another image added 60 px to the right

Empty areas are filled with real sky pixels sampled from the image's own border.
Test sets (validation, fixed seed): all true Merger, 250 Elliptical, 250 Spiral
(same random draw as perturbation_test.py), all true Irregular.

Output: results/perturbations2.csv
Usage:  python src/perturbation_test2.py
"""
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
from model import ROOT, REPO, CLASS_NAMES, TRANSFORM, load_model  # noqa: E402

N = 256
YY, XX = np.mgrid[:N, :N]
RR = np.hypot(YY - 127.5, XX - 127.5)
KINDS = ["original", "blur", "squash", "shift", "no_context", "add_neighbour"]


def border_px(x):
    return np.concatenate([x[:10].reshape(-1, 3), x[-10:].reshape(-1, 3), x[:, :10].reshape(-1, 3), x[:, -10:].reshape(-1, 3)])


def sky_canvas(x, seed):
    b = border_px(x)
    return b[np.random.default_rng(seed).integers(0, len(b), N * N)].reshape(N, N, 3).astype(np.float32)


PY, PX = np.mgrid[:64, :64]
SOFT = np.exp(-((PY - 31.5) ** 2 + (PX - 31.5) ** 2) / (2 * 10 ** 2))[..., None]   # round, fading mask


def perturb(im, kind, neighbour=None, seed=0, r50=20.0):
    x = im.astype(np.float32)
    if kind == "original":
        return im
    if kind == "blur":
        return np.asarray(Image.fromarray(im).filter(ImageFilter.GaussianBlur(3)))
    if kind == "squash":
        c = sky_canvas(x, seed)
        h = np.asarray(Image.fromarray(im).resize((N, N // 2), Image.LANCZOS), np.float32)
        c[N // 4: 3 * N // 4] = h
        return c.clip(0, 255).astype(np.uint8)
    if kind == "shift":
        c = sky_canvas(x, seed)
        c[40:, 40:] = x[:-40, :-40]
        return c.clip(0, 255).astype(np.uint8)
    if kind == "no_context":
        # keep the galaxy itself (radius ~2.5x its half-light radius, soft 16 px edge), sky elsewhere
        r0 = float(np.clip(2.5 * r50, 30, 90))
        w = np.clip((r0 + 8 - RR) / 16, 0, 1)[..., None]
        return (w * x + (1 - w) * sky_canvas(x, seed)).clip(0, 255).astype(np.uint8)
    if kind == "add_neighbour":
        n = neighbour.astype(np.float32)
        patch = (n[96:160, 96:160] - np.median(border_px(n), 0)).clip(0, None) * SOFT  # galaxy light only, soft edge
        patch = np.asarray(Image.fromarray(patch.clip(0, 255).astype(np.uint8)).resize((40, 40), Image.LANCZOS), np.float32)
        out = x.copy()
        out[108:148, 168:208] += patch                                # 60 px right of centre
        return out.clip(0, 255).astype(np.uint8)
    raise ValueError(kind)


def main():
    df = pd.read_csv(ROOT / "results" / "predictions.csv")
    v = df[df.split == "val"]
    rng = np.random.default_rng(0)
    irr = v[v.label5 == 3].idx.to_numpy()
    ell = rng.choice(v[v.label5 == 1].idx.to_numpy(), 250, replace=False)
    spi = rng.choice(v[v.label5 == 0].idx.to_numpy(), 250, replace=False)
    mer = v[v.label5 == 4].idx.to_numpy()
    sel = np.sort(np.concatenate([irr, ell, spi, mer]))
    # neighbours: small round ellipticals the model is sure about (not in the test set)
    pool = v[(v.label10 == 2) & (v.pred == 1) & (v.confidence > 0.95) & ~v.idx.isin(sel)].idx.to_numpy()
    meta = df.set_index("idx").loc[sel, ["label5", "label10"]]
    r50 = pd.read_csv(ROOT / "results" / "input_props.csv").set_index("idx").r50
    model = load_model()
    rows = []
    with h5py.File(REPO / "data" / "Galaxy10_DECals.h5", "r") as f:
        nb = f["images"][np.sort(pool[:64])]
        for b in range(0, len(sel), 32):
            ids = sel[b:b + 32]
            imgs = f["images"][ids]
            for kind in KINDS:
                x = torch.stack([TRANSFORM(Image.fromarray(perturb(im, kind, nb[int(i) % len(nb)], int(i), r50.at[int(i)])))
                                 for i, im in zip(ids, imgs)])
                with torch.no_grad():
                    p = torch.softmax(model(x), 1).numpy()
                rows += [[int(i), kind, int(pi.argmax()), *pi.round(4)] for i, pi in zip(ids, p)]
            print(f"\r{min(b + 32, len(sel))}/{len(sel)}", end="", flush=True)
    print()
    out = pd.DataFrame(rows, columns=["idx", "perturbation", "pred", *[f"p_{c}" for c in CLASS_NAMES]])
    out = out.merge(meta, left_on="idx", right_index=True)
    out.to_csv(ROOT / "results" / "perturbations2.csv", index=False)
    out["pred_name"] = out.pred.map(dict(enumerate(CLASS_NAMES)))
    for c in [4, 1, 0, 3]:
        g = out[out.label5 == c]
        print(f"\n== true {CLASS_NAMES[c]} (n={g.idx.nunique()})")
        print(pd.crosstab(g.perturbation, g.pred_name, normalize="index").reindex(KINDS).round(3))


if __name__ == "__main__":
    main()
