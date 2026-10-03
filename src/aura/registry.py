"""Finds pictures: the ones shipped in the package + the ones you add yourself."""

from __future__ import annotations

import os
import re
from importlib.resources import files
from pathlib import Path
from typing import Dict

# Names that would clash with real CLI options / commands.
RESERVED = {
    "help", "version", "list", "variant", "width", "contrast", "gamma",
    "sharpen", "ramp", "invert", "no-invert", "color", "no-color", "crop", "out",
    "file", "add",
}

_PATTERN = re.compile(r"^([a-z][a-z0-9]*)(?:[_-](\d+))?\.(?:jpe?g|png|webp|bmp|gif)$", re.I)


def user_dir() -> Path:
    """Where `aura add` saves pictures. Override with the AURA_HOME env var."""
    base = os.environ.get("AURA_HOME")
    return (Path(base) if base else Path.home() / ".aura") / "images"


def bundled_dir():
    return files("aura") / "images"


def _parse(item):
    m = _PATTERN.match(item.name)
    if not m:
        return None
    name = m.group(1).lower()
    if name in RESERVED:
        return None
    return name, int(m.group(2)) if m.group(2) else None


def discover() -> Dict[str, Dict[int, object]]:
    """{'piccolo': {1: <file>, 2: <file>}, ...} - built from file names alone.

    Bundled pictures keep their numbers. Pictures from your own folder fill the
    next free numbers, so nothing ever overwrites anything.
    """
    found: Dict[str, Dict[int, object]] = {}

    root = bundled_dir()
    if root.is_dir():
        for item in sorted(root.iterdir(), key=lambda t: t.name):
            parsed = _parse(item)
            if parsed:
                name, num = parsed
                variants = found.setdefault(name, {})
                n = num or 1
                while n in variants:
                    n += 1
                variants[n] = item

    mine = user_dir()
    if mine.is_dir():
        for item in sorted(mine.iterdir(), key=lambda t: t.name):
            parsed = _parse(item)
            if parsed:
                name, num = parsed
                variants = found.setdefault(name, {})
                n = num or 1
                while n in variants:
                    n += 1
                variants[n] = item

    return found
