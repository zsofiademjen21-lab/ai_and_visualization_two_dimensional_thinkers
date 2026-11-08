Phase I.

# AI Reflection: Midpoint

AI-aided pair: 
Zsófia Demjén-Nagy k12413807
Livia Koch  k09956227


Tool: Claude Code. Full record: [ai-interactions/ai-use-log.md](ai-interactions/ai-use-log.md).

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

- **High confidence:** the disturbed-galaxy blind spot, loss of detail causing "Elliptical" mistakes, the fragility of disturbed predictions, and the much weaker results for the rare classes on new images. These are based on hundreds of images, hold on both the training and validation data, and the causes were tested by editing images where possible. That rarity causes the weak rare classes, and that the gap is memorisation, are interpretations we could not test in Phase I.
- **Medium confidence:** the map regions. The same bridges and hidden group came back when we rebuilt the map from three other random starts, but the exact number of regions changed.
- **Corrected by data:** the AI's visual impression suggested that many confident mistakes were wrong labels. The volunteers' own votes showed this explains only about 1 in 10 mistakes; most "disturbed" galaxies called Spiral are disturbed spirals, where both answers fit. A good example of why an AI's visual judgement needs checking against real data.

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

## Points to compare with the human-only pair

- Did they find the disturbed-galaxy blind spot and the size/detail effect, and did they test the cause or only observe it?
- Did they also see the colour pattern, and did they conclude that the model uses colour?
- How did their visualisations differ? Ours are interactive and linked, and include before/after image pairs.
- Did they find something we missed because the AI steered us in a particular direction?
