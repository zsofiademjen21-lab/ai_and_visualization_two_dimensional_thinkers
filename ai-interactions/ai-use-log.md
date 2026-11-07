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

**What Claude did:** It built one interactive page (`ai_aided/vis/explorer.html`) with linked views:
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

**What Claude did:** It made `ai_aided/vis/findings.html`. Each finding gets one chart and real example galaxies, and all numbers are calculated from the data.

**What went wrong:** When checking the page against the data, two of Claude's own sentences were wrong:
- It called Disturbed the "third-rarest" class, but it's the second-rarest.
- The size claim skipped one group of the data, which made the effect look stronger than it really is.

Both were corrected.

**Something to check:** Some of the most "confident mistakes" look like wrong labels rather than model mistakes. For example, one galaxy labelled as a spiral is clearly two galaxies merging.

---

## 6. Further findings

**Prompt:** "Can you find further findings?"

**What Claude did:**
- It checked colour, distance and neighbours in the data.
- It found that red Irregulars are called Elliptical much more often than blue ones. Size, colour and distance are all mixed together in real data, though, so it suggested a test: edit the images directly. It made the galaxies redder or bluer, removed the colour, shrank them, or rotated them, and compared the predictions (`ai_aided/src/perturbation_test.py`, 705 validation galaxies).
- It looked through the 40 most confident mistakes.

**Results:**
1. Changing the colour barely changes the predictions. The colour pattern was only a side effect, not what the model uses.
2. Shrinking a galaxy really does make the model call it Elliptical more often. Spirals go from 1% to 14%. This confirms the size finding.
3. Just rotating the image changes 13% of the Irregular predictions, although the model was trained on rotated images. The Irregular predictions are fragile.
4. In Claude's view, about 16 of the 40 most confident mistakes look like wrong labels (for example "Disturbed" galaxies that look like normal spirals). This still needs our own check.

**What went wrong:** The first version of the shrink test filled the empty space with flat grey. That looks artificial, and the model could react to it instead of the size. Claude saw it in a preview and changed it to real sky pixels.

**My decision:** Accepted. The colour result was important: without the test we would have reported a colour shortcut that isn't real.

---

## 7. Adding the new findings to the visualisation

**Prompt:** "Add them to the visualisations"

**What Claude did:** It added the new findings to `ai_aided/vis/findings.html`, which now has 5 takeaways. The three findings from the image-editing test are marked "tested by editing images". Each one shows before/after pairs of the same galaxy with the model's answer. The label-noise point is shown as "still to check", because it is only Claude's first visual impression.

**My decision:** Accepted. The before/after images make the experiment easy to understand without any statistics.

---

## 8. Searching for more findings

**Prompt:** "could you search for more findings?"

**What Claude did:** First it checked the existing results again, comparing training images with new images, distance, and the model's second choice:
1. The model memorised the rare classes instead of learning them. Disturbed galaxies are 74% correct on training images but only 56% on new ones, and Cigar-shaped 97% vs 85%. For the common classes the gap is at most 5 points. Even on its own training images the model gets 26% of disturbed galaxies wrong, which also fits the idea that these labels are inconsistent.
2. Distance alone doesn't matter. Accuracy is 92–94% from the nearest to the farthest galaxies.
3. Most mistakes are near misses. In 82% of them, the correct class is the model's second choice.

Then it started a second image-editing test (`ai_aided/src/perturbation_test2.py`, 1,115 galaxies). It blurs the images, squashes round galaxies flat, removes the surroundings or adds a neighbour galaxy, and moves the galaxy off-centre.

**What went wrong:** In the preview, two of the edits looked artificial. The added neighbour had a visible square box around it, and the "remove surroundings" edit had a hard circle edge that also cut off large galaxies. The model could have reacted to these artefacts instead of the real change. Claude fixed both before running the test.

**Results of the second test:**
1. Blurring (same size, less detail) makes spirals look like ellipticals to the model (1% → 10%). So it's the loss of detail that matters, not the size itself.
2. Squashing round ellipticals flat almost never makes the model say Edge-on (1.5%). Being elongated alone isn't enough, so the model needs real disk features. This makes the earlier Cigar-shaped idea weaker.
3. Removing the surroundings or adding a small neighbour galaxy barely changes anything (Mergers stay at 90–91%). The model isn't fooled by an added companion. Real merger pairs are very close together, though, so this only shows that distant surroundings don't matter.
4. Disturbed galaxies are the least stable under every harmless edit: blur changes 38% of the answers, moving off-centre 17%, rotating 13%. For the other classes it's mostly 2–10%.

**My decision:** Accepted. Finding 2 shows that a test can also weaken an earlier idea, not just confirm it.

---

## 9. Adding the second test to the visualisation

**Prompt:** "add this too to the visualisation"

**What Claude did:** It reorganised `ai_aided/vis/findings.html` into 6 takeaways so the page stays simple:
1. Disturbed galaxies are hard for the model.
2. Losing detail makes galaxies look like ellipticals (shrink and blur tests, with before/after images).
3. Small, harmless changes (rotate, move, blur) flip the answer for disturbed galaxies.
4. The model memorised the rare classes (training vs new images).
5. The model is often very sure when it is wrong.
6. What does *not* confuse the model: colour, shape alone, neighbours, surroundings and distance, shown as simple "before → after" numbers.

**What went wrong:** In the first version, the "distance" row sat in the "tested by editing images" card although it comes from the real images. Claude added a label so it isn't mistaken for an experiment.

**My decision:** Accepted. Putting all the "this doesn't matter" results in one card keeps the page short.

---

## Failure patterns we saw

- Generated code can contain small bugs even when it looks fine.
- Numbers can look reasonable but come from a wrong calculation (the measurement bug).
- The AI fills gaps in the task with "standard practice", even when that breaks the task rules (Phase II drift).
- AI-written summaries can choose comparisons that make results look stronger than they are.
- Edited test images can contain artefacts (boxes, hard edges) that the model may react to instead of the real change.

## Best practices

- Let the AI read the real source (code, documentation) instead of answering from memory.
- Give it the exact task rules at the beginning.
- Check every number against something you already know is true.
- Look at the rendered charts, not just the code.
- Re-read every claim the AI writes against the actual numbers in the chart.
- Don't trust a pattern in the data alone. Test it by changing the input (the colour pattern turned out to be false).
- Look at the edited test images before running the test.
