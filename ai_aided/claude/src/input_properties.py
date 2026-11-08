"""Measure simple, model-independent properties of every input image (Phase I).

These describe the INPUT only (no model internals), so we can ask black-box
questions like "does the model fail more on small / distant / round galaxies?".

Output: results/input_props.csv with columns
  idx, redshift, r50, central, axis_ratio, colour, outer_frac

  r50         half-light radius in pixels (within r<64 px), apparent size
  central     mean brightness in the central r<8 px (0..1), core brightness
  axis_ratio  b/a from flux-weighted second moments (1 = round, ->0 = elongated)
  colour      log(R/B) of background-subtracted flux in r<32 px (higher = redder)
  outer_frac  share of flux beyond r>=64 px, i.e. neighbours, companions, extended light

Usage:  python src/input_properties.py
"""
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from model import ROOT, REPO  # noqa: E402

N = 256
YY, XX = np.mgrid[:N, :N].astype(np.float32)
RR = np.hypot(YY - (N - 1) / 2, XX - (N - 1) / 2)
INNER, CORE, MID, OUTER = RR < 64, RR < 8, RR < 32, RR >= 64
ORDER = np.argsort(RR[INNER])
R_SORTED = RR[INNER][ORDER]
BORDER = np.zeros((N, N), bool)
BORDER[:10], BORDER[-10:], BORDER[:, :10], BORDER[:, -10:] = True, True, True, True


def props(imgs):
    x = imgs.astype(np.float32) / 255.0                     # (B,N,N,3)
    sky = x[:, BORDER]                                      # (B,P,3) border pixels
    bg = np.median(sky, axis=1)                             # (B,3) per-channel sky level
    sig = 1.4826 * np.median(np.abs(sky - bg[:, None]), axis=1) + 1e-4  # robust noise
    # keep only pixels clearly above the sky (2 sigma); plain clipping at 0 lets the
    # positive half of the noise dominate any large-area sum
    fc = x - bg[:, None, None, :]
    fc = np.where(fc > 2 * sig[:, None, None, :], fc, 0)
    f = fc.mean(-1)                                         # (B,N,N) grey flux
    tot_in = f[:, INNER].sum(1) + 1e-6

    cum = np.cumsum(f[:, INNER][:, ORDER], 1) / tot_in[:, None]
    r50 = R_SORTED[np.argmax(cum >= 0.5, 1)]

    central = x[:, CORE].mean((1, 2))

    w = f * INNER
    xc = (w * XX).sum((1, 2)) / tot_in
    yc = (w * YY).sum((1, 2)) / tot_in
    dx, dy = XX[None] - xc[:, None, None], YY[None] - yc[:, None, None]
    mxx = (w * dx * dx).sum((1, 2)) / tot_in
    myy = (w * dy * dy).sum((1, 2)) / tot_in
    mxy = (w * dx * dy).sum((1, 2)) / tot_in
    half_tr, d = (mxx + myy) / 2, np.sqrt(((mxx - myy) / 2) ** 2 + mxy ** 2)
    axis_ratio = np.sqrt(np.clip(half_tr - d, 1e-9, None) / (half_tr + d + 1e-9))

    rgb = fc[:, MID].sum(1)                                 # (B,3)
    colour = np.log((rgb[:, 0] + 1e-3) / (rgb[:, 2] + 1e-3))

    outer_frac = f[:, OUTER].sum(1) / (f.sum((1, 2)) + 1e-6)
    return r50, central, axis_ratio, colour, outer_frac


def main():
    out = []
    with h5py.File(REPO / "data" / "Galaxy10_DECals.h5", "r") as h:
        n = len(h["ans"])
        z = h["redshift"][:]
        for b in range(0, n, 128):
            vals = props(h["images"][b:b + 128])
            out.append(np.stack(vals, 1))
            print(f"\r{min(b + 128, n)}/{n}", end="", flush=True)
    print()
    a = np.concatenate(out)
    df = pd.DataFrame(a, columns=["r50", "central", "axis_ratio", "colour", "outer_frac"])
    df.insert(0, "redshift", z)
    df.insert(0, "idx", np.arange(n))
    df.to_csv(ROOT / "results" / "input_props.csv", index=False)
    print(df.describe().T[["mean", "min", "50%", "max"]])


if __name__ == "__main__":
    main()
