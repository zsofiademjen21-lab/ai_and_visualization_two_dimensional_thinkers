"""Build the data files for vis/explorer.html from results/ (run after run_inference.py).

Writes:
  vis/explorer_data.js   predictions (compact), t-SNE of val output probabilities,
                         input properties (needs results/input_props.csv), class names
  vis/thumbs.js          64px JPEG thumbnails (base64) of every validation image

Usage:  python src/build_explorer.py
"""
import base64
import io
import json
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.manifold import TSNE

sys.path.insert(0, str(Path(__file__).parent))
from ai_aided.claude.figures.src.model import ROOT, REPO, CLASS_NAMES, GALAXY10_NAMES, GALAXY10_TO_5  # noqa: E402

RES, VIS = ROOT / "results", ROOT / "vis"
THUMB = 64
PROPS = [  # key in input_props.csv, display name, description
    ("redshift", "Redshift", "distance proxy from the catalogue (higher = farther, smaller, fainter)"),
    ("r50", "Apparent size", "half-light radius in pixels"),
    ("central", "Core brightness", "mean pixel value in the central 8 px"),
    ("axis_ratio", "Axis ratio b/a", "1 = round, lower = more elongated"),
    ("colour", "Colour", "log red/blue flux ratio, higher = redder"),
    ("outer_frac", "Outer light share", "share of light beyond 64 px, i.e. neighbours, companions, extended light"),
]


def main():
    VIS.mkdir(exist_ok=True)
    df = pd.read_csv(RES / "predictions.csv")
    pcols = [f"p_{c}" for c in CLASS_NAMES]

    # --- Phase I is black-box: map built from model OUTPUTS only ---
    # t-SNE of the 5-d log-probability vectors (validation images). Galaxies are
    # close when the model responds to them similarly. No internal features used.
    val = df.split.eq("val").to_numpy()
    logp = np.log(np.clip(df.loc[val, pcols].to_numpy(), 1e-6, 1))
    xy = TSNE(2, init="pca", perplexity=30, random_state=0).fit_transform(logp)
    xy = (xy - xy.min(0)) / (xy.max(0) - xy.min(0))
    emb = np.full((len(df), 2), np.nan)
    emb[val] = xy

    probs = df[pcols].to_numpy().round(4)
    # input properties (src/input_properties.py), aligned by image index
    ip = pd.read_csv(RES / "input_props.csv").set_index("idx").loc[df.idx]
    pvals = ip[[k for k, *_ in PROPS]].to_numpy()
    rows = []
    for i, r in enumerate(df.itertuples(index=False)):
        rows.append([
            int(r.idx), 0 if r.split == "val" else 1, int(r.label10), int(r.label5), int(r.pred),
            probs[i].tolist(),
            None if np.isnan(emb[i, 0]) else emb[i].round(4).tolist(),
            [None if np.isnan(v) else round(float(v), 4) for v in pvals[i]],
        ])
    data = {
        "classes": CLASS_NAMES, "classes10": GALAXY10_NAMES,
        "map10to5": [GALAXY10_TO_5[i] for i in range(10)],
        "props": [{"key": k, "name": n, "desc": d} for k, n, d in PROPS],
        "fields": ["idx", "split", "label10", "label5", "pred", "probs", "xy", "props"],
        "rows": rows,
    }
    (VIS / "explorer_data.js").write_text(
        "window.EXPLORER_DATA = " + json.dumps(data, separators=(",", ":")) + ";\n", encoding="utf-8")

    # --- thumbnails for validation images ---
    thumbs = {}
    with h5py.File(REPO / "data" / "Galaxy10_DECals.h5", "r") as f:
        ids = np.sort(df.loc[val, "idx"].to_numpy())
        for b in range(0, len(ids), 256):
            chunk = ids[b:b + 256]
            for i, im in zip(chunk, f["images"][chunk]):
                # centre crop 160px (galaxy is centred), then downsample
                c = Image.fromarray(im).crop((48, 48, 208, 208)).resize((THUMB, THUMB), Image.LANCZOS)
                buf = io.BytesIO()
                c.save(buf, "JPEG", quality=72)
                thumbs[int(i)] = base64.b64encode(buf.getvalue()).decode()
    (VIS / "thumbs.js").write_text(
        "window.EXPLORER_THUMBS = " + json.dumps(thumbs, separators=(",", ":")) + ";\n", encoding="utf-8")

    for p in ("explorer_data.js", "thumbs.js"):
        print(p, f"{(VIS / p).stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
