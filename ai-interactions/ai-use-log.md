# AI-Use Log (AI-aided pair)

Model: [zev-walker/astrovision-advanced](https://huggingface.co/zev-walker/astrovision-advanced)
AI tool: Claude Code (Claude Opus 5.5)

---

## 1. Understanding the model

**Prompt:** I shared the model link and the assignment text.

**What Claude did:** It read the model card and the author's GitHub code. What it found:
- The model is a fine-tuned Zoobot (ConvNeXt-Nano) trained on Galaxy10 DECals.
- The 10 original classes are merged into 5.
- The only reported number is 92.9% validation accuracy.
- Images are resized to 224 px with ImageNet normalisation, and validation is a random 20% split with seed 42, so we could rebuild the exact same split.
- Claude wrote a small loader with `timm`, so we didn't need to install the `zoobot` package.

**What it pointed out:**
- There is no separate test set, so the validation split is our only held-out data.
- The encoder was pretrained on images from the same survey, so it may have seen our "validation" images before.
- The model was trained without class weights, even though the classes are very imbalanced.

**My decision:** Accepted. These points became our starting hypotheses (for example: rare classes should do worse).

---

## 2. Building the explorer

**Prompt:** "can you help with the visualization?"

**What Claude did:** It built one interactive page (`vis/explorer.html`) with linked views:
- a confusion matrix (5 or 10 classes)
- recall bars
- a 2D map of the galaxies
- a calibration chart
- an image gallery

Clicking a matrix cell shows those galaxies everywhere else.

**My decision:** Accepted. It gave much more interaction than we would have built by hand in the same time.

**What went wrong:** The first version of the build script had a broken line of code. Claude noticed and fixed it itself, but it shows that generated code needs checking.

---

## 3. Staying inside Phase I

**Prompt:** I pasted the Phase I description and asked: "did you only do this part? don't do phase 2"

**What went wrong:** Claude's 2D map used the model's internal features. That means looking inside the model, which belongs to Phase II. It had done this out of habit, because I hadn't given it the phase rules before.

**What changed:** The map now uses only the model's output probabilities. Claude also suggested going deeper in a black-box way: measure properties of the input images and check whether mistakes depend on them.

**My decision:** Accepted both.

**What I learned:** Give the AI the exact rules of the task at the start.

---

## 4. Real results and input properties

This follows from the suggestion in 3.

**Check:** Our validation accuracy came out at exactly 92.9%, the same as the model card, so our setup matches the author's.

**What Claude did:**
- It measured six things for every image: distance (redshift), apparent size, core brightness, roundness (axis ratio), colour, and how much light comes from outside the galaxy.
- It added a chart to the explorer showing what the model predicts across different ranges of each property.

**What went wrong:** The first measurements were wrong. Edge-on disks came out almost as round as round ellipticals, which is impossible. Claude found this by checking the numbers against known differences between the classes. Background noise was being added up. After the fix, the numbers made sense: round > cigar > edge-on, and ellipticals redder than spirals.

**First findings:**
1. Disturbed (Irregular) galaxies are only recognised 56% of the time. They are mostly called Spiral or Elliptical.
2. Cigar-shaped Ellipticals are only 85% correct. This is hidden when the classes are merged.
3. Small Disturbed galaxies get called Elliptical much more often than large ones. The training set shows the same pattern.
4. Confidence looks fine on average, but a third of the mistakes are made with 90%+ confidence.

**My decision:** Kept all four, but they still need to be checked by looking at the images ourselves.

---

## 5. Visualising the findings

**Prompt:** "can you visualize your findings?"

**What Claude did:** It made `vis/findings.html`. Each finding gets one chart and real example galaxies, and all numbers are calculated from the data.

**What went wrong:** When checking the page against the data, two of Claude's own sentences were wrong:
- It called Disturbed the "third-rarest" class, but it's the second-rarest.
- The size claim skipped one group of the data, which made the effect look stronger than it really is.

Both were corrected.

**Something to check:** Some of the most "confident mistakes" look like wrong labels rather than model mistakes. For example, one galaxy labelled as a spiral is clearly two galaxies merging.

---

## Failure patterns we saw

- Generated code can contain small bugs even when it looks fine.
- Numbers can look reasonable but come from a wrong calculation (the measurement bug).
- The AI fills gaps in the task with "standard practice", even when that breaks the task rules (Phase II drift).
- AI-written summaries can choose comparisons that make results look stronger than they are.

## Best practices

- Let the AI read the real source (code, documentation) instead of answering from memory.
- Give it the exact task rules at the beginning.
- Check every number against something you already know is true.
- Look at the rendered charts, not just the code.
- Re-read every claim the AI writes against the actual numbers in the chart.
