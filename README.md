# Two Dimensional Thinkers: Vis4AI on AstroVision-Advanced

Group project for the course *AI and Visualization*. We use visualisation to understand how an image classifier behaves: what it gets right, where it fails, and why.

## Model

[zev-walker/astrovision-advanced](https://huggingface.co/zev-walker/astrovision-advanced) is a Zoobot (ConvNeXt-Nano) galaxy morphology classifier, fine-tuned on [Galaxy10 DECals](https://zenodo.org/records/10845026). It sorts galaxy images into five classes: Spiral, Elliptical, Edge-on Disk, Irregular and Merger. The author reports 92.9% validation accuracy.

## Team

| Name | Student ID |
|---|---|
| Zsófia Demjén-Nagy | k12413807 |
| Livia Koch | k09956227 |
| Daniel Morgunov | k12141900 |
| Bence Kovács | K12245534 |

Zsófia and Livia form the AI-aided pair; Daniel and Bence form the human-only pair. Details are in [`team-info.json`](team-info.json) and [`workload.json`](workload.json).

## Where to start

- **Phase I report:** [`ai_aided/report_phase1.md`](ai_aided/report_phase1.md). It covers both AI-aided parts (ChatGPT and Claude Code) and compares them.
- **Key takeaways page:** open [`ai_aided/claude/vis/findings.html`](ai_aided/claude/vis/findings.html) in a browser.
- **Interactive explorer:** open [`ai_aided/claude/vis/explorer.html`](ai_aided/claude/vis/explorer.html) in a browser (confusion matrix, map of the model's answers, calibration, image gallery).
- **Human-only pair's Phase I work:** [`human_only/README.md`](human_only/README.md), with all code and figures in [`human_only/Phase1_Human_Only.ipynb`](human_only/Phase1_Human_Only.ipynb).
- **AI reflection (midpoint):** [`ai_reflection_midpoint.md`](ai_reflection_midpoint.md).

The HTML pages are self-contained: they need no server and no downloads.

## Repository structure

| Path | Contents |
|---|---|
| [`ai_aided/`](ai_aided/) | AI-aided pair's Phase I work and report (see [its README](ai_aided/README.md)) |
| [`ai_aided/chatgpt/`](ai_aided/chatgpt/) | ChatGPT part: 25 independent galaxy images and image-editing tests on one image (figures only) |
| [`ai_aided/claude/`](ai_aided/claude/) | Claude Code part: full Galaxy10 validation set, with code (`src/`), results (`results/`), interactive pages (`vis/`) and one chart per takeaway (`figures/`) |
| [`human_only/`](human_only/) | Human-only pair's Phase I work: notebook, figures (`figures/`) and results (`results/`) |
| [`ai-interactions/ai-use-log.md`](ai-interactions/ai-use-log.md) | AI-use log: prompts, AI answers and what we checked or changed |
| [`ai_reflection_midpoint.md`](ai_reflection_midpoint.md) | Midpoint reflection on working with AI, including a comparison with the human-only pair |
| `data/` | Shared dataset (gitignored, see below) |
| `models/` | Shared model checkpoint, stored with Git LFS (see below) |

## Reproducing the results

The dataset (2.7 GB) and the checkpoint (172 MB) are shared by the whole group, so they live at the repository root. The dataset is not committed. The checkpoint is committed with [Git LFS](https://git-lfs.com/), so run `git lfs install` once before cloning (or `git lfs pull` after cloning) to get the real file instead of a small placeholder.

```bash
pip install torch torchvision timm h5py pandas scikit-learn pillow huggingface_hub
mkdir -p data
curl -L -o data/Galaxy10_DECals.h5 https://zenodo.org/records/10845026/files/Galaxy10_DECals.h5
```

If `models/zoobot_finetuned.ckpt` is missing, the AI-aided code downloads it from Hugging Face on the first run. For the AI-aided code the `zoobot` package is **not** needed: `ai_aided/claude/src/model.py` rebuilds the network with plain `timm` and loads the checkpoint with `weights_only=True`.

The full pipeline (inference, measurements, image-editing tests, data for the pages) is described step by step in [`ai_aided/README.md`](ai_aided/README.md#pipeline).

The human-only notebook loads the model with `zoobot` (`pip install zoobot[pytorch]`) and expects the same `data/` and `models/` folders; see [`human_only/README.md`](human_only/README.md#running-the-notebook).
