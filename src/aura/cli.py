"""The `aura` command:  aura --piccolo -1"""

from __future__ import annotations

import argparse
import os
import random
import re
import sys
from pathlib import Path
from typing import List, Optional

from PIL import Image

from . import __version__
from .addimg import add_pictures, collect
from .registry import bundled_dir, discover, user_dir
from .render import RAMPS, render
from .tuning import TUNING

DEFAULTS = dict(
    width=None, contrast=1.3, gamma=1.0, sharpen=1.5,
    ramp="dense", invert=False, color=False, crop=None,
)

_NUMBER_FLAG = re.compile(r"^-(\d+)$")
_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def expand_number_flags(argv: List[str]) -> List[str]:
    """Lets people type `-1` instead of `--variant 1`."""
    return [f"--variant={m.group(1)}" if (m := _NUMBER_FLAG.match(a)) else a for a in argv]


def build_parser(images) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="aura",
        description="✨ ASCII portraits for your terminal.",
        epilog=(
            "examples:\n"
            "  aura --piccolo -1\n"
            "  aura --piccolo                      (surprise me)\n"
            "  aura --piccolo -2 --width 200 --contrast 1.8 --color\n"
            "  aura --file ~/Downloads/pic.jpg     (try any picture, no setup)\n"
            "  aura add goku https://site.com/goku.jpg   (add your own - see: aura add -h)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    pick = p.add_mutually_exclusive_group()
    for name, variants in images.items():
        pick.add_argument(
            f"--{name}", dest="pick", action="store_const", const=name,
            help=f"show {name} ({len(variants)} picture{'s' if len(variants) != 1 else ''})",
        )

    p.add_argument("--variant", type=int, default=None, metavar="N",
                   help="which picture to show (shortcut: -1, -2, ...). Leave out for a random one")
    p.add_argument("--file", metavar="PATH_OR_URL", help="render any picture file or link")
    p.add_argument("--list", action="store_true", help="list everything available")

    look = p.add_argument_group("look & feel")
    look.add_argument("--width", type=int, help="characters per row (default: fit terminal)")
    look.add_argument("--contrast", type=float, help="1.0 = as-is, higher = punchier (default 1.3)")
    look.add_argument("--gamma", type=float, help=">1 darker, <1 brighter midtones (default 1.0)")
    look.add_argument("--sharpen", type=float, help="0 = off, 1.5 = crisp face details (default 1.5)")
    look.add_argument("--ramp", choices=sorted(RAMPS), help="character set (default dense)")
    look.add_argument("--invert", action=argparse.BooleanOptionalAction, default=None,
                      help="flip light/dark (use on light terminals)")
    look.add_argument("--color", action=argparse.BooleanOptionalAction, default=None,
                      help="colour the characters")
    look.add_argument("--crop", type=float, nargs=4, metavar=("L", "T", "R", "B"),
                      help="zoom in: left top right bottom as 0-1 fractions")
    look.add_argument("--out", metavar="FILE", help="also save the plain-text art to a file")

    p.add_argument("--version", action="version", version=f"aura {__version__}")
    return p


def build_add_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="aura add",
        description="Add your own pictures. They're numbered automatically, resized, "
                    "border-trimmed, and duplicates are skipped.",
        epilog=(
            "examples:\n"
            "  aura add goku https://site.com/goku.jpg\n"
            "  aura add goku ~/Downloads/goku.png\n"
            "  aura add goku ~/Downloads/goku-pack/     (a whole folder)\n"
            "  aura add goku --clipboard                (after right-click > Copy image)\n"
            f"\nSaved to: {user_dir()}  (change with the AURA_HOME env var)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("name", help="character name, lowercase letters/digits (becomes the --flag)")
    p.add_argument("sources", nargs="*", help="files, folders or http(s) links")
    p.add_argument("--clipboard", action="store_true", help="grab the image you just copied")
    p.add_argument("--no-trim", action="store_true", help="don't trim plain borders")
    p.add_argument("--bundle", action="store_true",
                   help="(for the maintainer) save into the package's own images folder")
    return p


def print_menu(images) -> None:
    print("✨ aura - ASCII portraits for your terminal\n")
    if not images:
        print("No pictures yet! Add one:  aura add piccolo <file-or-link>")
        return
    for name, variants in images.items():
        nums = ", ".join(f"-{n}" for n in sorted(variants))
        print(f"  aura --{name} {{{nums}}}")
    print("\nMore:  aura --help   |   aura add -h   |   aura --file <picture>")


def run_add(argv: List[str], images) -> int:
    args = build_add_parser().parse_args(argv)
    if args.bundle:
        if getattr(sys, "frozen", False):
            print("--bundle only works when running from the source code.", file=sys.stderr)
            return 2
        target = Path(str(bundled_dir()))
    else:
        target = user_dir()
    added = add_pictures(
        args.name.lower(), args.sources, target,
        existing=images.get(args.name.lower(), {}),
        clipboard=args.clipboard, trim=not args.no_trim,
    )
    if added:
        print(f"\nDone - {added} added to {target}")
    return 0 if added else 1


def main(argv: Optional[List[str]] = None) -> int:
    try:  # make block characters survive odd terminals
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    argv = list(sys.argv[1:] if argv is None else argv)
    images = discover()

    if argv and argv[0] == "add":
        return run_add(argv[1:], images)

    argv = expand_number_flags(argv)
    parser = build_parser(images)
    args = parser.parse_args(argv)

    if args.file:
        items = collect([args.file], clipboard=False)
        if not items:
            return 1
        img, tuning, label = items[0][1], {}, None
    else:
        if args.list or not args.pick:
            print_menu(images)
            return 0
        variants = images[args.pick]
        number = args.variant
        if number is None:
            number = random.choice(sorted(variants))
            label = f"{args.pick} -{number}"
        else:
            label = None
        if number not in variants:
            have = ", ".join(f"-{n}" for n in sorted(variants))
            parser.error(f"{args.pick} has no picture #{number} (available: {have})")
        with variants[number].open("rb") as fh:
            img = Image.open(fh)
            img.load()
        tuning = TUNING.get(args.pick, {})

    settings = {**DEFAULTS, **tuning}
    for key in settings:
        value = getattr(args, key)
        if value is not None:
            settings[key] = value

    if settings["color"] and os.name == "nt":
        os.system("")  # switches on ANSI colours in the Windows console

    art = render(img, **settings)
    print(art)
    if label:
        print(f"\n({label})", file=sys.stderr)

    if args.out:
        Path(args.out).write_text(_ANSI.sub("", art), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
