Phase I.

# AI Reflection: Midpoint

AI-aided pair: 
Zsófia Demjén-Nagy k12413807
Livia Koch  k09956227


Tool: Claude Code, ChatGPT
Full record: [ai-interactions/ai-use-log.md](ai-interactions/ai-use-log.md).

## What the AI did for us

- **Setup:** It read the model card and the author's code, and wrote a loader for the model. It reproduced the author's exact validation split, so our accuracy matched the reported 92.9%.
- **Visualisation:** It built an interactive explorer with linked views (confusion matrix, map of the model's answers, calibration, image gallery). It also built a findings page with 7 key takeaways.
- **Broader analysis:**
  - It measured properties of every input image (size, roundness, colour, …).
  - It ran two image-editing experiments (shrink, blur, recolour, squash, rotate, move, add a neighbour) to test causes rather than just correlations.
  - It ran a cluster analysis of the map.
  - It checked whether the model's mistakes are really wrong labels, using the Galaxy Zoo volunteers' own votes.

## Did AI change the breadth or depth of our analysis?

Both. **Breadth:** we tested many more hypotheses than we could have by hand: six image properties, ten kinds of image edits, a cluster analysis and a comparison with the volunteers' votes. **Depth:** the AI suggested testing patterns by editing the images. This let us go past "we see a pattern" to "this is the cause". For example, it showed that colour is not the reason for a mistake, even though the data suggested it was.

## Did it make us faster, or did checking it cost extra work?

Both. Building the pipeline and the interactive pages was much faster than writing them ourselves. But we had to check almost everything:
- a measurement bug that gave plausible-looking but wrong numbers;
- summary sentences that made results look stronger than they were;
- artefacts in edited test images;
- a map that broke the Phase I rules.

Checking is quicker than building, but it is real work. It only works if you know what the right answer should roughly look like.

## How confident are we in our conclusions, and why?

- **High confidence:** the irregular-galaxy blind spot, loss of detail causing "Elliptical" mistakes, the fragility of irregular predictions, and the much weaker results for the rare classes on new images. These are based on hundreds of images, hold on both the training and validation data, and the causes were tested by editing images where possible. That rarity causes the weak rare classes, and that the gap is memorisation, are interpretations we could not test in Phase I.
- **Medium confidence:** the map regions. The same bridges and hidden group came back when we rebuilt the map from three other random starts, but the exact number of regions changed.
- **Corrected by data:** the AI's visual impression suggested that many confident mistakes were wrong labels. The volunteers' own votes showed this explains only about 1 in 10 mistakes; most "irregular" galaxies called Spiral are disturbed spirals, where both answers fit. A good example of why an AI's visual judgement needs checking against real data.

## Strengths and limitations of AI assistance

**Strengths**
- It is fast at building code and interactive visualisations.
- It suggests ways to test an idea, not just to describe it.
- When asked to check its own output (screenshots, sanity checks), it finds many of its own mistakes.

**Limitations**
- It fills gaps with "standard practice" even when that breaks the task rules.
- It can produce numbers and sentences that look right but aren't.
- Its judgement of images is not a substitute for a human check.
- Without clear instructions, its first output is often too detailed for presenting.

## What the human-only pair did

Daniel and Bence worked in one Jupyter notebook ([human_only/](human_only/README.md)). They rebuilt the same validation split and also got 92.9%. Their analysis used only real images and model outputs:
- accuracy per class, a confusion matrix and the 10 original subtypes;
- confidence of correct vs wrong predictions, per class;
- accuracy against four simple image properties (distance, size, core brightness, redness);
- grids of example images (most confident mistakes, most common mistakes, correct vs wrong per class);
- a visual check of all 91 wrongly predicted irregular galaxies ("looks disturbed" or "looks normal");
- a near/far × blue/red split of the irregular galaxies.

## Comparison with the human-only pair

**Same core result.** Both pairs found the irregular-galaxy blind spot: 56% correct, with the mistakes going mostly to Spiral and Elliptical, and the class being rare in training (876 images). Both found that the model is confidently wrong on this class. Both also saw the smaller Cigar-shaped elliptical problem: they found it confused with Edge-on (9% of 53), we found its accuracy drops from training to new images (97% to 85%).

**Size and detail.** They saw that irregular accuracy changes with distance (73% near vs 39% at medium distance), but they only observed it. We tested it by shrinking and blurring spirals, which showed that *loss of detail* turns galaxies into "Elliptical".

**Colour: same pattern, opposite conclusion.** Both pairs saw that red irregular galaxies are called Elliptical much more often than blue ones. They concluded that "colour matters more than distance" and that the model has learned something like "red and smooth means Elliptical". Our recolouring test showed that making red irregular galaxies bluer does not change the answer (33% vs 32% called Elliptical). So colour goes along with the mistakes but does not cause them; a smoother shape is the more likely reason. This is the clearest case where testing with edited images changed the conclusion.

**Labels: visual judgement vs volunteer votes.** Their visual check found that only 24 of the 91 mistakes look disturbed, and 34 of the 36 "called Elliptical" look like normal ellipticals. They concluded that the low irregular accuracy is partly a label problem. Our first visual impression pointed the same way (about 16 of 40 confident mistakes looked mislabelled). The volunteers' votes did not support this: wrong labels explain only about 1 in 10 mistakes, and no irregular mistake had votes backing the model. Both pairs' visual judgements overstated label noise. The disturbances are often faint and hard to see at this image size, but the volunteers did see them.

**Visualisations.** Theirs are static charts and image grids that are easy to read and explain one finding each. Ours are interactive and linked (map, calibration, gallery) and include before/after image pairs. Ours allow more exploration, but they took much longer to check and needed simplifying before we could present them.

**What they found that we did not.**
- The per-class confidence histograms make the "confidently wrong on irregular" point very directly: for irregular galaxies, wrong and correct predictions have about the same confidence.
- The 2×2 near/far × blue/red table is a simple and clear way to separate two linked factors, without any image editing.
- A concrete Phase II question: saliency maps for irregular galaxies that really look disturbed.

**What we found that they did not.** The detail-loss cause, the instability of irregular answers under rotation and shifting, the gap between training and new images, the two-class "bridges" on the map, the label check with volunteer votes, and (with ChatGPT) the drop to 64% on images from other telescopes.

**What this says about AI assistance.** Both pairs reached the same main finding, so AI was not needed to find the blind spot. AI widened the analysis and, more importantly, pushed us to test causes. Without the tests, both pairs drew the same wrong conclusion about colour and label noise from what they observed. The human-only pair's work is smaller but more focused, and each figure answers one question.
