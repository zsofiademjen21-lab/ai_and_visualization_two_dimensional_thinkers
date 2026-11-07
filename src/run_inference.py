"""Run AstroVision on Galaxy10 DECals and cache everything later analyses need.

Reproduces the author's train/val split exactly (train.py: seed 42,
np.random.default_rng(42).permutation, first 20% = val), so we can analyse
both held-out (val) and seen (train) images.

Outputs (results/):
  predictions.csv  one row per image: idx, split, label10/5, pred, probs, logits, ra/dec/redshift
  features.npy     640-d pooled encoder embeddings (float16), row-aligned with predictions.csv

Usage:  python src/run_inference.py [--limit N] [--split val|train|all]
"""
import argparse
import sys
import time
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import torch
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from model import ROOT, CLASS_NAMES, GALAXY10_TO_5, TRANSFORM, load_model  # noqa: E402

DATA = ROOT / "data" / "Galaxy10_DECals.h5"
OUT = ROOT / "results"
VAL_SPLIT, SEED = 0.2, 42


def split_labels(n):
    idx = np.random.default_rng(SEED).permutation(n)
    split = np.full(n, "train", dtype=object)
    split[idx[: int(n * VAL_SPLIT)]] = "val"
    return split


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="all", choices=["all", "val", "train"])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--batch", type=int, default=64)
    args = ap.parse_args()

    torch.set_num_threads(max(1, torch.get_num_threads()))
    model = load_model()
    OUT.mkdir(exist_ok=True)

    with h5py.File(DATA, "r") as f:
        n = len(f["ans"])
        label10 = f["ans"][:].astype(int)
        meta = {k: f[k][:] for k in ("ra", "dec", "redshift", "pxscale") if k in f}
        split = split_labels(n)
        sel = np.arange(n) if args.split == "all" else np.where(split == args.split)[0]
        sel = np.sort(sel)
        if args.limit:
            sel = sel[: args.limit]

        logits_all, feats_all = [], []
        t0 = time.time()
        for b in range(0, len(sel), args.batch):
            ids = sel[b : b + args.batch]
            imgs = f["images"][ids]  # sel is sorted -> increasing indices, as h5py requires
            x =torch.stack([TRANSFORM(Image.fromarray(im)) for im in imgs])
            with torch.no_grad():
                lg, ft = model(x, return_features=True)
            logits_all.append(lg.numpy())
            feats_all.append(ft.numpy().astype(np.float16))
            done = b + len(ids)
            rate = done / (time.time() - t0)
            print(f"\r{done}/{len(sel)}  {rate:.1f} img/s  eta {(len(sel)-done)/rate/60:.1f} min",
                  end="", flush=True)
    print()

    logits = np.concatenate(logits_all)
    probs = torch.softmax(torch.from_numpy(logits), 1).numpy()
    l5 = np.array([GALAXY10_TO_5[l] for l in label10[sel]])
    df = pd.DataFrame({"idx": sel, "split": split[sel], "label10": label10[sel], "label5": l5,
                       "pred": probs.argmax(1), "confidence": probs.max(1)})
    for i, c in enumerate(CLASS_NAMES):
        df[f"p_{c}"] = probs[:, i]
    for i, c in enumerate(CLASS_NAMES):
        df[f"logit_{c}"] = logits[:, i]
    for k, v in meta.items():
        df[k] = v[sel]
    df.to_csv(OUT / "predictions.csv", index=False)
    np.save(OUT / "features.npy", np.concatenate(feats_all))

    for s, g in df.groupby("split"):
        print(f"{s}: n={len(g)}  accuracy={(g.pred == g.label5).mean():.4f}")


if __name__ == "__main__":
    main()
