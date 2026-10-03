from PIL import Image, ImageDraw

from aura.cli import expand_number_flags
from aura.render import render


def _face():
    im = Image.new("RGB", (200, 200), (120, 200, 60))
    d = ImageDraw.Draw(im)
    d.ellipse((50, 70, 90, 100), fill=(0, 0, 0))
    d.ellipse((110, 70, 150, 100), fill=(0, 0, 0))
    return im


def test_number_flags_expand():
    assert expand_number_flags(["--piccolo", "-1"]) == ["--piccolo", "--variant=1"]
    assert expand_number_flags(["--width", "100"]) == ["--width", "100"]


def test_render_shape():
    art = render(_face(), width=60)
    lines = art.split("\n")
    assert len(lines) == 30  # 200x200 at 0.5 cell aspect
    assert max(len(l) for l in lines) <= 60


def test_eyes_differ_from_skin():
    art = render(_face(), width=60, contrast=1.5)
    assert len(set(art.replace("\n", ""))) > 3


def test_color_emits_ansi():
    assert "\x1b[38;2;" in render(_face(), width=40, color=True)
