"""Cluster analysis of the output map (black-box) for vis/findings.html.

The output map is a t-SNE of the model's output probabilities (validation images,
computed in build_explorer.py). Here we
  - find regions on the map with HDBSCAN (leaf selection, min 30 galaxies),
  - measure how crowded each point's neighbourhood is (mean distance to 10 nearest points),
  - mark the regions we discuss on the findings page.

Writes vis/map_data.js:
  points   [idx, region] for every validation galaxy on the map (-1 = no region)
  regions  [{id, x, y, r, n, err}] centre, size and error rate of every region
  notes    regions highlighted on the page, with a short label
  density  error rate in the sparsest and densest fifth of the map

Usage:  python src/build_map_data.py   (after build_explorer.py and input_properties.py)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.neighbors import NearestNeighbors

sys.path.insert(0, str(Path(__file__).parent))
from ai_aided.claude.figures.src.model import ROOT, CLASS_NAMES  # noqa: E402


def main():
    raw = (ROOT / "vis" / "explorer_data.js").read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";")
    rows = [r for r in json.loads(raw)["rows"] if r[6] is not None]
    df = pd.DataFrame({"idx": [r[0] for r in rows], "x": [r[6][0] for r in rows], "y": [r[6][1] for r in rows]})
    df = df.merge(pd.read_csv(ROOT / "results" / "predictions.csv"), on="idx")
    df = df.merge(pd.read_csv(ROOT / "results" / "input_props.csv").drop(columns="redshift"), on="idx")
    df["wrong"] = df.pred != df.label5

    df["region"] = HDBSCAN(min_cluster_size=30, min_samples=8, cluster_selection_method="leaf",
                           copy=True).fit_predict(df[["x", "y"]])
    d, _ = NearestNeighbors(n_neighbors=11).fit(df[["x", "y"]]).kneighbors(df[["x", "y"]])
    df["crowd"] = pd.qcut(-d[:, 1:].mean(1), 5, labels=False)  # 0 = sparsest fifth, 4 = densest

    regions = []
    for rid, t in df[df.region >= 0].groupby("region"):
        regions.append({"id": int(rid), "x": round(t.x.mean(), 4), "y": round(t.y.mean(), 4),
                        "r": round(float(np.hypot(t.x.std(), t.y.std())), 4), "n": len(t), "err": round(t.wrong.mean(), 3)})

    # describe each error-heavy region by the two classes the model hesitates between
    P = df[[f"p_{c}" for c in CLASS_NAMES]].to_numpy()
    notes = []
    for reg in regions:
        if reg["err"] < 0.25:
            continue
        t = df[df.region == reg["id"]]
        mp = P[t.index].mean(0)
        a, b = np.argsort(-mp)[:2]
        true_mix = t.label5.value_counts(normalize=True)
        if mp[b] > 0.15:   # probability shared between two classes: a bridge
            label = f"{CLASS_NAMES[a]} ↔ {CLASS_NAMES[b]}"
            kind = "bridge"
        else:              # model is sure, but many true labels disagree
            other = [c for c in true_mix.index if c != a][0]
            label = f"{true_mix[other]:.0%} {CLASS_NAMES[other]} hidden among {CLASS_NAMES[a]}"
            kind = "hidden"
        notes.append({"id": reg["id"], "label": label, "kind": kind, "conf": round(t.confidence.mean(), 2)})

    dens = df.groupby("crowd").wrong.mean()
    data = {"points": [[int(i), int(r)] for i, r in zip(df.idx, df.region)], "regions": regions, "notes": notes,
            "density": {"sparsest": round(dens.loc[0], 3), "densest": round(dens.loc[4], 3)}}
    out = ROOT / "vis" / "map_data.js"
    out.write_text("window.MAP_DATA = " + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n", encoding="utf-8")
    print(out.name, f"{out.stat().st_size / 1e3:.0f} kB", len(regions), "regions")
    for n in notes:
        r = next(x for x in regions if x["id"] == n["id"])
        print(f"  {n['kind']:6s} {n['label']:45s} n={r['n']:3d} err={r['err']:.0%} conf={n['conf']:.0%}")


if __name__ == "__main__":
    main()
