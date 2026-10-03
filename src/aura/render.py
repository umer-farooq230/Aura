"""Image -> ASCII. Pure functions, no CLI stuff in here."""

from __future__ import annotations

import shutil
from typing import Optional, Sequence

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Ramps run from "most ink" to "least ink".
RAMPS = {
    "dense": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "simple": "@%#*+=-:. ",
    "blocks": "█▓▒░ ",
}

# Terminal cells are roughly twice as tall as they are wide.
CELL_ASPECT = 0.5


def default_width(cap: int = 160) -> int:
    return min(shutil.get_terminal_size((120, 40)).columns, cap)


def fit_width(img_w: int, img_h: int, cap: int = 160) -> int:
    """Widest size that fits the terminal's width AND height (tall pictures shrink)."""
    cols, rows = shutil.get_terminal_size((120, 40))
    by_height = int((rows - 3) * img_w / (img_h * CELL_ASPECT))
    return max(20, min(cols, cap, by_height))


def render(
    img: Image.Image,
    width: Optional[int] = None,
    contrast: float = 1.3,
    gamma: float = 1.0,
    sharpen: float = 1.5,
    ramp: str = "dense",
    invert: bool = False,
    color: bool = False,
    crop: Optional[Sequence[float]] = None,
) -> str:
    """Turn a PIL image into a string of ASCII art.

    width     characters per row (None = fit your terminal)
    contrast  1.0 = as-is, higher = punchier (eyes and outlines pop)
    gamma     >1 darkens midtones, <1 brightens them
    sharpen   0 = off, ~1.5 = good for faces
    ramp      one of RAMPS, or any string ordered dense -> sparse
    invert    flip it (use on light-background terminals)
    color     colour each character with the pixel's real colour (ANSI)
    crop      (left, top, right, bottom) as 0-1 fractions, to zoom in
    """
    img = ImageOps.exif_transpose(img).convert("RGB")

    if crop:
        left, top, right, bottom = crop
        w, h = img.size
        img = img.crop((int(left * w), int(top * h), int(right * w), int(bottom * h)))

    width = max(8, width or fit_width(img.width, img.height))
    height = max(1, round(img.height * width / img.width * CELL_ASPECT))
    small = img.resize((width, height), Image.LANCZOS)

    gray = ImageOps.autocontrast(small.convert("L"), cutoff=2)
    gray = Image.blend(gray, ImageOps.equalize(gray), 0.5)  # separates dark eyes from skin
    gray = ImageEnhance.Contrast(gray).enhance(contrast)
    if sharpen > 0:
        gray = gray.filter(ImageFilter.UnsharpMask(radius=1.2, percent=int(120 * sharpen), threshold=2))

    chars = RAMPS.get(ramp, ramp)
    n = len(chars) - 1
    gray_px = gray.tobytes()
    rgb_px = small.tobytes() if color else None

    lines = []
    for y in range(height):
        row = []
        for x in range(width):
            i = y * width + x
            v = (gray_px[i] / 255) ** gamma
            # Dark terminals: bright pixel -> dense char. Light terminals (--invert): the opposite.
            idx = round(v * n) if invert else round((1 - v) * n)
            ch = chars[idx]
            if color and ch != " ":
                r, g, b = rgb_px[i * 3 : i * 3 + 3]
                row.append(f"\x1b[38;2;{r};{g};{b}m{ch}")
            else:
                row.append(ch)
        line = "".join(row)
        lines.append(line + "\x1b[0m" if color else line.rstrip())

    return "\n".join(lines)
