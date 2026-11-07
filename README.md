# Two Dimensional Thinkers: Vis4AI on AstroVision-Advanced

Model under study: [zev-walker/astrovision-advanced](https://huggingface.co/zev-walker/astrovision-advanced).
It is Zoobot (ConvNeXt-Nano), fine-tuned on Galaxy10 DECals, and classifies galaxy images into 5 classes:
Spiral, Elliptical, Edge-on Disk, Irregular, Merger.

## Setup

```bash
pip install torch torchvision timm h5py pandas scikit-learn pillow huggingface_hub
```

The `zoobot` package is **not** needed. `src/model.py` rebuilds the network with plain `timm` and loads the checkpoint with `weights_only=True`.

Download the data (2.7 GB, gitignored) into `data/`:

```bash
curl -L -o data/Galaxy10_DECals.h5 https://zenodo.org/records/10845026/files/Galaxy10_DECals.h5
```

The checkpoint (180 MB) is downloaded automatically into `models/` the first time you run the code.

## Pipeline

| Step | Command | Output |
|---|---|---|
| 1. Inference on all 17,736 images (about 40 min on CPU) | `python src/run_inference.py` | `results/predictions.csv`, `results/features.npy` |
| 2. Measure input-image properties (size, axis ratio, colour, …; a few min) | `python src/input_properties.py` | `results/input_props.csv` |
| 3. Build the explorer data (t-SNE of output probabilities, thumbnails) | `python src/build_explorer.py` | `vis/explorer_data.js`, `vis/thumbs.js` |
| 4. Image-editing test (shrink / recolour / rotate; ~10 min) | `python src/perturbation_test.py` then `python src/build_findings_data.py` | `results/perturbations.csv`, `vis/perturbation_data.js` |
| 5. Explore | open `vis/explorer.html` in a browser | |

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

## Repository layout

```
src/model.py           model loader, class names, label mapping, preprocessing
src/run_inference.py   predictions + embeddings for every image
src/build_explorer.py  data for the interactive explorer
src/perturbation_test.py synthetic test: recolour / shrink / rotate images, compare predictions
vis/explorer.html      Phase I (black-box) linked views: confusion matrix, recall, output map, calibration, gallery
vis/findings.html      Phase I key takeaways: one chart + example galaxies per takeaway
ai-interactions/       AI-use log (AI-aided pair)
```
