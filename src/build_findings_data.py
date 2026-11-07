"""Export the perturbation test (results/perturbations.csv) for vis/findings.html.

Writes vis/perturbation_data.js:
  rows      [idx, kind_index, pred] for every tested image and edit
  kinds     names of the edits
  examples  before/after image pairs (base64 JPEG) for the page

Usage:  python src/build_findings_data.py   (after src/perturbation_test.py)
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

sys.path.insert(0, str(Path(__file__).parent))
from model import ROOT, CLASS_NAMES  # noqa: E402
from perturbation_test import KINDS, perturb  # noqa: E402


def b64(im):
    c = Image.fromarray(im).crop((48, 48, 208, 208)).resize((112, 112), Image.LANCZOS)
    buf = io.BytesIO()
    c.save(buf, "JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode()


def main():
    p = pd.read_csv(ROOT / "results" / "perturbations.csv")
    props = pd.read_csv(ROOT / "results" / "input_props.csv").set_index("idx")
    w = p.pivot(index="idx", columns="perturbation", values="pred")
    lab = p.drop_duplicates("idx").set_index("idx")[["label5", "label10"]]
    w = w.join(lab).join(props[["r50", "colour"]])
    p_ell = p[p.perturbation == "shrink"].set_index("idx")["p_Elliptical"]

    picks = []
    # shrink: true spirals that flip Spiral -> Elliptical
    s = w[(w.label5 == 0) & (w.original == 0) & (w.shrink == 1)]
    for i in p_ell.loc[s.index].sort_values(ascending=False).index[:3]:
        picks.append(("shrink", int(i), "shrink"))
    # colour: red irregulars still called Elliptical after making them bluer
    irr = w[w.label5 == 3]
    red = irr[irr.colour > irr.colour.median()]
    for i in red[(red.original == 1) & (red.bluer == 1)].sort_values("colour", ascending=False).index[:3]:
        picks.append(("colour", int(i), "bluer"))
    # rotation: irregulars recognised correctly, wrong after a 90 degree turn
    for i in irr[(irr.original == 3) & (irr.rot90 != 3)].index[:3]:
        picks.append(("rotate", int(i), "rot90"))

    ex = []
    with h5py.File(ROOT / "data" / "Galaxy10_DECals.h5", "r") as f:
        for group, i, kind in picks:
            im = f["images"][i]
            ex.append({"group": group, "idx": i, "kind": kind,
                       "before": b64(im), "after": b64(perturb(im, kind)),
                       "pred_before": int(w.at[i, "original"]), "pred_after": int(w.at[i, kind])})

    kidx = {k: j for j, k in enumerate(KINDS)}
    data = {"kinds": KINDS, "classes": CLASS_NAMES,
            "rows": [[int(r.idx), kidx[r.perturbation], int(r.pred)] for r in p.itertuples()],
            "examples": ex}
    out = ROOT / "vis" / "perturbation_data.js"
    out.write_text("window.PERTURB_DATA = " + json.dumps(data, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(out.name, f"{out.stat().st_size / 1e3:.0f} kB", {g: sum(e['group'] == g for e in ex) for g in ['shrink', 'colour', 'rotate']})


if __name__ == "__main__":
    main()
