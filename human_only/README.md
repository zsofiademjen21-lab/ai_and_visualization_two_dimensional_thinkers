# Phase I – Human-only pair: How does AstroVision behave?

In this phase we treated AstroVision Advanced as a black box. We only looked at what goes in
(a galaxy image) and what comes out (a probability for each of the five classes: Spiral,
Elliptical, Edge-on, Irregular and Merger), and tried to find out where the model does well,
where it fails, and why.

All code and figures are in [`Phase1_Human_Only.ipynb`](Phase1_Human_Only.ipynb). The figures
are also saved in `figures/`.

## Setup

The model was fine-tuned on Galaxy10 DECals with a random 80/20 split. We rebuilt exactly the same
split (same seed as in `train.py`), so all our results are on the 3,547 validation images the
model never saw during training. We get an accuracy of 92.9%, the same number the model's authors
report, which told us the setup was right.

For every image we stored the prediction, the confidence (the probability of the predicted class)
and four simple properties of the image: the redshift (how far away the galaxy is), the size of the
galaxy in the image, the brightness of its centre, and how red it is (mean red channel minus mean
blue channel).

## One class is the problem

The overall accuracy hides a very uneven picture (fig1). Four of the five classes are recognised
91–98% of the time, but **Irregular galaxies only 56% of the time**. It is also the rarest class
in the training data: 876 images, compared to 5,200 spirals.

The confusion matrix (fig2) shows where these galaxies go: 49 of them are predicted as Spiral and
36 as Elliptical. Together that is a third of all 252 mistakes. When we split the classes back into
the ten original Galaxy10 subtypes (fig3), "Disturbed" is the only subtype that really stands out.
The one smaller issue is Cigar Smooth ellipticals, which are sometimes taken for edge-on disks
(9% of 53 images). That is understandable, since both look like a thin elongated shape.

The confidence values (fig4) made this more interesting. For most classes, wrong predictions have
clearly lower confidence than correct ones (median 0.79 vs 0.99), so the model "knows" when it is
unsure. For Irregular galaxies this is not the case: the wrong predictions are about as confident
as the correct ones. **The model is confidently wrong** on exactly the class it struggles with most.

## What affects the results?

Next we checked whether distance, size, brightness or colour make a difference (fig5). For the
model as a whole they barely matter: every group lands between 92% and 95%. Irregular galaxies are
the exception again. The closest ones are recognised 73% of the time, those at medium distance only
39%. The bluest ones reach 68%, the reddest only 37%. With about 40 Irregular images per group these
numbers are noisy, but the trend is clear enough to follow up.

Looking at the actual images (section 5 of the notebook) gave us the most useful hint: many of the
"Disturbed" galaxies that the model calls Elliptical simply look like smooth, round, reddish
ellipticals.

## Going deeper

**Is it the model or the label?** The Galaxy10 labels come from Galaxy Zoo volunteers, so they are
not perfect. To check this, all 91 wrongly predicted Irregular galaxies were labeled visually as
"looks disturbed" or "looks normal", with the model's prediction hidden (fig6). Only 24 of the 91
clearly look disturbed. The difference between the two big mistake types is striking:

- Of the 36 galaxies predicted as **Elliptical**, only 2 look disturbed. The other 34 look like
  ordinary ellipticals, so for most of these "mistakes" the model's answer is at least as plausible
  as the label.
- Of the 49 predicted as **Spiral**, 18 look disturbed, so here we see a mix of debatable labels
  and real model errors.
- All 3 predicted as **Merger** show interacting galaxies, which is a reasonable confusion.

**Colour or distance?** Far away galaxies also look redder, so we could not tell from fig5 which of
the two actually matters. We split the Irregular galaxies into four groups: near/far and blue/red
(fig8).

| | blue | red |
|---|---|---|
| **near** | 70% correct, 3% called Elliptical (n=73) | 43% correct, 27% called Elliptical (n=30) |
| **far** | 53% correct, 13% called Elliptical (n=30) | 47% correct, 31% called Elliptical (n=72) |

Near and blue is the only group the model handles well. Red galaxies are called Elliptical almost
equally often whether they are near or far, so **colour matters more than distance**. The model
seems to have learned something like "red and smooth means Elliptical". The Spiral mistakes, on the
other hand, happen in all four groups (20–30%), so colour and distance do not explain them.

## Conclusion

The model works well on four of five classes and is robust to distance, size, brightness and colour.
Its weak spot is the Irregular class, which is rare in the training data and where the model is
confidently wrong. A large part of these errors, especially the ones predicted as Elliptical, are
galaxies that do not look disturbed at all, and their colour plays a big role. So the low Irregular
accuracy is partly a problem with the labels and only partly a problem with the model.

**Limitations.** There are only 205 Irregular galaxies in the validation set, so the group-level
numbers are noisy. The visual labels are a single subjective judgement. Our image properties are
simple: redness, for example, is measured over the whole image, including the sky and other objects.

**Questions for Phase II.** For the Irregular galaxies that really do look disturbed but are still
predicted as Spiral or Elliptical, what does the model look at? We expect saliency maps to show that
it focuses on the bright core and the colour, and ignores the faint disturbed features such as tidal
tails.

## Running the notebook

```bash
source venv/bin/activate
jupyter notebook phase1/Phase1_Human_Only.ipynb
```

The notebook expects `data/Galaxy10_DECals.h5` and `model/zoobot_finetuned.ckpt` one folder above
it. The first run reads the images from the `.h5` file once and caches them in
`results/validation_images.npy` (about 700 MB, not in git).
