# Phase I: How does the model behave?

> We test the model on galaxy images it has never seen, to understand what it does well
> and where it makes mistakes. We look for patterns in its predictions and investigate
> which factors affect its results.

The model is treated as a **black box**: we only look at the input image and the
output (5 class probabilities), never inside the network.

---

## 1. How to run it

Everything is in one notebook: **`Phase1_Human_Only.ipynb`**. Open it in VS Code (select the
`venv` Python as kernel) or in the browser, and run all cells from top to bottom:

```bash
source venv/bin/activate
jupyter notebook phase1/Phase1_Human_Only.ipynb
```

Needs `data/Galaxy10_DECals.h5` and `model/zoobot_finetuned.ckpt` (both already downloaded),
and Jupyter in the venv (`pip install notebook ipykernel`).

## 2. What the notebook contains

| Section | What it does |
|---|---|
| 1. Setup | Rebuilds the **validation set** from `train.py` (same seed 42 → same 3,547 images the model was *not* trained on), runs the model, and builds a table with, per image: true class, original Galaxy10 subtype, prediction, confidence, all 5 probabilities, plus 4 simple **image factors**. |
| 2. Behaviour per class | fig1-fig3, most common mistakes |
| 3. Confidence | fig4 |
| 4. Image factors | fig5 |
| 5. Looking at the images | the `examples_*` image grids |
| 6. Going deeper | the labeling grid, fig6-fig9 |

Every figure is also saved as PNG to `figures/` (for the slides), and the table to
`results/predictions.csv` (one row per image, open it in Excel / pandas for your own questions).

**Check that the setup is correct:** our accuracy is **92.9%**, exactly the number in the model's README. So we rebuilt the same validation set.

### The 4 image factors (all computed on the raw 256×256 image)

| Factor | How it's computed | Meaning |
|---|---|---|
| `redshift` | stored in the dataset | how far away the galaxy is (bigger = farther) |
| `size` | fraction of pixels brighter than 60/255 (sky ≈ 35) | how much of the image the galaxy covers |
| `center_brightness` | mean brightness of the central 32×32 pixels | how bright the galaxy core is |
| `redness` | mean red channel − mean blue channel | > 0 = redder (old stars), < 0 = bluer (young stars) |

## 3. The figures and what we found (sections 2-5)

| Figure | Question it answers | What it shows |
|---|---|---|
| `fig1_class_counts_and_accuracy` | Are rare classes predicted worse? | **Irregular** is the rarest class (876 training images vs 5,200 Spiral) and the worst by far: **56% accuracy**. All others are 91-98%. |
| `fig2_confusion_matrix` | What gets confused with what? | Most errors are *Irregular → Spiral* (49) and *Irregular → Elliptical* (36). |
| `fig3_subtypes_vs_prediction` | Which original subtype causes errors? | "Disturbed" is the only weak subtype. **Cigar Smooth** ellipticals (only 53 images) are mistaken for Edge-on 9% of the time. |
| `fig4_confidence_correct_vs_wrong` | Does the model know when it's wrong? | Mostly yes for 4 classes (errors have lower confidence). But for **Irregular, the errors are just as confident as the correct predictions**: the model is *confidently wrong*. |
| `fig5_accuracy_vs_factors` | Do distance / size / brightness / colour matter? | **Overall: hardly** (all groups ~92-95%). **But Irregular depends strongly on them:** 73% correct for the closest galaxies vs 39% at medium distance; 68% for the bluest vs 37% for the reddest. ⚠️ Only ~41 Irregular images per group, so this is noisy. |
| `examples_*` | What do the mistakes look like? | Many "Disturbed" galaxies predicted *Elliptical* **look smooth and elliptical to the human eye too**. |

## 4. Going deeper (section 6)

| Figure | Question | What it shows |
|---|---|---|
| `labeling_grid_irregular` + `fig6_irregular_labels` | **Is it the model or the label?** | All 91 wrong Irregular images were labeled by eye, with the prediction hidden. Only **24 of 91** clearly look disturbed. Of the 36 predicted *Elliptical*, only **2** look disturbed; the other 34 look like ordinary ellipticals. Of the 49 predicted *Spiral*, 18 look disturbed. All 3 predicted *Merger* look like interacting systems. So **most "Elliptical" mistakes are really ambiguous labels**, while the "Spiral" mistakes are a mix of label ambiguity and real model errors. |
| `fig7_irregular_redshift_vs_redness` + `fig8_irregular_distance_and_colour_groups` | **Colour or distance?** | **Colour matters more than distance for the "Elliptical" mistakes.** Near + blue Irregulars are almost never called Elliptical (3%), but near + red ones are (27%), as often as far + red ones (31%). Near + blue is the only group the model handles well (70% correct vs 43-53%). The "Spiral" mistakes (20-30%) happen in all four groups, so colour and distance don't explain them. |
| `fig9_true_class_probability_and_rank` | **Was the right answer a close call?** | When the model gets an Irregular galaxy wrong, Irregular is its 2nd choice in 83% of cases, exactly the same as for the mistakes of all other classes. So the model doesn't ignore the Irregular class more than other classes; it just loses the close call more often. |

**Hand-off to Phase II (when we open the black box):** for the misclassified Irregular galaxies that *do*
look disturbed, does the model look at the colour and the bright core and ignore the faint disturbed
features (tidal tails etc.)? Saliency maps can answer this.