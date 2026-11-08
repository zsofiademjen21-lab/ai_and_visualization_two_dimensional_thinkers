"""Synthetic black-box test: change ONE input property and watch the prediction.

Correlations in the real data cannot separate colour, size and distance (they
are entangled). Here we edit the images directly:

  original   unchanged
  gray       colour removed (all channels = luminance), shape unchanged
  redder     R x1.25, B x0.75 (shape unchanged)
  bluer      R x0.75, B x1.25 (shape unchanged)
  shrink     galaxy downscaled to half size, pasted on its own sky level (colour unchanged)
  rot90      rotated 90 degrees: control, the model was trained with rotations

Test sets (validation split only, fixed seed): all true Irregular, 250 random
true Elliptical, 250 random true Spiral.

Output: results/perturbations.csv (idx, label5, label10, perturbation, pred, probs)
Usage:  python src/perturbation_test.py
"""
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import torch
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from ai_aided.claude.figures.src.model import ROOT, REPO, CLASS_NAMES, TRANSFORM, load_model  # noqa: E402

N = 256


def sky(im):
    b = np.concatenate([im[:10].reshape(-1, 3), im[-10:].reshape(-1, 3), im[:, :10].reshape(-1, 3), im[:, -10:].reshape(-1, 3)])
    return np.median(b, 0)


def perturb(im, kind):
    x = im.astype(np.float32)
    if kind == "original":
        return im
    if kind == "gray":
        g = x @ np.array([0.299, 0.587, 0.114], np.float32)
        return np.repeat(g[..., None], 3, -1).clip(0, 255).astype(np.uint8)
    if kind in ("redder", "bluer"):
        s = sky(x)
        f = np.array([1.25, 1.0, 0.75] if kind == "redder" else [0.75, 1.0, 1.25], np.float32)
        return (s + (x - s) * f).clip(0, 255).astype(np.uint8)  # scale galaxy light, keep sky level
    if kind == "shrink":
        # fill with real sky pixels sampled from the image border (keeps the noise texture;
        # a flat fill would be an artificial cue the model could react to)
        border = np.concatenate([x[:10].reshape(-1, 3), x[-10:].reshape(-1, 3), x[:, :10].reshape(-1, 3), x[:, -10:].reshape(-1, 3)])
        rs = np.random.default_rng(int(x.sum()) % 2**32)
        canvas = border[rs.integers(0, len(border), N * N)].reshape(N, N, 3).copy()
        small = np.asarray(Image.fromarray(im).resize((N // 2, N // 2), Image.LANCZOS), np.float32)
        canvas[N // 4: 3 * N // 4, N // 4: 3 * N // 4] = small
        return canvas.clip(0, 255).astype(np.uint8)
    if kind == "rot90":
        return np.rot90(im).copy()
    raise ValueError(kind)


KINDS = ["original", "gray", "redder", "bluer", "shrink", "rot90"]


def main():
    df = pd.read_csv(ROOT / "results" / "predictions.csv")
    v = df[df.split == "val"]
    rng = np.random.default_rng(0)
    sel = np.concatenate([
        v[v.label5 == 3].idx.to_numpy(),
        rng.choice(v[v.label5 == 1].idx.to_numpy(), 250, replace=False),
        rng.choice(v[v.label5 == 0].idx.to_numpy(), 250, replace=False),
    ])
    sel = np.sort(sel)
    meta = df.set_index("idx").loc[sel, ["label5", "label10"]]
    model = load_model()
    rows = []
    with h5py.File(REPO / "data" / "Galaxy10_DECals.h5", "r") as f:
        for b in range(0, len(sel), 32):
            ids = sel[b:b + 32]
            imgs = f["images"][ids]
            for kind in KINDS:
                x = torch.stack([TRANSFORM(Image.fromarray(perturb(im, kind))) for im in imgs])
                with torch.no_grad():
                    p = torch.softmax(model(x), 1).numpy()
                for i, pi in zip(ids, p):
                    rows.append([int(i), kind, int(pi.argmax()), *pi.round(4)])
            print(f"\r{min(b + 32, len(sel))}/{len(sel)}", end="", flush=True)
    print()
    out = pd.DataFrame(rows, columns=["idx", "perturbation", "pred", *[f"p_{c}" for c in CLASS_NAMES]])
    out = out.merge(meta, left_on="idx", right_index=True)
    out.to_csv(ROOT / "results" / "perturbations.csv", index=False)
    # quick summary: prediction shares per true class and perturbation
    out["pred_name"] = out.pred.map(dict(enumerate(CLASS_NAMES)))
    for c in [3, 1, 0]:
        g = out[out.label5 == c]
        print(f"\n== true {CLASS_NAMES[c]} (n={g.idx.nunique()})")
        print(pd.crosstab(g.perturbation, g.pred_name, normalize="index").reindex(KINDS).round(3))


if __name__ == "__main__":
    main()
