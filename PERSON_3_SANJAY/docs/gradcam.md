# Grad-CAM Explainability (Phase 6)

## Purpose and Prerequisite

Grad-CAM was implemented after confirming that the trained ResNet-18 checkpoint
loads and supports CPU inference. It explains a fixed model prediction; it does
not alter training, labels, thresholds, or held-out evaluation.

## Method and Target Layer

The implementation captures activations and gradients from
`resnet.layer4[-1].conv2`. This is ResNet-18's final convolutional layer before
global average pooling and the classifier, retaining the deepest spatial features
that contribute to the final class logits. Gradients for the selected class weight
those activations; the positive weighted sum is resized to the original image and
rendered as a heatmap and semi-transparent overlay.

## Outputs

`generate_gradcam(image_path, model_path, output_dir)` returns the prediction,
explained class, target layer, warnings, and output paths. It saves original,
heatmap, and overlay PNGs when an output directory is supplied.

Measured Phase 4 categories allow examples for `img_050` (correct modified) and
`img_049` (false-positive original). No correctly classified original or false
negative existed in that held-out run, so no such example is claimed. Outputs and
the category record are in `results/gradcam/`.

## Interpretation and Limitations

Grad-CAM highlights regions contributing to the model's selected output. It does
not establish that a highlighted region was manipulated, that fraud occurred, or
that a transaction was fake. The map can emphasize text, layout, logos, borders,
or other irrelevant context. The baseline has a small, synthetic, imbalanced test
set and three observed false positives, so maps should be used only for cautious
qualitative inspection.
