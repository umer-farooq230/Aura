"""Per-character defaults. Anything here beats the global defaults,
and anything typed on the command line beats this.

Keys: width, contrast, gamma, sharpen, ramp, invert, color, crop
crop = (left, top, right, bottom) as 0-1 fractions of the picture.

Example:
    "piccolo": {"crop": (0.25, 0.05, 0.75, 0.55), "gamma": 1.1, "contrast": 1.6},
"""

TUNING = {
    # "piccolo": {"crop": (0.25, 0.05, 0.75, 0.55), "gamma": 1.1, "contrast": 1.6},
}
