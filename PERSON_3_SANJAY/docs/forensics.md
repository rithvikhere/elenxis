# Image Forensics Prototype (Phase 5)

## Scope

This component supplies image-level evidence for academic inspection. It does not
verify a financial transaction, determine that a screenshot was manipulated, or
prove fraud.

## Error Level Analysis

ELA re-saves an RGB image as JPEG at a controlled quality (default 90), compares
the pixels, and saves an amplified difference visualisation. The result includes
mean, maximum, standard-deviation, and 95th-percentile absolute differences. These
are descriptive statistics, not a forensic or fraud probability.

Prior JPEG recompression, resizing, screenshots, messaging apps, and ordinary
editing can all create ELA differences. Therefore a bright region or a larger
summary value warrants inspection only; it does not establish malicious editing.

## Metadata and EXIF

The metadata inspector reports actual file format, dimensions, file size, image
information fields, EXIF fields, software value, and timestamps when available.
It never treats absent EXIF as manipulation evidence: screenshots and shared files
commonly contain no EXIF data.

## Interface and Examples

`forensic_analysis.analyze_image` returns separate `ela` and `metadata` evidence
with warnings and explanations. It contains no final decision or score. Example
ELA images and a measured summary for original, controlled edited, recompressed,
and resized examples are stored in `results/ela/`.
