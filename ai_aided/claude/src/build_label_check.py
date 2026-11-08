"""Data for vis/label_check.html: the 40 most confident mistakes on the validation set.

For each one: the full image (256 px) and a zoomed centre (160 px crop, upscaled),
its Galaxy10 label, and the model's probabilities. Used for a human check of
whether the label or the model is wrong.

Writes vis/label_check_data.js.
Usage:  python src/build_label_check.py
"""
import base64
import io
import json
import sys
from pathlib import Path

import h5py
import pandas as pd
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from ai_aided.claude.figures.src.model import ROOT, REPO, CLASS_NAMES, GALAXY10_NAMES  # noqa: E402

N_SHOW = 40


def jpg(im, size):
    buf = io.BytesIO()
    im.resize((size, size), Image.LANCZOS).save(buf, "JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()


def main():
    d = pd.read_csv(ROOT / "results" / "predictions.csv")
    v = d[(d.split == "val") & (d.pred != d.label5)].sort_values("confidence", ascending=False).head(N_SHOW)
    pcols = [f"p_{c}" for c in CLASS_NAMES]
    vf = ROOT / "results" / "volunteer_votes.csv"   # from volunteer_votes.py; only ~46% of galaxies have votes
    votes = pd.read_csv(vf).set_index("idx") if vf.exists() else pd.DataFrame()
    items = []
    with h5py.File(REPO / "data" / "Galaxy10_DECals.h5", "r") as f:
        for _, r in v.iterrows():
            im = Image.fromarray(f["images"][int(r.idx)])
            items.append({
                "idx": int(r.idx), "label10": GALAXY10_NAMES[int(r.label10)], "label5": CLASS_NAMES[int(r.label5)],
                "pred": CLASS_NAMES[int(r.pred)], "conf": round(float(r.confidence), 4),
                "probs": [round(float(r[c]), 4) for c in pcols],
                "full": jpg(im, 384), "zoom": jpg(im.crop((48, 48, 208, 208)), 384),
                "votes": None if int(r.idx) not in votes.index else {
                    "n": int(votes.at[int(r.idx), "votes"]),
                    "support": [round(float(votes.at[int(r.idx), c]), 3) for c in CLASS_NAMES],
                    "verdict": votes.at[int(r.idx), "verdict"]},
            })
    out = ROOT / "vis" / "label_check_data.js"
    out.write_text("window.LABEL_CHECK = " + json.dumps({"classes": CLASS_NAMES, "items": items}, separators=(",", ":")) + ";\n",
                   encoding="utf-8")
    print(out.name, f"{out.stat().st_size / 1e6:.1f} MB", len(items), "galaxies")


if __name__ == "__main__":
    main()
