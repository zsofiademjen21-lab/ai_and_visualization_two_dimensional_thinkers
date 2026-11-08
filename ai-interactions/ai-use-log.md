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

## 6. Making the visualisation simpler

**Prompt:** "Make the visualisations simpler and easier to understand. Only show the key takeaways."

**What Claude did:** It rewrote the findings page:
- Each finding now has one plain-language headline, one or two sentences, one simple chart with only two or three bars, and a few example galaxies.
- Technical words like "recall" and "quintile" were removed.
- It dropped the Cigar-shaped Elliptical finding, because the evidence was weak (only about 18 galaxies per group).
- The detailed interactive explorer was kept separately for anyone who wants to dig deeper.

**My decision:** Modified. Claude's first version was correct but too detailed and technical to present. I asked for it to be simplified, and I agreed with dropping the weak finding.

---

## 7. Further findings

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

## 8. Adding the new findings to the visualisation

**Prompt:** "Add them to the visualisations"

**What Claude did:** It added the new findings to `ai_aided/vis/findings.html`, which now has 5 takeaways. The three findings from the image-editing test are marked "tested by editing images". Each one shows before/after pairs of the same galaxy with the model's answer. The label-noise point is shown as "still to check", because it is only Claude's first visual impression.

**My decision:** Accepted. The before/after images make the experiment easy to understand without any statistics.

---

## 9. Searching for more findings

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

## 10. Adding the second test to the visualisation

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

## 11. Analysing the map of the model's answers

**Prompt:** Analyse the clusters on the map of the model's answers

**What Claude did:** The explorer already had a 2D map of the model's answers, but its clusters had not been analysed yet. Claude:
- found the regions on the map automatically (HDBSCAN, `ai_aided/src/build_map_data.py`);
- compared the regions by error rate, true labels, confidence and image properties;
- checked whether mistakes happen more in sparse or crowded parts of the map;
- looked inside the error regions for sub-groups.

**Results:**
1. Most of the map is dense islands where the model is sure and never wrong (25 regions with 0 mistakes).
2. Mistakes sit in two kinds of places: on "bridges" between two classes, where the model is torn between exactly two answers, and in groups hidden inside the Spiral island, where the model is sure but about a quarter of the galaxies are labelled disturbed.
3. When the model is unsure, 82% of the time almost all its doubt is between exactly two classes. Spiral is part of most of these pairs.
4. On the Spiral ↔ Edge-on bridge, true spirals and true edge-on disks are equally flat (tilted disks), and mistakes go both ways equally.
5. The disturbed galaxies hidden among spirals look like the spirals around them in colour, size and shape. This again points to unclear labels.
6. Sparse vs crowded parts of the map have the same error rate (9% vs 9%), so density doesn't explain the mistakes. About half the mistakes are unsure ones on bridges, half are confident ones inside islands.

**What went wrong:** The first clustering (default settings) found only 2 big clusters, which was useless, so Claude switched to a finer setting. In the first version of the page, the text named the regions by hard-coded numbers, and one circle was drawn far too big. Both were fixed.

**My decision:** Accepted. The map now shows where the mistakes are and explains why they happen there.

---

## 12. Making the explorer easier to understand

**Prompt:** "make the visualisations more understandable if it is possible"

**What Claude did:** It rewrote the wording of the interactive explorer (`ai_aided/vis/explorer.html`) for readers without a machine-learning background:
- a 3-step "how to use" guide at the top, and a link to the key takeaways;
- plain names instead of jargon, for example "Confusion matrix" became "What the model answers for each true class", "Recall" became "How often each class is recognised", and "Calibration" became "Is the model as sure as it should be?";
- one "Look for: ..." hint under each chart that says what to pay attention to;
- the "What does the answer depend on?" chart now opens on Irregular galaxies, where a real pattern is visible straight away. With "all classes" every bar looked the same.

**What went wrong:** One axis label was cut off and some labels still used jargon ("misclassified", "n="). Claude found these in the screenshots and fixed them.

**My decision:** Accepted. The charts themselves stayed the same; only the explanations changed.

---

## 13. Report, slides and a label-check tool

**Prompts:** "Write the Phase I section of our report from the findings page and the log.", "Make a short slide deck of the 7 takeaways for the group meeting.", "Export each takeaway chart as a picture for the report." and "Show me the 40 most confident mistakes one by one so I can decide myself whether the label is wrong."

**What Claude did:**
- Exported each takeaway as a picture (`ai_aided/figures/`).
- Wrote the report section (`ai_aided/report_phase1.md`), checking its numbers against the charts.
- Made a 12-slide deck for the group meeting, including a slide of questions for the human-only pair.
- Built `ai_aided/vis/label_check.html`. It shows the 40 most confident mistakes one by one with large images, and has buttons for "label wrong / model wrong / unsure" and a CSV download. It deliberately doesn't show Claude's own earlier impression, so it doesn't bias our judgement.

**My decision:** Accepted the tool, but in the end I didn't use it to decide the labels myself (see 14).

---

## 14. Checking the labels with the volunteers' own votes

**Prompts:** "what if I can't know enough to decide?" and then "Use the volunteers' own votes, the most objective option."

**What Claude did:**
- Suggested several options for when I can't judge a galaxy myself: "unsure" as valid data, letting all four of us judge and comparing, a deeper sky image, or the volunteers' own votes.
- Downloaded the public Galaxy Zoo DECaLS vote catalogue (Walmsley et al. 2022) and matched it to our galaxies by sky position (`ai_aided/src/volunteer_votes.py`). Only 45% of Galaxy10 galaxies have public votes.
- Turned the votes into a "support" score for each of our five classes and compared the support for the label with the support for the model's answer.
- Added the votes to the label-check page, revealed only after I decide, with a count of how often I agree with the volunteers.

**Results (202 mistakes with votes):**
- The votes back the label (the model is wrong) in 54% of mistakes. The volunteers were split in 18%, both answers fit in 17%, and the votes back the model (the label is wrong) in only 10%.
- No disturbed-galaxy mistake had votes backing the model. When the model calls a disturbed galaxy a spiral, most volunteers had seen both the disturbance (68%) and spiral arms (51%). These are disturbed spirals: the five classes force one answer for a galaxy that is both.

**What went wrong:** Claude's earlier visual impression, "about 16 of the 40 most confident mistakes look mislabelled", was too strong. Of the 15 of those 40 that have votes, only 3 have votes backing the model. Claude was right that those galaxies look like spirals, but wrong that the label was therefore wrong. Claude corrected the findings page, report, reflection and slides.

**My decision:** I decided not to judge the 40 galaxies by hand. As a non-expert I couldn't tell reliably whether a label was wrong, so my judgement would have been weak evidence. The volunteers' votes are a more objective source, because they come from the people who made the labels in the first place. I accepted the result: wrong labels are only a minor explanation (about 1 in 10 mistakes), and "disturbed spirals" is the better one. The label-check page stays available, for example for the comparison with the human-only pair.

---

## Which AI suggestions we accepted, changed or rejected

| AI suggestion | Decision | Why |
|---|---|---|
| Load the model with plain `timm` instead of the `zoobot` package | Accepted | We checked it: our accuracy matched the author's 92.9% exactly. |
| Map of the galaxies built from the model's internal features | Rejected, replaced | Phase I must be black-box, so the map now uses only the model's answers. |
| t-SNE for the map instead of UMAP | Accepted | UMAP wasn't installed, and t-SNE is a standard choice. |
| Measuring size, roundness, colour etc. on each image | Accepted after a fix | The first measurements had a bug that a sanity check caught. |
| First findings page with detailed charts | Modified | Too technical. We asked for a simpler page with key takeaways only. |
| Cigar-shaped Elliptical finding | Dropped from the takeaways | Weak evidence (about 18 galaxies per group), and the squash test weakened it further. It is still visible in the explorer. |
| "The model uses colour" (pattern in the data) | Rejected after testing | Changing only the colour of the images didn't change the answers. |
| "Small galaxies get called Elliptical" | Refined | The blur test showed the real cause is loss of detail, not size itself. |
| Testing ideas by editing the images | Accepted | It separates causes from coincidences, and the assignment allows a synthetic dataset. |
| "Many confident mistakes are wrong labels" (Claude looking at the images) | Rejected after checking | The volunteers' own votes back the model in only 10% of mistakes. Most were disturbed spirals, where both answers fit. |
| Cluster analysis of the map | Accepted | It shows where the mistakes are and why. |
| Judging the 40 most confident mistakes by hand (label-check page) | Not used | As a non-expert my judgement would have been weak evidence. We used the volunteers' own votes instead. |

## How the AI changed the direction of our analysis

1. **From the model's code to our first hypothesis.** Claude read the author's code and pointed out that the classes are imbalanced and no class weights were used. That made us look at the rare classes first, which led to takeaway 1 (disturbed galaxies are the blind spot).
2. **From a pattern to a test.** Claude measured properties of the images and found that small and red disturbed galaxies are often called Elliptical. Because size, colour and distance are mixed together in real images, it suggested editing the images to find the real cause. The test showed colour doesn't matter (rejected) and the loss of detail does (refined). We restructured our takeaways around this.
3. **One idea connecting several findings.** Claude's look at the most confident mistakes raised the idea that some labels may be wrong. This was later supported in two other places: the model gets 26% of disturbed galaxies wrong even on its own training images, and disturbed galaxies hidden among spirals on the map look exactly like spirals. It became a thread through several takeaways. When we checked it with the volunteers' own votes, it turned out mostly wrong: the votes back the model in only 10% of mistakes. The better explanation is that many disturbed galaxies are also spirals, so two answers fit.
4. **A correction that made later work possible.** Moving the map from internal features to the model's answers (to stay black-box) later allowed the cluster analysis of the map.

---

## Failure patterns we saw

The section numbers point to the log entries above.

**Code and numbers**
- Generated code can contain small bugs even when it looks fine (§2).
- Numbers can look reasonable but come from a wrong calculation. The first roundness values made edge-on disks almost as round as ellipticals (§4).
- The AI's first default settings can give useless results. The first clustering found only 2 clusters (§11).

**Following the task**
- The AI fills gaps in the task with "standard practice", even when that breaks the task rules. It used the model's internal features, which belongs to Phase II (§3).

**Claims and writing**
- AI-written text can contain small factual slips ("third-rarest" instead of second-rarest) and can choose comparisons that make results look stronger than they are (§5).
- A pattern in real data can look like a cause when it isn't. Red disturbed galaxies were called Elliptical more often, but changing only the colour changed nothing (§7).
- Results from different kinds of evidence can get mixed up. A result from the real images was shown in the "tested by editing images" card (§10).
- Page text can contain hard-coded values that no longer match the data, such as region numbers written by hand (§11).
- The first version of the output is often correct but too detailed and full of jargon for the audience (§6, §12).

**Experiments and images**
- Edited test images can contain artefacts (flat grey padding, square boxes, hard circle edges) that the model may react to instead of the real change (§7, §9).
- Charts can have layout problems that only show when they are rendered: a cut-off axis label, a circle drawn far too big (§11, §12).
- A default view can hide the pattern. With "all classes" selected, every bar looked the same (§12).

**Judgement**
- The AI's visual judgement of images is not reliable on its own. It thought about 16 of 40 confident mistakes were mislabelled, but the volunteers' votes backed that for only 3 of the 15 that have votes (§14).
- Once an idea is raised, later results get read as support for it. The "wrong labels" idea was linked to the training-set gap (§9) and the map regions (§11) and spread to the findings page, report, reflection and slides before it was checked. It then had to be corrected everywhere (§14).

## Best practices

**Before starting**
- Let the AI read the real source (code, documentation) instead of answering from memory (§1).
- Give it the exact task rules at the beginning (§3).
- Say who the output is for (for example "readers without a machine-learning background") so the first version doesn't need rewriting (§6, §12).

**Checking the work**
- Check every number against something you already know is true: the reported 92.9% accuracy, known differences between classes (§4).
- Re-read every claim the AI writes against the actual numbers in the chart (§5).
- Look at the rendered charts and screenshots, not just the code. Asking the AI to check its own screenshots caught many of its mistakes (§11, §12).
- Calculate the numbers in the text from the data instead of typing them in (§5, §11).
- Don't accept the first default settings. Check whether the result is useful and try other settings (§11).

**Testing ideas**
- Don't trust a pattern in the data alone. Test it by changing the input (the colour pattern turned out to be false, §7).
- Look at the edited test images before running the test (§7, §9).
- Accept results that weaken an earlier idea, not only ones that confirm it (the squash test, §9).
- Drop findings with too little data rather than presenting them (Cigar-shaped Ellipticals, about 18 galaxies per group, §6).
- Label where each result comes from: real data or edited images (§10).

**Judgements**
- Mark the AI's impressions as "still to check" and keep them out of the report until they are checked (§8, §14).
- Check the AI's judgements against independent data where it exists (here, the volunteers' votes, §14).
- When we judge something ourselves, hide the AI's opinion first so it doesn't bias us (the label-check page, §13).
