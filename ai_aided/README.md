# AI-aided pair: Vis4AI on AstroVision-Advanced

Model under study: [zev-walker/astrovision-advanced](https://huggingface.co/zev-walker/astrovision-advanced).
It is Zoobot (ConvNeXt-Nano), fine-tuned on Galaxy10 DECals, and classifies galaxy images into 5 classes:
Spiral, Elliptical, Edge-on Disk, Irregular, Merger.

This folder holds the AI-aided pair's Phase I work. The AI-use log is in [`../ai-interactions/ai-use-log.md`](../ai-interactions/ai-use-log.md).

**To see the results:** open [`vis/findings.html`](vis/findings.html) (key takeaways) or [`vis/explorer.html`](vis/explorer.html) (interactive explorer) in a browser. The written Phase I section is [`report_phase1.md`](report_phase1.md), with its charts in `figures/`. [`vis/label_check.html`](vis/label_check.html) is a tool for checking the labels of the 40 most confident mistakes by hand.

## Setup

```bash
pip install torch torchvision timm h5py pandas scikit-learn pillow huggingface_hub
```

The `zoobot` package is **not** needed. `src/model.py` rebuilds the network with plain `timm` and loads the checkpoint with `weights_only=True`.

The dataset and the checkpoint are shared with the whole group, so they live at the **repository root**, not in this folder. Both are gitignored.
- Download the data (2.7 GB) into `data/` at the repo root:
  ```bash
  curl -L -o data/Galaxy10_DECals.h5 https://zenodo.org/records/10845026/files/Galaxy10_DECals.h5
  ```
- The checkpoint (180 MB) downloads automatically into `models/` at the repo root the first time you run the code.

## Pipeline

Run these from this folder (`ai_aided/`):

| Step | Command | Output |
|---|---|---|
| 1. Inference on all 17,736 images (about 40 min on CPU) | `python src/run_inference.py` | `results/predictions.csv` |
| 2. Measure input-image properties (a few min) | `python src/input_properties.py` | `results/input_props.csv` |
| 3. Build the explorer data | `python src/build_explorer.py` | `vis/explorer_data.js`, `vis/thumbs.js` |
| 4. Image-editing tests (about 10 + 15 min) | `python src/perturbation_test.py`, `python src/perturbation_test2.py` | `results/perturbations.csv`, `results/perturbations2.csv` |
| 5. Build the findings data | `python src/build_findings_data.py`, `python src/build_map_data.py` | `vis/perturbation_data.js`, `vis/map_data.js` |

`predictions.csv` has one row per image with these columns:
- `idx`: row in the h5 file
- `split`: train/val
- `label10`, `label5`: true labels
- `pred`, `confidence`: predicted class and its probability
- `p_*`, `logit_*`: per-class probabilities and logits
- `ra`, `dec`, `redshift`, `pxscale`: image metadata

## Things to know about the model and data

- **Train/val split.** We reproduce it exactly from the author's `train.py`: `np.random.default_rng(42).permutation`, first 20% = val (3,547 images). There is **no separate test set**.
- **Preprocessing** is Resize(224×224) plus ImageNet mean/std, the same as the author's `app.py`.
- **The h5 file is sorted by class.** Never take the first N images as a "random" sample.
- **Possible pretraining overlap.** The Zoobot encoder was pretrained on Galaxy Zoo DECaLS, the same survey these images come from.
- **Class imbalance and no class weights.** The card states Irregular has 1,081 images vs 6,500 Spiral, and the model was trained without class weights.

## Folder layout

```
src/model.py               model loader, class names, label mapping, preprocessing
src/run_inference.py       model outputs (predictions, probabilities) for every image
src/input_properties.py    size, roundness, colour, ... measured on each input image
src/build_explorer.py      data for the interactive explorer
src/perturbation_test.py   image-editing test 1: recolour / shrink / rotate
src/perturbation_test2.py  image-editing test 2: blur / squash / shift / surroundings / neighbour
src/build_findings_data.py data for the findings page (image-editing tests)
src/build_map_data.py      regions on the output map (clusters, crowdedness) for the findings page
src/build_label_check.py   data for the label-check tool (40 most confident mistakes)
src/volunteer_votes.py     Galaxy Zoo volunteer votes matched to our galaxies (needs data/gz_decals/, see the script)
results/                   model outputs and test results (CSV)
vis/findings.html          Phase I key takeaways
vis/explorer.html          Phase I interactive explorer (linked views)
vis/label_check.html       hand check of the 40 most confident mistakes
figures/                   one picture per takeaway, for the report
report_phase1.md           Phase I report section
```
