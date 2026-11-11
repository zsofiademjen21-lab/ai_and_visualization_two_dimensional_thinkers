# AI-aided pair: Vis4AI on AstroVision-Advanced

## Task

In Phase I, we tested the model on galaxy images to understand what it does well and where it makes mistakes. We looked for patterns in its predictions and investigated which factors affect its results.

## Model

AstroVision Advanced — Galaxy Morphology Classifier: [zev-walker/astrovision-advanced](https://huggingface.co/zev-walker/astrovision-advanced).

It is a Zoobot model (ConvNeXt-Nano) fine-tuned on Galaxy10 DECals. It sorts galaxy images into 5 classes: Spiral, Elliptical, Edge-on Disk, Irregular and Merger.

## This folder

This folder holds the AI-aided pair's Phase I work. We used two AI tools, each in its own subfolder:
- **`chatgpt/`**: 25 independent galaxy images (Wikimedia Commons, ESA/Hubble) and image-editing tests on one ESA/Hubble merger image (crop, background, apparent scale, image quality). ChatGPT designed and generated the edits, and we ran the model on them ourselves. Only the figures are stored here; the prompts and all result tables are in the AI-use log.
- **`claude/`**: the full Galaxy10 DECals validation set, with code, results and interactive visualisations (Claude Code).

The written Phase I section, covering both parts and comparing them, is [`report_phase1.md`](report_phase1.md). The AI-use log is in [`../ai-interactions/ai-use-log.md`](../ai-interactions/ai-use-log.md).

**To see the results:**
- ChatGPT part: the charts in [`chatgpt/figures/`](chatgpt/figures/) (confusion matrix on the 25 images, response to apparent scale, predicted class across all edits).
- Claude part: open [`claude/vis/findings.html`](claude/vis/findings.html) (key takeaways) or [`claude/vis/explorer.html`](claude/vis/explorer.html) (interactive explorer) in a browser. [`claude/vis/label_check.html`](claude/vis/label_check.html) is a tool for checking the labels of the 40 most confident mistakes by hand. One chart per takeaway is in [`claude/figures/`](claude/figures/).

The rest of this README describes how to reproduce the Claude part.

## Setup

Install the packages and download the dataset as described in the [main README](../README.md#reproducing-the-results). The dataset and the checkpoint live at the repository root, not in this folder.

## Pipeline

Run these in order from the `ai_aided/claude/` folder:

| Step | Command |
|---|---|
| 1. Inference on all 17,736 images (about 40 min on CPU) | `python src/run_inference.py` |
| 2. Measure input-image properties | `python src/input_properties.py` |
| 3. Build the explorer data | `python src/build_explorer.py` |
| 4. Image-editing tests (about 25 min) | `python src/perturbation_test.py`, `python src/perturbation_test2.py` |
| 5. Build the findings data | `python src/build_findings_data.py`, `python src/build_map_data.py` |
| 6. Volunteer votes and label check (download the catalogues first, see the script) | `python src/volunteer_votes.py`, `python src/build_label_check.py` |

Note: the h5 file is sorted by class, so never take the first N images as a "random" sample.
