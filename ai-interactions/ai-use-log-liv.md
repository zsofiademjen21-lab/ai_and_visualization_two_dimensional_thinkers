## 1. Understanding the model

First I started off with downloading images from commons.wikimedia.org and https://esahubble.org/news/heic2101/. I classified the images and stored the results in a csv-file. I found many misclassified images.

**Prompt:** I shared the model and the image sources with ChatGPT and stated, that there have been many misclassifications, and then asked: I want to understand why this is the case. What can we try?

**ChatGPT:** It analyzed the model and pointed out hypotheses why the images are misclassified:
	- Hypothesis A: The labels are not equivalent
	- Hypothesis B: The images are different from the Galaxy10 training images
	- Hypothesis C: The model relies on the wrong visual features
	
	It suggested several controlled experiments, investigating the confidence scores, and then wanted to dive into the code of the model - I had not been specific enough in my prompt. 
	Then it asked me to upload a screenshot of the AstroVision results for one or two of the HEIC2101 merger galaxies.
	
**my decision:** I agreed:the merger galaxies were those that were definitely labeld correctly, coming from an official source. I shared the results:

**Prompt:**
	image			true label	prediction		confidence		merger probability
	m001_heic1811a	merger	irregular galaxy	97,40%		0,04%
	
	I uploaded the image.
	
	Also, I told ChatGPT to treat the model as a black box.
	
**ChatGPT:**
	It analyzed the picture: The image is almost square, so there is no obvious aspect-ratio problem. It also has no transparency channel.
	This means we can investigate the model's behavior without first correcting an obvious image-format issue.
	It generated 6 images from the original image: center crop, grayscale, reduced resolution, lower contrast, mild blur, asked me to classify the images with the model and upload the results.
	
**my decision:** I agreed and uploaded the results:
	Image				predicted class		Confidence	Merger probability
	00_original			irregular galaxy		97,40%		0,04%
	01_center_crop_72pct	spiral galaxy		50,99%		3,95%
	02_grayscale			irregular galaxy		97,06%		0,06%
	03_downsampled_upscaled	irregular galaxy		97,29%		0,04%
	04_lower_contrast		irregular galaxy		98,10%		0,05%
	05_mild_blur			irregular galaxy		97,27%		0,04%
	
**ChatGPT:** Observations:

	AstroVision consistently classifies the original ESA/Hubble image as an irregular galaxy with high confidence. 
	Its prediction is relatively insensitive to grayscale conversion, moderate resolution reduction, lower contrast, and mild blur. 
	However, a central crop changes the predicted class to spiral galaxy and substantially increases the merger probability. 
	This suggests that image framing, apparent scale, or the amount of visible outer structure has a stronger influence on the model's output than the tested image-quality transformations.
	
	It suggested generating the next set of images directly from the original file, focusing on the crop experiment and the scale-versus-framing experiment.
	
**my decision:** I agreed, let ChatGPT create the images and uploaded the results from the model:
	Image							predicted class		Confidence	Merger probability
	crop_55pct_resized_to_full				spiral galaxy			88,01%	8,68%
	crop_72pct_original_scale_black_canvas	irregular galaxy			80,03%	0,31%
	crop_72pct_original_scale_gray_canvas	spiral galaxy			64,72%	0,93%
	crop_72pct_resized_to_full				spiral galaxy			55,52%	4%
	crop_85pct_resized_to_full				irregular galaxy			85,24%	0,57%
	original_reference					irregular galaxy			97,40%	0,04%
	original_zoom_1.39x_centered			spiral galaxy			56,48%	3,88%
	
**ChatGPT:** 
	Observations:
	AstroVision's classification of the investigated galaxy is highly sensitive to image framing and apparent scale. 
	The original image is classified as Irregular Galaxy with 97.40% confidence. Cropping the image changes the predicted class to Spiral Galaxy, 
	while the merger probability increases from 0.04% to 8.68% for the tightest crop tested. Changes in grayscale, resolution, contrast, and mild blur have comparatively little effect. 
	In addition, changing the background of a cropped image from black to gray changes the predicted class from Irregular Galaxy to Spiral Galaxy. 
	These observations indicate that the model's predictions are not invariant to several image transformations that preserve the identity of the galaxy.
	
	It suggested going deeper into the question by
	- checking background sensitivity
	- Apparent scale
	- outer morphology
	
**my decision:** I agreed. I was curious. It generated the images, I uploaded the results:
	Image					predicted class	Confidence	Merger probability
	reference_original			irregular galaxy	97,40%	0,04%
	background_00_black			irregular galaxy	80,03%	0,31%
	background_01_dark_gray_16	irregular galaxy	79,68%	0,26%
	background_02_gray_32		spiral galaxy	64,72%	0,93%
	background_03_gray_48		spiral galaxy	80,10%	1,80%
	background_04_gray_64		spiral galaxy	82,93%	1,85%
	background_05_mid_gray_96	spiral galaxy	84,39%	1,61%
	
**ChatGPT:** 
	Observations:
	Merger probability vs. background brightness is not a monotonic relationship. It suggests that the model does not simply interpret brighter backgrounds as increasingly merger-like.
	Instead, the background seems to influence the output in a more complex way.
	
	Experiment	Main observation
	Image quality	Grayscale, resolution, contrast, and blur have little effect
	Cropping		Cropping changes the predicted class and increases merger probability
	Background	Changing the background alone changes the predicted class
	
	It wanted to dive deeper into the background.
	
**my decision:** let's change to the next experiment: apparent scale. ChatGPT cerated the images, I uploaded the results:
	Image				predicted class	Confidence	Merger probability
	original_reference		irregular galaxy	97,40%	0,04%
	apparent_scale_0.60x	irregular galaxy	97,61%	0,04%
	apparent_scale_0.75x	irregular galaxy	89,92%	0,27%
	apparent_scale_0.90x	irregular galaxy	53,34%	1,38%
	apparent_scale_1.00x	spiral galaxy	55,52%	4%
	apparent_scale_1.15x	spiral galaxy	79,12%	9,26%
	apparent_scale_1.30x	spiral galaxy	86,80%	9,45%
	apparent_scale_1.45x	spiral galaxy	80,32%	17,82%
	
**ChatGPT:** 
	Observations:
	Experiment B shows a strong, systematic dependence on apparent scale—much stronger than the effects you observed from grayscale, mild blur, or contrast changes.
	The classifier is not simply responding to the galaxy's overall identity. Its prediction is strongly affected by how much of the image the galaxy occupies.
	
	It wanted to dive deeper into this question.
	
**my decision:** I asked what visualisations it suggested for the results so far?

**ChatGPT:**
	It  suggested visualisations that show not only which class was predicted, but also how sensitive the prediction is to image transformations.
	It created the images.
	
**Prompt:** Summarise the findings.

**ChatGPT**
	1. Classification performance on 25 independent images (5 per class): AstroVision correctly classified 16 out of 25 images
	2. Important class confusions: The merger–irregular confusion is particularly notable.
	3. High confidence does not guarantee correctness
	4. Strong sensitivity to apparent scale and framing: There is a strong indication that the model's prediction depends on apparent scale and framing, not only on the underlying galaxy.
	However, these tests also change the amount of background around the galaxy. They therefore establish sensitivity to the combined scale-and-framing change, rather than isolating scale completely.
	5. Other image transformations: For this particular image, crop, framing, and background changes had a larger effect than mild image degradation.
	The experiments do not identify the exact internal mechanism. Background sensitivity, for example, could arise from the model's learned features, preprocessing, or their interaction.
		
	
	



