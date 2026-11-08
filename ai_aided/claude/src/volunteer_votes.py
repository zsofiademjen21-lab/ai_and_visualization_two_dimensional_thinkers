"""Match Galaxy10 galaxies to the Galaxy Zoo DECaLS volunteer votes (Walmsley et al. 2022).

Galaxy10 labels were made from Galaxy Zoo volunteer votes. The public catalogues
(zenodo.org/records/4573248) give, for each galaxy, how many volunteers chose each
answer, so we can see how strongly the volunteers supported a label.

Download into <repo>/data/gz_decals/ (gitignored):
  gz_decals_volunteers_5.csv, gz_decals_volunteers_1_and_2.csv
Only about 46% of Galaxy10 galaxies are in these public catalogues.

"Support" for a class = share of volunteers whose answers point to it. It follows the
Galaxy Zoo decision tree and is an approximation:
  Elliptical  = smooth
  Edge-on     = featured x edge-on
  Spiral      = featured x not edge-on x has spiral arms
  Irregular   = merging question: minor + major disturbance (DR5) / tidal debris (DR1+2)
  Merger      = merging question: merger (DR5) / merger + both (DR1+2)
The merging question is asked about every galaxy, so a galaxy can support both
"Spiral" and "Irregular" at once (a disturbed spiral).

Verdict for a mistake (label support L, support for the model's answer M):
  both fit           L >= 0.5 and M >= 0.5
  votes back label   L >= M + 0.15
  votes back model   M >= L + 0.15
  volunteers split   otherwise

Output: results/volunteer_votes.csv (one row per matched galaxy)
Usage:  python src/volunteer_votes.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

sys.path.insert(0, str(Path(__file__).parent))
from model import ROOT, REPO, CLASS_NAMES  # noqa: E402

CATS = [("dr5", "gz_decals_volunteers_5.csv", True), ("dr12", "gz_decals_volunteers_1_and_2.csv", False)]
MAX_SEP_ARCSEC = 1.0


def frac(r, q, answers):
    tot = r[f"{q}_total-votes"].replace(0, np.nan)
    return (r[[f"{q}_{a}" for a in answers]].sum(axis=1) / tot).fillna(0)


def support(r, dr5):
    smooth = frac(r, "smooth-or-featured", ["smooth"])
    feat = frac(r, "smooth-or-featured", ["featured-or-disk"])
    edge = frac(r, "disk-edge-on", ["yes"])
    arms = frac(r, "has-spiral-arms", ["yes"])
    if dr5:
        dist = frac(r, "merging", ["minor-disturbance", "major-disturbance"])
        merg = frac(r, "merging", ["merger"])
    else:
        dist = frac(r, "merging", ["tidal-debris"])
        merg = frac(r, "merging", ["merger", "both"])
    return pd.DataFrame({"Spiral": feat * (1 - edge) * arms, "Elliptical": smooth, "Edge-on Disk": feat * edge,
                         "Irregular": dist, "Merger": merg, "votes": r["smooth-or-featured_total-votes"]})


def verdict(L, M):
    if L >= 0.5 and M >= 0.5:
        return "both fit"
    if L >= M + 0.15:
        return "votes back label"
    if M >= L + 0.15:
        return "votes back model"
    return "volunteers split"


def main():
    p = pd.read_csv(ROOT / "results" / "predictions.csv")
    xyz = np.radians(p[["dec", "ra"]].to_numpy())
    parts = []
    for name, fname, dr5 in CATS:
        c = pd.read_csv(REPO / "data" / "gz_decals" / fname)
        d, i = BallTree(np.radians(c[["dec", "ra"]].to_numpy()), metric="haversine").query(xyz, k=1)
        ok = np.degrees(d[:, 0]) * 3600 < MAX_SEP_ARCSEC
        s = support(c.iloc[i[ok, 0]].reset_index(drop=True), dr5)
        s.insert(0, "catalogue", name)
        s.insert(0, "idx", p.idx.to_numpy()[ok])
        parts.append(s)
    v = pd.concat(parts).drop_duplicates("idx")          # DR5 first, so it wins when a galaxy is in both
    v = p[["idx", "split", "label10", "label5", "pred", "confidence"]].merge(v, on="idx")
    v["label_support"] = [r[CLASS_NAMES[r.label5]] for _, r in v.iterrows()]
    v["model_support"] = [r[CLASS_NAMES[r.pred]] for _, r in v.iterrows()]
    v["verdict"] = [verdict(L, M) if a != b else "" for L, M, a, b in zip(v.label_support, v.model_support, v.label5, v.pred)]
    v.round(4).to_csv(ROOT / "results" / "volunteer_votes.csv", index=False)

    w = v[v.pred != v.label5]
    print(f"matched {len(v)} of {len(p)} galaxies ({len(v) / len(p):.0%}); mistakes with votes: {len(w)}")
    print(w.verdict.value_counts(normalize=True).round(2).to_dict())
    print("disturbed mistakes:", w[w.label10 == 0].verdict.value_counts().to_dict())


if __name__ == "__main__":
    main()
