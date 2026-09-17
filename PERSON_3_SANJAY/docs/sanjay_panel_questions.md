# Person 3 Panel Questions: Concise Answers

## CNN and Training

- **What is a CNN?** A neural network designed to learn patterns from images.
- **What is convolution?** Applying a small learned filter across an image to detect local patterns.
- **What are kernels?** The learned small filters used by convolution.
- **What are feature maps?** The spatial outputs showing where a kernel responded.
- **Why ResNet18?** It is a manageable residual CNN with pretrained weights for this small baseline dataset.
- **What is transfer learning?** Starting from ImageNet features and fine-tuning them for this screenshot task.
- **Why pretrained weights?** They provide useful generic edge and texture features when labelled data is limited.
- **What is an epoch?** One full pass through the training set.
- **What is batch size?** Images processed together before one optimizer update; this run used 8.
- **What is learning rate?** The optimizer step size; this run used 0.0001.
- **What is loss?** A value measuring disagreement between model logits and labels; cross-entropy was used.
- **What is an optimizer?** The method updating weights to reduce loss; AdamW was used.
- **What is overfitting?** Learning the small training set too specifically and failing on new images.
- **How did you prevent leakage?** Each original receipt and its variants share a group and remain in one split only.

## Evaluation

- **Why accuracy?** It gives the overall fraction correct, but can mislead on imbalanced data.
- **Why precision?** Of modified predictions, it measures how many were actually modified.
- **Why recall?** Of modified examples, it measures how many were found.
- **Why F1?** It combines precision and recall in one value.
- **What is a confusion matrix?** A table of true versus predicted class counts.
- **What are TP/TN/FP/FN?** Correct modified, correct original, original predicted modified, and modified predicted original respectively.
- **What are false positives?** Original screenshots predicted modified; Phase 4 observed three.
- **What are false negatives?** Modified screenshots predicted original; Phase 4 observed zero.

## Forensics

- **What is ELA?** Comparison with a controlled JPEG recompression, visualised as amplified pixel differences.
- **Why JPEG recompression?** JPEG compression makes measurable pixel changes that can expose compression differences.
- **What can ELA show?** Regions or images with different recompression behaviour that warrant inspection.
- **Why is ELA not proof?** Resizing, sharing, screenshots, and normal editing can also change its appearance.
- **Why can screenshots have no EXIF?** Screenshot tools and messaging platforms commonly omit or strip it.
- **Why is missing EXIF not proof of fraud?** It is common normal metadata absence, not a manipulation finding.

## Grad-CAM

- **What does Grad-CAM show?** Regions that contributed to a selected ResNet-18 class output.
- **Why is it useful?** It helps qualitatively inspect what influenced the model.
- **Why is it not proof of manipulation?** Attention can fall on irrelevant layout or text and does not establish causation.

## Project Limits

- **Does it verify money was transferred?** No; it analyses the supplied screenshot only.
- **Can a CNN prove fraud?** No; it returns a learned-class prediction.
- **What happens when the model is wrong?** The result must be treated as uncertain and reviewed with other evidence.
- **Why combine CNN/rules/forensics?** Different signals can be complementary, but their combined value must be measured before claiming benefit.
