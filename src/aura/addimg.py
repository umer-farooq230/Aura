"""`aura add` - bring your own pictures without any manual file shuffling.

    aura add goku https://example.com/goku.jpg      # straight from a link
    aura add goku ~/Downloads/goku.png              # a file
    aura add goku ~/Downloads/goku-pack/            # a whole folder
    aura add goku --clipboard                       # right-click > "Copy image", then run this

Each picture is auto-numbered, shrunk to a sensible size, has plain borders
trimmed off, and is skipped if it's a duplicate of one you already have.
"""

from __future__ import annotations

import io
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image, ImageChops

NAME_RE = re.compile(r"^[a-z][a-z0-9]*$")
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
MAX_BYTES = 25 * 1024 * 1024
MAX_SIDE = 1200


# ---------- getting pictures in ----------

def fetch_url(url: str) -> Image.Image:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (aura)"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = resp.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("file is bigger than 25 MB")
    img = Image.open(io.BytesIO(data))
    img.load()
    return img


def grab_clipboard() -> List[Tuple[str, Image.Image]]:
    from PIL import ImageGrab

    got = ImageGrab.grabclipboard()
    if got is None:
        raise ValueError(
            "no image on the clipboard (on Linux this needs xclip or wl-clipboard installed)"
        )
    if isinstance(got, Image.Image):
        return [("clipboard", got)]
    out = []
    for path in got:  # copied files
        out.extend(load_path(Path(path)))
    return out


def load_path(path: Path) -> List[Tuple[str, Image.Image]]:
    if path.is_dir():
        out = []
        for f in sorted(path.iterdir()):
            if f.suffix.lower() in IMAGE_EXTS:
                out.extend(load_path(f))
        return out
    img = Image.open(path)
    img.load()
    return [(path.name, img)]


def collect(sources: List[str], clipboard: bool) -> List[Tuple[str, Image.Image]]:
    items: List[Tuple[str, Image.Image]] = []
    problems = []
    if clipboard:
        try:
            items.extend(grab_clipboard())
        except Exception as e:  # noqa: BLE001 - show any reason to the user
            problems.append(f"clipboard: {e}")
    for src in sources:
        try:
            if re.match(r"^https?://", src, re.I):
                items.append((src, fetch_url(src)))
            else:
                items.extend(load_path(Path(src).expanduser()))
        except Exception as e:  # noqa: BLE001
            problems.append(f"{src}: {e}")
    for p in problems:
        print(f"  ! could not read {p}", file=sys.stderr)
    return items


# ---------- tidying ----------

def trim_border(img: Image.Image, tol: int = 24, margin: float = 0.03) -> Image.Image:
    """Crop away a plain-colour border (white page, black bars...).

    Only acts when all four corners share one colour. Pictures with busy
    backgrounds are left alone - crop those by hand or with --crop.
    """
    img = img.convert("RGB")
    w, h = img.size
    corners = [img.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    bg = corners[0]
    if any(max(abs(a - b) for a, b in zip(bg, c)) > tol for c in corners[1:]):
        return img
    diff = ImageChops.difference(img, Image.new("RGB", img.size, bg)).convert("L")
    bbox = diff.point(lambda v: 255 if v > tol else 0).getbbox()
    if not bbox:
        return img
    l, t, r, b = bbox
    mx, my = int(w * margin), int(h * margin)
    box = (max(0, l - mx), max(0, t - my), min(w, r + mx), min(h, b + my))
    if (box[2] - box[0]) * (box[3] - box[1]) > 0.95 * w * h:
        return img
    return img.crop(box)


def ahash(img: Image.Image) -> int:
    """Tiny perceptual fingerprint - near-identical pictures get near-identical bits."""
    px = list(img.convert("L").resize((8, 8), Image.LANCZOS).tobytes())
    avg = sum(px) / 64
    return sum(1 << i for i, v in enumerate(px) if v > avg)


def is_duplicate(a: int, b: int, tolerance: int = 4) -> bool:
    return bin(a ^ b).count("1") <= tolerance


# ---------- the command ----------

def add_pictures(
    name: str,
    sources: List[str],
    target_dir: Path,
    existing: Dict[int, object],
    clipboard: bool = False,
    trim: bool = True,
) -> int:
    """Save pictures as <name>_<n>.jpg in target_dir. Returns how many were added."""
    if not NAME_RE.match(name):
        print("Names must be lowercase letters/digits and start with a letter (e.g. goku).", file=sys.stderr)
        return 0
    if not sources and not clipboard:
        print("Give me a file, folder, link, or use --clipboard.", file=sys.stderr)
        return 0

    items = collect(sources, clipboard)
    if not items:
        return 0

    # fingerprints of what we already have, so repeats get skipped
    seen = []
    for item in existing.values():
        try:
            with item.open("rb") as fh:
                im = Image.open(fh)
                im.load()
            seen.append(ahash(im))
        except Exception:  # noqa: BLE001
            pass

    target_dir.mkdir(parents=True, exist_ok=True)
    next_n = max(existing, default=0) + 1
    added = 0

    for label, img in items:
        img = img.convert("RGB")
        fp = ahash(img)
        if any(is_duplicate(fp, s) for s in seen):
            print(f"  = skipped {label} (already have it)")
            continue
        if trim:
            img = trim_border(img)
        if max(img.size) > MAX_SIDE:
            img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        dest = target_dir / f"{name}_{next_n}.jpg"
        img.save(dest, "JPEG", quality=90)
        seen.append(fp)
        print(f"  + {dest.name}  <- {label}   try: aura --{name} -{next_n}")
        next_n += 1
        added += 1
    return added
